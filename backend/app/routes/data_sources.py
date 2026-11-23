
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.data_source import ExternalDatabaseCreate,ExternalDatabaseResponse


from app.services.external_database import (
    build_database_url,
    test_database_connection,
    create_connection_config,
    get_database_url_from_config,
    discover_database_schema,
)

from sqlalchemy.exc import SQLAlchemyError

from app.models.data_source import DataSource

from app.models.dataset import Dataset



router = APIRouter(prefix="/data-sources", tags=["Data Sources"])


@router.post("/test-connection")
def test_external_connection(
    request: ExternalDatabaseCreate,
    current_user: User = Depends(get_current_user),
):
    try:
        database_url = build_database_url(
            database_type=request.database_type,
            host=request.host,
            port=request.port,
            database=request.database,
            username=request.username,
            password=request.password,
        )

        test_database_connection(
            database_url,
            database_type=request.database_type,
            ssl_enabled=request.ssl_enabled,
        )

        return {
            "status": "success",
            "message": "Database connection successful.",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from None

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to connect to the external database. Check your connection details.",
        ) from None


@router.post(
    "/connect",
    response_model=ExternalDatabaseResponse,
    status_code=201,
)
def connect_external_database(
    request: ExternalDatabaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        connection_config = create_connection_config(
            database_type=request.database_type,
            host=request.host,
            port=request.port,
            database=request.database,
            username=request.username,
            password=request.password,
            ssl_enabled=request.ssl_enabled,
        )

        # Verify the connection before saving it.
        database_url = get_database_url_from_config(connection_config)
        test_database_connection(
            database_url,
            database_type=connection_config["database_type"],
            ssl_enabled=connection_config.get("ssl_enabled", False),
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to connect to the external database.",
        ) from None

    try:
        data_source = DataSource(
            user_id=current_user.id,
            source_type=request.database_type,
            source_name=request.source_name,
            file_path=None,
            connection_config=connection_config,
            connection_status="connected",
        )

        db.add(data_source)
        db.commit()
        db.refresh(data_source)

        return data_source

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save the database connection.",
        ) from None

@router.get("/", response_model=list[ExternalDatabaseResponse])
def list_external_databases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(DataSource)
        .filter(
            DataSource.user_id == current_user.id,
            DataSource.source_type.in_(["mysql", "postgresql"]),
        )
        .order_by(DataSource.created_at.desc())
        .all()
    )


@router.get("/{data_source_id}/schema")
def get_external_database_schema(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data_source = (
        db.query(DataSource)
        .filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id,
            DataSource.source_type.in_(["mysql", "postgresql"]),
        )
        .first()
    )

    if data_source is None:
        raise HTTPException(
            status_code=404,
            detail="External database connection not found.",
        )
    if data_source.connection_status != "connected":
        raise HTTPException(
            status_code=409,
            detail="This database is disconnected. Reconnect before accessing its schema.",
        )

    try:
        database_url = get_database_url_from_config(
            data_source.connection_config
        )
        schema = discover_database_schema(
            database_url,
            database_type=data_source.source_type,
            ssl_enabled=data_source.connection_config.get("ssl_enabled", False),
        )

        return {
            "data_source_id": data_source.id,
            "source_name": data_source.source_name,
            "schema": schema,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to discover the external database schema.",
        ) from None



@router.delete("/{data_source_id}")
def delete_external_database(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data_source = (
        db.query(DataSource)
        .filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id,
            DataSource.source_type.in_(["mysql", "postgresql"]),
        )
        .first()
    )

    if data_source is None:
        raise HTTPException(
            status_code=404,
            detail="External database connection not found.",
        )

    linked_datasets = (
        db.query(Dataset)
        .filter(
            Dataset.data_source_id == data_source_id,
            Dataset.user_id == current_user.id,
        )
        .first()
    )

    if linked_datasets:
        raise HTTPException(
            status_code=409,
            detail="This connection has linked datasets. Remove those datasets first.",
        )

    try:
        db.delete(data_source)
        db.commit()
        return {"message": "External database connection deleted successfully."}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to delete the database connection.",
        ) from None


@router.post("/{data_source_id}/disconnect")
def disconnect_external_database(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data_source = (
        db.query(DataSource)
        .filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id,
            DataSource.source_type.in_(["mysql", "postgresql"]),
        )
        .first()
    )

    if data_source is None:
        raise HTTPException(
            status_code=404,
            detail="External database connection not found.",
        )

    if data_source.connection_status == "disconnected":
        return {"message": "Database is already disconnected."}

    try:
        data_source.connection_status = "disconnected"
        db.commit()

        return {"message": "External database disconnected successfully."}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to disconnect the database.",
        ) from None



@router.post("/{data_source_id}/reconnect")
def reconnect_external_database(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data_source = (
        db.query(DataSource)
        .filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id,
            DataSource.source_type.in_(["mysql", "postgresql"]),
        )
        .first()
    )

    if data_source is None:
        raise HTTPException(
            status_code=404,
            detail="External database connection not found.",
        )

    try:
        database_url = get_database_url_from_config(
            data_source.connection_config
        )
        test_database_connection(
            database_url,
            database_type=data_source.source_type,
            ssl_enabled=data_source.connection_config.get("ssl_enabled", False),
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to reconnect. Check whether the external database is available.",
        ) from None

    try:
        data_source.connection_status = "connected"
        db.commit()

        return {"message": "External database reconnected successfully."}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update database connection status.",
        ) from None

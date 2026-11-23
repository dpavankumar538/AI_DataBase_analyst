
from sqlalchemy import create_engine, text

from app.models.data_source import DataSource
from app.services.external_database import (
    get_database_url_from_config,
    get_database_connect_args,
)
from app.services.sql_validator import (
    validate_read_only_sql,
    validate_allowed_tables,
)


MAX_RESULT_ROWS = 1000


def execute_external_query(
    db,
    user_id: int,
    data_source_id: int,
    query: str,
    allowed_tables: set[str],
) -> dict:
    """Execute a validated read-only query against an owned external database."""

    data_source = (
        db.query(DataSource)
        .filter(
            DataSource.id == data_source_id,
            DataSource.user_id == user_id,
            DataSource.source_type.in_(["mysql", "postgresql"]),
        )
        .first()
    )

    if data_source is None:
        raise ValueError("External data source not found.")

    if data_source.connection_status != "connected":
        raise ValueError(
            "This database is disconnected. Reconnect before running queries."
        )

    if not data_source.connection_config:
        raise ValueError("External database configuration is missing.")

    database_type = data_source.connection_config.get("database_type")

    validated_query = validate_read_only_sql(
        query,
        database_type,
    )

    validate_allowed_tables(
        validated_query,
        database_type,
        allowed_tables,
    )

    database_url = get_database_url_from_config(
        data_source.connection_config
    )

    ssl_enabled = data_source.connection_config.get(
        "ssl_enabled", False
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args=get_database_connect_args(
            database_type=database_type,
            ssl_enabled=ssl_enabled,
        ),
    )

    try:
        with engine.connect() as connection:
            result = connection.execute(text(validated_query))

            rows = result.mappings().fetchmany(MAX_RESULT_ROWS + 1)

            truncated = len(rows) > MAX_RESULT_ROWS
            rows = rows[:MAX_RESULT_ROWS]

            return {
                "columns": list(result.keys()),
                "rows": [dict(row) for row in rows],
                "row_count": len(rows),
                "truncated": truncated,
            }

    finally:
        engine.dispose()

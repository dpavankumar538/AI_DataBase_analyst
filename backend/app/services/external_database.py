
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL

from app.core.encryption import encrypt_secret, decrypt_secret
from app.services.host_validation import validate_database_host


SUPPORTED_DATABASES = {
    "mysql": {
        "driver": "mysql+pymysql",
        "default_port": 3306,
    },
    "postgresql": {
        "driver": "postgresql+psycopg",
        "default_port": 5432,
    },
}


def build_database_url(
    database_type: str,
    host: str,
    port: int | None,
    database: str,
    username: str,
    password: str,
) -> URL:
    """Build a SQLAlchemy URL for a supported external database."""

    config = SUPPORTED_DATABASES.get(database_type)

    if config is None:
        raise ValueError("Unsupported database type.")

    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Invalid database port.")

    host = validate_database_host(host)

    return URL.create(
        drivername=config["driver"],
        username=username,
        password=password,
        host=host,
        port=port or config["default_port"],
        database=database,
    )


def get_database_connect_args(
    database_type: str,
    ssl_enabled: bool = False,
) -> dict:
    """Build driver-specific connection arguments."""

    if database_type not in SUPPORTED_DATABASES:
        raise ValueError("Unsupported database type.")

    connect_args = {"connect_timeout": 5}

    if database_type == "mysql":
        if ssl_enabled:
            connect_args["ssl"] = {"check_hostname": True}

        return connect_args

    if database_type == "postgresql":
        if ssl_enabled:
            connect_args["sslmode"] = "require"

        return connect_args

    raise ValueError("Unsupported database type.")


def test_database_connection(
    database_url: URL,
    database_type: str,
    ssl_enabled: bool = False,
) -> bool:
    """Test an external database connection."""

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
            connection.exec_driver_sql("SELECT 1")

        return True

    finally:
        engine.dispose()


def discover_database_schema(
    database_url: URL,
    database_type: str,
    ssl_enabled: bool = False,
) -> dict:
    """Discover tables and columns in an external database."""

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args=get_database_connect_args(
            database_type=database_type,
            ssl_enabled=ssl_enabled,
        ),
    )

    try:
        inspector = inspect(engine)
        schema = {}

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)

            schema[table_name] = [
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "primary_key": column.get("primary_key", False),
                }
                for column in columns
            ]

        return schema

    finally:
        engine.dispose()


def create_connection_config(
    database_type: str,
    host: str,
    port: int | None,
    database: str,
    username: str,
    password: str,
    ssl_enabled: bool = False,
) -> dict:
    """Prepare external database configuration for secure storage."""

    if database_type not in SUPPORTED_DATABASES:
        raise ValueError("Unsupported database type.")

    if not all([host, database, username, password]):
        raise ValueError("Connection details cannot be empty.")

    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Invalid database port.")

    host = validate_database_host(host)

    return {
        "database_type": database_type,
        "host": host,
        "port": port or SUPPORTED_DATABASES[database_type]["default_port"],
        "database": database,
        "username": username,
        "encrypted_password": encrypt_secret(password),
        "ssl_enabled": ssl_enabled,
    }


def get_database_url_from_config(connection_config: dict) -> URL:
    """Rebuild an external database URL using encrypted credentials."""

    required_fields = [
        "database_type",
        "host",
        "database",
        "username",
        "encrypted_password",
    ]

    if not isinstance(connection_config, dict):
        raise ValueError("Invalid connection configuration.")

    if not all(connection_config.get(field) for field in required_fields):
        raise ValueError("Incomplete connection configuration.")

    database_type = connection_config["database_type"]

    if database_type not in SUPPORTED_DATABASES:
        raise ValueError("Unsupported database type.")

    password = decrypt_secret(
        connection_config["encrypted_password"]
    )

    return build_database_url(
        database_type=database_type,
        host=connection_config["host"],
        port=connection_config.get("port"),
        database=connection_config["database"],
        username=connection_config["username"],
        password=password,
    )

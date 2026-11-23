
from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import URL

from app.services import external_database

from cryptography.fernet import Fernet
from app.core import encryption


def test_build_mysql_url():
    url = external_database.build_database_url(
        database_type="mysql",
        host="localhost",
        port=3306,
        database="sales_db",
        username="admin",
        password="test@123",
    )

    assert url.drivername == "mysql+pymysql"
    assert url.host == "localhost"
    assert url.database == "sales_db"
    assert url.password == "test@123"


def test_build_postgresql_url():
    url = external_database.build_database_url(
        database_type="postgresql",
        host="localhost",
        port=5432,
        database="sales_db",
        username="admin",
        password="test123",
    )

    assert url.drivername == "postgresql+psycopg"
    assert url.port == 5432


def test_unsupported_database():
    with pytest.raises(ValueError, match="Unsupported"):
        external_database.build_database_url(
            database_type="mongodb",
            host="localhost",
            port=27017,
            database="test",
            username="admin",
            password="test",
        )


def test_database_connection_success(monkeypatch):
    mock_engine = MagicMock()
    mock_connection = MagicMock()

    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    monkeypatch.setattr(
        external_database,
        "create_engine",
        lambda *args, **kwargs: mock_engine,
    )

    url = URL.create("mysql+pymysql", username="admin", host="localhost")

    result = external_database.test_database_connection(url, "mysql" )

    assert result is True
    mock_connection.exec_driver_sql.assert_called_once_with("SELECT 1")
    mock_engine.dispose.assert_called_once()


def test_schema_discovery(monkeypatch):
    mock_engine = MagicMock()
    mock_inspector = MagicMock()

    mock_inspector.get_table_names.return_value = ["employees"]
    mock_inspector.get_columns.return_value = [
        {
            "name": "id",
            "type": "INTEGER",
            "nullable": False,
            "primary_key": True,
        },
        {
            "name": "name",
            "type": "VARCHAR(100)",
            "nullable": False,
            "primary_key": False,
        },
    ]

    monkeypatch.setattr(
        external_database,
        "create_engine",
        lambda *args, **kwargs: mock_engine,
    )

    monkeypatch.setattr(
        external_database,
        "inspect",
        lambda engine: mock_inspector,
    )

    url = URL.create("mysql+pymysql", username="admin", host="localhost")

    result = external_database.discover_database_schema(url, "mysql")

    assert "employees" in result
    assert len(result["employees"]) == 2
    assert result["employees"][0]["name"] == "id"
    mock_engine.dispose.assert_called_once()



@pytest.fixture
def encryption_key(monkeypatch):
    key = Fernet.generate_key().decode("utf-8")
    monkeypatch.setattr(encryption, "DB_ENCRYPTION_KEY", key)


def test_create_connection_config(encryption_key):
    config = external_database.create_connection_config(
        database_type="mysql",
        host="localhost",
        port=3306,
        database="sales_db",
        username="admin",
        password="MySecretPassword123",
    )

    assert config["database_type"] == "mysql"
    assert config["host"] == "localhost"
    assert config["username"] == "admin"
    assert config["encrypted_password"] != "MySecretPassword123"
    assert encryption.decrypt_secret(config["encrypted_password"]) == "MySecretPassword123"


def test_reconstruct_database_url(encryption_key):
    config = external_database.create_connection_config(
        database_type="postgresql",
        host="localhost",
        port=5432,
        database="sales_db",
        username="admin",
        password="MySecretPassword123",
    )

    url = external_database.get_database_url_from_config(config)

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "localhost"
    assert url.database == "sales_db"
    assert url.password == "MySecretPassword123"


def test_reject_incomplete_connection_config():
    with pytest.raises(ValueError, match="Incomplete"):
        external_database.get_database_url_from_config({
            "database_type": "mysql",
            "host": "localhost",
        })

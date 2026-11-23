
import pytest
from cryptography.fernet import Fernet

from app.core import encryption


@pytest.fixture
def test_key(monkeypatch):
    key = Fernet.generate_key().decode("utf-8")
    monkeypatch.setattr(encryption, "DB_ENCRYPTION_KEY", key)


def test_encrypt_decrypt_success(test_key):
    original = "MyDatabasePassword123"

    encrypted = encryption.encrypt_secret(original)
    decrypted = encryption.decrypt_secret(encrypted)

    assert encrypted != original
    assert decrypted == original


def test_decrypt_with_wrong_key(test_key, monkeypatch):
    encrypted = encryption.encrypt_secret("DatabasePassword123")

    wrong_key = Fernet.generate_key().decode("utf-8")
    monkeypatch.setattr(encryption, "DB_ENCRYPTION_KEY", wrong_key)

    with pytest.raises(ValueError, match="Unable to decrypt"):
        encryption.decrypt_secret(encrypted)


def test_encrypt_empty_secret(test_key):
    with pytest.raises(ValueError, match="cannot be empty"):
        encryption.encrypt_secret("")


def test_decrypt_invalid_token(test_key):
    with pytest.raises(ValueError, match="Unable to decrypt"):
        encryption.decrypt_secret("invalid-token")


def test_missing_encryption_key(monkeypatch):
    monkeypatch.setattr(encryption, "DB_ENCRYPTION_KEY", None)

    with pytest.raises(RuntimeError, match="missing"):
        encryption.encrypt_secret("DatabasePassword123")

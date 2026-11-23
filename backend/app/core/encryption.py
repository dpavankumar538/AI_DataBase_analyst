
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import DB_ENCRYPTION_KEY


def get_fernet() -> Fernet:
    """Create a Fernet encryption instance using the configured key."""
    if not DB_ENCRYPTION_KEY:
        raise RuntimeError("DB_ENCRYPTION_KEY is missing from .env")

    try:
        return Fernet(DB_ENCRYPTION_KEY.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise RuntimeError("DB_ENCRYPTION_KEY is invalid") from exc


def encrypt_secret(value: str) -> str:
    """Encrypt a sensitive value and return the encrypted token."""
    if not isinstance(value, str):
        raise TypeError("Secret must be a string")

    if not value:
        raise ValueError("Secret cannot be empty")

    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str) -> str:
    """Decrypt a Fernet token and return the original value."""
    if not isinstance(token, str) or not token:
        raise ValueError("Encrypted token must be a non-empty string")

    try:
        return get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise ValueError("Unable to decrypt the supplied value") from None

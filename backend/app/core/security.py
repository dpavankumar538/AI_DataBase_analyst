import bcrypt
import hashlib

_BCRYPT_MAX_BYTES = 72


def _enforce_bcrypt_limit(password: str) -> bytes:
    """Encode and enforce bcrypt's 72-byte UTF-8 limit."""
    encoded = password.encode("utf-8")
    if len(encoded) > _BCRYPT_MAX_BYTES:
        raise ValueError(
            f"Password exceeds bcrypt's {_BCRYPT_MAX_BYTES}-byte limit"
        )
    return encoded


def hash_password(password: str) -> str:
    password_bytes = _enforce_bcrypt_limit(password)
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        encoded = _enforce_bcrypt_limit(plain_password)
    except ValueError:
        return False
    return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


_BCRYPT_MAX_BYTES = 72


def _check_password_bytes(v: str) -> str:
    if len(v.encode("utf-8")) > _BCRYPT_MAX_BYTES:
        raise ValueError(
            f"Password must not exceed {_BCRYPT_MAX_BYTES} UTF-8 bytes"
        )
    return v


# User registration
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_bytes_limit(cls, v: str) -> str:
        return _check_password_bytes(v)


# User login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# User response
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str

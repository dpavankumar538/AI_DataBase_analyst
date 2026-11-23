from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password

from app.schemas.user import UserLogin, TokenResponse
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_current_user

from datetime import timedelta

from app.models.user_session import UserSession
from app.core.security import hash_refresh_token
from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS

import jwt

from app.core.config import SECRET_KEY, ALGORITHM
from app.schemas.user import RefreshTokenRequest

from app.core.time import utc_now

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    try:
        hashed_password = hash_password(user_data.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    try:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        refresh_token_hash = hash_refresh_token(refresh_token)
        expires_at = utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        user_session = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at
        )

        db.add(user_session)
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        raw_sub = payload.get("sub")
        if raw_sub is None or not str(raw_sub).isdigit():
            raise ValueError("Invalid subject claim")

        user_id = int(raw_sub)

        if user_id <= 0:
            raise ValueError("Invalid user ID")

    except HTTPException:
        raise

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    token_hash = hash_refresh_token(request.refresh_token)

    user_session = db.scalar(
        select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.refresh_token_hash == token_hash,
            UserSession.revoked_at.is_(None)
        )
    )

    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session not found or revoked"
        )

    current_time = utc_now()

    if user_session.expires_at <= current_time:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session expired"
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    try:
        result = db.execute(
            update(UserSession)
            .where(
                UserSession.id == user_session.id,
                UserSession.user_id == user_id,
                UserSession.refresh_token_hash == token_hash,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > current_time
            )
            .values(revoked_at=current_time)
            .execution_options(synchronize_session=False)
        )

        if result.rowcount != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token already used or session expired"
            )

        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)
        new_refresh_hash = hash_refresh_token(new_refresh_token)

        new_session = UserSession(
            user_id=user.id,
            refresh_token_hash=new_refresh_hash,
            expires_at=current_time + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        db.add(new_session)
        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh tokens"
        )


@router.post("/logout")
def logout_user(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        raw_sub = payload.get("sub")
        if raw_sub is None or not str(raw_sub).isdigit():
            raise ValueError("Invalid subject claim")

        user_id = int(raw_sub)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    token_hash = hash_refresh_token(request.refresh_token)

    user_session = db.scalar(
        select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.refresh_token_hash == token_hash,
            UserSession.revoked_at.is_(None)
        )
    )

    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or already logged out"
        )

    current_time = utc_now()

    if user_session.expires_at <= current_time:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )

    try:
        user_session.revoked_at = current_time
        db.commit()
        return {"message": "Logged out successfully"}

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

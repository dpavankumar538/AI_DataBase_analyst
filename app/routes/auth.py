
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password

##User login
from app.schemas.user import UserLogin, TokenResponse
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_current_user

from datetime import datetime, timedelta, timezone

from app.models.user_session import UserSession
from app.core.security import hash_refresh_token
from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS


import jwt

from app.core.config import SECRET_KEY, ALGORITHM
from app.schemas.user import RefreshTokenRequest

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
    # Check whether the email already exists
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create a new user
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
    # 1. Find user by email
    user = db.scalar(
        select(User).where(User.email == form_data.username)
    )

    # 2. Check whether user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 3. Verify password
    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    try:
        # 4. Generate access token
        access_token = create_access_token(user.id)

        # 5. Generate refresh token
        refresh_token = create_refresh_token(user.id)

        # 6. Hash refresh token before storing it
        refresh_token_hash = hash_refresh_token(refresh_token)

        # 7. Calculate refresh token expiration
        expires_at = (
            datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # 8. Create user session
        user_session = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at
        )

        # 9. Save session in database
        db.add(user_session)
        db.commit()

        # 10. Return tokens
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
    # 1. Decode and verify refresh token
    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # 2. Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = int(payload.get("sub"))

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # 3. Hash the received refresh token
    token_hash = hash_refresh_token(request.refresh_token)

    # 4. Find the matching active session
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

    # 5. Check session expiration
    if user_session.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session expired"
        )

    # 6. Check whether user exists
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    try:
        # 7. Revoke old session
        user_session.revoked_at = datetime.utcnow()

        # 8. Generate new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        # 9. Hash new refresh token
        new_refresh_hash = hash_refresh_token(new_refresh_token)

        # 10. Calculate new expiration
        new_expires_at = (
            datetime.utcnow()
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # 11. Create new session
        new_session = UserSession(
            user_id=user.id,
            refresh_token_hash=new_refresh_hash,
            expires_at=new_expires_at
        )

        db.add(new_session)
        db.commit()

        # 12. Return new tokens
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

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
    # 1. Decode and verify refresh token
    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # 2. Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = int(payload.get("sub"))

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # 3. Hash the refresh token
    token_hash = hash_refresh_token(request.refresh_token)

    # 4. Find the active session
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

    # 5. Check session expiration
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)

    if user_session.expires_at <= current_time:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )

    try:
        # 6. Revoke the session
        user_session.revoked_at = current_time

        db.commit()

        return {
            "message": "Logged out successfully"
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
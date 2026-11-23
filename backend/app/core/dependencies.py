
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import jwt

from app.database.dependencies import get_db
from app.models.user import User
from app.core.config import SECRET_KEY, ALGORITHM


oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Decode and verify JWT
        token = credentials.credentials
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Extract user ID and token type
        user_id = payload.get("sub")
        token_type = payload.get("type")

        # Validate token type and user ID
        if (
            token_type != "access"
            or not isinstance(user_id, str)
            or not user_id.isdigit()
            or int(user_id) <= 0
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )

        user_id = int(user_id)

    except HTTPException:
        raise

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    # Find user in database
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

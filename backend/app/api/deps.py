import uuid
from typing import Optional
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.models.user import User


async def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extracts bearer token from the Authorization header."""
    if not authorization:
        raise AuthenticationError("Authorization header is missing")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid Authorization header format. Expected 'Bearer <token>'")

    return parts[1]


async def get_current_user(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Validates bearer token and returns the authenticated User instance."""
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if not sub:
        raise AuthenticationError("Invalid token subject")

    try:
        user_id = uuid.UUID(sub)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token subject")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError("User not found or account inactive")

    return user


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """Optionally returns authenticated User if Authorization header is provided."""
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    try:
        payload = decode_access_token(parts[1])
        sub = payload.get("sub")
        if not sub:
            return None
        user_id = uuid.UUID(sub)
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    except Exception:
        return None


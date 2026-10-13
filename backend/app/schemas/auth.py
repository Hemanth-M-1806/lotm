import uuid
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserRead


class UserLogin(BaseModel):
    username_or_email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    type: str = "access"

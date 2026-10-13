import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPreferencesBase(BaseModel):
    theme: str = Field(default="backlund_dark", max_length=50)
    preferred_deck_style: str = Field(default="victorian_anime", max_length=50)
    default_spread: str = Field(default="three_card", max_length=50)


class UserPreferencesRead(UserPreferencesBase):
    user_id: uuid.UUID
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Alphanumeric, underscores, or dashes (3-50 characters)",
    )
    email: EmailStr = Field(..., max_length=255)
    display_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be between 8 and 128 characters",
    )


class UserRead(UserBase):
    id: uuid.UUID
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

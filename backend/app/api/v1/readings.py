import math
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_current_user
from app.core.database import get_db_session
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.reading import (
    ReadingCreate,
    ReadingFavoriteUpdate,
    ReadingRead,
)
from app.services.reading_service import (
    create_reading,
    get_reading_by_id,
    list_readings,
    update_reading_favorite,
)

router = APIRouter(prefix="/readings", tags=["Tarot Divination"])


@router.post(
    "",
    response_model=ReadingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate Tarot Reading",
    description="Draws cards with cryptographic randomness, synthesizes interpretation, and persists the reading.",
)
async def post_reading(
    reading_in: ReadingCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> ReadingRead:
    user_id = current_user.id if current_user else None
    reading = await create_reading(db, reading_in, user_id=user_id)
    return ReadingRead.model_validate(reading)


@router.get(
    "",
    response_model=PaginatedResponse[ReadingRead],
    status_code=status.HTTP_200_OK,
    summary="List User Readings",
    description="Lists paginated consultation history for the authenticated querent.",
)
async def get_readings_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite flag"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ReadingRead]:
    readings, total = await list_readings(
        db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        is_favorite=is_favorite,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse[ReadingRead](
        items=[ReadingRead.model_validate(r) for r in readings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{reading_id}",
    response_model=ReadingRead,
    status_code=status.HTTP_200_OK,
    summary="Get Reading by ID",
    description="Retrieves a consultation reading with cards and interpretation.",
)
async def get_single_reading(
    reading_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> ReadingRead:
    user_id = current_user.id if current_user else None
    reading = await get_reading_by_id(db, reading_id=reading_id, user_id=user_id)
    return ReadingRead.model_validate(reading)


@router.patch(
    "/{reading_id}/favorite",
    response_model=ReadingRead,
    status_code=status.HTTP_200_OK,
    summary="Toggle Reading Favorite",
    description="Marks or unmarks a reading as a favorite consultation.",
)
async def patch_reading_favorite(
    reading_id: uuid.UUID,
    fav_in: ReadingFavoriteUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ReadingRead:
    reading = await update_reading_favorite(
        db,
        reading_id=reading_id,
        user_id=current_user.id,
        is_favorite=fav_in.is_favorite,
    )
    return ReadingRead.model_validate(reading)

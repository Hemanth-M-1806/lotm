import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SpreadType(str, Enum):
    SINGLE_CARD = "single_card"
    THREE_CARD = "three_card"
    CELTIC_CROSS = "celtic_cross"


SPREAD_CONFIG = {
    SpreadType.SINGLE_CARD: [
        {"index": 0, "name": "Guidance"},
    ],
    SpreadType.THREE_CARD: [
        {"index": 0, "name": "Past / Cause"},
        {"index": 1, "name": "Present / Catalyst"},
        {"index": 2, "name": "Future / Outcome"},
    ],
    SpreadType.CELTIC_CROSS: [
        {"index": 0, "name": "Present Condition"},
        {"index": 1, "name": "Obstacle / Challenge"},
        {"index": 2, "name": "Subconscious Foundation"},
        {"index": 3, "name": "Recent Past"},
        {"index": 4, "name": "Conscious Goal"},
        {"index": 5, "name": "Near Future"},
        {"index": 6, "name": "The Querent / Attitude"},
        {"index": 7, "name": "External Environment"},
        {"index": 8, "name": "Hopes and Doubts"},
        {"index": 9, "name": "Ultimate Culmination"},
    ],
}


class TarotCardSummary(BaseModel):
    id: int
    name: str
    arcana_type: str
    card_number: int
    upright_meaning: str
    reversed_meaning: str
    mystical_lore: Optional[str] = None
    image_asset_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReadingCardRead(BaseModel):
    id: uuid.UUID
    card_id: int
    position_index: int
    position_name: str
    is_reversed: bool
    card_notes: Optional[str] = None
    card: Optional[TarotCardSummary] = None

    model_config = ConfigDict(from_attributes=True)


class ReadingCreate(BaseModel):
    spread_type: SpreadType = Field(
        default=SpreadType.THREE_CARD,
        description="Divination spread type (single_card, three_card, celtic_cross)",
    )
    question: Optional[str] = Field(
        None,
        max_length=500,
        description="Querent's question or focal thought",
    )


class ReadingRead(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    spread_type: str
    question: Optional[str] = None
    interpretation: Optional[str] = None
    is_favorite: bool
    created_at: datetime
    cards: List[ReadingCardRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReadingFavoriteUpdate(BaseModel):
    is_favorite: bool

import secrets
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, ValidationError
from app.models.card import TarotCard
from app.models.reading import Reading, ReadingCard
from app.schemas.reading import SPREAD_CONFIG, ReadingCreate, SpreadType


def _fisher_yates_sample(population: List[TarotCard], k: int) -> List[TarotCard]:
    """Cryptographically secure sampling of k unique items without replacement."""
    if k > len(population):
        raise ValidationError(f"Cannot draw {k} cards from a pool of {len(population)} cards.")

    pool = list(population)
    n = len(pool)
    for i in range(k):
        # Pick index uniformly from i to n - 1
        j = i + secrets.randbelow(n - i)
        pool[i], pool[j] = pool[j], pool[i]

    return pool[:k]


def synthesize_interpretation(
    spread_type: SpreadType,
    cards_with_meta: List[dict],
    question: Optional[str] = None,
) -> str:
    """Deterministically synthesizes mystical interpretation based on cards and spread positions."""
    lines = []
    if question:
        lines.append(f"Inquiry into the Fog of History: \"{question.strip()}\"")
        lines.append("")

    lines.append(f"Consultation Spread: {spread_type.value.replace('_', ' ').title()}")
    lines.append("The crimson moon casts light upon the symbols:")
    lines.append("")

    for item in cards_with_meta:
        card: TarotCard = item["card"]
        pos_name: str = item["position_name"]
        is_reversed: bool = item["is_reversed"]

        orientation = "Reversed" if is_reversed else "Upright"
        meaning = card.reversed_meaning if is_reversed else card.upright_meaning

        lines.append(f"• [{pos_name}] {card.name} ({orientation}):")
        lines.append(f"  {meaning}")
        if card.mystical_lore:
            lines.append(f"  Occult resonance: {card.mystical_lore}")
        lines.append("")

    lines.append(
        "Synthesis: The threads of fate converge. Heed the sequence progression and maintain rationality."
    )
    return "\n".join(lines)


async def create_reading(
    db: AsyncSession,
    reading_in: ReadingCreate,
    user_id: Optional[uuid.UUID] = None,
) -> Reading:
    """Executes a tarot reading ritual, drawing cards with cryptographic fairness."""
    spread_positions = SPREAD_CONFIG.get(reading_in.spread_type)
    if not spread_positions:
        raise ValidationError(f"Unsupported spread type: {reading_in.spread_type}")

    # Load canonical Major Arcana cards
    stmt = select(TarotCard).order_by(TarotCard.id)
    result = await db.execute(stmt)
    all_cards = list(result.scalars().all())

    if len(all_cards) < len(spread_positions):
        raise ValidationError("Insufficient canonical cards in the deck to perform the spread.")

    # Cryptographically secure draw without replacement
    drawn_cards = _fisher_yates_sample(all_cards, len(spread_positions))

    now = datetime.now(timezone.utc)
    reading = Reading(
        id=uuid.uuid4(),
        user_id=user_id,
        spread_type=reading_in.spread_type.value,
        question=reading_in.question.strip() if reading_in.question else None,
        is_favorite=False,
        created_at=now,
    )

    drawn_metadata = []
    reading_cards_list = []

    for pos, card in zip(spread_positions, drawn_cards):
        # 50% independent probability of card reversal
        is_reversed = secrets.randbelow(2) == 1
        rc = ReadingCard(
            id=uuid.uuid4(),
            reading_id=reading.id,
            card_id=card.id,
            position_index=pos["index"],
            position_name=pos["name"],
            is_reversed=is_reversed,
            created_at=now,
        )
        rc.card = card
        reading_cards_list.append(rc)
        drawn_metadata.append(
            {
                "card": card,
                "position_name": pos["name"],
                "is_reversed": is_reversed,
            }
        )

    reading.interpretation = synthesize_interpretation(
        spread_type=reading_in.spread_type,
        cards_with_meta=drawn_metadata,
        question=reading_in.question,
    )
    reading.cards = reading_cards_list

    db.add(reading)
    await db.commit()
    return reading


async def get_reading_by_id(
    db: AsyncSession,
    reading_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None,
) -> Reading:
    """Retrieves a reading by ID with strict ownership validation (anti-IDOR)."""
    stmt = (
        select(Reading)
        .options(selectinload(Reading.cards).selectinload(ReadingCard.card))
        .where(Reading.id == reading_id)
    )
    result = await db.execute(stmt)
    reading = result.scalar_one_or_none()

    if reading is None:
        raise NotFoundError("Reading not found")

    # Anti-IDOR: If reading is user-owned, query must match authenticated user
    if reading.user_id is not None and reading.user_id != user_id:
        raise NotFoundError("Reading not found")

    return reading


async def list_readings(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int = 1,
    page_size: int = 10,
    is_favorite: Optional[bool] = None,
) -> Tuple[List[Reading], int]:
    """Lists readings for the authenticated user with bounded pagination."""
    safe_page_size = min(max(page_size, 1), 50)
    safe_page = max(page, 1)
    offset = (safe_page - 1) * safe_page_size

    filters = [Reading.user_id == user_id]
    if is_favorite is not None:
        filters.append(Reading.is_favorite == is_favorite)

    count_stmt = select(func.count(Reading.id)).where(*filters)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar_one()

    query_stmt = (
        select(Reading)
        .options(selectinload(Reading.cards).selectinload(ReadingCard.card))
        .where(*filters)
        .order_by(Reading.created_at.desc())
        .offset(offset)
        .limit(safe_page_size)
    )
    result = await db.execute(query_stmt)
    readings = list(result.scalars().all())

    return readings, total


async def update_reading_favorite(
    db: AsyncSession,
    reading_id: uuid.UUID,
    user_id: uuid.UUID,
    is_favorite: bool,
) -> Reading:
    """Updates favorite flag on a user's reading with ownership validation."""
    reading = await get_reading_by_id(db, reading_id=reading_id, user_id=user_id)
    reading.is_favorite = is_favorite
    await db.commit()
    return reading

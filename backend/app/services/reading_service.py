import json
import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ValidationError
from app.models.card import TarotCard
from app.models.reading import Reading, ReadingCard
from app.schemas.reading import SPREAD_CONFIG, ReadingCreate, SpreadType

log = logging.getLogger(__name__)


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


# ---------------------------------------------------------------------------
# Per-card prediction templates keyed by (card_number, is_reversed)
# Provide real, actionable tarot guidance for each of the 22 Major Arcana.
# ---------------------------------------------------------------------------
_CARD_PREDICTIONS: dict[tuple[int, bool], str] = {
    # The Fool
    (0, False): "A bold new chapter is opening for you. Trust your instincts and take the leap — hesitation will cost you more than a mistake would. Something unexplored is calling; answer it.",
    (0, True):  "You may be rushing into something without enough preparation. Pause and ground yourself before committing. Check whether excitement is masking a lack of readiness.",
    # The Magician
    (1, False): "You already possess every resource, skill, and connection you need. Stop waiting for permission — take focused action now and watch circumstances bend to your will.",
    (1, True):  "Energy is being wasted or misdirected. Beware of someone using clever words to manipulate. Reconnect with your core intention before investing more effort.",
    # The High Priestess
    (2, False): "Something important is not yet visible on the surface. Listen to your deeper intuition rather than external noise. The answer you seek will surface through stillness.",
    (2, True):  "You are ignoring vital inner signals. Suppressed feelings or half-known truths are steering decisions unconsciously. Create space to hear what you already sense but will not say aloud.",
    # The Empress
    (3, False): "A period of growth, creativity, and abundance is flowering around you. Nurture your projects and relationships generously — what you tend now will bear significant fruit.",
    (3, True):  "Stagnation or overextension is draining your vitality. You may be smothering a situation by trying to control its growth. Step back and let things breathe.",
    # The Emperor
    (4, False): "Establish clear structure and boundaries. Taking charge with calm authority will resolve the current uncertainty. Build foundations now — stability you create today will protect you for years.",
    (4, True):  "Rigid control or abuse of authority is at the root of this difficulty. Either you or someone around you is leading through fear rather than strength. Flexibility is not weakness here.",
    # The Hierophant
    (5, False): "Seek guidance from an established mentor, tradition, or structured system. There is wisdom in proven methods — don't dismiss conventional paths out of pride.",
    (5, True):  "Blind adherence to rules or dogma is holding you back. Question the institution or belief that feels restrictive. Your personal truth may diverge from the accepted path.",
    # The Lovers
    (6, False): "A significant choice aligned with your deepest values is at hand. This may involve relationships, partnerships, or a moral crossroads. Choose from the heart — not from fear or habit.",
    (6, True):  "Misalignment of values is creating friction. A relationship or commitment is pulling you away from who you truly are. Honest examination is needed before things deepen further.",
    # The Chariot
    (7, False): "Victory is within reach if you harness your will and push forward with discipline. External obstacles can be overcome — the real test is maintaining inner focus under pressure.",
    (7, True):  "Aggression without direction is scattering your efforts. You may be forcing outcomes that require a different approach. Regroup, clarify your destination, then move.",
    # Strength
    (8, False): "Your greatest power right now lies in patience and inner composure — not force. Approach a difficult person or situation with quiet confidence and compassion. Endurance wins.",
    (8, True):  "Self-doubt or unmanaged fear is undermining you. Anxiety is posing as realism. Challenge the internal voice saying you are not enough; it is not telling the truth.",
    # The Hermit
    (9, False): "Withdraw from noise and seek your own counsel. A period of introspection will illuminate the answer far more effectively than seeking outside opinions. Solitude is productive now.",
    (9, True):  "Isolation has tipped into avoidance. You are withdrawing from connection and support you genuinely need. Re-engage carefully — vulnerability is not a trap here.",
    # Wheel of Fortune
    (10, False): "A significant turning point is in motion. Circumstances are shifting in your favour; be ready to move quickly when the opportunity presents itself. Cycles turn — your tide is rising.",
    (10, True): "Resistance to inevitable change is prolonging difficulty. Clinging to what no longer fits is the source of the stuck feeling. Release your grip and let the wheel turn.",
    # Justice
    (11, False): "A fair outcome is coming. Act with honesty and integrity — truth will surface and accountability will be served, whether you seek it or someone else does.",
    (11, True): "An imbalance or injustice is at play. You may be judging yourself too harshly, or someone else is not playing fair. Examine where bias — yours or another's — is distorting the picture.",
    # The Hanged Man
    (12, False): "The situation requires you to pause and see it from a completely new angle. Surrender the urge to act and let go of a fixed perspective — revelation is the gift of this suspension.",
    (12, True): "You are sacrificing too much without purpose or return. Martyrdom disguised as virtue is not noble here. Examine what you are giving away and why.",
    # Death
    (13, False): "A necessary ending is clearing space for transformation. Something must close — a relationship, a phase, a self-image — so that something truer can begin. Do not resist it.",
    (13, True): "Fear of change is keeping you locked in a decaying situation. The reluctance to let go is more costly than the ending itself. What are you clinging to that no longer serves life?",
    # Temperance
    (14, False): "Balance, patience, and measured synthesis are the keys right now. Avoid extremes. The blending of different elements — ideas, people, approaches — will produce something greater than any one part.",
    (14, True): "Excess or imbalance is causing harm. Something is being overdone — work, an emotion, a substance, a relationship dynamic. Recalibrate before the excess creates real damage.",
    # The Devil
    (15, False): "A pattern of unhealthy attachment, compulsion, or toxic dynamic is binding you more tightly than you realise. Name it clearly — awareness is the first step toward freedom.",
    (15, True): "You are awakening to a manipulation or self-destructive pattern and beginning to break free. The chains are real but loosening. Keep moving toward clarity and independence.",
    # The Tower
    (16, False): "A sudden disruption or revelation is imminent. Something built on false foundations will not survive — but what falls was never truly stable. Embrace the clearing, painful as it is.",
    (16, True): "You may be narrowly avoiding a collapse — or prolonging the inevitable by refusing to see cracks. Delayed reckoning accumulates interest. Face the instability now, on your terms.",
    # The Star
    (17, False): "After difficulty, genuine renewal and hope are available to you. Allow yourself to receive healing, rest, and inspiration. The dark period is passing — open to what is being offered.",
    (17, True): "Disillusionment or cynicism is blocking recovery. You have closed off from the possibility of better things. Identify where you stopped believing and gently challenge that conclusion.",
    # The Moon
    (18, False): "Illusion, anxiety, or confusion is distorting your perception of a situation. Do not make major decisions in the dark. Wait for clarity; not everything is as it appears.",
    (18, True): "Hidden fears are surfacing and can now be examined in the light. The paranoia or confusion that was running unconsciously is becoming visible — which means you can finally address it.",
    # The Sun
    (19, False): "Clarity, confidence, and genuine joy are accessible now. A situation that felt murky is becoming transparent. Let yourself celebrate and share your light — this energy is real.",
    (19, True): "Pride or over-optimism may be obscuring an important nuance. Joy can be genuine while still needing some tempering with realism. Check that enthusiasm is not blocking honest appraisal.",
    # Judgement
    (20, False): "A powerful calling or awakening is reaching you. Something from your past — a pattern, a wound, an unfinished chapter — is ready to be resolved and transcended. Answer the call.",
    (20, True): "Self-judgement or avoidance of accountability is keeping you trapped. You are refusing a reckoning that would ultimately free you. The longer the delay, the heavier it grows.",
    # The World
    (21, False): "A significant cycle is completing in your life. Wholeness, mastery, and earned fulfilment are available. Acknowledge how far you have come before rushing into whatever comes next.",
    (21, True): "Completion feels tantalizingly close but something keeps delaying it — fear of success, an unresolved loose end, or reluctance to fully commit. Identify what is holding you at the threshold.",
}

_DEFAULT_PREDICTION_UPRIGHT = "Trust the energy of this card — it points toward an area of your life calling for attention, growth, and conscious choice."
_DEFAULT_PREDICTION_REVERSED = "This card reversed signals inner resistance or a blocked energy. Reflect on where you may be avoiding or over-controlling the theme it represents."


def _get_card_prediction(card: TarotCard, is_reversed: bool) -> str:
    """Return a substantive, real-world tarot prediction for the given card and orientation."""
    key = (card.card_number, is_reversed)
    return _CARD_PREDICTIONS.get(key, _DEFAULT_PREDICTION_REVERSED if is_reversed else _DEFAULT_PREDICTION_UPRIGHT)


def _build_fallback_interpretation(
    spread_type: SpreadType,
    cards_with_meta: List[dict],
    question: Optional[str] = None,
) -> str:
    """Deterministic fallback interpretation used when the AI service is unavailable.

    Delivers genuine, substantive tarot predictions for each card rather than
    LOTM lore descriptions. The LOTM setting is present only as light framing.
    """
    lines = []
    if question:
        lines.append(f'Your question: "{question.strip()}"')
        lines.append("")

    lines.append(f"Spread: {spread_type.value.replace('_', ' ').title()}")
    lines.append("")

    # Per-card substantive predictions
    for item in cards_with_meta:
        card: TarotCard = item["card"]
        pos_name: str = item["position_name"]
        is_reversed: bool = item["is_reversed"]
        orientation = "Reversed" if is_reversed else "Upright"

        prediction = _get_card_prediction(card, is_reversed)

        lines.append(f"— {pos_name}: {card.name} ({orientation})")
        lines.append(f"  {prediction}")
        lines.append("")

    # Synthesis
    n = len(cards_with_meta)
    if n == 1:
        single = cards_with_meta[0]
        c: TarotCard = single["card"]
        lines.append(
            f"Overall Guidance: The {c.name} is your primary message. Sit with the prediction above "
            f"and ask yourself honestly where in your current life it applies most directly."
        )
    else:
        first_card: TarotCard = cards_with_meta[0]["card"]
        last_card: TarotCard = cards_with_meta[-1]["card"]
        lines.append(
            f"Overall Synthesis: Moving from the energy of {first_card.name} through to {last_card.name}, "
            f"the reading as a whole invites you to examine the connected threads above. "
            f"Where do these themes intersect in your life right now? The pattern they form together "
            f"is often more telling than any single card."
        )
    return "\n".join(lines)


def _build_ai_prompt(
    spread_type: SpreadType,
    cards_with_meta: List[dict],
    question: Optional[str] = None,
) -> str:
    """Constructs the prompt sent to the AI model.

    The prompt requests REAL tarot predictions — specific, actionable guidance
    about love, career, inner growth, decisions, relationships — not LOTM lore.
    The app's aesthetic is referenced as light framing only.
    """
    card_lines = []
    for item in cards_with_meta:
        card: TarotCard = item["card"]
        pos_name: str = item["position_name"]
        is_reversed: bool = item["is_reversed"]
        orientation = "Reversed" if is_reversed else "Upright"
        upright_m = card.upright_meaning
        reversed_m = card.reversed_meaning
        active_meaning = reversed_m if is_reversed else upright_m
        card_lines.append(
            f"  Position: {pos_name}\n"
            f"  Card: {card.name} ({orientation})\n"
            f"  Core meaning: {active_meaning}"
        )

    cards_block = "\n\n".join(card_lines)
    question_part = (
        f'The querent is asking: "{question.strip()}"\n'
        f"Address this question directly in your reading.\n\n"
    ) if question else "The querent has not posed a specific question — provide a general life guidance reading.\n\n"

    return (
        f"You are an expert tarot reader providing a genuine, substantive reading.\n"
        f"Your reading must give REAL predictions and practical guidance — not vague platitudes.\n\n"
        f"{question_part}"
        f"Spread type: {spread_type.value.replace('_', ' ').title()}\n\n"
        f"Cards drawn (in position order):\n\n{cards_block}\n\n"
        f"Write a detailed 4–6 paragraph tarot reading that:\n"
        f"1. Interprets EACH card in its specific position with genuine meaning — what it signals about "
        f"the querent's situation (love, career, relationships, inner life, decisions, timing).\n"
        f"2. Reveals HOW the cards interact and what story they collectively tell.\n"
        f"3. Provides SPECIFIC, actionable guidance — what the querent should do, avoid, or pay attention to.\n"
        f"4. Addresses the querent's question (if given) with a direct, honest answer drawn from the cards.\n"
        f"5. Ends with a clear synthesis of the overall message and the most important next step.\n\n"
        f"Tone: confident, warm, insightful. You may use slightly poetic language but prioritise CLARITY "
        f"and SPECIFICITY over mystical atmosphere. Do NOT pad with vague filler. "
        f"Do NOT repeat the card list or their raw meanings verbatim — interpret and apply them.\n"
        f"The app has a Victorian-occult aesthetic (Lord of the Mysteries universe) so you may use "
        f"occasional atmospheric language, but the substance must be grounded real tarot guidance."
    )


async def synthesize_interpretation(
    spread_type: SpreadType,
    cards_with_meta: List[dict],
    question: Optional[str] = None,
) -> str:
    """Calls OpenRouter (Gemma 3 27B free) to generate a mystical reading overview.

    Falls back gracefully to the deterministic synthesizer if the API is
    unavailable or the key is not configured.
    """
    settings = get_settings()

    if not settings.OPENROUTER_API_KEY:
        log.warning("OPENROUTER_API_KEY not set — using deterministic fallback interpretation.")
        return _build_fallback_interpretation(spread_type, cards_with_meta, question)

    prompt = _build_ai_prompt(spread_type, cards_with_meta, question)

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Hemanth-M-1806/lotm",
        "X-Title": "LOTM Tarot App",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                content=json.dumps(payload),
            )
            response.raise_for_status()
            data = response.json()
            ai_text: str = data["choices"][0]["message"]["content"].strip()
            return ai_text
    except Exception as exc:  # noqa: BLE001
        log.error("OpenRouter request failed (%s) — falling back to deterministic interpretation.", exc)
        return _build_fallback_interpretation(spread_type, cards_with_meta, question)


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

    reading.interpretation = await synthesize_interpretation(
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

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, ForeignKey, Index, SmallInteger, String, Text, UUID, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.card import TarotCard
    from app.models.user import User


class Reading(Base, TimestampMixin):
    __tablename__ = "readings"
    __table_args__ = (
        Index("idx_readings_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    spread_type: Mapped[str] = mapped_column(String(50), nullable=False)
    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interpretation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="readings")
    cards: Mapped[List["ReadingCard"]] = relationship(
        "ReadingCard",
        back_populates="reading",
        cascade="all, delete-orphan",
        order_by="ReadingCard.position_index"
    )


class ReadingCard(Base, TimestampMixin):
    __tablename__ = "reading_cards"
    __table_args__ = (
        UniqueConstraint("reading_id", "position_index", name="uq_reading_position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    reading_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("readings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    card_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("tarot_cards.id", ondelete="RESTRICT"),
        nullable=False
    )
    position_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    position_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_reversed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    card_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    reading: Mapped["Reading"] = relationship("Reading", back_populates="cards")
    card: Mapped["TarotCard"] = relationship("TarotCard", back_populates="reading_cards")

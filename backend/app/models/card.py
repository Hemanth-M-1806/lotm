from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.pathway import Pathway
    from app.models.reading import ReadingCard


class TarotCard(Base, TimestampMixin):
    __tablename__ = "tarot_cards"
    __table_args__ = (
        CheckConstraint("arcana_type IN ('major', 'minor')", name="chk_arcana_type"),
        CheckConstraint(
            "suit IS NULL OR suit IN ('wands', 'cups', 'swords', 'pentacles')",
            name="chk_card_suit"
        ),
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    arcana_type: Mapped[str] = mapped_column(String(10), nullable=False)
    suit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    card_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    pathway_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("pathways.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    upright_meaning: Mapped[str] = mapped_column(Text, nullable=False)
    reversed_meaning: Mapped[str] = mapped_column(Text, nullable=False)
    mystical_lore: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_asset_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    pathway: Mapped[Optional["Pathway"]] = relationship("Pathway", back_populates="cards")
    reading_cards: Mapped[List["ReadingCard"]] = relationship(
        "ReadingCard",
        back_populates="card"
    )

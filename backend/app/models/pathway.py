from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.card import TarotCard


class Pathway(Base, TimestampMixin):
    __tablename__ = "pathways"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    chinese_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    sequences: Mapped[List["Sequence"]] = relationship(
        "Sequence",
        back_populates="pathway",
        cascade="all, delete-orphan",
        order_by="Sequence.sequence_number.desc()"
    )
    cards: Mapped[List["TarotCard"]] = relationship(
        "TarotCard",
        back_populates="pathway"
    )


class Sequence(Base, TimestampMixin):
    __tablename__ = "sequences"
    __table_args__ = (
        UniqueConstraint("pathway_id", "sequence_number", name="uq_pathway_sequence"),
        CheckConstraint("sequence_number BETWEEN 0 AND 9", name="chk_sequence_number_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pathway_id: Mapped[int] = mapped_column(
        ForeignKey("pathways.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    sequence_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    acting_method_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    pathway: Mapped["Pathway"] = relationship("Pathway", back_populates="sequences")

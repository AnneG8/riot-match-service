from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .player import Player


class RankedEntry(Base, TimestampMixin):
    __tablename__ = 'ranked_entries'

    __table_args__ = (
        UniqueConstraint(
            'player_puuid',
            'queue_type',
            name='uq_ranked_entry_player_queue',
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    player_puuid: Mapped[str] = mapped_column(
        ForeignKey('players.puuid', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    queue_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )

    tier: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    rank: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
    )

    league_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    losses: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    raw_data: Mapped[dict] = mapped_column(
        JSONB,
    )

    player: Mapped[Player] = relationship(
        'Player',
        back_populates='ranked_entries',
    )

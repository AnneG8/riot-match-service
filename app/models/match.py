from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .match_participant import MatchParticipant


class Match(Base, TimestampMixin):
    __tablename__ = 'matches'

    match_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )

    queue_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    game_mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    game_version: Mapped[str] = mapped_column(
        String(32),
    )

    patch: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
    )

    game_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    raw_data: Mapped[dict] = mapped_column(
        JSONB,
    )

    participants: Mapped[list[MatchParticipant]] = relationship(
        'MatchParticipant',
        back_populates='match',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

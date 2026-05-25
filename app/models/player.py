from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .ranked_entry import RankedEntry


class Player(Base, TimestampMixin):
    __tablename__ = 'players'

    __table_args__ = (
        Index(
            'ix_players_game_name_tag_line',
            'game_name',
            'tag_line',
            postgresql_where=text(
                'game_name IS NOT NULL '
                'AND tag_line IS NOT NULL'
            ),
        ),
    )

    puuid: Mapped[str] = mapped_column(
        String(90),
        primary_key=True,
    )

    is_tracked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    game_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    tag_line: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summoner_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    profile_icon_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    ranked_entries: Mapped[list[RankedEntry]] = relationship(
        'RankedEntry',
        back_populates='player',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

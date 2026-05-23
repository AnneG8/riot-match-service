from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
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
        ),
    )

    puuid: Mapped[str] = mapped_column(
        String(90),
        primary_key=True,
    )

    game_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    tag_line: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    summoner_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    profile_icon_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    raw_data: Mapped[dict] = mapped_column(
        JSONB,
    )

    ranked_entries: Mapped[list[RankedEntry]] = relationship(
        'RankedEntry',
        back_populates='player',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

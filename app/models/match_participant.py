from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .match import Match
    from .player import Player


class MatchParticipant(Base, TimestampMixin):
    __tablename__ = 'match_participants'

    __table_args__ = (
        Index(
            'ix_match_participant_player_champion',
            'player_puuid',
            'champion_name',
        ),
        UniqueConstraint(
            'player_puuid',
            'match_id',
            name='uq_match_player_match_participant',
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    match_id: Mapped[str] = mapped_column(
        ForeignKey('matches.match_id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    player_puuid: Mapped[str] = mapped_column(
        ForeignKey('players.puuid'),
        nullable=False,
    )

    champion_name: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    team_position: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )

    kills: Mapped[int] = mapped_column(
        Integer,
    )

    deaths: Mapped[int] = mapped_column(
        Integer,
    )

    assists: Mapped[int] = mapped_column(
        Integer,
    )

    win: Mapped[bool] = mapped_column(
        Boolean,
    )

    gold_earned: Mapped[int] = mapped_column(
        Integer,
    )

    gold_spent: Mapped[int] = mapped_column(
        Integer,
    )

    total_damage_dealt: Mapped[int] = mapped_column(
        Integer,
    )

    total_damage_dealt_to_champions: Mapped[int] = mapped_column(
        Integer,
    )

    creep_score: Mapped[int] = mapped_column(
        Integer,
    )

    match: Mapped[Match] = relationship(
        'Match',
        back_populates='participants',
    )

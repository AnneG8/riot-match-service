from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Match, MatchParticipant

from .types import MatchData, MatchParticipantData


class MatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_latest_match_end(
        self,
        puuid: str,
    ) -> datetime | None:
        stmt = (
            select(func.max(Match.ended_at))
            .join(
                MatchParticipant,
                MatchParticipant.match_id == Match.match_id,
            )
            .where(MatchParticipant.player_puuid == puuid)
        )

        return await self.session.scalar(stmt)

    async def insert_match(self, match_data: MatchData) -> None:
        values = match_data.to_insert_dict(
            exclude={
                'created_at',
                'updated_at',
            },
        )

        stmt = insert(Match).values(**values)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=[Match.match_id],
        )

        await self.session.execute(stmt)

    async def insert_participants(
        self,
        participants_data: list[MatchParticipantData],
    ) -> None:
        if not participants_data:
            return

        values = [
            participant_data.to_insert_dict(
                exclude={
                    'id',
                    'created_at',
                    'updated_at',
                },
            ) for participant_data in participants_data
        ]

        stmt = insert(MatchParticipant).values(values)
        stmt = stmt.on_conflict_do_nothing(
            constraint='uq_match_participant_match_player',
        )

        await self.session.execute(stmt)

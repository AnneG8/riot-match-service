from datetime import datetime

from sqlalchemy import Float, Integer, cast, desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.dto import ChampionStatsDTO, MatchSummaryDTO
from app.enums import QueueId
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
            constraint='uq_match_player_match_participant',
        )

        await self.session.execute(stmt)

    async def get_recent_matches(
            self,
            puuid: str,
            *,
            limit: int = 20
    ) -> list[MatchSummaryDTO]:
        stmt = (
            select(MatchParticipant)
            .join(Match)
            .options(contains_eager(MatchParticipant.match))
            .where(MatchParticipant.player_puuid == puuid)
            .order_by(desc(Match.started_at))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        participants = result.scalars().all()

        return [
            MatchSummaryDTO.from_models(participant=participant)
            for participant in participants
        ]


    async def get_champion_stats(
            self,
            *,
            puuid: str,
            queue_id: QueueId | None = None,
            recent_matches: int = 20,
    ) -> list[ChampionStatsDTO]:
        recent_matches_subquery = (
            select(MatchParticipant.id)
            .join(
                Match,
                Match.match_id == MatchParticipant.match_id,
            )
            .where(MatchParticipant.player_puuid == puuid)
            .order_by(desc(Match.started_at))
            .limit(recent_matches)
        )

        if queue_id is not None:
            recent_matches_subquery = recent_matches_subquery.where(
                Match.queue_id == queue_id.value,
            )

        recent_matches_subquery = recent_matches_subquery.subquery()

        wins_expr = func.sum(cast(MatchParticipant.win, Integer))

        games_expr = func.count()

        average_kda_expr = func.avg(
            cast(MatchParticipant.kills + MatchParticipant.assists, Float)
            / func.greatest(MatchParticipant.deaths, 1)
        )

        stmt = (
            select(
                MatchParticipant.champion_name.label('champion_name'),
                games_expr.label('games'),
                wins_expr.label('wins'),
                (games_expr - wins_expr).label('losses'),
                (cast(wins_expr, Float) / games_expr * 100).label('win_rate'),
                func.avg(MatchParticipant.kills).label('average_kills'),
                func.avg(MatchParticipant.deaths).label('average_deaths'),
                func.avg(MatchParticipant.assists).label('average_assists'),
                average_kda_expr.label('average_kda'),
                func.avg(MatchParticipant.creep_score).label('average_cs'),
            )
            .where(MatchParticipant.id.in_(select(recent_matches_subquery.c.id)))
            .group_by(MatchParticipant.champion_name)
            .order_by(desc('games'),desc('win_rate'))
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            ChampionStatsDTO(
                champion_name=row.champion_name,
                games=row.games,
                wins=row.wins,
                losses=row.losses,
                win_rate=round(row.win_rate, 2),
                average_kills=round(row.average_kills, 2),
                average_deaths=round(row.average_deaths, 2),
                average_assists=round(row.average_assists, 2),
                average_kda=round(row.average_kda, 2),
                average_cs=round(row.average_cs, 2),
            )
            for row in rows
        ]

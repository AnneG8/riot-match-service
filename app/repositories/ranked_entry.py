from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RankedEntry

from .types import RankedEntryData


class RankedEntryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, entry_data: RankedEntryData) -> None:
        values = entry_data.to_insert_dict(
            exclude={
                'id',
                'created_at',
                'updated_at',
            }
        )

        stmt = insert(RankedEntry).values(**values)
        stmt = stmt.on_conflict_do_update(
            constraint='uq_ranked_entry_player_queue',
            set_={
                'tier': stmt.excluded.tier,
                'rank': stmt.excluded.rank,
                'league_points': stmt.excluded.league_points,
                'wins': stmt.excluded.wins,
                'losses': stmt.excluded.losses,
                'raw_data': stmt.excluded.raw_data,
                'updated_at': func.now(),
            },
        )

        await self.session.execute(stmt)

    async def upsert_entries(self, entries_data: list[RankedEntryData]) -> None:
        if not entries_data:
            return

        values = [
            entry_data.to_insert_dict(
                exclude={
                    'id',
                    'created_at',
                    'updated_at',
                },
            )
            for entry_data in entries_data
        ]

        stmt = insert(RankedEntry).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint='uq_ranked_entry_player_queue',
            set_={
                'tier': stmt.excluded.tier,
                'rank': stmt.excluded.rank,
                'league_points': stmt.excluded.league_points,
                'wins': stmt.excluded.wins,
                'losses': stmt.excluded.losses,
                'raw_data': stmt.excluded.raw_data,
                'updated_at': func.now(),
            },
        )

        await self.session.execute(stmt)

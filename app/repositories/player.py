from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player

from .types import PlayerData


class PlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_puuid(self, puuid: str) -> PlayerData | None:
        player = await self.session.get(Player, puuid)

        if player is None:
            return None

        return PlayerData.from_model(player)
        

    async def get_by_riot_id(
            self,
            *,
            game_name: str,
            tag_line: str,
    ) -> PlayerData | None:
        stmt = select(Player).where(
            Player.game_name == game_name,
            Player.tag_line == tag_line
        )

        result = await self.session.execute(stmt)
        player = result.scalar_one_or_none()

        if player is None:
            return None

        return PlayerData.from_model(player)

    async def create_untracked_players(self, puuids: list[str]) -> None:
        if not puuids:
            return

        values = [
            {'puuid': puuid}
            for puuid in puuids
        ]

        stmt = insert(Player).values(values)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=[Player.puuid],
        )

        await self.session.execute(stmt)

    async def upsert(self, player_data: PlayerData) -> None:
        values = player_data.to_insert_dict(
            exclude={
                'created_at',
                'updated_at',
            }
        )

        stmt = insert(Player).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Player.puuid],
            set_={
                'game_name': stmt.excluded.game_name,
                'tag_line': stmt.excluded.tag_line,
                'summoner_level': stmt.excluded.summoner_level,
                'profile_icon_id': stmt.excluded.profile_icon_id,
                'is_tracked': stmt.excluded.is_tracked,
                'last_synced_at': stmt.excluded.last_synced_at,
                'updated_at': func.now(),
            },
        )

        await self.session.execute(stmt)

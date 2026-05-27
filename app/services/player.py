from collections.abc import Callable

from app.constants import QueueId
from app.core import UnitOfWork
from app.services.dto import ChampionStatsDTO, MatchSummaryDTO, PlayerProfileDTO

from .sync import SyncService


class PlayerService:
    def __init__(
            self,
            *,
            uow_factory: Callable[[], UnitOfWork],
            sync_service: SyncService,
    ) -> None:
        self._uow_factory = uow_factory
        self._sync_service = sync_service

    async def find_player_by_riot_id(
            self,
            *,
            platform: str,
            game_name: str,
            tag_line: str,
    ) -> str:
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_riot_id(
                game_name=game_name,
                tag_line=tag_line,
            )

        if player is not None:
            return player.puuid

        puuid = await self._sync_service.sync_player_profile(
            platform=platform,
            game_name=game_name,
            tag_line=tag_line,
        )
        return puuid

    async def get_profile(self, puuid: str) -> PlayerProfileDTO | None:
        async with self._uow_factory() as uow:
            return await uow.players.get_by_puuid(puuid)

    async def get_recent_matches(
            self,
            *,
            puuid: str,
            limit: int = 20,
    ) -> list[MatchSummaryDTO]:
        async with self._uow_factory() as uow:
            return await uow.matches.get_recent_matches(puuid=puuid, limit=limit)

    async def get_champion_stats(
            self,
            *,
            puuid: str,
            queue_id: QueueId | None = None,
            recent_matches: int,
    ) -> list[ChampionStatsDTO]:
        async with self._uow_factory() as uow:
            return await uow.matches.get_champion_stats(
                puuid=puuid,
                queue_id=queue_id,
                recent_matches=recent_matches,
            )

from collections.abc import Callable

from app.constants import QueueId
from app.core import UnitOfWork
from app.services.dto import ChampionStatsDTO, MatchSummaryDTO, PlayerProfileDTO


class PlayerService:
    def __init__(self, *, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

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
                soloq_only=queue_id,
                recent_matches=recent_matches,
            )

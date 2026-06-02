from collections.abc import Callable

import structlog

from app.core import UnitOfWork
from app.dto import ChampionStatsDTO, MatchSummaryDTO, PlayerProfileDTO
from app.enums import Platform, QueueId

from .exceptions import PlayerNotFoundError
from .sync import SyncService

logger = structlog.get_logger(__name__)


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
            platform: Platform,
            game_name: str,
            tag_line: str,
    ) -> str:
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_riot_id(
                game_name=game_name,
                tag_line=tag_line,
            )

        if player is not None:
            logger.info(
                'player_found_in_db',
                game_name=game_name,
                tag_line=tag_line,
                puuid=player.puuid,
            )

            return player.puuid

        logger.info(
            'player_not_found_in_db',
            game_name=game_name,
            tag_line=tag_line,
        )

        puuid = await self._sync_service.sync_player_profile(
            platform=platform,
            game_name=game_name,
            tag_line=tag_line,
        )
        return puuid

    async def get_profile(self, puuid: str) -> PlayerProfileDTO | None:
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_puuid(puuid)
            if player is None:
                logger.warning(
                    'player_not_found',
                    puuid=puuid,
                )

                raise PlayerNotFoundError(puuid)

            return player

    async def get_recent_matches(
            self,
            *,
            puuid: str,
            limit: int = 20,
    ) -> list[MatchSummaryDTO]:
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_puuid(puuid)
            if player is None:
                logger.warning(
                    'player_not_found',
                    puuid=puuid,
                )

                raise PlayerNotFoundError(puuid)

            return await uow.matches.get_recent_matches(puuid=puuid, limit=limit)

    async def get_champion_stats(
            self,
            *,
            puuid: str,
            queue_id: QueueId | None = None,
            recent_matches: int,
    ) -> list[ChampionStatsDTO]:
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_puuid(puuid)
            if player is None:
                logger.warning(
                    'player_not_found',
                    puuid=puuid,
                )

                raise PlayerNotFoundError(puuid)

            return await uow.matches.get_champion_stats(
                puuid=puuid,
                queue_id=queue_id,
                recent_matches=recent_matches,
            )

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import structlog

from app.core import UnitOfWork
from app.enums import Platform
from app.integrations.riot import RiotAPIClient
from app.integrations.riot.exceptions import RiotNotFoundError
from app.mappers import MatchMapper, PlayerMapper, RankedEntryMapper, RegionMapper

logger = structlog.get_logger(__name__)


class SyncService:
    def __init__(
            self,
            *,
            uow_factory: Callable[[], UnitOfWork],
            riot_client: RiotAPIClient,
    ) -> None:
        self._uow_factory = uow_factory
        self.riot_client = riot_client

    async def sync_player_profile(
            self,
            *,
            platform: Platform,
            game_name: str,
            tag_line: str,
    ) -> str:
        logger.info(
            'player_profile_sync_started',
            platform=platform.value,
            game_name=game_name,
            tag_line=tag_line,
        )

        region = RegionMapper.from_platform(platform).value

        account = await self.riot_client.get_account_by_riot_id(
            region=region,
            game_name=game_name,
            tag_line=tag_line,
        )

        summoner = await self.riot_client.get_summoner_by_puuid(
            platform=platform,
            puuid=account.puuid,
        )

        player_data = PlayerMapper.from_riot(account=account, summoner=summoner)

        league_entries = await self.riot_client.get_league_entries_by_puuid(
            platform=platform,
            puuid=account.puuid,
        )

        logger.info(
            'player_profile_fetched',
            puuid=account.puuid,
            ranked_entries=len(league_entries),
        )

        ranked_entries = RankedEntryMapper.entries_from_riot(league_entries)

        async with self._uow_factory() as uow:
            player_data.last_synced_at = datetime.now(timezone.utc)
            await uow.players.upsert(player_data)

            await uow.ranked.upsert_entries(ranked_entries)

            logger.info(
                'player_profile_sync_finished',
                puuid=account.puuid,
            )

        return account.puuid

    async def sync_player_matches(
            self,
            *,
            platform: Platform,
            puuid: str,
    ) -> None:
        logger.info(
            'player_matches_sync_started',
            puuid=puuid,
            platform=platform.value,
        )

        region = RegionMapper.from_platform(platform)

        history_cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        async with self._uow_factory() as uow:
            latest_match_end = await uow.matches.get_latest_match_end(puuid)

        start_time = int(history_cutoff.timestamp())

        if latest_match_end is not None:
            start_time = max(
                int(latest_match_end.timestamp()) + 2,
                start_time,
            )

        logger.info(
            'player_matches_sync_window',
            puuid=puuid,
            start_time=start_time,
        )

        async for match_ids in self.riot_client.iter_match_id_pages(
            region=region,
            puuid=puuid,
            start_time=start_time,
        ):
            logger.info(
                'match_page_loaded',
                puuid=puuid,
                matches_count=len(match_ids),
            )

            saved_matches = 0
            skipped_matches = 0

            coros = [
                self.riot_client.get_match(region=region, match_id=match_id)
                for match_id in match_ids
            ]
            results = await asyncio.gather(*coros, return_exceptions=True)

            async with self._uow_factory() as uow:
                for result in results:
                    if isinstance(result, RiotNotFoundError):
                        continue

                    if isinstance(result, Exception):
                        raise result

                    match_data = MatchMapper.from_riot(result)

                    if match_data is None:
                        skipped_matches += 1
                        continue

                    participants_data = MatchMapper.participants_from_riot(
                        match_id=match_data.match_id,
                        participants=result.info.participants,
                    )

                    participant_puuids = [
                        participant.player_puuid
                        for participant in participants_data
                        if participant.player_puuid != puuid
                    ]

                    await uow.players.create_untracked_players(participant_puuids)
                    await uow.matches.insert_match(match_data)
                    await uow.matches.insert_participants(participants_data)

                    saved_matches += 1

            logger.info(
                'match_page_processed',
                puuid=puuid,
                matches_count=len(match_ids),
                saved_matches=saved_matches,
                skipped_matches=skipped_matches,
            )

        logger.info(
            'player_matches_sync_finished',
            puuid=puuid,
        )

    async def full_sync_player(
            self,
            *,
            platform: Platform,
            game_name: str,
            tag_line: str,
    ) -> None:
        puuid = await self.sync_player_profile(
            platform=platform,
            game_name=game_name,
            tag_line=tag_line,
        )

        await self.sync_player_matches(
            platform=platform,
            puuid=puuid,
        )

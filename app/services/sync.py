import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from app.core import UnitOfWork
from app.integrations.riot import RiotAPIClient
from app.integrations.riot.exceptions import RiotNotFoundError
from app.mappers import MatchMapper, PlayerMapper, RankedEntryMapper, RegionMapper


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
            platform: str,
            game_name: str,
            tag_line: str,
    ) -> str:
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

        ranked_entries = RankedEntryMapper.entries_from_riot(league_entries)

        async with self._uow_factory() as uow:
            player_data.last_synced_at = datetime.now(timezone.utc)
            await uow.players.upsert(player_data)

            await uow.ranked.upsert_entries(ranked_entries)
            
        return account.puuid

    async def sync_player_matches(
            self,
            *,
            platform: str,
            puuid: str,
    ) -> None:
        region = RegionMapper.from_platform(platform)

        history_cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        async with self._uow_factory() as uow:
            latest_match_end = await uow.matches.get_latest_match_end(puuid)
            
        if latest_match_end is None:
            latest_match_end = 0

        start_time = max(
            int(latest_match_end.timestamp()) + 2,
            int(history_cutoff.timestamp()),
        )

        async for match_ids in self.riot_client.iter_match_id_pages(
            region=region,
            puuid=puuid,
            start_time=start_time,
        ):
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

    async def full_sync_player(
            self,
            *,
            platform: str,
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

import asyncio
from collections.abc import Callable
from datetime import datetime, timezone

from app.core import UnitOfWork
from app.integrations.riot import RiotAPIClient
from app.integrations.riot.exceptions import RiotNotFoundError
from app.mappers import MatchMapper, PlayerMapper, RankedEntryMapper

from .utils import get_region_by_platform


class SyncService:
    def __init__(
            self,
            *,
            uow_factory: Callable[[], UnitOfWork],
            riot_client: RiotAPIClient,
    ) -> None:
        self._uow_factory = uow_factory
        self.riot_client = riot_client

    async def sync_player(
            self,
            *,
            platform: str,
            game_name: str,
            tag_line: str,
    ) -> None:
        region = get_region_by_platform(platform)
        
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
            await uow.players.upsert(player_data)

            await uow.ranked.upsert_entries(ranked_entries)

            latest_match_end = await uow.matches.get_latest_match_end(account.puuid)

        start_time = None
        if latest_match_end is not None:
            start_time = int(latest_match_end.timestamp())

        async for match_ids in self.riot_client.iter_match_id_pages(
            region=region,
            puuid=account.puuid,
            start_time=start_time,
        ):
            coros = [
                self.riot_client.get_match(
                    region=region,
                    match_id=match_id,
                )
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
                        if participant.player_puuid != account.puuid
                    ]

                    await uow.players.create_untracked_players(participant_puuids)

                    await uow.matches.insert_match(match_data)

                    await uow.matches.insert_participants(participants_data)

        async with self._uow_factory() as uow:
            player_data.last_synced_at = datetime.now(timezone.utc)

            await uow.players.upsert(player_data)

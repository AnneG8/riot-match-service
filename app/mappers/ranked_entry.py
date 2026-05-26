from app.integrations.riot.schemas import RiotRankedEntrySchema
from app.repositories.types import RankedEntryData


class RankedEntryMapper:
    @staticmethod
    def entry_from_riot(entry: RiotRankedEntrySchema) -> RankedEntryData:
        return RankedEntryData(
            player_puuid=entry.puuid,
            queue_type=entry.queue_type,
            tier=entry.tier,
            rank=entry.rank,
            league_points=entry.league_points,
            wins=entry.wins,
            losses=entry.losses,
            raw_data=entry.model_dump(mode='json'),
        )

    @staticmethod
    def entries_from_riot(
            entries: list[RiotRankedEntrySchema]
    ) -> list[RankedEntryData]:
        entries_data = [
            RankedEntryMapper.entry_from_riot(entry=entry)
            for entry in entries
        ]

        return entries_data

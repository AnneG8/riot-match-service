from app.integrations.riot.schemas import RiotRankedEntrySchema
from app.models import RankedEntry


def map_ranked_entry(
    *,
    player_puuid: str,
    entry: RiotRankedEntrySchema,
) -> RankedEntry:
    return RankedEntry(
        player_puuid=player_puuid,
        queue_type=entry.queue_type,
        tier=entry.tier,
        rank=entry.rank,
        league_points=entry.league_points,
        wins=entry.wins,
        losses=entry.losses,
        raw_data=entry.model_dump(mode='json'),
    )

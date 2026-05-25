from typing import Any

from app.integrations.riot.schemas import (
    RiotAccountSchema,
    RiotSummonerSchema,
)
from app.models import Player


def map_player(
    *,
    account: RiotAccountSchema,
    summoner: RiotSummonerSchema,
    is_tracked: bool = True,
) -> Player:
    return Player(
        puuid=account.puuid,
        game_name=account.game_name,
        tag_line=account.tag_line,
        summoner_level=summoner.summoner_level,
        profile_icon_id=summoner.profile_icon_id,
        is_tracked=is_tracked,
    )


def map_player_data(
    *,
    account: RiotAccountSchema,
    summoner: RiotSummonerSchema,
    is_tracked: bool = True,
) -> dict[str, Any]:
    player = account.model_dump()
    player.update(summoner.model_dump())
    player['is_tracked'] = is_tracked
    
    return player

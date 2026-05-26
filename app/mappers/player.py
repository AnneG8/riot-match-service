from app.integrations.riot.schemas import (
    RiotAccountSchema,
    RiotSummonerSchema,
)
from app.repositories.types import PlayerData


class PlayerMapper:
    @staticmethod
    def from_riot(
        *,
        account: RiotAccountSchema,
        summoner: RiotSummonerSchema,
        is_tracked: bool = True,
    ) -> PlayerData:
        return PlayerData(
            puuid=account.puuid,
            game_name=account.game_name,
            tag_line=account.tag_line,
            summoner_level=summoner.summoner_level,
            profile_icon_id=summoner.profile_icon_id,
            is_tracked=is_tracked,
        )

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator


class RiotBaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra='ignore',
    )


class RiotAccountSchema(RiotBaseSchema):
    puuid: str
    game_name: str = Field(alias='gameName')
    tag_line: str = Field(alias='tagLine')


class RiotSummonerSchema(RiotBaseSchema):
    puuid: str
    profile_icon_id: int = Field(alias='profileIconId')
    summoner_level: int = Field(alias='summonerLevel')


class RiotRankedEntrySchema(RiotBaseSchema):
    puuid: str
    queue_type: str = Field(alias='queueType')
    tier: str
    rank: str
    league_points: int = Field(alias='leaguePoints')
    wins: int
    losses: int


class RiotRankedEntriesSchema(RootModel[list[RiotRankedEntrySchema]]):
    pass


class RiotMatchesSchema(RootModel[list[str]]):
    pass


class RiotParticipantSchema(RiotBaseSchema):
    puuid: str
    champion_name: str = Field(alias='championName')
    team_position: str | None = Field(
        default=None,
        alias='teamPosition',
    )
    kills: int
    deaths: int
    assists: int
    win: bool
    gold_earned: int = Field(alias='goldEarned')
    gold_spent: int = Field(alias='goldSpent')
    total_damage_dealt: int = Field(alias='totalDamageDealt')
    total_damage_dealt_to_champions: int = Field(alias='totalDamageDealtToChampions')
    total_minions_killed: int = Field(alias='totalMinionsKilled')
    neutral_minions_killed: int = Field(alias='neutralMinionsKilled')


class RiotMatchInfoSchema(RiotBaseSchema):
    game_duration: int = Field(alias='gameDuration')
    start_time: datetime = Field(alias='gameStartTimestamp')
    end_time: datetime | None = Field(
        default=None,
        alias='gameEndTimestamp',
    )
    game_mode: str = Field(alias='gameMode')
    game_version: str = Field(alias='gameVersion')
    queue_id: int = Field(alias='queueId')
    participants: list[RiotParticipantSchema]

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def parse_timestamp(cls, value: int) -> datetime:
        return datetime.fromtimestamp(value / 1000 - 1, tz=UTC)


class RiotMatchSchema(RiotBaseSchema):
    info: RiotMatchInfoSchema

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import Platform


class PlayerRequest(BaseModel):
    platform: Platform
    game_name: str = Field(max_length=50)
    tag_line: str = Field(max_length=50)


class FindPlayerResponse(BaseModel):
    puuid: str


class RankedEntryResponse(BaseModel):
    queue_type: str
    tier: str
    rank: str | None
    league_points: int
    wins: int
    losses: int

    model_config = ConfigDict(from_attributes=True)


class PlayerProfileResponse(BaseModel):
    puuid: str
    game_name: str | None
    tag_line: str | None

    summoner_level: int | None
    profile_icon_id: int | None

    ranked_entries: list[RankedEntryResponse]

    model_config = ConfigDict(from_attributes=True)


class MatchSummaryResponse(BaseModel):
    match_id: str
    queue_id: int
    game_mode: str
    game_patch: str
    started_at: datetime
    game_duration: int

    champion_name: str
    team_position: str | None

    kills: int
    deaths: int
    assists: int

    win: bool

    model_config = ConfigDict(from_attributes=True)


class ChampionStatsResponse(BaseModel):
    champion_name: str

    games: int
    wins: int
    losses: int
    win_rate: float

    average_kills: float
    average_deaths: float
    average_assists: float

    average_kda: float
    average_cs: float

    model_config = ConfigDict(from_attributes=True)

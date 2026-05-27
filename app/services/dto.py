from dataclasses import dataclass
from datetime import datetime
from typing import Self

from app.models import MatchParticipant, Player, RankedEntry


@dataclass(slots=True)
class RankedEntryDTO:
    queue_type: str
    tier: str
    rank: str
    league_points: int
    wins: int
    losses: int

    @classmethod
    def from_model(cls, ranked_entry: RankedEntry) -> Self:
        return cls(
            queue_type=ranked_entry.queue_type,
            tier=ranked_entry.tier,
            rank=ranked_entry.rank,
            league_points=ranked_entry.league_points,
            wins=ranked_entry.wins,
            losses=ranked_entry.losses,
        )


@dataclass(slots=True)
class PlayerProfileDTO:
    puuid: str
    game_name: str | None
    tag_line: str | None
    summoner_level: int | None
    profile_icon_id: int | None
    ranked_entries: list[RankedEntryDTO]

    @classmethod
    def from_model(cls, player: Player) -> Self:
        return cls(
            puuid=player.puuid,
            game_name=player.game_name,
            tag_line=player.tag_line,
            summoner_level=player.summoner_level,
            profile_icon_id=player.profile_icon_id,
            ranked_entries=[
                RankedEntryDTO.from_model(entry) for entry in player.ranked_entries
            ],
        )


@dataclass(slots=True)
class MatchSummaryDTO:
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

    @classmethod
    def from_models(cls, *, participant: MatchParticipant) -> Self:
        match = participant.match

        return cls(
            match_id=match.match_id,
            queue_id=match.queue_id,
            game_mode=match.game_mode,
            game_patch=match.game_patch,
            started_at=match.started_at,
            game_duration=match.game_duration,
            champion_name=participant.champion_name,
            team_position=participant.team_position,
            kills=participant.kills,
            deaths=participant.deaths,
            assists=participant.assists,
            win=participant.win,
        )

    
@dataclass(slots=True)
class ChampionStatsDTO:
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
    
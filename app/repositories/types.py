from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Self

from app.models import Match, MatchParticipant, Player, RankedEntry


@dataclass(slots=True)
class BaseData:
    def to_insert_dict(
        self,
        *,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        values = asdict(self)

        exclude = exclude or set()

        for field in exclude:
            values.pop(field, None)

        return values


@dataclass(slots=True)
class PlayerData(BaseData):
    puuid: str
    game_name: str | None
    tag_line: str | None
    summoner_level: int | None
    profile_icon_id: int | None
    is_tracked: bool = False
    last_synced_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_model(cls, player: Player) -> Self:
        return cls(
            puuid=player.puuid,
            game_name=player.game_name,
            tag_line=player.tag_line,
            summoner_level=player.summoner_level,
            profile_icon_id=player.profile_icon_id,
            is_tracked=player.is_tracked,
            last_synced_at=player.last_synced_at,
            created_at=player.created_at,
            updated_at=player.updated_at,
        )


@dataclass(slots=True)
class RankedEntryData(BaseData):
    player_puuid: str
    queue_type: str
    tier: str
    rank: str
    league_points: int
    wins: int
    losses: int
    raw_data: dict[str, Any]

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_model(cls, ranked_entry: RankedEntry) -> Self:
        return cls(
            id=ranked_entry.id,
            player_puuid=ranked_entry.player_puuid,
            queue_type=ranked_entry.queue_type,
            tier=ranked_entry.tier,
            rank=ranked_entry.rank,
            league_points=ranked_entry.league_points,
            wins=ranked_entry.wins,
            losses=ranked_entry.losses,
            raw_data=ranked_entry.raw_data,
            created_at=ranked_entry.created_at,
            updated_at=ranked_entry.updated_at,
        )


@dataclass(slots=True)
class MatchData(BaseData):
    match_id: str
    queue_id: int
    game_mode: str
    game_patch: str
    game_duration: int
    started_at: datetime
    ended_at: datetime
    raw_data: dict[str, Any]

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_model(cls, match: Match) -> Self:
        return cls(
            match_id=match.match_id,
            queue_id=match.queue_id,
            game_mode=match.game_mode,
            game_patch=match.game_patch,
            game_duration=match.game_duration,
            started_at=match.started_at,
            ended_at=match.ended_at,
            raw_data=match.raw_data,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )


@dataclass(slots=True)
class MatchParticipantData(BaseData):
    match_id: str
    player_puuid: str
    champion_name: str
    team_position: str | None
    kills: int
    deaths: int
    assists: int
    win: bool
    gold_earned: int
    gold_spent: int
    total_damage_dealt: int
    total_damage_dealt_to_champions: int
    creep_score: int

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_model(cls, participant: MatchParticipant) -> Self:
        return cls(
            id=participant.id,
            match_id=participant.match_id,
            player_puuid=participant.player_puuid,
            champion_name=participant.champion_name,
            team_position=participant.team_position,
            kills=participant.kills,
            deaths=participant.deaths,
            assists=participant.assists,
            win=participant.win,
            gold_earned=participant.gold_earned,
            gold_spent=participant.gold_spent,
            total_damage_dealt=participant.total_damage_dealt,
            total_damage_dealt_to_champions=(
                participant.total_damage_dealt_to_champions
            ),
            creep_score=participant.creep_score,
            created_at=participant.created_at,
            updated_at=participant.updated_at,
        )

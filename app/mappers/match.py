from app.integrations.riot.schemas import (
    RiotMatchSchema,
    RiotParticipantSchema,
)
from app.models import Match, MatchParticipant


def map_match(match_data: RiotMatchSchema) -> Match | None:
    info = match_data.info

    if info.end_time is None:
        return None

    return Match(
        match_id=match_data.metadata.match_id,
        queue_id=info.queue_id,
        game_mode=info.game_mode,
        game_patch=_extract_patch(info.game_version),
        game_duration=info.game_duration,
        started_at=info.start_time,
        ended_at=info.end_time,
        raw_data=match_data.model_dump(mode='json'),
    )


def map_match_participant(
    *,
    match_id: str,
    participant: RiotParticipantSchema,
) -> MatchParticipant:
    return MatchParticipant(
        match_id=match_id,
        player_puuid=participant.puuid,
        champion_name=participant.champion_name,
        team_position=participant.team_position,
        kills=participant.kills,
        deaths=participant.deaths,
        assists=participant.assists,
        win=participant.win,
        gold_earned=participant.gold_earned,
        gold_spent=participant.gold_spent,
        total_damage_dealt=participant.total_damage_dealt,
        total_damage_dealt_to_champions=participant.total_damage_dealt_to_champions,
        creep_score=(
            participant.total_minions_killed
            + participant.neutral_minions_killed
        ),
    )


def _extract_patch(version: str) -> str:
    parts = version.split('.')

    if len(parts) < 2:
        return version

    return f'{parts[0]}.{parts[1]}'

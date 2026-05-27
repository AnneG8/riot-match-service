from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.dependencies import get_player_service
from app.api.schemas.player import (
    ChampionStatsResponse,
    FindPlayerResponse,
    MatchSummaryResponse,
    PlayerProfileResponse,
    PlayerRequest,
)
from app.enums import QueueId
from app.services import PlayerService

router = APIRouter(prefix='/players', tags=['players'])


@router.get('/by-riot-id', response_model=FindPlayerResponse)
async def find_player_by_riot_id(
    query: PlayerRequest = Depends(),
    service: PlayerService = Depends(get_player_service),
):
    puuid = await service.find_player_by_riot_id(
        platform=query.platform,
        game_name=query.game_name,
        tag_line=query.tag_line,
    )

    return {'puuid': puuid}


@router.get('/{puuid}', response_model=PlayerProfileResponse)
async def get_profile(
    puuid: Annotated[str, Path(min_length=60, max_length=90)],
    service: PlayerService = Depends(get_player_service),
):
    return await service.get_profile(puuid)


@router.get('/{puuid}/matches', response_model=list[MatchSummaryResponse])
async def get_recent_matches(
    puuid: Annotated[str, Path(min_length=60, max_length=90)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    service: PlayerService = Depends(get_player_service),
):
    return await service.get_recent_matches(
        puuid=puuid,
        limit=limit,
    )


@router.get('/{puuid}/champions', response_model=list[ChampionStatsResponse])
async def get_champion_stats(
    puuid: Annotated[str, Path(min_length=60, max_length=90)],
    recent_matches: Annotated[int, Query(ge=1, le=50)] = 20,
    service: PlayerService = Depends(get_player_service),
):
    queue_id = QueueId.SOLOQ

    return await service.get_champion_stats(
        puuid=puuid,
        queue_id=queue_id,
        recent_matches=recent_matches,
    )
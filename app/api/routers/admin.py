import asyncio

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_sync_service
from app.api.schemas.player import PlayerRequest
from app.services import SyncService

router = APIRouter(prefix='/admin', tags=['admin'])


@router.post('/players/sync', status_code=status.HTTP_202_ACCEPTED)
async def sync_player(
    data: PlayerRequest,
    request: Request,
    service: SyncService = Depends(get_sync_service),
):
    task = asyncio.create_task(
        service.full_sync_player(
            platform=data.platform,
            game_name=data.game_name,
            tag_line=data.tag_line,
        ),
        name=f'sync-{data.game_name}-{data.tag_line}',
    )

    request.app.state.background_tasks.add(task)
    task.add_done_callback(request.app.state.background_tasks.discard)

    return {'status': 'sync_started'}

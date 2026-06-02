import asyncio

import structlog
from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_sync_service
from app.api.schemas.player import PlayerRequest
from app.services import SyncService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix='/admin', tags=['admin'])


@router.post('/players/sync', status_code=status.HTTP_202_ACCEPTED)
async def sync_player(
    data: PlayerRequest,
    request: Request,
    service: SyncService = Depends(get_sync_service),
):
    logger.info(
        'background_sync_requested',
        platform=data.platform.value,
        game_name=data.game_name,
        tag_line=data.tag_line,
    )

    task = asyncio.create_task(
        service.full_sync_player(
            platform=data.platform,
            game_name=data.game_name,
            tag_line=data.tag_line,
        ),
        name=f'sync-{data.game_name}-{data.tag_line}',
    )

    request.app.state.background_tasks.add(task)

    task.add_done_callback(_task_done)
    task.add_done_callback(request.app.state.background_tasks.discard)

    return {'status': 'sync_started'}


def _task_done(task: asyncio.Task) -> None:
    try:
        task.result()

        logger.info(
            'background_sync_finished',
            task_name=task.get_name(),
        )

    except Exception as exc:
        logger.exception(
            'background_sync_failed',
            task_name=task.get_name(),
            error_type=type(exc).__name__,
        )

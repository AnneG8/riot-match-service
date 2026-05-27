from collections.abc import Callable

from fastapi import Depends, Request

from app.core import UnitOfWork
from app.core.database import async_session_factory
from app.integrations.riot import RiotAPIClient
from app.services import PlayerService, SyncService


def get_riot_client(request: Request) -> RiotAPIClient:
    return request.app.state.riot_client


def get_uow_factory() -> Callable[[], UnitOfWork]:
    def factory() -> UnitOfWork:
        return UnitOfWork(async_session_factory)
    return factory


def get_sync_service(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    riot_client: RiotAPIClient = Depends(get_riot_client),
) -> SyncService:
    return SyncService(
        uow_factory=uow_factory,
        riot_client=riot_client,
    )


def get_player_service(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    sync_service: SyncService = Depends(get_sync_service),
) -> PlayerService:
    return PlayerService(
        uow_factory=uow_factory,
        sync_service=sync_service,
    )

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.integrations.riot.exceptions import (
    RiotAPIError,
    RiotForbiddenError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotRequestError,
    RiotServerError,
)
from app.services.exceptions import PlayerNotFoundError


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(PlayerNotFoundError)
    async def player_not_found_handler(
        request: Request,
        exc: PlayerNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'player_not_found',
            },
        )

    @app.exception_handler(RiotNotFoundError)
    async def riot_not_found_handler(
        request: Request,
        exc: RiotNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'riot_not_found',
            },
        )


    @app.exception_handler(RiotRateLimitError)
    async def riot_rate_limit_handler(
        request: Request,
        exc: RiotRateLimitError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'riot_rate_limit',
            },
        )

    @app.exception_handler(RiotForbiddenError)
    async def riot_forbidden_handler(
        request: Request,
        exc: RiotForbiddenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'riot_forbidden',
            },
        )

    @app.exception_handler(RiotRequestError)
    async def riot_request_handler(
        request: Request,
        exc: RiotRequestError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'riot_request_error',
            },
        )

    @app.exception_handler(RiotServerError)
    async def riot_server_handler(
        request: Request,
        exc: RiotServerError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'riot_server_error',
            },
        )

    @app.exception_handler(RiotAPIError)
    async def riot_api_handler(
        request: Request,
        exc: RiotAPIError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'riot_api_error',
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'error': str(exc) if settings.debug else 'Internal server error',
                'type': 'internal_error',
            },
        )
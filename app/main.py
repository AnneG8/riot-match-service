import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import register_exception_handlers
from app.api.routers import admin_router, players_router
from app.core.config import settings
from app.core.database import get_async_session
from app.integrations.riot import RiotAPIAuth, RiotAPIClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    http_client = httpx.AsyncClient(
        auth=RiotAPIAuth(token=settings.riot_api_key),
        timeout=httpx.Timeout(15.0),
    )
    riot_client = RiotAPIClient(client=http_client)

    app.state.http_client = http_client
    app.state.riot_client = riot_client
    app.state.background_tasks = set()
    
    yield

    tasks = list(app.state.background_tasks)
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    await app.state.http_client.aclose()


app = FastAPI(title='Riot Match Service', lifespan=lifespan)

register_exception_handlers(app)

app.include_router(admin_router, prefix='/api')
app.include_router(players_router, prefix='/api')


@app.get('/healthz')
async def healthz(session: AsyncSession = Depends(get_async_session)):
    await session.execute(text('SELECT 1'))
    return {'status': 'ok'}

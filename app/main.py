from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.integrations.riot import RiotAPIAuth, RiotAPIClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient(
        auth=RiotAPIAuth(token=settings.riot_api_key),
        timeout=httpx.Timeout(15.0),
    )
    riot_client = RiotAPIClient(client=http_client)

    app.state.http_client = http_client
    app.state.riot_client = riot_client
    
    yield

    await app.state.http_client.aclose()


app = FastAPI(title='Riot Match Service', lifespan=lifespan)


@app.get('/healthz')
async def healthz(session: AsyncSession = Depends(get_async_session)):
    await session.execute(text('SELECT 1'))
    return {'status': 'ok'}

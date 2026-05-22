from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title='Riot Match Service', lifespan=lifespan)


@app.get('/healthz')
async def healthz(session: AsyncSession = Depends(get_async_session)):
    await session.execute(text('SELECT 1'))
    return {'status': 'ok'}

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import (
    MatchRepository,
    PlayerRepository,
    RankedEntryRepository,
)


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> 'UnitOfWork':
        self.session = self._session_factory()
        self.players = PlayerRepository(self.session)
        self.ranked = RankedEntryRepository(self.session)
        self.matches = MatchRepository(self.session)
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()

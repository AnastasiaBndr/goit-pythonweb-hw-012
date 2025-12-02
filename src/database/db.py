"""
Database session management module.

Provides async database engine and session management
using SQLAlchemy AsyncEngine and async_sessionmaker.
"""

import contextlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from src.conf.config import settings


class DatabaseSessionManager:
    """
    Async database session manager.

    Handles the creation of database engine and provides
    an async context manager for database sessions.

    Parameters
    ----------
    url : str
        Database connection URL.
    """

    def __init__(self, url: str) -> None:
        self._engine: AsyncEngine | None = create_async_engine(url, echo=False)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Async context manager for database sessions.

        Yields
        ------
        AsyncSession
            An SQLAlchemy async session.

        Raises
        ------
        SQLAlchemyError
            If an error occurs during the session, it rolls back.
        Exception
            If the session maker is not initialized.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


# Global session manager instance
sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    FastAPI dependency to provide an async database session.

    Yields
    ------
    AsyncSession
        SQLAlchemy async session for database operations.
    """
    async with sessionmanager.session() as session:
        yield session

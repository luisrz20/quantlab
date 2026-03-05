"""Async SQLAlchemy session factory."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from quantlab.config import Settings


def build_engine(s: Settings) -> AsyncEngine:
    url = s.DATABASE_URL
    for old, new in [("postgresql://", "postgresql+asyncpg://"), ("postgres://", "postgresql+asyncpg://")]:
        if url.startswith(old):
            url = new + url[len(old):]
    return create_async_engine(url, pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=300, echo=s.DEBUG)


def build_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

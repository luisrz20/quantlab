"""Alembic async migration runner."""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from quantlab.infrastructure.db.orm_models import Base

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _url() -> str:
    u = os.environ["DATABASE_URL"]
    for old, new in [("postgresql://", "postgresql+asyncpg://"), ("postgres://", "postgresql+asyncpg://")]:
        if u.startswith(old):
            return new + u[len(old):]
    return u


async def _run() -> None:
    engine = create_async_engine(_url())
    async with engine.connect() as conn:
        await conn.run_sync(
            lambda c: (
                context.configure(connection=c, target_metadata=target_metadata, compare_type=True),
                context.begin_transaction().__enter__(),
                context.run_migrations(),
            )
        )
    await engine.dispose()


asyncio.run(_run())

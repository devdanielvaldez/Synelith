from collections.abc import AsyncIterator

import pytest_asyncio
from neurogenesis_api.database import Database
from neurogenesis_api.models import Base
from neurogenesis_api.settings import Settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool


@pytest_asyncio.fixture
async def database() -> AsyncIterator[Database]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database = Database("sqlite+aiosqlite://", engine=engine)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield database
    await database.dispose()


def make_settings(database_url: str = "sqlite+aiosqlite://") -> Settings:
    return Settings(
        environment="test",
        database_url=database_url,
        cors_origins=("http://localhost:3001",),
        ncbi_api_key=None,
        ncbi_email="test@example.org",
    )

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app
from db.database import Base
from db.db_handlers import create_initial_data
import config
from routes.dependencies import get_db

DATABASE_URL = (f"postgresql+asyncpg://{config.DB_USER_TEST}:{config.DB_PASS_TEST}@"
                f"{config.DB_HOST_TEST}:{config.DB_PORT_TEST}/{config.DB_NAME_TEST}")

engine_test = create_async_engine(DATABASE_URL, poolclass=NullPool)

# Создание асинхронной сессии
async_session_maker = sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
Base.metadata.bind = engine_test


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db



import time

@pytest.fixture(scope="session", autouse=True)
async def async_db_session():
    # Создание всех таблиц
    async with create_async_engine(DATABASE_URL, echo=True).begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Даем базе данных время на инициализацию
    time.sleep(1)

    # Создание сессии
    async with async_session_maker() as session:
        # Вызов функции для создания начальных данных
        await create_initial_data(session)
        yield session

    # Удаление всех таблиц после завершения тестов
    async with create_async_engine(DATABASE_URL, echo=True).begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

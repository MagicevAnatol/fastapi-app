import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine

from db_test import Base, DATABASE_URL, async_session_maker, create_initial_data
from schemas.schemas import TweetCreateRequest

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app


@pytest.fixture(scope="session", autouse=True)
async def async_db_session():
    # Создание всех таблиц
    async with create_async_engine(DATABASE_URL, echo=True).begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создание сессии
    async with async_session_maker() as session:
        # Вызов функции для создания начальных данных
        await create_initial_data(session)
        yield session

    # Удаление всех таблиц после завершения тестов
    async with create_async_engine(DATABASE_URL, echo=True).begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def created_tweet_id():
    tweet_request = TweetCreateRequest(tweet_data="Test tweet", tweet_media_ids=[])
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/tweets/", headers={"api-key": "test"}, json=tweet_request.dict()
        )
    return response.json()["tweet_id"]


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

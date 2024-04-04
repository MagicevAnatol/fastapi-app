import sys
from pathlib import Path
import pytest_asyncio
from httpx import AsyncClient

# Добавляем корневой каталог проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app  # Импорт после добавления пути


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

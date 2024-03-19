from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio

DATABASE_URL = "postgresql+asyncpg://admin:admin@localhost/clone_twitter_db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Создание асинхронной сессии
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Вызов функции инициализации базы данных

asyncio.run(init_db())

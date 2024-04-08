from functools import lru_cache
from pathlib import Path
from typing import List, AsyncGenerator
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Table,
    ARRAY,
    LargeBinary,
    select,
    NullPool,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app
from config import settings
from routes.dependencies import get_db



DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine_test = create_async_engine(DATABASE_URL, poolclass=NullPool)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

async_session_maker = sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
Base = declarative_base()
Base.metadata.bind = engine_test

likes_table = Table(
    "likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("tweet_id", ForeignKey("tweets.id"), primary_key=True, index=True),
)

followers = Table(
    "followers",
    Base.metadata,
    Column("follower_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("followed_id", ForeignKey("users.id"), primary_key=True, index=True),
)


class User(Base):
    """Модель для хранения информации о пользователях."""

    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_key: str = Column(String(length=50), unique=True)
    name: str = Column(String(length=50))

    # Отношение к лайкам пользователя
    likes = relationship("Tweet", secondary=likes_table, back_populates="liked_by")

    # Отношение к твитам пользователя
    tweets = relationship("Tweet", back_populates="user")

    # Отношение к подписчикам пользователя
    followed = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.follower_id,
        secondaryjoin=id == followers.c.followed_id,
        back_populates="follower",
    )

    # Отношение к подпискам пользователя
    follower = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.followed_id,
        secondaryjoin=id == followers.c.follower_id,
        back_populates="followed",
    )


class Tweet(Base):
    """Модель для хранения информации о твитах."""

    __tablename__ = "tweets"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tweet_data: str = Column(String(length=10000))
    tweet_media_ids: List[int] = Column(ARRAY(Integer), nullable=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="tweets")
    liked_by = relationship("User", secondary=likes_table, back_populates="likes")


class Media(Base):
    """Модель для хранения изображений."""

    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_data = Column(LargeBinary)


async def create_initial_data(session: AsyncSession) -> None:
    """
     Создает начальные данные в базе данных, включая пользователей, твиты, медиафайлы,
     подписчиков и лайки для тестирования.

    Эта функция создает начальный набор пользователей, твитов и медиафайлов,
    если в базе данных еще нет данных. Если данные уже существуют, функция
    прерывает свою работу.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных для выполнения операций.

    """
    # Проверка на наличие данных
    existing_user = await session.execute(select(User))
    if existing_user.scalars().first():
        print("База данных уже содержит данные. Процесс инициализации прерван.")
        return

    # Создаем пользователей
    user1 = User(name="test", api_key="test")
    user2 = User(name="User2", api_key="test_2")
    session.add(user1)
    session.add(user2)
    await session.commit()

    # Создаем твиты
    tweet1 = Tweet(tweet_data="Hello, World! This is tweet 1", user_id=user1.id)
    tweet2 = Tweet(tweet_data="This is tweet 2", user_id=user2.id)
    tweet3 = Tweet(tweet_data="Another day, another tweet!", user_id=user1.id)
    session.add(tweet1)
    session.add(tweet2)
    session.add(tweet3)
    await session.commit()

    # Читаем и добавляем изображения
    with open("images/image_1.jpg", "rb") as file:
        binary_data_1 = file.read()
        media1 = Media(filename="image1.jpg", file_data=binary_data_1)
        session.add(media1)

    with open("images/image_2.jpg", "rb") as file:
        binary_data_2 = file.read()
        media2 = Media(filename="image2.jpg", file_data=binary_data_2)
        session.add(media2)

    with open("images/image_3.jpg", "rb") as file:
        binary_data_3 = file.read()
        media3 = Media(filename="image3.jpg", file_data=binary_data_3)
        session.add(media3)

    await session.commit()

    # Обновляем твиты с ID медиа
    tweet1.tweet_media_ids = [media1.id]
    tweet2.tweet_media_ids = [media2.id]
    tweet3.tweet_media_ids = [media3.id]
    await session.commit()

    # Добавляем подписчиков
    user1_follow_user2 = followers.insert().values(
        follower_id=user1.id, followed_id=user2.id
    )
    user2_follow_user1 = followers.insert().values(
        follower_id=user2.id, followed_id=user1.id
    )
    # Выполняем запросы на добавление подписчиков
    await session.execute(user1_follow_user2)
    await session.execute(user2_follow_user1)
    await session.commit()

    # Добавляем лайки на твитах
    like1 = likes_table.insert().values(tweet_id=tweet1.id, user_id=user2.id)
    like2 = likes_table.insert().values(tweet_id=tweet2.id, user_id=user1.id)
    like3 = likes_table.insert().values(tweet_id=tweet3.id, user_id=user2.id)
    # Выполняем запросы на добавление лайков
    await session.execute(like1)
    await session.execute(like2)
    await session.execute(like3)
    await session.commit()
    print("Начальные данные успешно созданы.")

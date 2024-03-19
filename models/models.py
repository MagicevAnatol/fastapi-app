from typing import List
from sqlalchemy import Column, String, Integer, ForeignKey, Table, ARRAY
from sqlalchemy.orm import relationship
from models.init_db import Base

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

    # Уникальный идентификатор пользователя
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # API ключ пользователя
    api_key: str = Column(String(), unique=True)

    # Имя пользователя
    name: str = Column(String(length=50))

    # Отношение к лайкам пользователя
    likes = relationship("Tweet", secondary=likes_table, back_populates="users")

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

    # Уникальный идентификатор твита
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Текст твита
    tweet_data: str = Column(String(length=10000))

    # Ссылки на медиафайлы в твите
    tweet_media_ids: List[str] = Column(ARRAY(String(200)), nullable=True)

    # Идентификатор пользователя, создавшего твит
    user_id: int = Column(Integer, ForeignKey("users.id"), index=True)

    # Отношение к пользователю, создавшему твит
    user = relationship("User", back_populates="tweets")

    # Отношение к лайкам твита
    likes = relationship("User", secondary=likes_table, back_populates="likes")


class Image(Base):
    """Модель для хранения информации об изображениях."""

    __tablename__ = "images"

    # Уникальный идентификатор изображения
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Ссылка на изображение
    url: str = Column(String(length=200))

    # Идентификатор пользователя, создавшего изображение
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Отношение к пользователю, создавшему изображение
    user = relationship("User", back_populates="images")
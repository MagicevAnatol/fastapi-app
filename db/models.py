from typing import List
from sqlalchemy import Column, String, Integer, ForeignKey, Table, ARRAY, LargeBinary
from sqlalchemy.orm import relationship
from db.database import Base

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
    api_key: str = Column(String(), unique=True)
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
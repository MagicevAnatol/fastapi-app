from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import Media, Tweet, User, likes_table, followers


async def get_user_by_api(api_key: str, db: AsyncSession) -> User:
    try:
        result = await db.execute(select(User).filter(User.api_key == api_key))
        user = result.scalar_one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=401, detail="Invalid API key")


async def save_media(db: AsyncSession, filename: str, file_data: bytes) -> int:
    media = Media(filename=filename, file_data=file_data)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media.id


async def create_tweet(
    db: AsyncSession,
    user_id: int,
    tweet_data: str,
    tweet_media_ids: Optional[List[int]] = None,
) -> int:
    tweet_media_ids = tweet_media_ids or []
    tweet = Tweet(
        user_id=user_id, tweet_data=tweet_data, tweet_media_ids=tweet_media_ids
    )
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)
    return tweet.id


async def delete_tweet(db: AsyncSession, tweet_id: int, user_id: int) -> None:
    result = await db.execute(select(Tweet).filter(Tweet.id == tweet_id))
    tweet = result.scalar_one_or_none()

    if not tweet or tweet.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete this tweet"
        )

    await db.delete(tweet)
    await db.commit()


async def like_tweet(db: AsyncSession, tweet_id: int, user_id: int) -> None:
    await db.execute(likes_table.insert().values(tweet_id=tweet_id, user_id=user_id))
    await db.commit()


async def unlike_tweet(db: AsyncSession, tweet_id: int, user_id: int) -> None:
    await db.execute(
        likes_table.delete().where(
            (likes_table.c.tweet_id == tweet_id) & (likes_table.c.user_id == user_id)
        )
    )
    await db.commit()


async def is_tweet_owner(db: AsyncSession, tweet_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(Tweet).filter(Tweet.id == tweet_id, Tweet.user_id == user_id)
    )
    tweet = result.first()
    return tweet is not None


async def get_likes_for_tweet(db: AsyncSession, tweet_id: int) -> List[int]:
    result = await db.execute(
        select(likes_table.c.user_id).where(likes_table.c.tweet_id == tweet_id)
    )
    likes = [user_id for user_id in result.scalars().all()]
    return likes


async def get_tweet_feed(db: AsyncSession) -> List[dict]:
    result = await db.execute(
        select(Tweet)
        .options(selectinload(Tweet.user))
        .order_by(Tweet.id.desc())
        .limit(50)
    )
    tweets = result.scalars().all()
    tweet_list = []
    for tweet in tweets:
        likes = await get_likes_for_tweet(db, tweet.id)

        attachments = []
        if tweet.tweet_media_ids:
            for media_id in tweet.tweet_media_ids:
                attachment_link = f"/api/media/{media_id}"
                attachments.append(attachment_link)

        tweet_dict = {
            "id": tweet.id,
            "content": tweet.tweet_data,
            "attachments": attachments,
            "author": {"id": tweet.user.id, "name": tweet.user.name},
            "likes": likes,
        }
        tweet_list.append(tweet_dict)

    return tweet_list


async def get_media_handler(db: AsyncSession, media_id: int):
    result = await db.execute(select(Media).filter(Media.id == media_id))
    media = result.scalar_one_or_none()
    return media


async def get_followers(user_id: int, db: AsyncSession) -> List[dict]:
    result = await db.execute(
        select(User)
        .join(followers, User.id == followers.c.follower_id)
        .where(followers.c.followed_id == user_id)
    )
    followers_list = [
        {"id": follower.id, "name": follower.name}
        for follower in result.scalars().all()
    ]
    return followers_list


async def get_following(user_id: int, db: AsyncSession) -> List[dict]:
    result = await db.execute(
        select(User)
        .join(followers, User.id == followers.c.followed_id)
        .where(followers.c.follower_id == user_id)
    )
    following_list = [
        {"id": following.id, "name": following.name}
        for following in result.scalars().all()
    ]
    return following_list


async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


# Функция для добавления подписки на пользователя
async def follow_user(follower_id: int, followed_id: int, db: AsyncSession) -> bool:
    new_follow = followers.insert().values(
        follower_id=follower_id, followed_id=followed_id
    )
    try:
        await db.execute(new_follow)
        await db.commit()
        return True
    except Exception as e:
        # Обработка возможных исключений, например, если подписка уже существует
        await db.rollback()
        return False


# Функция для удаления подписки на пользователя
async def unfollow_user(follower_id: int, followed_id: int, db: AsyncSession) -> bool:
    unfollow = followers.delete().where(
        (followers.c.follower_id == follower_id)
        & (followers.c.followed_id == followed_id)
    )
    result = await db.execute(unfollow)
    if result.rowcount > 0:
        await db.commit()
        return True
    else:
        # Если подписка не найдена
        await db.rollback()
        return False


async def create_initial_data(session: AsyncSession):
    # Проверка на наличие данных
    existing_user = await session.execute(select(User))
    if existing_user.scalars().first():
        print("База данных уже содержит данные. Процесс инициализации прерван.")
        return

        # Создаем пользователей
    user1 = User(name="User1", api_key="test_1")
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

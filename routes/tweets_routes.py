from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import db_handlers
from schemas.schemas import TweetCreateRequest, api_key_dependency, get_db

router = APIRouter(
    prefix="/api/tweets"
)


@router.get("/", tags=["tweets"])
async def get_tweets(api_key: str = Depends(api_key_dependency), db: AsyncSession = Depends(get_db)):
    user = await db_handlers.get_user_by_api(api_key, db)
    tweets = await db_handlers.get_tweet_feed(db)
    return {"result": True, "tweets": tweets}


# Создание нового твита
@router.post("/", tags=["tweets"])
async def create_tweet(tweet_request: TweetCreateRequest,
                       api_key: str = Depends(api_key_dependency),
                       db: AsyncSession = Depends(get_db)):
    # Создаем новый твит и сохраняем его в базу данных
    user = await db_handlers.get_user_by_api(api_key, db)
    tweet_id = await db_handlers.create_tweet(db, user.id, tweet_request.tweet_data, tweet_request.tweet_media_ids)
    return {"result": True, "tweet_id": tweet_id}


# Удаление твита
@router.delete("/{tweet_id}", tags=["tweets"])
async def delete_tweet(tweet_id: int, api_key: str = Depends(api_key_dependency), db: AsyncSession = Depends(get_db)):
    user = await db_handlers.get_user_by_api(api_key, db)
    # Проверка принадлежности твита
    if not db_handlers.is_tweet_owner(db, tweet_id, user.id):
        raise HTTPException(status_code=403, detail="You are not allowed to delete this tweet")
    # Удаление твита
    await db_handlers.delete_tweet(db, tweet_id, user.id)
    return {"result": True}


# Добавление лайка к твиту
@router.post("/{tweet_id}/likes", tags=["tweets"])
async def like_tweet(tweet_id: int, api_key: str = Depends(api_key_dependency), db: AsyncSession = Depends(get_db)):
    user = await db_handlers.get_user_by_api(api_key, db)
    await db_handlers.like_tweet(db, tweet_id, user.id)
    return {"result": True}


# Удаление лайка у твита
@router.delete("/{tweet_id}/likes", tags=["tweets"])
async def unlike_tweet(tweet_id: int, api_key: str = Depends(api_key_dependency), db: AsyncSession = Depends(get_db)):
    user = await db_handlers.get_user_by_api(api_key, db)
    await db_handlers.unlike_tweet(db, tweet_id, user.id)
    return {"result": True}

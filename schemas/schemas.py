from pydantic import BaseModel
from typing import List, Optional
from fastapi import Header, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.database import async_session
from db.db_handlers import get_user_by_api


class TweetCreateRequest(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


def api_key_dependency(api_key: str = Header(...), db: Session = Depends(get_db)):
    user = get_user_by_api(api_key, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

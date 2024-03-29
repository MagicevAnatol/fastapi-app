from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import db_handlers
from db.db_handlers import get_user_by_api
from schemas.schemas import get_db, api_key_dependency

router = APIRouter(prefix="/api/users")


# Пользователь видит свой профиль.
@router.get("/me", tags=["users"])
async def get_current_user(
    api_key: str = Depends(api_key_dependency), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_api(api_key, db)
    followers = await db_handlers.get_followers(user.id, db)
    following = await db_handlers.get_following(user.id, db)
    return {
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": followers,
            "following": following,
        },
    }


# Отображение профиля по ID
@router.get("/{user_id}", tags=["users"])
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db_handlers.get_user_by_id(user_id, db)
    if not user:
        return {"result": False, "message": "User not found"}
    followers = await db_handlers.get_followers(user_id, db)
    following = await db_handlers.get_following(user_id, db)
    return {
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": followers,
            "following": following,
        },
    }


# Пользователь может зафоловить другого пользователя
@router.post("/{followed_id}/follow", tags=["users"])
async def follow_user(
    followed_id: int,
    api_key: str = Depends(api_key_dependency),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_api(api_key, db)
    success = await db_handlers.follow_user(user.id, followed_id, db)
    return {"result": success}


# Пользователь может убрать подписку на другого пользователя
@router.delete("/{followed_id}/follow", tags=["users"])
async def unfollow_user(
    followed_id: int,
    api_key: str = Depends(api_key_dependency),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_api(api_key, db)
    success = await db_handlers.unfollow_user(user.id, followed_id, db)
    return {"result": success}

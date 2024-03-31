from typing import List, Optional

from pydantic import BaseModel


class UserModel(BaseModel):
    id: int
    name: str


class TweetModel(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: UserModel
    likes: int


class TweetsResponseModel(BaseModel):
    result: bool
    tweets: List[TweetModel]


class TweetResponseModel(BaseModel):
    result: bool
    tweet_id: int


class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[UserModel]
    following: List[UserModel]


class UserResponseModel(BaseModel):
    result: bool
    user: Optional[UserProfile] = None


class MediaResponseModel(BaseModel):
    result: bool
    media_id: int

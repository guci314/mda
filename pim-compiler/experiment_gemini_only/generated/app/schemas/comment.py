import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserPublic


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentPublic(CommentBase):
    id: int
    author: UserPublic
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

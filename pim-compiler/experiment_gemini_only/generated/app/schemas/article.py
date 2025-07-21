import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.article import ArticleStatus
from app.schemas.comment import CommentPublic
from app.schemas.tag import TagPublic
from app.schemas.user import UserPublic


class ArticleBase(BaseModel):
    title: str
    content: Optional[str] = None


class ArticleCreate(ArticleBase):
    status: ArticleStatus = ArticleStatus.DRAFT
    tag_names: Optional[List[str]] = []


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None
    tag_names: Optional[List[str]] = None


class ArticlePublic(ArticleBase):
    id: int
    status: ArticleStatus
    author: UserPublic
    tags: List[TagPublic] = []
    comments: List[CommentPublic] = []
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# ruff: noqa: F401
from app.models.base import Base
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.association_tables import article_tag_association

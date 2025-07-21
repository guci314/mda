from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    async def create_with_author_and_article(
        self,
        db: AsyncSession,
        *,
        obj_in: CommentCreate,
        author_id: int,
        article_id: int,
    ) -> Comment:
        db_obj = Comment(
            **obj_in.model_dump(), author_id=author_id, article_id=article_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_article(
        self, db: AsyncSession, *, article_id: int, skip: int = 0, limit: int = 100
    ) -> list[Comment]:
        statement = (
            select(self.model)
            .where(self.model.article_id == article_id)
            .order_by(self.model.created_at.asc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(self.model.author))
        )
        result = await db.execute(statement)
        return result.scalars().all()


crud_comment = CRUDComment(Comment)

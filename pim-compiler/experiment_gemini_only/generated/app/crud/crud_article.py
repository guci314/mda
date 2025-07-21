from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.article import Article, ArticleStatus
from app.models.tag import Tag
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.crud.crud_tag import crud_tag


class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    async def create_with_author(
        self, db: AsyncSession, *, obj_in: ArticleCreate, author_id: int
    ) -> Article:
        db_obj = Article(
            **obj_in.model_dump(exclude={"tag_names"}), author_id=author_id
        )

        if obj_in.tag_names:
            await self._handle_tags(db, db_obj, obj_in.tag_names)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_published_articles(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        tag_name: Optional[str] = None,
    ) -> List[Article]:
        statement = (
            select(self.model)
            .where(self.model.status == ArticleStatus.PUBLISHED)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(self.model.author), selectinload(self.model.tags))
        )
        if tag_name:
            statement = statement.join(self.model.tags).where(Tag.name == tag_name)

        result = await db.execute(statement)
        return result.scalars().all()

    async def get(self, db: AsyncSession, id: int) -> Article | None:
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.author),
                selectinload(self.model.tags),
                selectinload(self.model.comments).selectinload("author"),
            )
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, *, db_obj: Article, obj_in: ArticleUpdate
    ) -> Article:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"tag_names"})

        if update_data:
            for field, value in update_data.items():
                setattr(db_obj, field, value)

        if obj_in.tag_names is not None:
            await self._handle_tags(db, db_obj, obj_in.tag_names)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _handle_tags(
        self, db: AsyncSession, article: Article, tag_names: List[str]
    ):
        # Clear existing tags
        article.tags.clear()
        # Find existing or create new tags
        for name in tag_names:
            tag = await crud_tag.get_by_name(db, name=name)
            if not tag:
                tag = await crud_tag.create(db, obj_in={"name": name})
            article.tags.append(tag)


crud_article = CRUDArticle(Article)

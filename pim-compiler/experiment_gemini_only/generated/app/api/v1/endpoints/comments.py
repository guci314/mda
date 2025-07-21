from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.CommentPublic, status_code=status.HTTP_201_CREATED)
async def create_comment(
    *,
    article_id: int,
    db: AsyncSession = Depends(deps.get_db),
    comment_in: schemas.CommentCreate,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Create a new comment for an article.
    """
    article = await crud.crud_article.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    comment = await crud.crud_comment.create_with_author_and_article(
        db=db, obj_in=comment_in, author_id=current_user.id, article_id=article_id
    )
    # Reload comment to get author relationship
    return await crud.crud_comment.get(db, id=comment.id)


@router.get("/", response_model=List[schemas.CommentPublic])
async def read_comments(
    *,
    article_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get comments for an article.
    """
    article = await crud.crud_article.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    comments = await crud.crud_comment.get_multi_by_article(
        db=db, article_id=article_id, skip=skip, limit=limit
    )
    return comments

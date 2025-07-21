from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.ArticlePublic, status_code=status.HTTP_201_CREATED)
async def create_article(
    *,
    db: AsyncSession = Depends(deps.get_db),
    article_in: schemas.ArticleCreate,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Create a new article.
    """
    article = await crud.crud_article.create_with_author(
        db=db, obj_in=article_in, author_id=current_user.id
    )
    # We need to fetch it again to load all relationships for the response model
    return await crud.crud_article.get(db, id=article.id)


@router.get("/", response_model=List[schemas.ArticlePublic])
async def read_articles(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    tag_name: Optional[str] = Query(None, description="Filter articles by tag name"),
):
    """
    Retrieve published articles.
    """
    articles = await crud.crud_article.get_published_articles(
        db=db, skip=skip, limit=limit, tag_name=tag_name
    )
    return articles


@router.get("/{article_id}", response_model=schemas.ArticlePublic)
async def read_article(
    *,
    db: AsyncSession = Depends(deps.get_db),
    article_id: int,
):
    """
    Get article by ID.
    """
    article = await crud.crud_article.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.status != models.ArticleStatus.PUBLISHED:
        # This part can be adjusted, maybe authors can see their drafts
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return article


@router.put("/{article_id}", response_model=schemas.ArticlePublic)
async def update_article(
    *,
    db: AsyncSession = Depends(deps.get_db),
    article_id: int,
    article_in: schemas.ArticleUpdate,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Update an article. Only the author can update it.
    """
    article = await crud.crud_article.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_article = await crud.crud_article.update(db=db, db_obj=article, obj_in=article_in)
    return await crud.crud_article.get(db, id=updated_article.id)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    *,
    db: AsyncSession = Depends(deps.get_db),
    article_id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Delete an article. Only the author can delete it.
    """
    article = await crud.crud_article.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await crud.crud_article.remove(db=db, id=article_id)


# Include comments router
from . import comments
router.include_router(comments.router, prefix="/{article_id}/comments", tags=["comments"])

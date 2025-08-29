from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from services.article_service import ArticleService
from schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse, ArticleQuery
)

router = APIRouter()


@router.post("/", response_model=ArticleResponse)
def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db)
):
    """创建新文章"""
    service = ArticleService(db)
    try:
        return service.create_article(article)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ArticleResponse])
def get_articles(
    category_id: Optional[str] = Query(None, description="分类ID"),
    status: Optional[str] = Query(None, description="文章状态"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    service = ArticleService(db)
    query = ArticleQuery(
        category_id=category_id,
        status=status,
        search=search,
        skip=skip,
        limit=limit
    )
    return service.get_articles(query)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: str,
    db: Session = Depends(get_db)
):
    """获取单篇文章"""
    service = ArticleService(db)
    article = service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: str,
    article: ArticleUpdate,
    db: Session = Depends(get_db)
):
    """更新文章"""
    service = ArticleService(db)
    try:
        updated_article = service.update_article(article_id, article)
        if not updated_article:
            raise HTTPException(status_code=404, detail="文章不存在")
        return updated_article
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{article_id}")
def delete_article(
    article_id: str,
    db: Session = Depends(get_db)
):
    """删除文章"""
    service = ArticleService(db)
    if not service.delete_article(article_id):
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"message": "文章删除成功"}


@router.post("/{article_id}/publish", response_model=ArticleResponse)
def publish_article(
    article_id: str,
    db: Session = Depends(get_db)
):
    """发布文章"""
    service = ArticleService(db)
    article = service.publish_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.post("/{article_id}/increment-view")
def increment_view(
    article_id: str,
    db: Session = Depends(get_db)
):
    """增加文章浏览量"""
    service = ArticleService(db)
    article = service.increment_view_count(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"message": "浏览量增加成功", "view_count": article.view_count}
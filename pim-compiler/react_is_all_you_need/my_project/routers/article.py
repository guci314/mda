from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleQuery
from repositories.article import ArticleRepository
from services.article import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])

def get_article_service(db: Session = Depends(get_db)):
    """获取文章服务依赖"""
    repository = ArticleRepository(db)
    return ArticleService(repository)

@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    category_id: str = Query(None, description="分类ID"),
    status: str = Query(None, description="文章状态"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    service: ArticleService = Depends(get_article_service)
):
    """获取文章列表"""
    query = ArticleQuery(
        category_id=category_id,
        status=status,
        search=search,
        skip=skip,
        limit=limit
    )
    articles = service.list_articles(query)
    return articles

@router.post("/", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    service: ArticleService = Depends(get_article_service)
):
    """创建文章"""
    try:
        article = service.create_article(article_data)
        return article
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """获取文章详情"""
    article = service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    service: ArticleService = Depends(get_article_service)
):
    """更新文章"""
    article = service.update_article(article_id, article_data)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article

@router.delete("/{article_id}")
async def delete_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """删除文章"""
    success = service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"message": "文章删除成功"}

@router.post("/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """发布文章"""
    article = service.publish_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article
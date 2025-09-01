from typing import List, Optional
from sqlalchemy.orm import Session
from models.article import ArticleDB
from schemas.article import ArticleCreate, ArticleUpdate, ArticleQuery
from repositories.article import ArticleRepository
from datetime import datetime

class ArticleService:
    """文章服务"""
    
    def __init__(self, repository: ArticleRepository):
        self.repository = repository
    
    def create_article(self, article_data: ArticleCreate) -> ArticleDB:
        """创建文章"""
        # 验证业务规则
        self._validate_article_publish(article_data)
        
        # 创建文章对象
        db_article = ArticleDB(
            title=article_data.title,
            content=article_data.content,
            summary=article_data.summary,
            author=article_data.author,
            category_id=article_data.category_id,
            status=article_data.status
        )
        
        return self.repository.save(db_article)
    
    def get_article(self, article_id: str) -> Optional[ArticleDB]:
        """获取文章"""
        return self.repository.get_by_id(article_id)
    
    def update_article(self, article_id: str, article_data: ArticleUpdate) -> Optional[ArticleDB]:
        """更新文章"""
        db_article = self.repository.get_by_id(article_id)
        if not db_article:
            return None
        
        # 更新字段
        if article_data.title is not None:
            db_article.title = article_data.title
        if article_data.content is not None:
            db_article.content = article_data.content
        if article_data.summary is not None:
            db_article.summary = article_data.summary
        if article_data.author is not None:
            db_article.author = article_data.author
        if article_data.category_id is not None:
            db_article.category_id = article_data.category_id
        if article_data.status is not None:
            db_article.status = article_data.status
        
        db_article.updated_at = datetime.now()
        
        return self.repository.save(db_article)
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        return self.repository.delete(article_id)
    
    def list_articles(self, query: ArticleQuery) -> List[ArticleDB]:
        """查询文章列表"""
        return self.repository.query_articles(query)
    
    def publish_article(self, article_id: str) -> Optional[ArticleDB]:
        """发布文章"""
        db_article = self.repository.get_by_id(article_id)
        if not db_article:
            return None
        
        # 验证发布规则
        self._validate_article_publish(db_article)
        
        db_article.status = "published"
        db_article.updated_at = datetime.now()
        
        return self.repository.save(db_article)
    
    def _validate_article_publish(self, article_data) -> None:
        """验证文章发布规则"""
        if not article_data.title or not article_data.title.strip():
            raise ValueError("文章标题不能为空")
        if not article_data.content or not article_data.content.strip():
            raise ValueError("文章内容不能为空")
        if len(article_data.title) > 200:
            raise ValueError("文章标题不能超过200字符")
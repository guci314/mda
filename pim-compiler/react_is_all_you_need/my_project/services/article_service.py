from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models.article import ArticleDB
from models.category import CategoryDB
from schemas.article import ArticleCreate, ArticleUpdate, ArticleQuery


class ArticleService:
    """文章业务服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_article(self, article_data: ArticleCreate) -> ArticleDB:
        """创建新文章（草稿状态）"""
        # 验证分类存在性
        if article_data.category_id:
            category = self.db.query(CategoryDB).filter(
                CategoryDB.id == article_data.category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {article_data.category_id}")
        
        article = ArticleDB(
            title=article_data.title,
            content=article_data.content,
            summary=article_data.summary,
            author=article_data.author,
            category_id=article_data.category_id,
            status="draft"
        )
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def get_articles(self, query: ArticleQuery) -> List[ArticleDB]:
        """获取文章列表，支持查询和分页"""
        db_query = self.db.query(ArticleDB)
        
        # 分类筛选
        if query.category_id:
            db_query = db_query.filter(ArticleDB.category_id == query.category_id)
        
        # 状态筛选
        if query.status:
            db_query = db_query.filter(ArticleDB.status == query.status)
        
        # 搜索功能
        if query.search:
            search_term = f"%{query.search}%"
            db_query = db_query.filter(
                or_(
                    ArticleDB.title.ilike(search_term),
                    ArticleDB.content.ilike(search_term),
                    ArticleDB.summary.ilike(search_term)
                )
            )
        
        # 排序和分页
        return db_query.order_by(ArticleDB.created_at.desc()).offset(
            query.skip
        ).limit(query.limit).all()
    
    def get_article_by_id(self, article_id: str) -> Optional[ArticleDB]:
        """根据ID获取文章"""
        return self.db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    
    def update_article(self, article_id: str, article_data: ArticleUpdate) -> Optional[ArticleDB]:
        """更新文章"""
        article = self.get_article_by_id(article_id)
        if not article:
            return None
        
        # 验证分类存在性
        if article_data.category_id:
            category = self.db.query(CategoryDB).filter(
                CategoryDB.id == article_data.category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {article_data.category_id}")
        
        # 更新字段
        update_data = article_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(article, field, value)
        
        article.updated_at = ArticleDB.updated_at.default
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        article = self.get_article_by_id(article_id)
        if not article:
            return False
        
        self.db.delete(article)
        self.db.commit()
        return True
    
    def publish_article(self, article_id: str) -> Optional[ArticleDB]:
        """发布文章"""
        article = self.get_article_by_id(article_id)
        if not article:
            return None
        
        article.status = "published"
        article.updated_at = ArticleDB.updated_at.default
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def increment_view_count(self, article_id: str) -> Optional[ArticleDB]:
        """增加文章浏览量"""
        article = self.get_article_by_id(article_id)
        if not article:
            return None
        
        article.view_count += 1
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def get_total_count(self, query: ArticleQuery) -> int:
        """获取文章总数"""
        db_query = self.db.query(ArticleDB)
        
        if query.category_id:
            db_query = db_query.filter(ArticleDB.category_id == query.category_id)
        if query.status:
            db_query = db_query.filter(ArticleDB.status == query.status)
        if query.search:
            search_term = f"%{query.search}%"
            db_query = db_query.filter(
                or_(
                    ArticleDB.title.ilike(search_term),
                    ArticleDB.content.ilike(search_term),
                    ArticleDB.summary.ilike(search_term)
                )
            )
        
        return db_query.count()
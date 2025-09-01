from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.article import ArticleDB
from schemas.article import ArticleQuery

class ArticleRepository:
    """文章仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, db_article: ArticleDB) -> ArticleDB:
        """保存或更新文章"""
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article
    
    def get_by_id(self, article_id: str) -> Optional[ArticleDB]:
        """根据ID获取文章"""
        return self.db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    
    def delete(self, article_id: str) -> bool:
        """删除文章"""
        db_article = self.get_by_id(article_id)
        if db_article:
            self.db.delete(db_article)
            self.db.commit()
            return True
        return False
    
    def query_articles(self, query: ArticleQuery) -> List[ArticleDB]:
        """查询文章"""
        q = self.db.query(ArticleDB)
        
        if query.category_id:
            q = q.filter(ArticleDB.category_id == query.category_id)
        
        if query.status:
            q = q.filter(ArticleDB.status == query.status)
        
        if query.search:
            search_term = f"%{query.search}%"
            q = q.filter(
                or_(
                    ArticleDB.title.ilike(search_term),
                    ArticleDB.content.ilike(search_term)
                )
            )
        
        q = q.offset(query.skip).limit(query.limit)
        return q.all()
    
    def get_all(self) -> List[ArticleDB]:
        """获取所有文章"""
        return self.db.query(ArticleDB).all()
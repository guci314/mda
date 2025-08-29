from typing import List, Optional
from sqlalchemy.orm import Session
from models.comment import CommentDB
from models.article import ArticleDB
from schemas.comment import CommentCreate, CommentUpdate, CommentQuery


class CommentService:
    """评论业务服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_comment(self, comment_data: CommentCreate) -> CommentDB:
        """创建新评论"""
        # 验证文章存在性
        article = self.db.query(ArticleDB).filter(
            ArticleDB.id == comment_data.article_id
        ).first()
        if not article:
            raise ValueError(f"文章不存在: {comment_data.article_id}")
        
        comment = CommentDB(
            article_id=comment_data.article_id,
            author_name=comment_data.author_name,
            email=comment_data.email,
            content=comment_data.content
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def get_comments(self, query: CommentQuery) -> List[CommentDB]:
        """获取评论列表，支持查询和分页"""
        db_query = self.db.query(CommentDB)
        
        # 文章筛选
        if query.article_id:
            db_query = db_query.filter(CommentDB.article_id == query.article_id)
        
        # 状态筛选
        if query.status:
            db_query = db_query.filter(CommentDB.status == query.status)
        
        # 排序和分页
        return db_query.order_by(CommentDB.created_at.desc()).offset(
            query.skip
        ).limit(query.limit).all()
    
    def get_comment_by_id(self, comment_id: str) -> Optional[CommentDB]:
        """根据ID获取评论"""
        return self.db.query(CommentDB).filter(
            CommentDB.id == comment_id
        ).first()
    
    def update_comment(self, comment_id: str, comment_data: CommentUpdate) -> Optional[CommentDB]:
        """更新评论"""
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            return None
        
        # 更新字段
        update_data = comment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)
        
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            return False
        
        self.db.delete(comment)
        self.db.commit()
        return True
    
    def approve_comment(self, comment_id: str) -> Optional[CommentDB]:
        """审核通过评论"""
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            return None
        
        comment.status = "published"
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def block_comment(self, comment_id: str) -> Optional[CommentDB]:
        """屏蔽评论"""
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            return None
        
        comment.status = "blocked"
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def get_total_count(self, query: CommentQuery) -> int:
        """获取评论总数"""
        db_query = self.db.query(CommentDB)
        
        if query.article_id:
            db_query = db_query.filter(CommentDB.article_id == query.article_id)
        if query.status:
            db_query = db_query.filter(CommentDB.status == query.status)
        
        return db_query.count()
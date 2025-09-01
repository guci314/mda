from typing import List, Optional
from sqlalchemy.orm import Session
from models.comment import CommentDB
from schemas.comment import CommentQuery

class CommentRepository:
    """评论仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, db_comment: CommentDB) -> CommentDB:
        """保存或更新评论"""
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def get_by_id(self, comment_id: str) -> Optional[CommentDB]:
        """根据ID获取评论"""
        return self.db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    
    def delete(self, comment_id: str) -> bool:
        """删除评论"""
        db_comment = self.get_by_id(comment_id)
        if db_comment:
            self.db.delete(db_comment)
            self.db.commit()
            return True
        return False
    
    def query_comments(self, query: CommentQuery) -> List[CommentDB]:
        """查询评论"""
        q = self.db.query(CommentDB).filter(CommentDB.article_id == query.article_id)
        
        if query.status:
            q = q.filter(CommentDB.status == query.status)
        
        q = q.offset(query.skip).limit(query.limit)
        return q.all()
    
    def get_all(self) -> List[CommentDB]:
        """获取所有评论"""
        return self.db.query(CommentDB).all()
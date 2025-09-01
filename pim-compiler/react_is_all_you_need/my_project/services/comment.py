from typing import List, Optional
from sqlalchemy.orm import Session
from models.comment import CommentDB
from schemas.comment import CommentCreate, CommentUpdate, CommentQuery
from repositories.comment import CommentRepository

class CommentService:
    """评论服务"""
    
    def __init__(self, repository: CommentRepository):
        self.repository = repository
    
    def create_comment(self, comment_data: CommentCreate) -> CommentDB:
        """创建评论"""
        # 验证评论内容
        self._validate_comment(comment_data)
        
        db_comment = CommentDB(
            article_id=comment_data.article_id,
            author_name=comment_data.author_name,
            email=comment_data.email,
            content=comment_data.content
        )
        
        return self.repository.save(db_comment)
    
    def get_comment(self, comment_id: str) -> Optional[CommentDB]:
        """获取评论"""
        return self.repository.get_by_id(comment_id)
    
    def update_comment(self, comment_id: str, comment_data: CommentUpdate) -> Optional[CommentDB]:
        """更新评论状态"""
        db_comment = self.repository.get_by_id(comment_id)
        if not db_comment:
            return None
        
        if comment_data.status is not None:
            db_comment.status = comment_data.status
        
        return self.repository.save(db_comment)
    
    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        return self.repository.delete(comment_id)
    
    def list_comments(self, query: CommentQuery) -> List[CommentDB]:
        """查询评论列表"""
        return self.repository.query_comments(query)
    
    def publish_comment(self, comment_id: str) -> Optional[CommentDB]:
        """发布评论"""
        db_comment = self.repository.get_by_id(comment_id)
        if not db_comment:
            return None
        
        db_comment.status = "published"
        return self.repository.save(db_comment)
    
    def block_comment(self, comment_id: str) -> Optional[CommentDB]:
        """屏蔽评论"""
        db_comment = self.repository.get_by_id(comment_id)
        if not db_comment:
            return None
        
        db_comment.status = "blocked"
        return self.repository.save(db_comment)
    
    def _validate_comment(self, comment_data: CommentCreate) -> None:
        """验证评论内容"""
        if not comment_data.author_name or not comment_data.author_name.strip():
            raise ValueError("评论者姓名不能为空")
        if not comment_data.email or not comment_data.email.strip():
            raise ValueError("邮箱不能为空")
        if not comment_data.content or not comment_data.content.strip():
            raise ValueError("评论内容不能为空")
        if len(comment_data.content) > 1000:
            raise ValueError("评论内容不能超过1000字符")
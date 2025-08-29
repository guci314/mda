from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from services.comment_service import CommentService
from schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentQuery

router = APIRouter()


@router.post("/", response_model=CommentResponse)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db)
):
    """创建新评论"""
    service = CommentService(db)
    try:
        return service.create_comment(comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CommentResponse])
def get_comments(
    article_id: Optional[str] = Query(None, description="文章ID"),
    status: Optional[str] = Query(None, description="评论状态"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取评论列表"""
    service = CommentService(db)
    query = CommentQuery(
        article_id=article_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return service.get_comments(query)


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: str,
    db: Session = Depends(get_db)
):
    """获取单个评论"""
    service = CommentService(db)
    comment = service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: str,
    comment: CommentUpdate,
    db: Session = Depends(get_db)
):
    """更新评论"""
    service = CommentService(db)
    updated_comment = service.update_comment(comment_id, comment)
    if not updated_comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return updated_comment


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db)
):
    """删除评论"""
    service = CommentService(db)
    if not service.delete_comment(comment_id):
        raise HTTPException(status_code=404, detail="评论不存在")
    return {"message": "评论删除成功"}


@router.post("/{comment_id}/approve", response_model=CommentResponse)
def approve_comment(
    comment_id: str,
    db: Session = Depends(get_db)
):
    """审核通过评论"""
    service = CommentService(db)
    comment = service.approve_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment


@router.post("/{comment_id}/block", response_model=CommentResponse)
def block_comment(
    comment_id: str,
    db: Session = Depends(get_db)
):
    """屏蔽评论"""
    service = CommentService(db)
    comment = service.block_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment
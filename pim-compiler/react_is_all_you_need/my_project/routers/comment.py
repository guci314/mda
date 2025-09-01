from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentQuery
from repositories.comment import CommentRepository
from services.comment import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])

def get_comment_service(db: Session = Depends(get_db)):
    """获取评论服务依赖"""
    repository = CommentRepository(db)
    return CommentService(repository)

@router.get("/", response_model=List[CommentResponse])
async def list_comments(
    article_id: str = Query(..., description="文章ID"),
    status: str = Query(None, description="评论状态"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    service: CommentService = Depends(get_comment_service)
):
    """获取评论列表"""
    query = CommentQuery(
        article_id=article_id,
        status=status,
        skip=skip,
        limit=limit
    )
    comments = service.list_comments(query)
    return comments

@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    service: CommentService = Depends(get_comment_service)
):
    """创建评论"""
    try:
        comment = service.create_comment(comment_data)
        return comment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """获取评论详情"""
    comment = service.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    service: CommentService = Depends(get_comment_service)
):
    """更新评论状态"""
    comment = service.update_comment(comment_id, comment_data)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """删除评论"""
    success = service.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="评论不存在")
    return {"message": "评论删除成功"}

@router.post("/{comment_id}/publish", response_model=CommentResponse)
async def publish_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """发布评论"""
    comment = service.publish_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment

@router.post("/{comment_id}/block", response_model=CommentResponse)
async def block_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """屏蔽评论"""
    comment = service.block_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.post import Post, PostCreate, PostUpdate
from ..database import get_db, Session

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=Post)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """创建新博客文章"""
    db_post = Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/", response_model=List[Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取博客文章列表"""
    return db.query(Post).offset(skip).limit(limit).all()

@router.get("/{post_id}", response_model=Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """获取单个博客文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=Post)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    """更新博客文章"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    for var, value in vars(post).items():
        if value is not None:
            setattr(db_post, var, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """删除博客文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}
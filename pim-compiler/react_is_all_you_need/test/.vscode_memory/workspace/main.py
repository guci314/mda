from fastapi import FastAPI, HTTPException
from .domain.models import BlogPost, BlogPostCreate, BlogPostUpdate
from .service.blog_service import BlogPostService
from .service.in_memory_repository import InMemoryBlogPostRepository

app = FastAPI(title="Blog System API", version="1.0.0")

# 初始化repository和service
repository = InMemoryBlogPostRepository()
blog_service = BlogPostService(repository)


@app.get("/")
def read_root():
    return {"message": "Welcome to Blog System API"}


@app.post("/posts", response_model=BlogPost)
def create_post(post: BlogPostCreate):
    return blog_service.create_post(post)


@app.get("/posts/{post_id}", response_model=BlogPost)
def get_post(post_id: int):
    post = blog_service.get_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.get("/posts", response_model=List[BlogPost])
def get_posts():
    return blog_service.get_all_posts()


@app.put("/posts/{post_id}", response_model=BlogPost)
def update_post(post_id: int, post_update: BlogPostUpdate):
    post = blog_service.update_post(post_id, post_update)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    success = blog_service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}
from typing import List, Optional, Dict
from datetime import datetime
from ..domain.models import BlogPost, BlogPostCreate, BlogPostUpdate
from ..domain.repository import BlogPostRepository


class InMemoryBlogPostRepository(BlogPostRepository):
    def __init__(self):
        self.posts: Dict[int, BlogPost] = {}
        self.counter = 1

    def create(self, post: BlogPostCreate) -> BlogPost:
        blog_post = BlogPost(
            id=self.counter,
            title=post.title,
            content=post.content,
            author=post.author,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.posts[self.counter] = blog_post
        self.counter += 1
        return blog_post

    def get_by_id(self, post_id: int) -> Optional[BlogPost]:
        return self.posts.get(post_id)

    def get_all(self) -> List[BlogPost]:
        return list(self.posts.values())

    def update(self, post_id: int, post_update: BlogPostUpdate) -> Optional[BlogPost]:
        if post_id not in self.posts:
            return None
            
        post = self.posts[post_id]
        if post_update.title is not None:
            post.title = post_update.title
        if post_update.content is not None:
            post.content = post_update.content
        post.updated_at = datetime.now()
        
        self.posts[post_id] = post
        return post

    def delete(self, post_id: int) -> bool:
        if post_id in self.posts:
            del self.posts[post_id]
            return True
        return False
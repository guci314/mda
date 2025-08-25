from typing import List, Optional
from ..domain.models import BlogPost, BlogPostCreate, BlogPostUpdate
from ..domain.repository import BlogPostRepository


class BlogPostService:
    def __init__(self, repository: BlogPostRepository):
        self.repository = repository

    def create_post(self, post_create: BlogPostCreate) -> BlogPost:
        return self.repository.create(post_create)

    def get_post_by_id(self, post_id: int) -> Optional[BlogPost]:
        return self.repository.get_by_id(post_id)

    def get_all_posts(self) -> List[BlogPost]:
        return self.repository.get_all()

    def update_post(self, post_id: int, post_update: BlogPostUpdate) -> Optional[BlogPost]:
        return self.repository.update(post_id, post_update)

    def delete_post(self, post_id: int) -> bool:
        return self.repository.delete(post_id)
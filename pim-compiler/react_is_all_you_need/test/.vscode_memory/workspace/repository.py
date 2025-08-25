from abc import ABC, abstractmethod
from typing import List, Optional
from .models import BlogPost, BlogPostCreate, BlogPostUpdate


class BlogPostRepository(ABC):
    @abstractmethod
    def create(self, post: BlogPostCreate) -> BlogPost:
        pass

    @abstractmethod
    def get_by_id(self, post_id: int) -> Optional[BlogPost]:
        pass

    @abstractmethod
    def get_all(self) -> List[BlogPost]:
        pass

    @abstractmethod
    def update(self, post_id: int, post_update: BlogPostUpdate) -> Optional[BlogPost]:
        pass

    @abstractmethod
    def delete(self, post_id: int) -> bool:
        pass
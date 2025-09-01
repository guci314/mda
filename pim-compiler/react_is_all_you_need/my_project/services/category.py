from typing import List, Optional
from sqlalchemy.orm import Session
from models.category import CategoryDB
from schemas.category import CategoryCreate, CategoryUpdate
from repositories.category import CategoryRepository

class CategoryService:
    """分类服务"""
    
    def __init__(self, repository: CategoryRepository):
        self.repository = repository
    
    def create_category(self, category_data: CategoryCreate) -> CategoryDB:
        """创建分类"""
        # 验证分类名称唯一性
        existing_category = self.repository.get_by_name(category_data.name)
        if existing_category:
            raise ValueError(f"分类名称 '{category_data.name}' 已存在")
        
        db_category = CategoryDB(
            name=category_data.name,
            description=category_data.description
        )
        
        return self.repository.save(db_category)
    
    def get_category(self, category_id: str) -> Optional[CategoryDB]:
        """获取分类"""
        return self.repository.get_by_id(category_id)
    
    def update_category(self, category_id: str, category_data: CategoryUpdate) -> Optional[CategoryDB]:
        """更新分类"""
        db_category = self.repository.get_by_id(category_id)
        if not db_category:
            return None
        
        # 如果更新名称，验证唯一性
        if category_data.name and category_data.name != db_category.name:
            existing_category = self.repository.get_by_name(category_data.name)
            if existing_category:
                raise ValueError(f"分类名称 '{category_data.name}' 已存在")
            db_category.name = category_data.name
        
        if category_data.description is not None:
            db_category.description = category_data.description
        
        return self.repository.save(db_category)
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        return self.repository.delete(category_id)
    
    def list_categories(self) -> List[CategoryDB]:
        """获取所有分类"""
        return self.repository.get_all()
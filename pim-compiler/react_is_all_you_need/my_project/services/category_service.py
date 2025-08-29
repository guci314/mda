from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.category import CategoryDB
from models.article import ArticleDB
from schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """分类业务服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_category(self, category_data: CategoryCreate) -> CategoryDB:
        """创建新分类"""
        # 检查分类名称是否已存在
        existing = self.db.query(CategoryDB).filter(
            CategoryDB.name == category_data.name
        ).first()
        
        if existing:
            raise ValueError(f"分类 '{category_data.name}' 已存在")
        
        # 创建新分类
        db_category = CategoryDB(**category_data.dict())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def get_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryDB]:
        """获取分类列表"""
        return self.db.query(CategoryDB).offset(skip).limit(limit).all()
    
    def get_category_by_id(self, category_id: str) -> Optional[CategoryDB]:
        """根据ID获取分类"""
        return self.db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    
    def get_category_by_name(self, name: str) -> Optional[CategoryDB]:
        """根据名称获取分类"""
        return self.db.query(CategoryDB).filter(CategoryDB.name == name).first()
    
    def update_category(self, category_id: str, category_data: CategoryUpdate) -> Optional[CategoryDB]:
        """更新分类"""
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            return None
        
        # 检查新名称是否已存在（如果名称被更新）
        if category_data.name and category_data.name != db_category.name:
            existing = self.get_category_by_name(category_data.name)
            if existing:
                raise ValueError(f"分类 '{category_data.name}' 已存在")
        
        # 更新字段
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            return False
        
        # 检查是否有文章使用该分类
        article_count = self.db.query(func.count(ArticleDB.id)).filter(
            ArticleDB.category_id == category_id
        ).scalar()
        
        if article_count > 0:
            raise ValueError("该分类下有文章，无法删除")
        
        self.db.delete(db_category)
        self.db.commit()
        return True
    
    def get_category_with_article_count(self, category_id: str) -> Optional[dict]:
        """获取分类及其文章数量"""
        category = self.get_category_by_id(category_id)
        if not category:
            return None
        
        article_count = self.db.query(func.count(ArticleDB.id)).filter(
            ArticleDB.category_id == category_id
        ).scalar()
        
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "article_count": article_count,
            "created_at": category.created_at
        }
    
    def get_categories_with_article_count(self) -> List[dict]:
        """获取所有分类及其文章数量"""
        categories = self.db.query(CategoryDB).all()
        result = []
        
        for category in categories:
            article_count = self.db.query(func.count(ArticleDB.id)).filter(
                ArticleDB.category_id == category.id
            ).scalar()
            
            result.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "article_count": article_count,
                "created_at": category.created_at
            })
        
        return result
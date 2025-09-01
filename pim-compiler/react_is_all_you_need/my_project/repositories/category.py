from typing import List, Optional
from sqlalchemy.orm import Session
from models.category import CategoryDB

class CategoryRepository:
    """分类仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, db_category: CategoryDB) -> CategoryDB:
        """保存或更新分类"""
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def get_by_id(self, category_id: str) -> Optional[CategoryDB]:
        """根据ID获取分类"""
        return self.db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    
    def get_by_name(self, name: str) -> Optional[CategoryDB]:
        """根据名称获取分类"""
        return self.db.query(CategoryDB).filter(CategoryDB.name == name).first()
    
    def delete(self, category_id: str) -> bool:
        """删除分类"""
        db_category = self.get_by_id(category_id)
        if db_category:
            self.db.delete(db_category)
            self.db.commit()
            return True
        return False
    
    def get_all(self) -> List[CategoryDB]:
        """获取所有分类"""
        return self.db.query(CategoryDB).all()
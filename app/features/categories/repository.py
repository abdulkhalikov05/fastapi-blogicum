from sqlalchemy.orm import Session
from typing import Optional, List
from app.features.categories import models, schemas


class CategoryRepository:
    """Репозиторий для работы с категориями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, category_id: int) -> Optional[models.Category]:
        """Получить категорию по ID"""
        return self.db.query(models.Category).filter(models.Category.id == category_id).first()
    
    def get_by_slug(self, slug: str) -> Optional[models.Category]:
        """Получить категорию по slug"""
        return self.db.query(models.Category).filter(models.Category.slug == slug).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[models.Category]:
        """Получить список всех категорий"""
        query = self.db.query(models.Category)
        if published_only:
            query = query.filter(models.Category.is_published == True)
        return query.offset(skip).limit(limit).all()
    
    def create(self, category_data: schemas.CategoryCreate) -> models.Category:
        """Создать новую категорию"""
        db_category = models.Category(**category_data.dict())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def update(self, category_id: int, category_data: schemas.CategoryUpdate) -> Optional[models.Category]:
        """Обновить категорию"""
        db_category = self.get(category_id)
        if not db_category:
            return None
        
        update_dict = category_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_category, field, value)
        
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def delete(self, category_id: int) -> bool:
        """Удалить категорию"""
        db_category = self.get(category_id)
        if not db_category:
            return False
        
        self.db.delete(db_category)
        self.db.commit()
        return True

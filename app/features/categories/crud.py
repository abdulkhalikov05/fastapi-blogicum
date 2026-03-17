from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.features.categories import models, schemas
from typing import Optional, List


def get_category(db: Session, category_id: int):
    """Получить категорию по ID"""
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str):
    """Получить категорию по slug"""
    return db.query(models.Category).filter(models.Category.slug == slug).first()


def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    published_only: bool = True
) -> List[models.Category]:
    """Получить список категорий"""
    query = db.query(models.Category)
    if published_only:
        query = query.filter(models.Category.is_published == True)
    return query.offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Создать новую категорию"""
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session, 
    category_id: int, 
    category_update: schemas.CategoryUpdate
) -> Optional[models.Category]:
    """Обновить категорию"""
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> Optional[models.Category]:
    """Удалить категорию"""
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

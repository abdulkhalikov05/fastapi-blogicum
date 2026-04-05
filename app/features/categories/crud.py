from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List

from app.features.categories import models, schemas
from app.core.exceptions import DatabaseError, NotFoundError


def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    try:
        return db.query(models.Category).filter(models.Category.id == category_id).first()
    except SQLAlchemyError as e:
        raise DatabaseError("получение категории", str(e))


def get_category_by_slug(db: Session, slug: str) -> Optional[models.Category]:
    try:
        return db.query(models.Category).filter(models.Category.slug == slug).first()
    except SQLAlchemyError as e:
        raise DatabaseError("получение категории по slug", str(e))


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True
) -> List[models.Category]:
    try:
        query = db.query(models.Category)
        if published_only:
            query = query.filter(models.Category.is_published == True)
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DatabaseError("получение списка категорий", str(e))


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    try:
        db_category = models.Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError("создание категории (нарушение целостности)", str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("создание категории", str(e))


def update_category(
    db: Session,
    category_id: int,
    category_update: schemas.CategoryUpdate
) -> Optional[models.Category]:
    try:
        db_category = get_category(db, category_id)
        if not db_category:
            raise NotFoundError("Category", category_id)

        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)

        db.commit()
        db.refresh(db_category)
        return db_category
    except NotFoundError:
        raise
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError("обновление категории (нарушение целостности)", str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("обновление категории", str(e))


def delete_category(db: Session, category_id: int) -> Optional[models.Category]:
    try:
        db_category = get_category(db, category_id)
        if not db_category:
            raise NotFoundError("Category", category_id)

        db.delete(db_category)
        db.commit()
        return db_category
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("удаление категории", str(e))

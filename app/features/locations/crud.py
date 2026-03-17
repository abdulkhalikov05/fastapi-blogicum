from sqlalchemy.orm import Session
from app.features.locations import models, schemas
from typing import Optional, List


def get_location(db: Session, location_id: int):
    """Получить местоположение по ID"""
    return db.query(models.Location).filter(models.Location.id == location_id).first()


def get_locations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    published_only: bool = True
) -> List[models.Location]:
    """Получить список местоположений"""
    query = db.query(models.Location)
    if published_only:
        query = query.filter(models.Location.is_published == True)
    return query.offset(skip).limit(limit).all()


def create_location(db: Session, location: schemas.LocationCreate) -> models.Location:
    """Создать новое местоположение"""
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(
    db: Session, 
    location_id: int, 
    location_update: schemas.LocationUpdate
) -> Optional[models.Location]:
    """Обновить местоположение"""
    db_location = get_location(db, location_id)
    if db_location:
        update_data = location_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_location, field, value)
        db.commit()
        db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: int) -> Optional[models.Location]:
    """Удалить местоположение"""
    db_location = get_location(db, location_id)
    if db_location:
        db.delete(db_location)
        db.commit()
    return db_location

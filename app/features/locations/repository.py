from sqlalchemy.orm import Session
from typing import Optional, List
from app.features.locations import models, schemas


class LocationRepository:
    """Репозиторий для работы с местоположениями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, location_id: int) -> Optional[models.Location]:
        """Получить местоположение по ID"""
        return self.db.query(models.Location).filter(models.Location.id == location_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[models.Location]:
        """Получить список всех местоположений"""
        query = self.db.query(models.Location)
        if published_only:
            query = query.filter(models.Location.is_published == True)
        return query.offset(skip).limit(limit).all()
    
    def create(self, location_data: schemas.LocationCreate) -> models.Location:
        """Создать новое местоположение"""
        db_location = models.Location(**location_data.dict())
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        return db_location
    
    def update(self, location_id: int, location_data: schemas.LocationUpdate) -> Optional[models.Location]:
        """Обновить местоположение"""
        db_location = self.get(location_id)
        if not db_location:
            return None
        
        update_dict = location_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_location, field, value)
        
        self.db.commit()
        self.db.refresh(db_location)
        return db_location
    
    def delete(self, location_id: int) -> bool:
        """Удалить местоположение"""
        db_location = self.get(location_id)
        if not db_location:
            return False
        
        self.db.delete(db_location)
        self.db.commit()
        return True

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List

from app.features.locations import models, schemas
from app.core.exceptions import DatabaseError, NotFoundError


def get_location(db: Session, location_id: int) -> Optional[models.Location]:
    try:
        return db.query(models.Location).filter(models.Location.id == location_id).first()
    except SQLAlchemyError as e:
        raise DatabaseError("получение местоположения", str(e))


def get_locations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True
) -> List[models.Location]:
    try:
        query = db.query(models.Location)
        if published_only:
            query = query.filter(models.Location.is_published == True)
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DatabaseError("получение списка местоположений", str(e))


def create_location(db: Session, location: schemas.LocationCreate) -> models.Location:
    try:
        db_location = models.Location(**location.dict())
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        return db_location
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError("создание местоположения (нарушение целостности)", str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("создание местоположения", str(e))


def update_location(
    db: Session,
    location_id: int,
    location_update: schemas.LocationUpdate
) -> Optional[models.Location]:
    try:
        db_location = get_location(db, location_id)
        if not db_location:
            raise NotFoundError("Location", location_id)

        update_data = location_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_location, field, value)

        db.commit()
        db.refresh(db_location)
        return db_location
    except NotFoundError:
        raise
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError("обновление местоположения (нарушение целостности)", str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("обновление местоположения", str(e))


def delete_location(db: Session, location_id: int) -> Optional[models.Location]:
    try:
        db_location = get_location(db, location_id)
        if not db_location:
            raise NotFoundError("Location", location_id)

        db.delete(db_location)
        db.commit()
        return db_location
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("удаление местоположения", str(e))
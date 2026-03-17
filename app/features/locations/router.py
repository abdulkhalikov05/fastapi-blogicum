from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import User
from app.features.locations import crud, schemas

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=List[schemas.Location])
async def read_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список местоположений"""
    return crud.get_locations(db, skip=skip, limit=limit)


@router.get("/{location_id}", response_model=schemas.Location)
async def read_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    """Получить местоположение по ID"""
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.post("/", response_model=schemas.Location, status_code=status.HTTP_201_CREATED)
async def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Только для админов
):
    """Создать местоположение (только для админов)"""
    return crud.create_location(db, location)


@router.put("/{location_id}", response_model=schemas.Location)
async def update_location(
    location_id: int,
    location_update: schemas.LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Только для админов
):
    """Обновить местоположение (только для админов)"""
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return crud.update_location(db, location_id, location_update)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Только для админов
):
    """Удалить местоположение (только для админов)"""
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    crud.delete_location(db, location_id)
    return None

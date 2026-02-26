from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=List[schemas.Location])
async def read_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех местоположений
    """
    locations = crud.get_locations(db, skip=skip, limit=limit)
    return locations


@router.get("/{location_id}", response_model=schemas.Location)
async def read_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить детальную информацию о местоположении
    """
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Местоположение не найдено"
        )
    return location


@router.post("/", response_model=schemas.Location, status_code=status.HTTP_201_CREATED)
async def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Создать новое местоположение (только для авторизованных)
    """
    return crud.create_location(db, location)


@router.put("/{location_id}", response_model=schemas.Location)
async def update_location(
    location_id: int,
    location_update: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Обновить местоположение (только для авторизованных)
    """
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Местоположение не найдено"
        )

    return crud.update_location(db, location_id, location_update)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Удалить местоположение (только для авторизованных)
    """
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Местоположение не найдено"
        )

    crud.delete_location(db, location_id)
    return None

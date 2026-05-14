from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError, DatabaseError
from app.core.dependencies import get_current_admin
from app.features.locations import crud, schemas
from app.features.auth.models import User

router = APIRouter(prefix="/locations", tags=["locations"])


# ====================== GET ALL ======================
@router.get("/", response_model=List[schemas.Location])
async def read_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        return crud.get_locations(db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


# ====================== GET ONE ======================
@router.get("/{location_id}", response_model=schemas.Location)
async def read_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    try:
        location = crud.get_location(db, location_id)

        if not location:
            raise NotFoundError("Location", location_id)

        return location

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


# ====================== CREATE ======================
@router.post("/", response_model=schemas.Location, status_code=status.HTTP_201_CREATED)
async def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return crud.create_location(db, location)

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


# ====================== UPDATE ======================
@router.put("/{location_id}", response_model=schemas.Location)
async def update_location(
    location_id: int,
    location_update: schemas.LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    try:
        location = crud.get_location(db, location_id)

        if not location:
            raise NotFoundError("Location", location_id)

        return crud.update_location(db, location_id, location_update)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


# ====================== DELETE ======================
@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    try:
        location = crud.get_location(db, location_id)

        if not location:
            raise NotFoundError("Location", location_id)

        crud.delete_location(db, location_id)
        return None

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
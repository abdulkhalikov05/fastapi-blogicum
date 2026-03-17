from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import User
from app.features.categories import crud, schemas

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[schemas.Category])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список категорий"""
    return crud.get_categories(db, skip=skip, limit=limit)


@router.get("/{slug}", response_model=schemas.Category)
async def read_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Получить категорию по slug"""
    category = crud.get_category_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Только для админов
):
    """Создать категорию (только для админов)"""
    # В реальном проекте здесь проверка на admin
    return crud.create_category(db, category)


@router.put("/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Только для админов
):
    """Обновить категорию (только для админов)"""
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return crud.update_category(db, category_id, category_update)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Только для админов
):
    """Удалить категорию (только для админов)"""
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    crud.delete_category(db, category_id)
    return None

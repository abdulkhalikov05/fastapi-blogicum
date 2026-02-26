from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[schemas.Category])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех категорий
    Аналог Category.objects.all() в Django
    """
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/{category_id}", response_model=schemas.Category)
async def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить детальную информацию о категории
    """
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    return category


@router.get("/slug/{slug}", response_model=schemas.Category)
async def read_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Получить категорию по slug
    Аналог get_object_or_404(Category, slug=slug) в Django
    """
    category = crud.get_category_by_slug(db, slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    return category


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Создать новую категорию (только для авторизованных)
    """
    # Проверяем, нет ли уже категории с таким slug
    existing = crud.get_category_by_slug(db, category.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким slug уже существует"
        )

    return crud.create_category(db, category)


@router.put("/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Обновить категорию (только для авторизованных)
    """
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )

    # Если меняется slug, проверяем уникальность
    if category_update.slug != category.slug:
        existing = crud.get_category_by_slug(db, category_update.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким slug уже существует"
            )

    return crud.update_category(db, category_id, category_update)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Удалить категорию (только для авторизованных)
    """
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )

    crud.delete_category(db, category_id)
    return None

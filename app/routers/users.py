from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db
from app.dependencies import get_current_active_user, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Получить список пользователей (только для авторизованных)
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
async def read_current_user(
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Получить информацию о текущем пользователе
    Аналог request.user в Django
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Получить информацию о пользователе по ID
    Аналог get_object_or_404(User, id=user_id)
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.get("/username/{username}", response_model=schemas.User)
async def read_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Получить информацию о пользователе по username
    Аналог profile() из Django
    """
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    Аналог создания пользователя в Django
    """
    # Проверяем уникальность username
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )

    # Проверяем уникальность email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    return crud.create_user(db, user)


@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Обновить данные текущего пользователя
    Аналог edit_profile() из Django
    """
    # Проверяем уникальность username если он меняется
    if user_update.username != current_user.username:
        db_user = crud.get_user_by_username(db, username=user_update.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )

    # Проверяем уникальность email если он меняется
    if user_update.email != current_user.email:
        db_user = crud.get_user_by_email(db, email=user_update.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

    return crud.update_user(db, current_user.id, user_update)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Удалить текущего пользователя
    """
    crud.delete_user(db, current_user.id)
    return None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.features.auth import crud, schemas
from app.features.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверяем, не занят ли username
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Проверяем, не занят ли email
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db, user)


@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: schemas.User = Depends(get_current_active_user)
):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/users", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)  # Только для админов
):
    """Получить список пользователей (только для админов)"""
    # В реальном проекте здесь проверка на admin
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """Получить информацию о пользователе по ID"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

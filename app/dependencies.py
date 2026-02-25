from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app import crud, schemas
from app.database import get_db

# Это заглушка для аутентификации
# В реальном проекте здесь будет JWT токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[schemas.User]:
    """
    Получить текущего пользователя из токена
    Аналог @login_required в Django
    """
    if not token:
        return None

    # Временная заглушка - возвращаем первого пользователя
    user = crud.get_user(db, user_id=1)
    return user


async def get_current_active_user(
    current_user: Optional[schemas.User] = Depends(get_current_user)
) -> schemas.User:
    """
    Проверка что пользователь авторизован и активен
    Аналог @login_required с redirect
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    return current_user


def get_pagination(skip: int = 0, limit: int = 10):
    """
    Пагинация для запросов
    """
    return {"skip": skip, "limit": limit}

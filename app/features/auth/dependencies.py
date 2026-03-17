from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.features.auth import crud, schemas

# Схема для получения токена (пока заглушка)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[schemas.User]:
    """
    Получить текущего пользователя по токену.
    Временная заглушка - просто возвращает пользователя по ID из токена.
    """
    if not token:
        return None
    
    # Пробуем интерпретировать токен как ID пользователя (временное решение)
    try:
        user_id = int(token)
        user = crud.get_user(db, user_id)
        if user:
            return user
    except (ValueError, TypeError):
        pass
    
    return None


async def get_current_active_user(
    current_user: Optional[schemas.User] = Depends(get_current_user)
) -> schemas.User:
    """
    Получить текущего активного пользователя или вернуть ошибку 401.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


# Для совместимости с роутерами, которые ожидают User из schemas
async def get_current_active_user_schemas(
    current_user = Depends(get_current_active_user)
) -> schemas.User:
    """Обертка для возврата правильного типа"""
    return current_user

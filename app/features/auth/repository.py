from typing import Optional

from sqlalchemy.orm import Session

from app.features.auth import models, schemas


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, user_id: int) -> models.User | None:
        """Получить пользователя по ID"""
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[models.User]:
        """Получить пользователя по username"""
        return self.db.query(models.User).filter(models.User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[models.User]:
        """Получить пользователя по email"""
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        """Получить список всех пользователей"""
        return self.db.query(models.User).offset(skip).limit(limit).all()
    
    def create(self, user_data: schemas.UserCreate) -> models.User:
        """Создать нового пользователя"""
        db_user = models.User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=f"temp_{user_data.password}",  # TODO: добавить хеширование
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update(self, user_id: int, user_data: schemas.UserUpdate) -> Optional[models.User]:
        """Обновить данные пользователя"""
        db_user = self.get(user_id)
        if not db_user:
            return None
        
        update_dict = user_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        db_user = self.get(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True

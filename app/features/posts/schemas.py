from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List

from app.features.categories.schemas import Category
from app.features.locations.schemas import Location
from app.features.comments.schemas import Comment


class PostBase(BaseModel):
    title: str
    text: str
    pub_date: datetime
    is_published: bool = True
    category_id: int
    location_id: Optional[int] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Заголовок не может быть пустым')
        if len(v) < 3:
            raise ValueError('Заголовок должен содержать минимум 3 символа')
        if len(v) > 256:
            raise ValueError('Заголовок не может превышать 256 символов')
        return v.strip()

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Текст поста не может быть пустым')
        if len(v) < 10:
            raise ValueError('Текст поста должен содержать минимум 10 символов')
        return v.strip()

    @field_validator('category_id')
    @classmethod
    def validate_category_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('ID категории должен быть положительным числом')
        return v

    @field_validator('location_id')
    @classmethod
    def validate_location_id(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError('ID местоположения должен быть положительным числом или null')
        return v

    @field_validator('pub_date')
    @classmethod
    def validate_pub_date(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v < now:
            raise ValueError('Дата публикации не может быть в прошлом')
        return v


class PostCreate(PostBase):
    """Схема для создания поста"""
    pass


class PostUpdate(BaseModel):
    """Схема для обновления поста"""
    title: Optional[str] = None
    text: Optional[str] = None
    pub_date: Optional[datetime] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Заголовок не может быть пустым')
            if len(v) < 3:
                raise ValueError('Заголовок должен содержать минимум 3 символа')
            if len(v) > 256:
                raise ValueError('Заголовок не может превышать 256 символов')
            return v.strip()
        return v

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Текст поста не может быть пустым')
            if len(v) < 10:
                raise ValueError('Текст поста должен содержать минимум 10 символов')
            return v.strip()
        return v

    @field_validator('pub_date')
    @classmethod
    def validate_pub_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v < now:
                raise ValueError('Дата публикации не может быть в прошлом')
        return v

    model_config = ConfigDict(from_attributes=True)


class Post(PostBase):
    """Основная схема поста"""
    id: int
    created_at: datetime
    author_id: int
    image: Optional[str] = Field(default=None)

    @field_validator('created_at', 'pub_date', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        """Преобразует дату из БД в строку для JSON"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    model_config = ConfigDict(from_attributes=True)


class PostWithRelations(Post):
    """Пост со всеми связями"""
    category: Category
    location: Optional[Location] = None
    comments: List[Comment] = []

    model_config = ConfigDict(from_attributes=True)
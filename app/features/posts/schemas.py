from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
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

    model_config = ConfigDict(from_attributes=True)


class Post(PostBase):
    """Основная схема поста"""
    id: int
    created_at: datetime
    author_id: int
    image: Optional[str] = Field(
        default=None,
        description="Имя файла изображения или null, если изображения нет",
        examples=[None, "20260402_182413_sunset.jpg"]
    )

    model_config = ConfigDict(from_attributes=True)


class PostWithRelations(Post):
    """Пост со всеми связями"""
    category: Category
    location: Optional[Location] = None
    comments: List[Comment] = []

    model_config = ConfigDict(from_attributes=True)
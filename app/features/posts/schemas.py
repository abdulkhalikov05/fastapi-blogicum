from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, ForwardRef
from app.features.auth.schemas import User
from app.features.categories.schemas import Category
from app.features.locations.schemas import Location

# Для избежания циклических ссылок
Comment = ForwardRef('Comment')


class PostBase(BaseModel):
    title: str
    text: str
    pub_date: datetime
    is_published: bool = True
    category_id: int
    location_id: Optional[int] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    pub_date: Optional[datetime] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None


class Post(PostBase):
    id: int
    created_at: datetime
    author_id: int
    image: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class PostWithRelations(Post):
    author: User
    category: Category
    location: Optional[Location] = None
    comments: List['Comment'] = []


# Импортируем Comment после объявления
from app.features.comments.schemas import Comment
PostWithRelations.model_rebuild()

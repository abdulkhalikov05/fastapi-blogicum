from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


# Базовые схемы для пользователя
class UserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# Базовые схемы для категорий
class CategoryBase(BaseModel):
    title: str
    description: str
    slug: str
    is_published: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Базовые схемы для местоположений
class LocationBase(BaseModel):
    name: str
    is_published: bool = True


class LocationCreate(LocationBase):
    pass


class Location(LocationBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Базовые схемы для постов
class PostBase(BaseModel):
    title: str
    text: str
    pub_date: datetime
    is_published: bool = True
    category_id: int
    location_id: Optional[int] = None


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


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


# Базовые схемы для комментариев
class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    created_at: datetime
    author_id: int
    post_id: int
    is_published: bool
    model_config = ConfigDict(from_attributes=True)


class CommentWithAuthor(Comment):
    author: User


# Чтобы работали ссылки вперед (PostWithRelations -> Comment)
PostWithRelations.model_rebuild()

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.features.auth.schemas import User


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class Comment(CommentBase):
    id: int
    created_at: datetime
    author_id: int
    post_id: int
    is_published: bool
    
    model_config = ConfigDict(from_attributes=True)


class CommentWithAuthor(Comment):
    author: User

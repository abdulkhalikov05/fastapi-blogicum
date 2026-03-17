from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):
    title: str
    description: str
    slug: str
    is_published: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

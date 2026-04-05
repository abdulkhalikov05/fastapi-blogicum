from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
import re


class CategoryBase(BaseModel):
    title: str
    description: str
    slug: str
    is_published: bool = True

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Название категории не может быть пустым')
        if len(v) < 3:
            raise ValueError('Название категории должно содержать минимум 3 символа')
        if len(v) > 256:
            raise ValueError('Название категории не может превышать 256 символов')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Описание категории не может быть пустым')
        if len(v) < 10:
            raise ValueError('Описание категории должно содержать минимум 10 символов')
        return v.strip()

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Slug не может быть пустым')
        if not re.match(r'^[a-z0-9_-]+$', v):
            raise ValueError('Slug может содержать только латинские буквы, цифры, дефис и подчеркивание')
        return v.strip().lower()


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Название категории не может быть пустым')
            if len(v) < 3:
                raise ValueError('Название категории должно содержать минимум 3 символа')
            if len(v) > 256:
                raise ValueError('Название категории не может превышать 256 символов')
            return v.strip()
        return v

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Slug не может быть пустым')
            if not re.match(r'^[a-z0-9_-]+$', v):
                raise ValueError('Slug может содержать только латинские буквы, цифры, дефис и подчеркивание')
            return v.strip().lower()
        return v


class Category(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

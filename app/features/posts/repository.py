from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List
from app.features.posts import models, schemas


class PostRepository:
    """Репозиторий для работы с постами"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, post_id: int, for_author: bool = False, author_id: Optional[int] = None) -> Optional[models.Post]:
        """Получить пост по ID"""
        query = self.db.query(models.Post).filter(models.Post.id == post_id)
        
        # Если не для автора - показываем только опубликованные
        if not for_author:
            query = query.filter(
                models.Post.is_published == True,
                models.Post.pub_date <= datetime.now()
            )
        elif author_id:
            query = query.filter(models.Post.author_id == author_id)
        
        return query.first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        published_only: bool = True,
        author_id: Optional[int] = None,
        category_id: Optional[int] = None,
        category_slug: Optional[str] = None,
        show_future: bool = False
    ) -> List[models.Post]:
        """Получить список постов с фильтрацией"""
        query = self.db.query(models.Post).join(models.Category)
        
        # Фильтр по публикации
        if published_only:
            query = query.filter(models.Post.is_published == True)
            query = query.filter(models.Category.is_published == True)
        
        # Фильтр по дате публикации
        if not show_future:
            query = query.filter(models.Post.pub_date <= datetime.now())
        
        # Фильтр по автору
        if author_id:
            query = query.filter(models.Post.author_id == author_id)
        
        # Фильтр по категории
        if category_id:
            query = query.filter(models.Post.category_id == category_id)
        if category_slug:
            query = query.filter(models.Category.slug == category_slug)
        
        return query.order_by(desc(models.Post.pub_date)).offset(skip).limit(limit).all()
    
    def create(self, post_data: schemas.PostCreate, author_id: int, image_path: Optional[str] = None) -> models.Post:
        """Создать новый пост"""
        db_post = models.Post(
            **post_data.dict(),
            author_id=author_id,
            image=image_path
        )
        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)
        return db_post
    
    def update(self, post_id: int, post_data: schemas.PostUpdate, image_path: Optional[str] = None) -> Optional[models.Post]:
        """Обновить пост"""
        db_post = self.get(post_id)
        if not db_post:
            return None
        
        update_dict = post_data.dict(exclude_unset=True)
        if image_path:
            update_dict['image'] = image_path
        
        for field, value in update_dict.items():
            setattr(db_post, field, value)
        
        self.db.commit()
        self.db.refresh(db_post)
        return db_post
    
    def delete(self, post_id: int) -> bool:
        """Удалить пост"""
        db_post = self.get(post_id)
        if not db_post:
            return False
        
        self.db.delete(db_post)
        self.db.commit()
        return True
    
    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 10) -> List[models.Post]:
        """Получить посты автора"""
        return self.get_all(
            skip=skip,
            limit=limit,
            author_id=author_id,
            published_only=False,
            show_future=True
        )

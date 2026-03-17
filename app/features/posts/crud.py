from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List

from app.features.posts import models, schemas


def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    is_published: bool = True,
    author_id: Optional[int] = None,
    category_slug: Optional[str] = None,
    category_id: Optional[int] = None,
    show_future: bool = False
) -> List[models.Post]:
    """
    Получить список постов с фильтрацией
    Аналог query_post из Django
    """
    query = db.query(models.Post).join(models.Category)

    # Фильтр по публикации
    if is_published:
        query = query.filter(models.Post.is_published == True)
        query = query.filter(models.Category.is_published == True)

    # Фильтр по дате публикации (отложенные посты)
    if not show_future:
        query = query.filter(models.Post.pub_date <= datetime.now())

    # Фильтр по автору
    if author_id:
        query = query.filter(models.Post.author_id == author_id)

    # Фильтр по категории
    if category_slug:
        query = query.filter(models.Category.slug == category_slug)
    if category_id:
        query = query.filter(models.Post.category_id == category_id)

    return query.order_by(desc(models.Post.pub_date)).offset(skip).limit(limit).all()


def get_post(
    db: Session, 
    post_id: int, 
    check_author: bool = False, 
    author_id: Optional[int] = None
) -> Optional[models.Post]:
    """
    Получить детали поста
    Аналог post_detail из Django
    """
    query = db.query(models.Post).filter(models.Post.id == post_id)

    # Если проверяем автора (для неавторизованных показываем только опубликованное)
    if not check_author:
        query = query.filter(models.Post.is_published == True)
        query = query.filter(models.Post.pub_date <= datetime.now())
    elif author_id:
        # Для автора показываем все его посты
        query = query.filter(models.Post.author_id == author_id)

    return query.first()


def create_post(
    db: Session, 
    post: schemas.PostCreate, 
    author_id: int, 
    image_path: Optional[str] = None
) -> models.Post:
    """Создать новый пост"""
    post_data = post.dict()
    db_post = models.Post(
        **post_data,
        author_id=author_id,
        image=image_path
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(
    db: Session, 
    post_id: int, 
    post_update: schemas.PostUpdate, 
    image_path: Optional[str] = None
) -> Optional[models.Post]:
    """Обновить пост"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        return None
    
    update_data = post_update.dict(exclude_unset=True)
    if image_path:
        update_data['image'] = image_path

    for field, value in update_data.items():
        setattr(db_post, field, value)

    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int) -> Optional[models.Post]:
    """Удалить пост"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post


def get_posts_by_author(
    db: Session, 
    author_id: int, 
    skip: int = 0, 
    limit: int = 10
) -> List[models.Post]:
    """Получить посты автора"""
    return get_posts(db, skip=skip, limit=limit, author_id=author_id, show_future=True)

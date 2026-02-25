from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List

from app import models, schemas


# ----- Пользователи -----
def get_user(db: Session, user_id: int):
    """Получить пользователя по ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """Получить пользователя по имени"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """Получить пользователя по email"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    """Список пользователей с пагинацией"""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    """Создать нового пользователя"""
    fake_hashed_password = user.password + "_not_really_hashed"
    db_user = models.User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=fake_hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Обновить данные пользователя"""
    db_user = get_user(db, user_id)
    for key, value in user_update.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    """Удалить пользователя"""
    db_user = get_user(db, user_id)
    db.delete(db_user)
    db.commit()
    return db_user


# ----- Категории -----
def get_category(db: Session, category_id: int):
    """Получить категорию по ID"""
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str):
    """Получить категорию по slug"""
    return db.query(models.Category).filter(models.Category.slug == slug).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100, published_only: bool = True):
    """Список категорий с пагинацией"""
    query = db.query(models.Category)
    if published_only:
        query = query.filter(models.Category.is_published == True)
    return query.offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate):
    """Создать новую категорию"""
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate):
    """Обновить категорию"""
    db_category = get_category(db, category_id)
    for key, value in category_update.dict().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    """Удалить категорию"""
    db_category = get_category(db, category_id)
    db.delete(db_category)
    db.commit()
    return db_category


# ----- Локации -----
def get_location(db: Session, location_id: int):
    """Получить локацию по ID"""
    return db.query(models.Location).filter(models.Location.id == location_id).first()


def get_locations(db: Session, skip: int = 0, limit: int = 100, published_only: bool = True):
    """Список локаций с пагинацией"""
    query = db.query(models.Location)
    if published_only:
        query = query.filter(models.Location.is_published == True)
    return query.offset(skip).limit(limit).all()


def create_location(db: Session, location: schemas.LocationCreate):
    """Создать новую локацию"""
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(db: Session, location_id: int, location_update: schemas.LocationCreate):
    """Обновить локацию"""
    db_location = get_location(db, location_id)
    for key, value in location_update.dict().items():
        setattr(db_location, key, value)
    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: int):
    """Удалить локацию"""
    db_location = get_location(db, location_id)
    db.delete(db_location)
    db.commit()
    return db_location


# ----- Посты -----
def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    published_only: bool = True,
    author_id: Optional[int] = None,
    category_slug: Optional[str] = None,
    show_future: bool = False,  # показывать ли отложенные посты
    is_admin: bool = False  # если админ - видит всё
):
    """
    Получить список постов с фильтрацией
    Аналог query_post() из Django
    """
    query = db.query(models.Post).join(models.Category)

    # Базовые фильтры публикации
    if published_only and not is_admin:
        query = query.filter(models.Post.is_published == True)
        query = query.filter(models.Category.is_published == True)

    # Фильтр по дате публикации (отложенные посты)
    if not show_future and not is_admin:
        query = query.filter(models.Post.pub_date <= datetime.now())

    # Фильтр по автору
    if author_id:
        query = query.filter(models.Post.author_id == author_id)

    # Фильтр по категории
    if category_slug:
        query = query.filter(models.Category.slug == category_slug)

    return query.order_by(desc(models.Post.pub_date)).offset(skip).limit(limit).all()


def get_post(
    db: Session,
    post_id: int,
    check_author: bool = False,
    author_id: Optional[int] = None,
    is_admin: bool = False
):
    """
    Получить один пост с проверкой прав
    Аналог get_object_or_404 с проверкой автора
    """
    query = db.query(models.Post).filter(models.Post.id == post_id)

    # Если проверяем автора (для неавторизованных показываем только опубликованное)
    if not check_author and not is_admin:
        query = query.filter(models.Post.is_published == True)
        query = query.filter(models.Post.pub_date <= datetime.now())
    elif author_id:
        # Для автора показываем все его посты
        query = query.filter(models.Post.author_id == author_id)

    return query.first()


def get_posts_count(db: Session, author_id: Optional[int] = None):
    """Получить количество постов (для пагинации)"""
    query = db.query(models.Post)
    if author_id:
        query = query.filter(models.Post.author_id == author_id)
    return query.count()


def create_post(db: Session, post: schemas.PostCreate, author_id: int, image_path: Optional[str] = None):
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


def update_post(db: Session, post_id: int, post_update: schemas.PostUpdate, image_path: Optional[str] = None):
    """Обновить пост"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    update_data = post_update.dict()
    if image_path:
        update_data['image'] = image_path

    for key, value in update_data.items():
        setattr(db_post, key, value)

    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int):
    """Удалить пост"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    db.delete(db_post)
    db.commit()
    return db_post


# ----- Комментарии -----
def get_comments(db: Session, post_id: int, skip: int = 0, limit: int = 50):
    """Получить комментарии к посту"""
    return db.query(models.Comment)\
        .filter(models.Comment.post_id == post_id)\
        .filter(models.Comment.is_published == True)\
        .order_by(models.Comment.created_at)\
        .offset(skip).limit(limit).all()


def get_comment(db: Session, comment_id: int):
    """Получить комментарий по ID"""
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int):
    """Создать новый комментарий"""
    db_comment = models.Comment(
        text=comment.text,
        author_id=author_id,
        post_id=comment.post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_comment(db: Session, comment_id: int, comment_update: schemas.CommentUpdate):
    """Обновить комментарий"""
    db_comment = get_comment(db, comment_id)
    for key, value in comment_update.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int):
    """Удалить комментарий"""
    db_comment = get_comment(db, comment_id)
    db.delete(db_comment)
    db.commit()
    return db_comment

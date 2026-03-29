from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List

from app.features.posts import models, schemas
from app.features.categories.models import Category


def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    is_published: bool = True,
    author_id: Optional[int] = None,
    category_slug: Optional[str] = None,
    show_future: bool = False
) -> List[models.Post]:
    query = db.query(models.Post).join(Category)

    if is_published:
        query = query.filter(models.Post.is_published == True)
        query = query.filter(Category.is_published == True)

    if not show_future:
        query = query.filter(models.Post.pub_date <= datetime.now())

    if author_id:
        query = query.filter(models.Post.author_id == author_id)

    if category_slug:
        query = query.filter(Category.slug == category_slug)

    return query.order_by(desc(models.Post.pub_date)).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int, check_author: bool = False, author_id: Optional[int] = None) -> Optional[models.Post]:
    query = db.query(models.Post).filter(models.Post.id == post_id)

    if not check_author:
        query = query.filter(models.Post.is_published == True)
        query = query.filter(models.Post.pub_date <= datetime.now())
    elif author_id:
        query = query.filter(models.Post.author_id == author_id)

    return query.first()


def create_post(db: Session, post: schemas.PostCreate, author_id: int, image_path: Optional[str] = None) -> models.Post:
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


def update_post(db: Session, post_id: int, post_update: schemas.PostUpdate, image_path: Optional[str] = None) -> Optional[models.Post]:
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
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post
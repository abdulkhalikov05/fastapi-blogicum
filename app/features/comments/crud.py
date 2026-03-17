from sqlalchemy.orm import Session
from app.features.comments import models, schemas
from typing import Optional, List


def get_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    """Получить комментарий по ID"""
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def get_comments(
    db: Session, 
    post_id: int, 
    skip: int = 0, 
    limit: int = 50
) -> List[models.Comment]:
    """Получить комментарии к посту"""
    return db.query(models.Comment)\
        .filter(models.Comment.post_id == post_id)\
        .filter(models.Comment.is_published == True)\
        .order_by(models.Comment.created_at)\
        .offset(skip).limit(limit).all()


def create_comment(
    db: Session, 
    comment: schemas.CommentCreate, 
    author_id: int
) -> models.Comment:
    """Создать комментарий"""
    db_comment = models.Comment(
        text=comment.text,
        author_id=author_id,
        post_id=comment.post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_comment(
    db: Session, 
    comment_id: int, 
    comment_update: schemas.CommentUpdate
) -> Optional[models.Comment]:
    """Обновить комментарий"""
    db_comment = get_comment(db, comment_id)
    if db_comment:
        update_data = comment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)
        db.commit()
        db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    """Удалить комментарий"""
    db_comment = get_comment(db, comment_id)
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment


def get_user_comments(
    db: Session, 
    author_id: int, 
    skip: int = 0, 
    limit: int = 50
) -> List[models.Comment]:
    """Получить комментарии пользователя"""
    return db.query(models.Comment)\
        .filter(models.Comment.author_id == author_id)\
        .order_by(desc(models.Comment.created_at))\
        .offset(skip).limit(limit).all()

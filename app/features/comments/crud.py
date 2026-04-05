from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List

from app.features.comments import models, schemas
from app.core.exceptions import DatabaseError, NotFoundError


def get_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    try:
        return db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    except SQLAlchemyError as e:
        raise DatabaseError("получение комментария", str(e))


def get_comments(
    db: Session,
    post_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[models.Comment]:
    try:
        return db.query(models.Comment)\
            .filter(models.Comment.post_id == post_id)\
            .filter(models.Comment.is_published == True)\
            .order_by(models.Comment.created_at)\
            .offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DatabaseError("получение комментариев", str(e))


def create_comment(
    db: Session,
    comment: schemas.CommentCreate,
    author_id: int
) -> models.Comment:
    try:
        db_comment = models.Comment(
            text=comment.text,
            author_id=author_id,
            post_id=comment.post_id
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError("создание комментария (нарушение целостности)", str(e))
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("создание комментария", str(e))


def update_comment(
    db: Session,
    comment_id: int,
    comment_update: schemas.CommentUpdate
) -> Optional[models.Comment]:
    try:
        db_comment = get_comment(db, comment_id)
        if not db_comment:
            raise NotFoundError("Comment", comment_id)

        update_data = comment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)

        db.commit()
        db.refresh(db_comment)
        return db_comment
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("обновление комментария", str(e))


def delete_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    try:
        db_comment = get_comment(db, comment_id)
        if not db_comment:
            raise NotFoundError("Comment", comment_id)

        db.delete(db_comment)
        db.commit()
        return db_comment
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("удаление комментария", str(e))


def get_user_comments(
    db: Session,
    author_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[models.Comment]:
    try:
        return db.query(models.Comment)\
            .filter(models.Comment.author_id == author_id)\
            .order_by(desc(models.Comment.created_at))\
            .offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DatabaseError("получение комментариев пользователя", str(e))

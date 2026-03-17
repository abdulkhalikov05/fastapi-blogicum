from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.features.comments import models, schemas


class CommentRepository:
    """Репозиторий для работы с комментариями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, comment_id: int) -> Optional[models.Comment]:
        """Получить комментарий по ID"""
        return self.db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 50) -> List[models.Comment]:
        """Получить комментарии к посту"""
        return self.db.query(models.Comment)\
            .filter(models.Comment.post_id == post_id)\
            .filter(models.Comment.is_published == True)\
            .order_by(models.Comment.created_at)\
            .offset(skip).limit(limit).all()
    
    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 50) -> List[models.Comment]:
        """Получить комментарии автора"""
        return self.db.query(models.Comment)\
            .filter(models.Comment.author_id == author_id)\
            .order_by(desc(models.Comment.created_at))\
            .offset(skip).limit(limit).all()
    
    def create(self, comment_data: schemas.CommentCreate, author_id: int) -> models.Comment:
        """Создать новый комментарий"""
        db_comment = models.Comment(
            text=comment_data.text,
            author_id=author_id,
            post_id=comment_data.post_id
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def update(self, comment_id: int, comment_data: schemas.CommentUpdate) -> Optional[models.Comment]:
        """Обновить комментарий"""
        db_comment = self.get(comment_id)
        if not db_comment:
            return None
        
        update_dict = comment_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_comment, field, value)
        
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def delete(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        db_comment = self.get(comment_id)
        if not db_comment:
            return False
        
        self.db.delete(db_comment)
        self.db.commit()
        return True

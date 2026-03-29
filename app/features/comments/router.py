from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.features.comments import crud, schemas
from app.features.posts import crud as post_crud

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/post/{post_id}", response_model=List[schemas.Comment])
async def read_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Получить комментарии к посту"""
    return crud.get_comments(db, post_id=post_id, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db)
):
    """Создать комментарий"""
    # Проверяем, что пост существует
    post = post_crud.get_post(db, comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Временно используем author_id = 1
    return crud.create_comment(db, comment, 1)


@router.put("/{comment_id}", response_model=schemas.Comment)
async def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: Session = Depends(get_db)
):
    """Обновить комментарий"""
    comment = crud.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return crud.update_comment(db, comment_id, comment_update)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """Удалить комментарий"""
    comment = crud.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    crud.delete_comment(db, comment_id)
    return None
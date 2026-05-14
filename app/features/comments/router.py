from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.exceptions import NotFoundError, DatabaseError, ValidationError
from app.features.comments import crud, schemas
from app.features.posts import crud as post_crud
from app.core.dependencies import get_current_user
from app.features.auth.models import User

router = APIRouter(prefix="/comments", tags=["comments"])


# ====================== GET ======================
@router.get("/post/{post_id}", response_model=List[schemas.Comment])
async def read_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    try:
        return crud.get_comments(db, post_id=post_id, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


# ====================== CREATE ======================
@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔥 защита
):
    try:
        post = post_crud.get_post(db, comment.post_id)

        if not post:
            raise NotFoundError("Post", comment.post_id)

        return crud.create_comment(
            db,
            comment,
            author_id=current_user.id  # 🔥 теперь реальный пользователь
        )

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


# ====================== UPDATE ======================
@router.put("/{comment_id}", response_model=schemas.Comment)
async def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔥 защита
):
    try:
        comment = crud.get_comment(db, comment_id)

        if not comment:
            raise NotFoundError("Comment", comment_id)

        # 🔥 ПРОВЕРКА ВЛАДЕЛЬЦА ИЛИ АДМИНА
        if comment.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Нет прав на редактирование комментария"
            )

        return crud.update_comment(db, comment_id, comment_update)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


# ====================== DELETE ======================
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔥 защита
):
    try:
        comment = crud.get_comment(db, comment_id)

        if not comment:
            raise NotFoundError("Comment", comment_id)

        if comment.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Нет прав на удаление комментария"
            )

        crud.delete_comment(db, comment_id)
        return None

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
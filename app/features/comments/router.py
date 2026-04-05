from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.exceptions import NotFoundError, DatabaseError, ValidationError
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
    try:
        return crud.get_comments(db, post_id=post_id, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db)
):
    try:
        post = post_crud.get_post(db, comment.post_id)
        if not post:
            raise NotFoundError("Post", comment.post_id)

        return crud.create_comment(db, comment, author_id=1)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{comment_id}", response_model=schemas.Comment)
async def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: Session = Depends(get_db)
):
    try:
        comment = crud.get_comment(db, comment_id)
        if not comment:
            raise NotFoundError("Comment", comment_id)

        return crud.update_comment(db, comment_id, comment_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    try:
        comment = crud.get_comment(db, comment_id)
        if not comment:
            raise NotFoundError("Comment", comment_id)

        crud.delete_comment(db, comment_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

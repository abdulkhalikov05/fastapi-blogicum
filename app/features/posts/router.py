from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user, get_current_active_user
from app.features.auth.schemas import User
from app.features.posts import crud, schemas

router = APIRouter(prefix="/posts", tags=["posts"])

UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=List[schemas.Post])
async def read_posts(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    author: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Получить список всех постов (аналог index в Django)"""
    posts = crud.get_posts(
        db, 
        skip=skip, 
        limit=limit,
        category_slug=category,
        author_id=author
    )
    return posts


@router.get("/{post_id}", response_model=schemas.PostWithRelations)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Получить детальную информацию о посте (аналог post_detail)"""
    # Проверяем, автор ли это (чтобы показывать черновики)
    check_author = current_user is not None
    author_id = current_user.id if current_user else None
    
    post = crud.get_post(db, post_id, check_author=check_author, author_id=author_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    text: str = Form(...),
    pub_date: datetime = Form(...),
    category_id: int = Form(...),
    location_id: Optional[int] = Form(None),
    is_published: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новый пост (аналог create_post в Django)"""
    # Сохраняем изображение если есть
    image_path = None
    if image:
        file_path = f"{UPLOAD_DIR}/{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = file_path
    
    post_data = schemas.PostCreate(
        title=title,
        text=text,
        pub_date=pub_date,
        category_id=category_id,
        location_id=location_id,
        is_published=is_published
    )
    
    return crud.create_post(db, post_data, current_user.id, image_path)


@router.put("/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: int,
    title: str = Form(...),
    text: str = Form(...),
    pub_date: datetime = Form(...),
    category_id: int = Form(...),
    location_id: Optional[int] = Form(None),
    is_published: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить пост (аналог edit_post в Django)"""
    # Проверяем, что пост существует и принадлежит текущему пользователю
    post = crud.get_post(db, post_id, check_author=True, author_id=current_user.id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Сохраняем новое изображение если есть
    image_path = None
    if image:
        file_path = f"{UPLOAD_DIR}/{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = file_path
    
    post_update = schemas.PostUpdate(
        title=title,
        text=text,
        pub_date=pub_date,
        category_id=category_id,
        location_id=location_id,
        is_published=is_published
    )
    
    return crud.update_post(db, post_id, post_update, image_path)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить пост (аналог delete_post в Django)"""
    # Проверяем, что пост существует и принадлежит текущему пользователю
    post = crud.get_post(db, post_id, check_author=True, author_id=current_user.id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Удаляем изображение если есть
    if post.image and os.path.exists(post.image):
        os.remove(post.image)
    
    crud.delete_post(db, post_id)
    return None

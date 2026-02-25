from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from app import crud, schemas
from app.database import get_db
from app.dependencies import get_current_user, get_pagination

router = APIRouter(prefix="/posts", tags=["posts"])

# Создаем папку для загрузки изображений
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
    """
    Получить список всех постов
    Аналог index() и category_posts() из Django
    """
    posts = crud.get_posts(
        db,
        skip=skip,
        limit=limit,
        category_slug=category,
        author_id=author,
        published_only=True  # Только опубликованные
    )
    return posts


@router.get("/{post_id}", response_model=schemas.PostWithRelations)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[schemas.User] = Depends(get_current_user)
):
    """
    Получить детальную информацию о посте
    Аналог post_detail() из Django
    """
    # Определяем, нужно ли показывать неопубликованные посты
    check_author = current_user is not None
    author_id = current_user.id if current_user else None

    post = crud.get_post(
        db,
        post_id,
        check_author=check_author,
        author_id=author_id
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )

    # Загружаем комментарии к посту
    post.comments = crud.get_comments(db, post_id)

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
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Создать новый пост
    Аналог create_post() из Django
    """
    # Сохраняем изображение если есть
    image_path = None
    if image and image.filename:
        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(image.filename)[1]
        file_name = f"{datetime.now().timestamp()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

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
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Обновить пост
    Аналог edit_post() из Django
    """
    # Проверяем существование поста и права доступа
    post = crud.get_post(db, post_id, check_author=True, author_id=current_user.id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для редактирования этого поста"
        )

    # Сохраняем новое изображение если есть
    image_path = None
    if image and image.filename:
        # Удаляем старое изображение если есть
        if post.image and os.path.exists(post.image):
            os.remove(post.image)

        # Сохраняем новое
        file_extension = os.path.splitext(image.filename)[1]
        file_name = f"{datetime.now().timestamp()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

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
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Удалить пост
    Аналог delete_post() из Django
    """
    post = crud.get_post(db, post_id, check_author=True, author_id=current_user.id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для удаления этого поста"
        )

    # Удаляем изображение если есть
    if post.image and os.path.exists(post.image):
        os.remove(post.image)

    crud.delete_post(db, post_id)
    return None

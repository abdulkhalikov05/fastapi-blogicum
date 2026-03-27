from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated, Union
from pathlib import Path
import os
from datetime import datetime

from app.core.database import get_db
from app.features.posts import crud, schemas

router = APIRouter(prefix="/posts", tags=["posts"])

UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ


# ====================== Вспомогательные функции ======================
async def save_uploaded_image(image: Union[UploadFile, str, None]) -> Optional[str]:
    """Сохраняет изображение. Защищено от пустых строк из curl."""
    # Защита от пустого поля (когда приходит image= или image="")
    if not image or isinstance(image, str) or not getattr(image, "filename", None):
        return None

    # Проверка типа файла
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тип изображения. Разрешено: {ALLOWED_IMAGE_TYPES}",
        )

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{os.path.basename(image.filename)}"
        file_path = UPLOAD_DIR / safe_filename

        content_size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await image.read(1024 * 1024):  # читаем по 1 МБ
                content_size += len(chunk)
                if content_size > MAX_FILE_SIZE:
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=400, detail="Файл слишком большой (макс. 10 МБ)")
                buffer.write(chunk)

        print(f"✅ Изображение сохранено: {safe_filename}")
        return safe_filename

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка при сохранении изображения: {e}")
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        return None


def delete_old_image(filename: Optional[str]) -> None:
    """Удаляет старое изображение"""
    if not filename:
        return
    file_path = UPLOAD_DIR / filename
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ Удалено старое изображение: {filename}")
    except Exception as e:
        print(f"⚠️ Не удалось удалить изображение {filename}: {e}")


# ====================== CREATE ======================
@router.post(
    "/",
    response_model=schemas.Post,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый пост",
    description="Создаёт пост с возможностью загрузки одного изображения.",
    responses={
        201: {
            "description": "Пост успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "title": "Мой первый пост",
                        "text": "Текст поста...",
                        "pub_date": "2026-04-02T20:00:00",
                        "is_published": True,
                        "category_id": 1,
                        "location_id": 0,
                        "id": 10,
                        "created_at": "2026-04-02T18:30:00",
                        "author_id": 1,
                        "image": None
                    }
                }
            }
        },
        400: {"description": "Ошибка валидации файла (слишком большой или неверный тип)"},
        422: {"description": "Ошибка валидации данных"},
    }
)
async def create_post(
    title: Annotated[str, Form(...)],
    text: Annotated[str, Form(...)],
    pub_date: Annotated[datetime, Form(...)],
    category_id: Annotated[int, Form(...)],
    location_id: Annotated[Optional[int], Form()] = None,
    is_published: Annotated[bool, Form()] = True,
    image: Annotated[Union[UploadFile, str, None], File()] = None,
    db: Session = Depends(get_db),
):
    """Создать новый пост"""
    image_path = await save_uploaded_image(image)

    post_data = schemas.PostCreate(
        title=title,
        text=text,
        pub_date=pub_date,
        category_id=category_id,
        location_id=location_id,
        is_published=is_published,
    )

    return crud.create_post(db, post_data, author_id=1, image_path=image_path)


# ====================== UPDATE ======================
@router.put(
    "/{post_id}",
    response_model=schemas.Post,
    status_code=status.HTTP_200_OK,
    summary="Обновить существующий пост",
    description="Обновляет пост. Все поля обязательны для передачи, кроме location_id. "
                "Изображение можно заменить (прислать новое) или оставить без изменений (не присылать файл).",
    responses={
        200: {
            "description": "Пост успешно обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "title": "Обновлённый заголовок поста",
                        "text": "Новый текст поста...",
                        "pub_date": "2026-04-02T20:00:00",
                        "is_published": True,
                        "category_id": 2,
                        "location_id": 0,
                        "id": 15,
                        "created_at": "2026-04-02T18:27:48",
                        "author_id": 1,
                        "image": "20260402_182748_new_photo.jpg"   # или null
                    }
                }
            }
        },
        404: {
            "description": "Пост не найден"
        },
        400: {
            "description": "Ошибка валидации изображения (слишком большой файл или неверный формат)"
        },
        422: {
            "description": "Ошибка валидации входных данных"
        }
    }
)
async def update_post(
    post_id: int,
    title: Annotated[str, Form(...)],
    text: Annotated[str, Form(...)],
    pub_date: Annotated[datetime, Form(...)],
    category_id: Annotated[int, Form(...)],
    location_id: Annotated[Optional[int], Form()] = None,
    is_published: Annotated[bool, Form()] = True,
    image: Annotated[Union[UploadFile, str, None], File()] = None,
    db: Session = Depends(get_db),
):
    """Обновить пост"""
    post = crud.get_post(db, post_id, check_author=False, author_id=None)
    if not post:
        raise HTTPException(
            status_code=404, 
            detail="Post not found"
        )

    image_path = await save_uploaded_image(image)

    # Удаляем старое изображение только если пришло новое
    if image_path and getattr(post, "image", None):
        delete_old_image(post.image)

    post_update = schemas.PostUpdate(
        title=title,
        text=text,
        pub_date=pub_date,
        category_id=category_id,
        location_id=location_id,
        is_published=is_published,
    )

    return crud.update_post(db, post_id, post_update, image_path)


# ====================== DELETE ======================
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = crud.get_post(db, post_id, check_author=False, author_id=None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    delete_old_image(getattr(post, "image", None))
    crud.delete_post(db, post_id)
    return None


# GET эндпоинты (без изменений)
@router.get("/", response_model=List[schemas.Post])
async def read_posts(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    author: Optional[int] = None,
    db: Session = Depends(get_db),
):
    posts = crud.get_posts(
        db, skip=skip, limit=limit, category_slug=category, author_id=author
    )
    return posts


@router.get("/{post_id}", response_model=schemas.PostWithRelations)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = crud.get_post(db, post_id, check_author=False, author_id=None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
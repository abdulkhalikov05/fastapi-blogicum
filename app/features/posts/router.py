from fastapi import (
    APIRouter,
    Depends,
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
from app.core.dependencies import get_current_user
from app.features.auth.models import User
from app.features.posts import schemas
from app.features.posts.repository import PostRepository
from app.features.posts.service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])

UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024


async def save_uploaded_image(image: Union[UploadFile, str, None]) -> Optional[str]:
    if not image or isinstance(image, str) or not getattr(image, "filename", None):
        return None

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise Exception("Недопустимый тип изображения")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{os.path.basename(image.filename)}"
    file_path = UPLOAD_DIR / safe_filename

    content_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := await image.read(1024 * 1024):
            content_size += len(chunk)
            if content_size > MAX_FILE_SIZE:
                file_path.unlink(missing_ok=True)
                raise Exception("Файл слишком большой")
            buffer.write(chunk)

    return safe_filename


def delete_old_image(filename: Optional[str]) -> None:
    if not filename:
        return

    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()


# ====================== CREATE ======================
@router.post(
    "/",
    response_model=schemas.Post,
    status_code=status.HTTP_201_CREATED,
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
    current_user: User = Depends(get_current_user),
):
    repo = PostRepository(db)
    service = PostService(repo)

    image_path = await save_uploaded_image(image)

    post_data = schemas.PostCreate(
        title=title,
        text=text,
        pub_date=pub_date,
        category_id=category_id,
        location_id=location_id,
        is_published=is_published,
    )

    return service.create_post(post_data, author_id=current_user.id, image_path=image_path)


# ====================== UPDATE ======================
@router.put(
    "/{post_id}",
    response_model=schemas.Post,
    status_code=status.HTTP_200_OK,
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
    current_user: User = Depends(get_current_user),
):
    repo = PostRepository(db)
    service = PostService(repo)

    image_path = await save_uploaded_image(image)

    post_update = schemas.PostUpdate(
        title=title,
        text=text,
        pub_date=pub_date,
        category_id=category_id,
        location_id=location_id,
        is_published=is_published,
    )

    return service.update_post(
        post_id=post_id,
        post_data=post_update,
        user_id=current_user.id,
        image_path=image_path,
    )


# ====================== DELETE ======================
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = PostRepository(db)
    service = PostService(repo)

    service.delete_post(post_id, user_id=current_user.id)
    return None


# ====================== GET ======================
@router.get("/", response_model=List[schemas.Post])
async def read_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    repo = PostRepository(db)
    service = PostService(repo)

    return service.get_posts(skip=skip, limit=limit)


@router.get("/{post_id}", response_model=schemas.PostWithRelations)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    repo = PostRepository(db)
    service = PostService(repo)

    return service.get_post(post_id)
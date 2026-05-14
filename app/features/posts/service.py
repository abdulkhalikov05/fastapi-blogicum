from typing import Optional, List

from app.features.posts.repository import PostRepository
from app.features.posts import schemas, models
from app.core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    AlreadyExistsError,
    DatabaseError,
)


class PostService:
    def __init__(self, repo: PostRepository):
        self.repo = repo

    def get_post(self, post_id: int) -> models.Post:
        post = self.repo.get(post_id)

        if not post:
            raise NotFoundError(f"Пост с id={post_id} не найден")

        return post

    def get_posts(self, skip: int = 0, limit: int = 10) -> List[models.Post]:
        return self.repo.get_all(skip=skip, limit=limit)

    def create_post(
        self,
        post_data: schemas.PostCreate,
        author_id: int,
        image_path: Optional[str] = None
    ) -> models.Post:
        try:
            return self.repo.create(post_data, author_id, image_path)

        except AlreadyExistsError:
            raise AlreadyExistsError("Пост уже существует")

        except DatabaseError:
            raise DatabaseError("Ошибка при создании поста")

    def update_post(
        self,
        post_id: int,
        post_data: schemas.PostUpdate,
        user_id: int,
        image_path: Optional[str] = None
    ) -> models.Post:

        post = self.repo.get(post_id)

        if not post:
            raise NotFoundError(f"Пост с id={post_id} не найден")

        if post.author_id != user_id:
            raise PermissionDeniedError("Нет прав на изменение поста")

        try:
            return self.repo.update(post_id, post_data, image_path)

        except AlreadyExistsError:
            raise AlreadyExistsError("Конфликт при обновлении поста")

        except DatabaseError:
            raise DatabaseError("Ошибка при обновлении поста")

    def delete_post(self, post_id: int, user_id: int) -> None:
        post = self.repo.get(post_id)

        if not post:
            raise NotFoundError(f"Пост с id={post_id} не найден")

        if post.author_id != user_id:
            raise PermissionDeniedError("Нет прав на удаление поста")

        try:
            success = self.repo.delete(post_id)

            if not success:
                raise NotFoundError(f"Пост с id={post_id} не найден")

        except DatabaseError:
            raise DatabaseError("Ошибка при удалении поста")
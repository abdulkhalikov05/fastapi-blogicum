from app.core.exceptions import ValidationError, NotFoundError
from app.core.security import verify_password, create_access_token
from app.features.auth.repository import AuthRepository


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def login(self, username: str, password: str) -> str:
        user = self.repo.get_by_username(username)

        if not user:
            raise NotFoundError("Пользователь не найден")

        if not verify_password(password, user.hashed_password):
            raise ValidationError("Неверный пароль")

        return create_access_token({"sub": str(user.id)})
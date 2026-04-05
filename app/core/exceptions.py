"""
Кастомные исключения для приложения Blogicum
"""

from typing import Any, Optional


class DomainError(Exception):
    """Базовое исключение для доменного слоя"""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(DomainError):
    """Сущность не найдена"""
    def __init__(self, entity_name: str, entity_id: Optional[int] = None, slug: Optional[str] = None):
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.slug = slug
        details = {"entity": entity_name, "id": entity_id, "slug": slug}
        message = f"{entity_name} не найден"
        if entity_id:
            message = f"{entity_name} с id={entity_id} не найден"
        if slug:
            message = f"{entity_name} с slug='{slug}' не найден"
        super().__init__(message, details)


class ValidationError(DomainError):
    """Ошибка валидации"""
    def __init__(self, field: str, error: str):
        self.field = field
        self.error = error
        details = {"field": field, "error": error}
        message = f"Ошибка валидации поля '{field}': {error}"
        super().__init__(message, details)


class DatabaseError(DomainError):
    """Ошибка базы данных"""
    def __init__(self, operation: str, error: str):
        self.operation = operation
        self.error = error
        details = {"operation": operation, "db_error": error}
        message = f"Ошибка базы данных при {operation}: {error}"
        super().__init__(message, details)


class AlreadyExistsError(DomainError):
    """Сущность уже существует"""
    def __init__(self, entity_name: str, field: str, value: str):
        self.entity_name = entity_name
        self.field = field
        self.value = value
        details = {"entity": entity_name, "field": field, "value": value}
        message = f"{entity_name} с {field}='{value}' уже существует"
        super().__init__(message, details)


class PermissionDeniedError(DomainError):
    """Доступ запрещен"""
    def __init__(self, action: str, user_id: Optional[int] = None):
        self.action = action
        self.user_id = user_id
        details = {"action": action, "user_id": user_id}
        message = f"Доступ запрещен для действия '{action}'"
        if user_id:
            message = f"Пользователь id={user_id} не имеет прав на {action}"
        super().__init__(message, details)

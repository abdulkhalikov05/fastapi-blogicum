"""
Кастомные исключения для приложения Blogicum
"""

from typing import Optional, Dict, Any


class DomainError(Exception):
    """Базовое исключение для доменного слоя"""

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(message)


# ====================== COMMON ======================

class NotFoundError(DomainError):
    """Сущность не найдена"""

    def __init__(
        self,
        message: str = "Ресурс не найден",
        *,
        entity: Optional[str] = None,
        entity_id: Optional[int] = None,
    ):
        details = {
            "entity": entity,
            "id": entity_id,
        }
        super().__init__(message, code="NOT_FOUND", details=details)


class PermissionDeniedError(DomainError):
    """Доступ запрещен"""

    def __init__(
        self,
        message: str = "Доступ запрещен",
        *,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
    ):
        details = {
            "action": action,
            "user_id": user_id,
        }
        super().__init__(message, code="PERMISSION_DENIED", details=details)


# ====================== VALIDATION ======================

class ValidationError(DomainError):
    """Ошибка валидации"""

    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
    ):
        details = {"field": field}
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class AlreadyExistsError(DomainError):
    """Сущность уже существует"""

    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        details = {
            "field": field,
            "value": value,
        }
        super().__init__(message, code="ALREADY_EXISTS", details=details)


# ====================== DATABASE ======================

class DatabaseError(DomainError):
    """Ошибка базы данных"""

    def __init__(
        self,
        message: str = "Ошибка базы данных",
        *,
        operation: Optional[str] = None,
    ):
        details = {"operation": operation}
        super().__init__(message, code="DATABASE_ERROR", details=details)
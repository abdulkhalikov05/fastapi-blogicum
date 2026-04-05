from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from app.core.exceptions import (
    DomainError,
    NotFoundError,
    ValidationError,
    DatabaseError,
    PermissionDeniedError,
    AlreadyExistsError
)


async def domain_exception_handler(request: Request, exc: DomainError):
    """Централизованный обработчик всех доменных ошибок"""
    status_code = 400

    if isinstance(exc, NotFoundError):
        status_code = 404
    elif isinstance(exc, ValidationError):
        status_code = 422
    elif isinstance(exc, PermissionDeniedError):
        status_code = 403
    elif isinstance(exc, AlreadyExistsError):
        status_code = 409
    elif isinstance(exc, DatabaseError):
        status_code = 500

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик стандартных HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик всех непредвиденных ошибок"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "type": type(exc).__name__
        }
    )
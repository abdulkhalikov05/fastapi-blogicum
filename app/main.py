"""
Главный файл FastAPI приложения Blogicum
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError as PydanticValidationError
from datetime import datetime
import os

from app.core.database import engine, Base
from app.features.posts.router import router as posts_router
from app.features.comments.router import router as comments_router
from app.features.categories.router import router as categories_router
from app.features.locations.router import router as locations_router

# Создаем таблицы в базе данных
print("Создаю таблицы в базе данных...")
Base.metadata.create_all(bind=engine)
print("Готово!")

# Создаем папки для загрузки файлов
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/avatars", exist_ok=True)
print("Папки для загрузок созданы")

# Создаем приложение
app = FastAPI(
    title="Blogicum API",
    description="API для блог-платформы Blogicum",
    version="1.0.0"
)


# Обработчик ошибок валидации Pydantic
@app.exception_handler(PydanticValidationError)
async def pydantic_validation_handler(request: Request, exc: PydanticValidationError):
    """Обработчик ошибок валидации Pydantic"""
    errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        msg = error["msg"]
        
        # Преобразуем datetime в строку для JSON
        input_value = error.get("input")
        if isinstance(input_value, datetime):
            input_value = input_value.isoformat()
        
        errors.append({
            "field": field,
            "message": msg,
            "type": error["type"],
            "input": input_value
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации данных",
            "errors": errors
        }
    )


# Обработчик ошибок валидации запроса
@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации запроса"""
    errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации запроса",
            "errors": errors
        }
    )


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем роутеры
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(categories_router)
app.include_router(locations_router)


# Для статических файлов
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Blogicum API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "posts": "/posts",
            "comments": "/comments",
            "categories": "/categories",
            "locations": "/locations",
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }
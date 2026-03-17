"""
Главный файл FastAPI приложения Blogicum
Перенос с Django на FastAPI
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Импортируем свои модули (исправленные пути)
from app.core.database import engine, Base
from app.features.posts.router import router as posts_router
from app.features.comments.router import router as comments_router
from app.features.categories.router import router as categories_router
from app.features.locations.router import router as locations_router
from app.features.auth.router import router as auth_router

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
app.include_router(auth_router)

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
            "auth": "/auth"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

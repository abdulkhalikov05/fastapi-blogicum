# -*- coding: utf-8 -*-
"""
Главный файл FastAPI приложения Blogicum
Перенос с Django на FastAPI
"""

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

# Импортируем свои модули
from app.database import engine, Base, get_db  # ВАЖНО: добавили get_db!
from app.routers import posts, comments, categories, locations, users
from app import crud

# Создаем таблицы в базе данных
print("Создаю таблицы в базе данных...")
Base.metadata.create_all(bind=engine)
print("Готово!")

# Создаем папки для загрузки файлов
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/avatars", exist_ok=True)
print("Папки для загрузок созданы")

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="Blogicum API",
    description="API для блог-платформы Blogicum. Перенос с Django на FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(categories.router)
app.include_router(locations.router)
app.include_router(users.router)

# Раздача статических файлов
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Blogicum API!",
        "documentation": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):  # ← теперь get_db определена!
    """
    Статистика по блогу
    """
    posts_count = len(crud.get_posts(db, limit=10000, published_only=False))
    categories_count = len(crud.get_categories(db, limit=1000, published_only=False))
    users_count = len(crud.get_users(db, limit=1000))
    
    return {
        "posts": posts_count,
        "categories": categories_count,
        "users": users_count,
    }


@app.get("/info")
async def info():
    return {
        "project": "Blogicum",
        "framework": "FastAPI",
        "original": "Django проект с 6 спринта",
        "endpoints": "/docs"
    }
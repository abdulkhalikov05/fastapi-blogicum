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
from app.core.logger import logger

from app.features.posts.router import router as posts_router
from app.features.comments.router import router as comments_router
from app.features.categories.router import router as categories_router
from app.features.locations.router import router as locations_router
from app.features.auth.router import router as auth_router

# ====================== INIT ======================

logger.info("Инициализация приложения...")

# ⚠️ Для сдачи (если у тебя нет 100% Alembic) — оставить
Base.metadata.create_all(bind=engine)
logger.info("Таблицы базы данных проверены/созданы")

# папки для файлов
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/avatars", exist_ok=True)
logger.info("Папки для загрузок созданы")

# ====================== APP ======================

app = FastAPI(
    title="Blogicum API",
    description="API для блог-платформы Blogicum",
    version="1.0.0"
)

# ====================== LOGGING MIDDLEWARE ======================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Запрос: {request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(
        f"Ответ: {request.method} {request.url.path} -> {response.status_code}"
    )

    return response

# ====================== CORS ======================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== ROUTERS ======================

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(categories_router)
app.include_router(locations_router)

# ====================== STATIC ======================

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ====================== EXCEPTION HANDLERS ======================

@app.exception_handler(PydanticValidationError)
async def pydantic_validation_handler(request: Request, exc: PydanticValidationError):
    error = exc.errors()[0]

    field = error["loc"][-1] if error["loc"] else "unknown"
    msg = error["msg"]

    input_value = error.get("input")
    if isinstance(input_value, datetime):
        input_value = input_value.isoformat()

    logger.warning(f"Pydantic validation error: {field} - {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации данных",
            "error": {
                "field": field,
                "message": msg,
                "type": error["type"],
                "input": input_value
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]

    field = error["loc"][-1] if error["loc"] else "unknown"
    msg = error["msg"]

    logger.warning(f"Request validation error: {field} - {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации запроса",
            "error": {
                "field": field,
                "message": msg,
                "type": error["type"]
            }
        }
    )

# ====================== ENDPOINTS ======================

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")

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
    logger.info("Health check")

    return {
        "status": "healthy",
        "database": "connected"
    }
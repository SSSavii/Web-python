from fastapi import FastAPI
from contextlib import asynccontextmanager

from database import engine, Base
from routers.users import router


# Создаем таблицы при запуске приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle событие для создания таблиц при старте"""
    # Startup
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована")
    yield
    # Shutdown
    print("Приложение завершает работу")


# Создаем приложение FastAPI
app = FastAPI(
    title="Lab4: Users CRUD API with Database",
    version="2.0.0",
    description="CRUD API для управления пользователями с использованием SQLAlchemy и базы данных",
    lifespan=lifespan
)

# Подключаем роутер
app.include_router(router)


@app.get("/", tags=["root"])
def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "Лабораторная работа 4: REST API с базой данных",
        "docs": "Перейдите на /docs для просмотра Swagger UI",
        "database": "SQLite (lab4_users.db)"
    }

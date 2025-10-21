from fastapi import FastAPI
from database import engine, Base
from routers.todos import router

# Создаем таблицы при запуске приложения
Base.metadata.create_all(bind=engine)

# Создаем приложение FastAPI
app = FastAPI(
    title="Lab5: Todo List API",
    description="CRUD API для управления задачами"
)

# Подключаем роутер
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Todo List API"}
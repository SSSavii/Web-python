# main.py
from fastapi import FastAPI
from routers.users import router  # <-- импортируем наш роутер

app = FastAPI(
    title="Lab3: Users CRUD API",
    version="1.0.0",
    description="Простейший CRUD для пользователей"
)

app.include_router(router)
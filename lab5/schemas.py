from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """Базовая схема задачи"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None)


class TodoCreate(TodoBase):
    """Схема для создания новой задачи"""
    pass


class TodoUpdate(BaseModel):
    """Схема для обновления существующей задачи"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    completed: Optional[bool] = Field(None)


class Todo(TodoBase):
    """Схема задачи для ответа"""
    id: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
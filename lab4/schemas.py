from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic.types import constr, conint


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Логин пользователя (3-50 символов)"
    )
    email: EmailStr = Field(
        ...,
        description="Email пользователя"
    )
    age: Optional[int] = Field(
        None,
        gt=0,
        lt=130,
        description="Возраст пользователя (1-129 лет)"
    )


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(
        ...,
        min_length=6,
        description="Пароль (минимум 6 символов)"
    )


class UserUpdate(UserBase):
    """Схема для обновления пользователя"""
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Новый логин пользователя"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Новый email пользователя"
    )
    password: Optional[str] = Field(
        None,
        min_length=6,
        description="Новый пароль"
    )


class User(UserBase):
    """Схема пользователя для ответа"""
    id: int = Field(..., description="Уникальный ID пользователя")

    class Config:
        from_attributes = True  # Для работы с ORM моделями
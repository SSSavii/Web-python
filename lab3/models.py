# models.py
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, constr, conint

class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., description="Логин пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    age: Optional[conint(gt=0, lt=130)] = Field(None, description="Возраст (1–129)")

class UserCreate(UserBase):
    password: constr(min_length=6) = Field(..., description="Пароль (минимум 6 символов)")

class User(UserBase):
    id: int = Field(..., description="Уникальный ID пользователя")
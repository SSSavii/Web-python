# routers/users.py
from fastapi import APIRouter, HTTPException, Path
from typing import List
from models import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])
db: List[User] = []


@router.get("/", response_model=List[User], summary="Список всех пользователей")
def list_users():
    return db


@router.get("/{user_id}", response_model=User, summary="Получить пользователя по ID")
def get_user(user_id: int = Path(..., gt=0, description="ID пользователя (>0)")):
    for u in db:
        if u.id == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/", response_model=User, status_code=201, summary="Создать нового пользователя")
def create_user(user_in: UserCreate):
    new_id = len(db) + 1
    user = User(id=new_id, **user_in.dict(exclude={"password"}))
    db.append(user)
    return user


@router.put("/{user_id}", response_model=User, summary="Обновить пользователя")
def update_user(
        user_id: int = Path(..., gt=0, description="ID пользователя (>0)"),
        user_in: UserCreate = ...
):
    for idx, u in enumerate(db):
        if u.id == user_id:
            updated = User(id=user_id, **user_in.dict(exclude={"password"}))
            db[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=204, summary="Удалить пользователя")
def delete_user(user_id: int = Path(..., gt=0, description="ID пользователя (>0)")):
    for idx, u in enumerate(db):
        if u.id == user_id:
            db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="User not found")

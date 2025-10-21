from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import hashlib

from database import get_db
from models import User as UserModel
from schemas import User, UserCreate, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Пользователь не найден"}}
)


def hash_password(password: str) -> str:
    """Простое хеширование пароля """
    return hashlib.sha256(password.encode()).hexdigest()


@router.get(
    "/",
    response_model=List[User],
    summary="Получить список всех пользователей",
    description="Возвращает список всех пользователей из базы данных"
)
def list_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Получить список всех пользователей с пагинацией"""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get(
    "/{user_id}",
    response_model=User,
    summary="Получить пользователя по ID",
    description="Возвращает данные конкретного пользователя по его ID"
)
def get_user(
        user_id: int = Path(..., gt=0, description="ID пользователя (должен быть > 0)"),
        db: Session = Depends(get_db)
):
    """Получить конкретного пользователя по ID"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    return user


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового пользователя",
    description="Создает нового пользователя в базе данных"
)
def create_user(
        user_in: UserCreate,
        db: Session = Depends(get_db)
):
    """Создать нового пользователя"""
    # Хешируем пароль
    hashed_password = hash_password(user_in.password)

    # Создаем объект пользователя
    db_user = UserModel(
        username=user_in.username,
        email=user_in.email,
        age=user_in.age,
        hashed_password=hashed_password
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username или email уже существует"
        )


@router.put(
    "/{user_id}",
    response_model=User,
    summary="Обновить данные пользователя",
    description="Обновляет данные существующего пользователя"
)
def update_user(
        user_id: int = Path(..., gt=0, description="ID пользователя (должен быть > 0)"),
        user_in: UserUpdate = ...,
        db: Session = Depends(get_db)
):
    """Обновить данные пользователя"""
    # Находим пользователя
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    # Обновляем поля, если они переданы
    update_data = user_in.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username или email уже существует"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    description="Удаляет пользователя из базы данных"
)
def delete_user(
        user_id: int = Path(..., gt=0, description="ID пользователя (должен быть > 0)"),
        db: Session = Depends(get_db)
):
    """Удалить пользователя по ID"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    db.delete(user)
    db.commit()
    return None


@router.get(
    "/search/by-username/{username}",
    response_model=User,
    summary="Найти пользователя по username",
    description="Поиск пользователя по точному совпадению username"
)
def search_by_username(
        username: str = Path(..., min_length=3, max_length=50),
        db: Session = Depends(get_db)
):
    """Поиск пользователя по username"""
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с username '{username}' не найден"
        )
    return user
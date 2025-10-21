from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Todo as TodoModel
from schemas import Todo, TodoCreate, TodoUpdate

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


@router.post(
    "/",
    response_model=Todo,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую задачу"
)
def create_todo(
        todo_in: TodoCreate,
        db: Session = Depends(get_db)
):
    """
    Создать новую задачу (Todo элемент).
    """
    # Создаем новую задачу с completed=False по умолчанию
    db_todo = TodoModel(
        title=todo_in.title,
        description=todo_in.description,
        completed=False  # По умолчанию задача не выполнена
    )

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo


@router.get(
    "/{todo_id}",
    response_model=Todo,
    summary="Получить задачу по ID"
)
def get_todo(
        todo_id: int = Path(..., gt=0, description="ID задачи"),
        db: Session = Depends(get_db)
):
    """
    Получить задачу по её ID.
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {todo_id} не найдена"
        )

    return todo


@router.put(
    "/{todo_id}",
    response_model=Todo,
    summary="Обновить существующую задачу"
)
def update_todo(
        todo_id: int = Path(..., gt=0, description="ID задачи"),
        todo_update: TodoUpdate = ...,
        db: Session = Depends(get_db)
):
    """
    Обновить существующую задачу.
    """
    # Находим задачу
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {todo_id} не найдена"
        )

    # Обновляем только переданные поля
    update_data = todo_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(todo, field, value)

    # Обновляем время изменения
    todo.updated_at = datetime.now()

    db.commit()
    db.refresh(todo)

    return todo


@router.delete(
    "/{todo_id}",
    summary="Удалить задачу"
)
def delete_todo(
        todo_id: int = Path(..., gt=0, description="ID задачи"),
        db: Session = Depends(get_db)
):
    """
    Удалить задачу по её ID.
    """
    # Находим задачу
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {todo_id} не найдена"
        )

    # Удаляем задачу
    db.delete(todo)
    db.commit()

    return {"message": "Задача успешно удалена"}
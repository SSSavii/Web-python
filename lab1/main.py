from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# экземпляр приложения
app = FastAPI()

# модель данных Pydantic
class Comments(BaseModel):
    username: str
    text: str

#список в памяти

comments_db = []

# маршрут для публикации нового комментария
@app.post("/comments")
def create_comment(comment: Comments):
    """
    Принимает новый комментарий и добавляет его в нашу "базу данных".
    """
    comments_db.append(comment.model_dump())
    return {"message": "Comment added successfully"}

#маршрут для получения всех комментариев
@app.get("/comments", response_model=List[Comments])
def get_comments():
    """
    Возвращает список всех ранее добавленных комментариев.
    """
    return comments_db
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from typing import List, Optional

app = FastAPI(title="Lab 6: Work with API", description="Interaction with Google Books and Chuck Norris Jokes API")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка Jinja2 для работы с HTML-шаблонами
templates = Jinja2Templates(directory="templates")


# ========== ЗАДАНИЕ 1: Google Books API ==========

class BookItem(BaseModel):
    """Модель для представления информации о книге."""
    title: str
    authors: List[str]
    published_date: Optional[str] = None
    description: Optional[str] = None
    page_count: Optional[int] = None
    categories: Optional[List[str]] = None


@app.get("/books/search", response_class=HTMLResponse)
async def search_books(request: Request, q: str = "Python programming"):
    """
    Поиск книг через Google Books API.
    По умолчанию ищет книги по запросу 'Python programming'.
    """
    api_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": q,
        "maxResults": 5,  # Получаем 5 результатов
        "printType": "books"
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()

        books = []
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            book = BookItem(
                title=volume_info.get("title", "No title"),
                authors=volume_info.get("authors", ["Unknown author"]),
                published_date=volume_info.get("publishedDate", ""),
                description=volume_info.get("description", "No description"),
                page_count=volume_info.get("pageCount"),
                categories=volume_info.get("categories", [])
            )
            books.append(book)

        # Возвращаем HTML-страницу с результатами
        return templates.TemplateResponse("index.html", {
            "request": request,
            "books": books,
            "query": q,
            "show_books": True
        })

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from Google Books API: {str(e)}")


# ========== ЗАДАНИЕ 2: Chuck Norris Jokes API ==========

class JokeResponse(BaseModel):
    """Модель для ответа с шуткой."""
    joke: str
    category: Optional[str] = None
    id: Optional[str] = None  # Исправлено: ID в API это строка, не число!


@app.get("/jokes/random", response_class=HTMLResponse)
async def get_random_joke(request: Request, category: str = None):
    """
    Получение случайной шутки о Чаке Норрисе.
    Можно указать категорию для фильтрации.
    """
    api_url = "https://api.chucknorris.io/jokes/random"

    try:
        if category:
            # Если указана категория, получаем шутку из конкретной категории
            categories_url = "https://api.chucknorris.io/jokes/categories"
            categories_response = requests.get(categories_url)
            categories_response.raise_for_status()
            available_categories = categories_response.json()

            if category not in available_categories:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category. Available categories: {', '.join(available_categories)}"
                )

            api_url = f"https://api.chucknorris.io/jokes/random?category={category}"

        response = requests.get(api_url)
        response.raise_for_status()
        joke_data = response.json()

        joke = JokeResponse(
            joke=joke_data.get("value", "No joke found"),
            category=category or (
                joke_data.get("categories", ["uncategorized"])[0] if joke_data.get("categories") else "uncategorized"),
            id=joke_data.get("id")
        )

        # Получаем список категорий для формы
        categories_response = requests.get("https://api.chucknorris.io/jokes/categories")
        categories = categories_response.json() if categories_response.status_code == 200 else []

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "joke": joke,
                "selected_category": category,
                "categories": categories,
                "show_joke": True
            }
        )

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching joke from API: {str(e)}")


@app.get("/jokes/categories")
async def get_joke_categories():
    """
    Получение списка всех доступных категорий шуток.
    """
    try:
        response = requests.get("https://api.chucknorris.io/jokes/categories")
        response.raise_for_status()
        categories = response.json()

        return {
            "categories": categories,
            "total_categories": len(categories)
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories from API: {str(e)}")


@app.get("/jokes/random/json")
async def get_random_joke_json(category: str = None):
    """
    Получение случайной шутки в формате JSON.
    """
    try:
        api_url = "https://api.chucknorris.io/jokes/random"

        if category:
            api_url = f"https://api.chucknorris.io/jokes/random?category={category}"

        response = requests.get(api_url)
        response.raise_for_status()
        joke_data = response.json()

        return {
            "id": joke_data.get("id"),
            "joke": joke_data.get("value"),
            "categories": joke_data.get("categories", []),
            "url": joke_data.get("url"),
            "icon_url": joke_data.get("icon_url"),
            "created_at": joke_data.get("created_at"),
            "updated_at": joke_data.get("updated_at")
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching joke from API: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница с ссылками на оба задания."""
    # Получаем список категорий для отображения на главной странице
    try:
        categories_response = requests.get("https://api.chucknorris.io/jokes/categories")
        categories = categories_response.json() if categories_response.status_code == 200 else []
    except:
        categories = []

    return templates.TemplateResponse("index.html", {
        "request": request,
        "categories": categories
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
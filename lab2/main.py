from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel

app = FastAPI(title="Product API", version="1.0")

# ---------------------------------------------------------
# 1) Pydantic-модель товара
# ---------------------------------------------------------
class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

# ---------------------------------------------------------
# 2) "База" из нескольких товаров для примера
# ---------------------------------------------------------
products_db = [
    Product(product_id=1, name="iPhone",         category="Electronics", price=792349.0),
    Product(product_id=2, name="MacBook Pro",       category="Electronics", price=193399.0),
    Product(product_id=3, name="Стакан", category="Home",        price=1234.5),
    Product(product_id=4, name="Термокружка",        category="Home",        price=25.0),
    Product(product_id=5, name="Футболка", category="Clothing",   price=1125.0),
    Product(product_id=6, name="Беспроводные наушники", category="Electronics", price=123210.0),
]

# ---------------------------------------------------------
# 3) Конечная точка: GET /product/{product_id}
#    Возвращает один товар по его ID
# ---------------------------------------------------------
@app.get("/product/{product_id}", response_model=Product)
def get_product(
    product_id: int = Path(..., title="ID товара", ge=1)
):
    for prod in products_db:
        if prod.product_id == product_id:
            return prod
    raise HTTPException(status_code=404, detail=f"Товар с product_id={product_id} не найден")

# ---------------------------------------------------------
# 4) Конечная точка: GET /products/search
#    Поиск по ключевому слову в названии с опциональной фильтрацией по категории
#    и ограничением числа возвращаемых результатов
# ---------------------------------------------------------
@app.get("/products/search", response_model=List[Product])
def search_products(
    keyword: str = Query(..., min_length=1, title="Ключевое слово для поиска"),
    category: Optional[str] = Query(None, title="Категория"),
    limit: int = Query(10, ge=1, le=100, title="Максимальное количество результатов")
):
    keyword_lower = keyword.lower()
    # Фильтрация
    filtered = [
        prod for prod in products_db
        if keyword_lower in prod.name.lower()
           and (category is None or prod.category.lower() == category.lower())
    ]
    # Ограничение по количеству
    return filtered[:limit]

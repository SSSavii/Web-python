from fastapi import FastAPI
from fastapi.responses import FileResponse

# экземпляр приложения
app = FastAPI()

# Создание endpoint для GET-запроса к корневому URL
@app.get("/")
def read_root():
    return FileResponse("lab1.html")
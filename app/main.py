from fastapi import FastAPI
from . import models, database
from .routers import notes

app = FastAPI()

# Tworzenie tabel w bazie danych
models.Base.metadata.create_all(bind=database.engine)

# Podstawowe endpointy
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# Dołączenie routera notatek
app.include_router(notes.router, prefix="/notes", tags=["notes"])
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Konfiguracja bazy danych
DEFAULT_DB_URL = "postgresql://user:password@localhost:5432/dbname"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Model SQLAlchemy
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)


# Model Pydantic
class NoteCreate(BaseModel):
    title: str
    content: str


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# Endpointy CRUD dla notatek
@app.post("/notes/", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    db = SessionLocal()
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    db.close()
    return db_note


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int):
    db = SessionLocal()
    note = db.query(Note).filter(Note.id == note_id).first()
    db.close()
    if note is None:
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")
    return note


@app.get("/notes/", response_model=list[NoteResponse])
async def read_notes():
    db = SessionLocal()
    notes = db.query(Note).all()
    db.close()
    return notes


@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: NoteCreate):
    db = SessionLocal()
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        db.close()
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")

    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    db.close()
    return db_note


@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    db = SessionLocal()
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        db.close()
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")

    db.delete(db_note)
    db.commit()
    db.close()
    return {"message": "Notatka została usunięta"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter()

@router.post("/", response_model=schemas.NoteResponse)
async def create_note(note: schemas.NoteCreate, db: Session = Depends(database.get_db)):
    db_note = models.Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/{note_id}", response_model=schemas.NoteResponse)
async def read_note(note_id: int, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")
    return note

@router.get("/", response_model=List[schemas.NoteResponse])
async def read_notes(db: Session = Depends(database.get_db)):
    notes = db.query(models.Note).all()
    return notes

@router.put("/{note_id}", response_model=schemas.NoteResponse)
async def update_note(note_id: int, note: schemas.NoteCreate, db: Session = Depends(database.get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")

    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note

@router.delete("/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(database.get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")

    db.delete(db_note)
    db.commit()
    return {"message": "Notatka została usunięta"} 
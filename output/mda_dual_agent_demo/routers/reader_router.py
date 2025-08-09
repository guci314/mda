from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import reader_service
from schemas.reader import ReaderCreate, ReaderResponse
from database import get_db

router = APIRouter()

@router.post("/readers/", response_model=ReaderResponse)
def register_reader(reader: ReaderCreate, db: Session = Depends(get_db)):
    return reader_service.register_reader(db=db, reader=reader)

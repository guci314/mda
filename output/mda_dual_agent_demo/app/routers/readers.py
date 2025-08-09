from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.schemas import ReaderCreate, ReaderResponse
from ..services.reader_service import ReaderService
from ..database import get_db

router = APIRouter(prefix="/readers", tags=["readers"])

@router.post("/", response_model=ReaderResponse)
def register_reader(reader_data: ReaderCreate, db: Session = Depends(get_db)):
    service = ReaderService(db)
    return service.register_reader(reader_data)

@router.get("/{reader_id}", response_model=ReaderResponse)
def get_reader(reader_id: str, db: Session = Depends(get_db)):
    service = ReaderService(db)
    reader = service.get_reader(reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader
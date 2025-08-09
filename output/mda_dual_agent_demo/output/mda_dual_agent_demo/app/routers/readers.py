from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..schemas.schemas import ReaderCreate, ReaderResponse
from ..services.reader_service import ReaderService
from ..dependencies import get_reader_service

router = APIRouter(prefix="/readers", tags=["readers"])

@router.post("/", response_model=ReaderResponse)
def register_reader(reader_data: ReaderCreate, service: ReaderService = Depends(get_reader_service)):
    return service.register_reader(reader_data)

@router.get("/{reader_id}", response_model=ReaderResponse)
def get_reader(reader_id: str, service: ReaderService = Depends(get_reader_service)):
    reader = service.get_reader(reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader
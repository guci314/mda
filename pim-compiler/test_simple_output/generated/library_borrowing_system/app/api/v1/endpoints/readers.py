from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.session import get_db
from app.services.reader_service import reader_service
from app.crud import reader as crud_reader

router = APIRouter()

@router.post("/", response_model=schemas.Reader, status_code=status.HTTP_201_CREATED)
def create_reader(
    *,
    db: Session = Depends(get_db),
    reader_in: schemas.ReaderCreate,
):
    """
    Register a new reader.
    """
    return reader_service.create_reader(db=db, reader_in=reader_in)

@router.get("/", response_model=List[schemas.Reader])
def get_all_readers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all readers.
    """
    return crud_reader.reader.get_multi(db, skip=skip, limit=limit)


@router.get("/{reader_id}", response_model=schemas.Reader)
def get_reader(
    *,
    db: Session = Depends(get_db),
    reader_id: str,
):
    """
    Get a reader by their ID.
    """
    return reader_service.get_reader_by_id(db=db, reader_id=reader_id)

@router.put("/{reader_id}", response_model=schemas.Reader)
def update_reader(
    *,
    db: Session = Depends(get_db),
    reader_id: str,
    reader_in: schemas.ReaderUpdate,
):
    """
    Update reader information.
    """
    return reader_service.update_reader(db=db, reader_id=reader_id, reader_in=reader_in)

@router.post("/{reader_id}/freeze", response_model=schemas.Reader)
def freeze_reader(
    *,
    db: Session = Depends(get_db),
    reader_id: str,
):
    """
    Freeze a reader's account.
    """
    return reader_service.freeze_reader(db=db, reader_id=reader_id)

@router.post("/{reader_id}/unfreeze", response_model=schemas.Reader)
def unfreeze_reader(
    *,
    db: Session = Depends(get_db),
    reader_id: str,
):
    """
    Unfreeze a reader's account.
    """
    return reader_service.unfreeze_reader(db=db, reader_id=reader_id)

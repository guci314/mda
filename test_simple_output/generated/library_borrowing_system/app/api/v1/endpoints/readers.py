from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, services, dependencies, models

router = APIRouter()

@router.post("/", response_model=schemas.Reader, status_code=status.HTTP_201_CREATED)
def register_reader(
    reader: schemas.ReaderCreate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Register a new reader.
    """
    return services.reader.create_reader(db=db, reader=reader)

@router.get("/{reader_id}", response_model=schemas.Reader)
def get_reader_info(
    reader_id: str,
    db: Session = Depends(dependencies.get_db)
):
    """
    Get a specific reader's information.
    """
    db_reader = services.reader.get_reader(db=db, reader_id=reader_id)
    if not db_reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
    return db_reader

@router.put("/{reader_id}", response_model=schemas.Reader)
def update_reader_info(
    reader_id: str,
    reader_update: schemas.ReaderUpdate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Update a reader's information.
    """
    return services.reader.update_reader(db=db, reader_id=reader_id, reader_update=reader_update)

@router.post("/{reader_id}/freeze", response_model=schemas.Reader)
def freeze_reader(
    reader_id: str,
    db: Session = Depends(dependencies.get_db)
):
    """
    Freeze a reader's account.
    """
    return services.reader.update_reader_status(db=db, reader_id=reader_id, new_status=models.ReaderStatus.FROZEN)

@router.post("/{reader_id}/unfreeze", response_model=schemas.Reader)
def unfreeze_reader(
    reader_id: str,
    db: Session = Depends(dependencies.get_db)
):
    """
    Unfreeze a reader's account.
    """
    return services.reader.update_reader_status(db=db, reader_id=reader_id, new_status=models.ReaderStatus.NORMAL)

@router.get("/{reader_id}/borrow-history", response_model=List[schemas.BorrowRecord])
def get_borrow_history(
    reader_id: str,
    db: Session = Depends(dependencies.get_db)
):
    """
    Get a reader's borrowing history.
    """
    return services.reader.get_borrow_history(db=db, reader_id=reader_id)
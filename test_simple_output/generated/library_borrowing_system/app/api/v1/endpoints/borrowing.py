from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, services, dependencies

router = APIRouter()

@router.post("/borrow", response_model=schemas.BorrowRecord, status_code=status.HTTP_201_CREATED)
def borrow_book(
    borrow_request: schemas.BorrowCreate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Borrow a book.
    """
    return services.borrowing.borrow_book(db=db, borrow_request=borrow_request)

@router.post("/return", response_model=schemas.BorrowRecord)
def return_book(
    return_request: schemas.ReturnCreate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Return a borrowed book.
    """
    return services.borrowing.return_book(db=db, borrow_id=return_request.borrow_id)

@router.post("/renew", response_model=schemas.BorrowRecord)
def renew_book(
    renew_request: schemas.RenewCreate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Renew a borrowed book.
    """
    return services.borrowing.renew_book(db=db, borrow_id=renew_request.borrow_id)

@router.post("/reserve", response_model=schemas.ReservationRecord, status_code=status.HTTP_201_CREATED)
def reserve_book(
    reserve_request: schemas.ReservationCreate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Reserve a book that is currently unavailable.
    """
    return services.reservation.reserve_book(db=db, reservation_request=reserve_request)

@router.get("/overdue", response_model=List[schemas.BorrowRecord])
def get_overdue_records(
    db: Session = Depends(dependencies.get_db)
):
    """
    Get all overdue borrowing records.
    """
    return services.borrowing.get_overdue_records(db=db)

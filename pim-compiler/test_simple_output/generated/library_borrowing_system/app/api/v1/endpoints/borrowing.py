from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.session import get_db
from app.services.borrowing_service import borrowing_service

router = APIRouter()

@router.post("/borrow", response_model=schemas.BorrowRecord, status_code=status.HTTP_201_CREATED)
def borrow_book(
    *,
    db: Session = Depends(get_db),
    borrow_request: schemas.BorrowCreateAction,
):
    """
    Borrow a book.
    """
    return borrowing_service.borrow_book(db=db, borrow_request=borrow_request)

@router.post("/return/{borrow_id}", response_model=schemas.ReturnResponse)
def return_book(
    *,
    db: Session = Depends(get_db),
    borrow_id: str,
):
    """
    Return a borrowed book.
    """
    return borrowing_service.return_book(db=db, borrow_id=borrow_id)

@router.post("/renew/{borrow_id}", response_model=schemas.BorrowRecord)
def renew_book(
    *,
    db: Session = Depends(get_db),
    borrow_id: str,
):
    """
    Renew a borrowed book.
    """
    return borrowing_service.renew_book(db=db, borrow_id=borrow_id)

@router.post("/reserve", response_model=schemas.ReservationRecord, status_code=status.HTTP_201_CREATED)
def reserve_book(
    *,
    db: Session = Depends(get_db),
    reservation_request: schemas.ReservationCreateAction,
):
    """
    Reserve a book that is currently unavailable.
    """
    return borrowing_service.reserve_book(db=db, reservation_request=reservation_request)

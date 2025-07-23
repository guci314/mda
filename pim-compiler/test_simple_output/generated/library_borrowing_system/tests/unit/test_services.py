import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.services.reader_service import reader_service
from app.services.book_service import book_service
from app.services.borrowing_service import borrowing_service
from app.schemas import ReaderCreate, BookCreate, BorrowCreateAction
from app.models.reader import ReaderType

def test_create_reader(db: Session):
    reader_in = ReaderCreate(
        reader_id="testuser001",
        name="Test User",
        id_card_number="123456789012345678",
        phone_number="1234567890",
        email="test@example.com",
        reader_type=ReaderType.STUDENT,
        valid_until=date.today() + timedelta(days=365)
    )
    reader = reader_service.create_reader(db, reader_in=reader_in)
    assert reader.reader_id == "testuser001"
    assert reader.email == "test@example.com"

def test_create_existing_reader_fails(db: Session):
    reader_in = ReaderCreate(
        reader_id="testuser002",
        name="Test User 2",
        id_card_number="223456789012345678",
        phone_number="2234567890",
        email="test2@example.com",
        reader_type=ReaderType.STUDENT,
        valid_until=date.today() + timedelta(days=365)
    )
    reader_service.create_reader(db, reader_in=reader_in)
    
    with pytest.raises(HTTPException) as excinfo:
        reader_service.create_reader(db, reader_in=reader_in)
    assert excinfo.value.status_code == 400

def test_borrow_book_not_found(db: Session):
    borrow_req = BorrowCreateAction(reader_id="nouser", isbn="nobook")
    with pytest.raises(HTTPException) as excinfo:
        borrowing_service.borrow_book(db, borrow_request=borrow_req)
    assert excinfo.value.status_code == 404
    assert "Reader not found" in excinfo.value.detail

def test_borrow_book_no_stock(db: Session):
    # Create reader
    reader_in = ReaderCreate(
        reader_id="testuser003", name="Test User 3", id_card_number="323456789012345678",
        phone_number="3234567890", email="test3@example.com", reader_type=ReaderType.STUDENT,
        valid_until=date.today() + timedelta(days=365)
    )
    reader = reader_service.create_reader(db, reader_in=reader_in)

    # Create book with no stock
    book_in = BookCreate(
        isbn="978-0262033848", title="Intro to Algorithms", author="CLRS",
        publisher="MIT Press", publish_year=2009, category="Algorithms",
        total_stock=1, available_stock=0, location="B-2-3"
    )
    book = book_service.create_book(db, book_in=book_in)

    borrow_req = BorrowCreateAction(reader_id=reader.reader_id, isbn=book.isbn)
    with pytest.raises(HTTPException) as excinfo:
        borrowing_service.borrow_book(db, borrow_request=borrow_req)
    assert excinfo.value.status_code == 400
    assert "No available stock" in excinfo.value.detail

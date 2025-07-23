from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy's metadata
# This is crucial for Alembic migrations.
from app.models.book import Book
from app.models.reader import Reader
from app.models.borrow_record import BorrowRecord
from app.models.reservation_record import ReservationRecord

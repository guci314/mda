from .book_router import router as books
from .reader_router import router as readers
from .borrowing_router import router as borrows
from .reservation_router import router as reservations

__all__ = ["books", "readers", "borrows", "reservations"]
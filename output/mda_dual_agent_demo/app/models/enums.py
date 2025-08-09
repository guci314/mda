from enum import Enum


class BookStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    REMOVED = "removed"


class ReaderType(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    STAFF = "staff"
    OTHER = "other"


class ReaderStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"


class BorrowStatus(str, Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
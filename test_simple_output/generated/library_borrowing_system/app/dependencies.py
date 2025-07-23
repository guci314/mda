from typing import Generator
from app.db.session import SessionLocal

def get_db() -> Generator:
    """
    Dependency to get a database session.
    Ensures the session is closed after the request is finished.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

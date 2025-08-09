from sqlalchemy.orm import Session
from typing import Optional
from ..models.domain import ReaderDB
from ..schemas.schemas import ReaderCreate, ReaderResponse
from ..repositories.reader_repository import ReaderRepository

class ReaderService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReaderRepository(db)

    def register_reader(self, reader_data: ReaderCreate) -> ReaderResponse:
        reader = ReaderDB(**reader_data.dict())
        self.repository.save(reader)
        return ReaderResponse.model_validate(reader)

    def get_reader(self, reader_id: str) -> Optional[ReaderResponse]:
        reader = self.repository.get_by_id(reader_id)
        if reader is None:
            return None
        return ReaderResponse.model_validate(reader)
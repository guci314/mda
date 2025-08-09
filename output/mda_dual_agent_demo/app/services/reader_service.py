from sqlalchemy.orm import Session
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta
from ..models.domain import ReaderDB
from ..models.enums import ReaderType, ReaderStatus
from ..schemas.schemas import ReaderCreate, ReaderResponse
from ..repositories.reader_repository import ReaderRepository

class ReaderService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReaderRepository(db)

    def register_reader(self, reader_data: ReaderCreate) -> ReaderResponse:
        reader = ReaderDB(**reader_data.model_dump(), reader_id=str(uuid4()), register_date=datetime.now(), valid_until=datetime.now() + timedelta(days=365), status=ReaderStatus.ACTIVE)
        reader = ReaderDB(**reader_data.model_dump(exclude={"reader_type"}), reader_id=str(uuid4()), register_date=datetime.now(), valid_until=datetime.now().date() + timedelta(days=365), status=ReaderStatus.ACTIVE, reader_type=ReaderType.STUDENT, credit_score=100)
        return ReaderResponse.model_validate(reader)

    def get_reader(self, reader_id: str) -> Optional[ReaderResponse]:
        reader = self.repository.get_by_id(reader_id)
        if reader is None:
            return None
        return ReaderResponse.model_validate(reader)
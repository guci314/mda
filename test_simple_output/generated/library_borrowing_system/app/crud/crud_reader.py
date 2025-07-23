from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.reader import Reader
from app.schemas.reader import ReaderCreate, ReaderUpdate

class CRUDReader(CRUDBase[Reader, ReaderCreate, ReaderUpdate]):
    def get_by_reader_id(self, db: Session, *, reader_id: str) -> Optional[Reader]:
        return db.query(Reader).filter(Reader.reader_id == reader_id).first()

    def get_by_id_card(self, db: Session, *, id_card_number: str) -> Optional[Reader]:
        return db.query(Reader).filter(Reader.id_card_number == id_card_number).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Reader]:
        return db.query(Reader).filter(Reader.email == email).first()

reader = CRUDReader(Reader)

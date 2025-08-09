from sqlalchemy.orm import Session
from models.reader import ReaderDB, ReaderStatus, ReaderType
from schemas.reader import ReaderCreate
from datetime import datetime, date, timedelta
import uuid

def register_reader(db: Session, reader: ReaderCreate):
    db_reader = ReaderDB(
        reader_id=str(uuid.uuid4()),
        **reader.model_dump(),
        register_date=datetime.now(),
        valid_until=date.today() + timedelta(days=365),
        status=ReaderStatus.ACTIVE,
        credit_score=100
    )
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader

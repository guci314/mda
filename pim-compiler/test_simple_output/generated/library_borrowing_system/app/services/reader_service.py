from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import crud, models, schemas
from app.models.reader import ReaderStatus

class ReaderService:
    def get_reader_by_id(self, db: Session, reader_id: str) -> models.Reader:
        reader = crud.reader.get_by_reader_id(db, reader_id=reader_id)
        if not reader:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
        return reader

    def create_reader(self, db: Session, reader_in: schemas.ReaderCreate) -> models.Reader:
        if crud.reader.get_by_reader_id(db, reader_id=reader_in.reader_id):
            raise HTTPException(status_code=400, detail="Reader with this ID already exists.")
        if crud.reader.get_by_id_card(db, id_card_number=reader_in.id_card_number):
            raise HTTPException(status_code=400, detail="Reader with this ID card number already exists.")
        if reader_in.email and crud.reader.get_by_email(db, email=reader_in.email):
            raise HTTPException(status_code=400, detail="Reader with this email already exists.")
            
        return crud.reader.create(db, obj_in=reader_in)

    def update_reader(self, db: Session, reader_id: str, reader_in: schemas.ReaderUpdate) -> models.Reader:
        reader = self.get_reader_by_id(db, reader_id)
        if reader_in.email and reader.email != reader_in.email:
            if crud.reader.get_by_email(db, email=reader_in.email):
                raise HTTPException(status_code=400, detail="This email is already registered.")
        
        return crud.reader.update(db, db_obj=reader, obj_in=reader_in)

    def _update_reader_status(self, db: Session, reader_id: str, new_status: ReaderStatus) -> models.Reader:
        reader = self.get_reader_by_id(db, reader_id)
        if reader.status == new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reader is already in '{new_status.value}' status"
            )
        update_data = schemas.ReaderUpdate(status=new_status)
        return crud.reader.update(db, db_obj=reader, obj_in=update_data)

    def freeze_reader(self, db: Session, reader_id: str) -> models.Reader:
        return self._update_reader_status(db, reader_id, ReaderStatus.FROZEN)

    def unfreeze_reader(self, db: Session, reader_id: str) -> models.Reader:
        return self._update_reader_status(db, reader_id, ReaderStatus.NORMAL)

reader_service = ReaderService()

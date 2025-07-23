from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app import crud, schemas, models

class ReaderService:
    def create_reader(self, db: Session, *, reader: schemas.ReaderCreate) -> models.Reader:
        """
        Creates a new reader.
        """
        if crud.reader.get_by_reader_id(db, reader_id=reader.reader_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reader ID already exists")
        if crud.reader.get_by_id_card(db, id_card_number=reader.id_card_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID card number already registered")
        if reader.email and crud.reader.get_by_email(db, email=reader.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
            
        return crud.reader.create(db, obj_in=reader)

    def get_reader(self, db: Session, *, reader_id: str) -> Optional[models.Reader]:
        """
        Retrieves a reader by their ID.
        """
        return crud.reader.get_by_reader_id(db, reader_id=reader_id)

    def update_reader(self, db: Session, *, reader_id: str, reader_update: schemas.ReaderUpdate) -> models.Reader:
        """
        Updates a reader's information.
        """
        db_reader = self.get_reader(db, reader_id=reader_id)
        if not db_reader:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
        
        return crud.reader.update(db, db_obj=db_reader, obj_in=reader_update)

    def update_reader_status(self, db: Session, *, reader_id: str, new_status: models.ReaderStatus) -> models.Reader:
        """
        Updates a reader's status (e.g., to FROZEN or NORMAL).
        """
        db_reader = self.get_reader(db, reader_id=reader_id)
        if not db_reader:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
        
        update_data = schemas.ReaderUpdate(status=new_status)
        return crud.reader.update(db, db_obj=db_reader, obj_in=update_data)

    def get_borrow_history(self, db: Session, *, reader_id: str) -> List[models.BorrowRecord]:
        """
        Retrieves the borrowing history for a specific reader.
        """
        if not self.get_reader(db, reader_id=reader_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
        
        return crud.borrow_record.get_all_by_reader_id(db, reader_id=reader_id)

reader = ReaderService()

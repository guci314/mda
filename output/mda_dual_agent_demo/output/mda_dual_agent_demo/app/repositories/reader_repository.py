from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.reader import Reader


class ReaderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reader_id: str) -> Optional[Reader]:
        """根据ID获取读者"""
        return self.db.query(Reader).filter(Reader.reader_id == reader_id).first()

    def get_by_id_card(self, id_card: str) -> Optional[Reader]:
        """根据身份证号获取读者"""
        return self.db.query(Reader).filter(Reader.id_card == id_card).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Reader]:
        """获取所有读者"""
        return self.db.query(Reader).offset(skip).limit(limit).all()

    def save(self, reader: Reader) -> Reader:
        """保存读者"""
        self.db.add(reader)
        self.db.commit()
        self.db.refresh(reader)
        return reader

    def update(self, reader: Reader) -> Reader:
        """更新读者"""
        self.db.commit()
        self.db.refresh(reader)
        return reader

    def delete(self, reader: Reader) -> None:
        """删除读者"""
        self.db.delete(reader)
        self.db.commit()
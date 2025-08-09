from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.domain import ReaderDB as Reader
from app.models.enums import ReaderStatus


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

    def get_active_readers(self, skip: int = 0, limit: int = 100) -> List[Reader]:
        """获取活动状态的读者"""
        return self.db.query(Reader).filter(Reader.status == ReaderStatus.ACTIVE).offset(skip).limit(limit).all()

    def save(self, reader: Reader) -> Reader:
        """保存读者"""
        self.db.add(reader)
        self.db.commit()
        self.db.refresh(reader)
        return reader

    def update(self, reader_id: str, **kwargs) -> Optional[Reader]:
        """更新读者信息"""
        reader = self.get_by_id(reader_id)
        if reader:
            for key, value in kwargs.items():
                setattr(reader, key, value)
            self.db.commit()
            self.db.refresh(reader)
        return reader

    def delete(self, reader_id: str) -> bool:
        """删除读者"""
        reader = self.get_by_id(reader_id)
        if reader:
            self.db.delete(reader)
            self.db.commit()
            return True
        return False
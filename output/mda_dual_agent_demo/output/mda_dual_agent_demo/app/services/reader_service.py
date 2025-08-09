"""
读者服务层
"""
import uuid
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import ReaderDB
from ..models.pydantic import ReaderCreate, ReaderUpdate, ReaderResponse
from ..models.enums import ReaderStatus, ReaderType
from ..repositories.reader_repository import ReaderRepository


class ReaderService:
    """读者服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReaderRepository(db)
    
    def _generate_reader_id(self) -> str:
        """生成读者ID"""
        return f"R{uuid.uuid4().hex[:8].upper()}"
    
    def _calculate_valid_until(self, reader_type: ReaderType) -> date:
        """计算有效期"""
        today = date.today()
        if reader_type == ReaderType.STUDENT:
            # 学生有效期1年
            return today + timedelta(days=365)
        elif reader_type == ReaderType.TEACHER:
            # 教师有效期3年
            return today + timedelta(days=365 * 3)
        else:
            # 社会人员有效期6个月
            return today + timedelta(days=180)
    
    async def register_reader(self, reader_data: ReaderCreate) -> ReaderResponse:
        """注册读者"""
        # 检查身份证号是否已存在
        if await self.repository.id_card_exists(reader_data.id_card):
            raise ValueError(f"身份证号 {reader_data.id_card} 已被注册")
        
        # 检查手机号是否已存在
        existing_reader = await self.repository.get_by_phone(reader_data.phone)
        if existing_reader and existing_reader.status != ReaderStatus.DELETED:
            raise ValueError(f"手机号 {reader_data.phone} 已被注册")
        
        # 生成读者ID和有效期
        reader_id = self._generate_reader_id()
        valid_until = self._calculate_valid_until(reader_data.reader_type)
        
        # 创建数据库模型
        reader_db = ReaderDB(
            reader_id=reader_id,
            name=reader_data.name,
            id_card=reader_data.id_card,
            phone=reader_data.phone,
            email=reader_data.email,
            reader_type=reader_data.reader_type,
            register_date=datetime.now(),
            valid_until=valid_until,
            status=ReaderStatus.ACTIVE,
            credit_score=100
        )
        
        # 保存到数据库
        created_reader = await self.repository.create(reader_db)
        
        # 转换为响应模型
        return ReaderResponse.model_validate(created_reader)
    
    async def get_reader(self, reader_id: str) -> Optional[ReaderResponse]:
        """获取读者信息"""
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            return None
        
        return ReaderResponse.model_validate(reader)
    
    async def get_readers(self, skip: int = 0, limit: int = 100) -> List[ReaderResponse]:
        """获取读者列表"""
        readers = await self.repository.get_all(skip=skip, limit=limit)
        return [ReaderResponse.model_validate(reader) for reader in readers]
    
    async def get_readers_by_type(self, reader_type: ReaderType, skip: int = 0, limit: int = 100) -> List[ReaderResponse]:
        """根据类型获取读者"""
        readers = await self.repository.get_by_type(reader_type, skip=skip, limit=limit)
        return [ReaderResponse.model_validate(reader) for reader in readers]
    
    async def get_readers_by_status(self, status: ReaderStatus, skip: int = 0, limit: int = 100) -> List[ReaderResponse]:
        """根据状态获取读者"""
        readers = await self.repository.get_by_status(status, skip=skip, limit=limit)
        return [ReaderResponse.model_validate(reader) for reader in readers]
    
    async def search_readers_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[ReaderResponse]:
        """根据姓名搜索读者"""
        readers = await self.repository.search_by_name(name, skip=skip, limit=limit)
        return [ReaderResponse.model_validate(reader) for reader in readers]
    
    async def update_reader(self, reader_id: str, reader_data: ReaderUpdate) -> Optional[ReaderResponse]:
        """更新读者信息"""
        # 检查读者是否存在
        existing_reader = await self.repository.get_by_id(reader_id)
        if not existing_reader:
            raise ValueError(f"读者ID {reader_id} 不存在")
        
        # 检查身份证号是否被其他读者使用
        if reader_data.id_card != existing_reader.id_card:
            if await self.repository.id_card_exists(reader_data.id_card):
                raise ValueError(f"身份证号 {reader_data.id_card} 已被其他读者使用")
        
        # 检查手机号是否被其他读者使用
        if reader_data.phone != existing_reader.phone:
            other_reader = await self.repository.get_by_phone(reader_data.phone)
            if other_reader and other_reader.reader_id != reader_id and other_reader.status != ReaderStatus.DELETED:
                raise ValueError(f"手机号 {reader_data.phone} 已被其他读者使用")
        
        # 如果读者类型发生变化，重新计算有效期
        valid_until = existing_reader.valid_until
        if reader_data.reader_type != existing_reader.reader_type:
            valid_until = self._calculate_valid_until(reader_data.reader_type)
        
        # 更新读者信息
        updated_reader = await self.repository.update(
            reader_id,
            name=reader_data.name,
            id_card=reader_data.id_card,
            phone=reader_data.phone,
            email=reader_data.email,
            reader_type=reader_data.reader_type,
            valid_until=valid_until
        )
        
        if not updated_reader:
            return None
        
        return ReaderResponse.model_validate(updated_reader)
    
    async def freeze_reader(self, reader_id: str) -> bool:
        """冻结读者"""
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            raise ValueError(f"读者ID {reader_id} 不存在")
        
        if reader.status == ReaderStatus.DELETED:
            raise ValueError("已注销的读者无法冻结")
        
        return await self.repository.freeze(reader_id)
    
    async def unfreeze_reader(self, reader_id: str) -> bool:
        """解冻读者"""
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            raise ValueError(f"读者ID {reader_id} 不存在")
        
        if reader.status == ReaderStatus.DELETED:
            raise ValueError("已注销的读者无法解冻")
        
        return await self.repository.unfreeze(reader_id)
    
    async def delete_reader(self, reader_id: str) -> bool:
        """注销读者"""
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            raise ValueError(f"读者ID {reader_id} 不存在")
        
        # 检查是否有未归还的图书
        # 这里应该调用借阅服务检查，为简化直接处理
        
        return await self.repository.delete(reader_id)
    
    async def update_credit_score(self, reader_id: str, score_change: int) -> bool:
        """更新信用分"""
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            raise ValueError(f"读者ID {reader_id} 不存在")
        
        return await self.repository.update_credit_score(reader_id, score_change)
    
    async def is_reader_active(self, reader_id: str) -> bool:
        """检查读者是否处于活跃状态"""
        return await self.repository.is_active(reader_id)
    
    async def is_reader_valid(self, reader_id: str) -> bool:
        """检查读者是否有效（未过期且状态正常）"""
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            return False
        
        # 检查状态
        if reader.status != ReaderStatus.ACTIVE:
            return False
        
        # 检查是否过期
        if reader.valid_until < date.today():
            return False
        
        return True
    
    async def can_borrow(self, reader_id: str) -> tuple[bool, str]:
        """检查读者是否可以借阅"""
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            return False, "读者不存在"
        
        if reader.status == ReaderStatus.DELETED:
            return False, "读者已注销"
        
        if reader.status == ReaderStatus.FROZEN:
            return False, "读者已被冻结"
        
        if reader.valid_until < date.today():
            return False, "读者证已过期"
        
        if reader.credit_score < 60:
            return False, "信用分过低，无法借阅"
        
        return True, "可以借阅"
    
    async def get_reader_count(self) -> int:
        """获取读者总数"""
        return await self.repository.count_total()
    
    async def reader_exists(self, reader_id: str) -> bool:
        """检查读者是否存在"""
        return await self.repository.exists(reader_id)
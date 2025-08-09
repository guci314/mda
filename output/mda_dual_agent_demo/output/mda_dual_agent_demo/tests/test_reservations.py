"""
预约API测试
"""
import pytest
from httpx import AsyncClient


class TestReservationsAPI:
    """预约API测试类"""
    
    @pytest.fixture
    async def borrowed_book_setup(self, client: AsyncClient, created_book, created_reader):
        """设置已借阅的图书（用于测试预约）"""
        # 先将图书的可借数量设为0（模拟已全部借出）
        isbn = created_book["isbn"]
        update_data = {
            "title": created_book["title"],
            "author": created_book["author"],
            "publisher": created_book["publisher"],
            "publish_year": created_book["publish_year"],
            "category": created_book["category"],
            "total_quantity": created_book["total_quantity"],
            "available_quantity": 0,  # 设为0
            "location": created_book["location"],
            "description": created_book["description"]
        }
        await client.put(f"/books/{isbn}", json=update_data)
        return created_book
    
    @pytest.mark.asyncio
    async def test_reserve_book(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试预约图书"""
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        
        response = await client.post("/reservations/", json=reservation_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["reader_id"] == created_reader["reader_id"]
        assert data["isbn"] == borrowed_book_setup["isbn"]
        assert data["status"] == "等待中"
        assert "reservation_id" in data
        assert "reserve_date" in data
    
    @pytest.mark.asyncio
    async def test_reserve_book_simple(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试预约图书（简化接口）"""
        reader_id = created_reader["reader_id"]
        isbn = borrowed_book_setup["isbn"]
        
        response = await client.post(f"/reservations/simple?reader_id={reader_id}&isbn={isbn}")
        assert response.status_code == 201
        
        data = response.json()
        assert data["reader_id"] == reader_id
        assert data["isbn"] == isbn
        assert data["status"] == "等待中"
    
    @pytest.mark.asyncio
    async def test_reserve_available_book(self, client: AsyncClient, created_book, created_reader):
        """测试预约可借阅的图书（应该失败）"""
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        
        response = await client.post("/reservations/", json=reservation_data)
        assert response.status_code == 400
        assert "无需预约" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_reserve_nonexistent_book(self, client: AsyncClient, created_reader):
        """测试预约不存在的图书"""
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": "9999999999999"
        }
        
        response = await client.post("/reservations/", json=reservation_data)
        assert response.status_code == 400
        assert "不存在" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_reserve_with_invalid_reader(self, client: AsyncClient, borrowed_book_setup):
        """测试无效读者预约图书"""
        reservation_data = {
            "reader_id": "INVALID_READER",
            "isbn": borrowed_book_setup["isbn"]
        }
        
        response = await client.post("/reservations/", json=reservation_data)
        assert response.status_code == 400
        assert "读者" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_duplicate_reservation(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试重复预约同一本书"""
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        
        # 第一次预约
        response = await client.post("/reservations/", json=reservation_data)
        assert response.status_code == 201
        
        # 第二次预约同一本书
        response = await client.post("/reservations/", json=reservation_data)
        assert response.status_code == 400
        assert "重复预约" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_reservation(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取预约记录"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        response = await client.post("/reservations/", json=reservation_data)
        reservation_record = response.json()
        reservation_id = reservation_record["reservation_id"]
        
        # 获取预约记录
        response = await client.get(f"/reservations/{reservation_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["reservation_id"] == reservation_id
        assert data["reader_id"] == created_reader["reader_id"]
        assert data["isbn"] == borrowed_book_setup["isbn"]
    
    @pytest.mark.asyncio
    async def test_get_reservation_not_found(self, client: AsyncClient):
        """测试获取不存在的预约记录"""
        response = await client.get("/reservations/INVALID_RESERVATION_ID")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_all_reservations(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取所有预约记录"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        # 获取所有预约记录
        response = await client.get("/reservations/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_reader_reservations(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取读者的预约记录"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        # 获取读者的预约记录
        reader_id = created_reader["reader_id"]
        response = await client.get(f"/reservations/reader/{reader_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["reader_id"] == reader_id
    
    @pytest.mark.asyncio
    async def test_get_reader_active_reservations(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取读者的活跃预约记录"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        # 获取读者的活跃预约记录
        reader_id = created_reader["reader_id"]
        response = await client.get(f"/reservations/reader/{reader_id}/active")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["status"] in ["等待中", "可借阅"]
    
    @pytest.mark.asyncio
    async def test_get_book_reservations(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取图书的预约记录"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        # 获取图书的预约记录
        isbn = borrowed_book_setup["isbn"]
        response = await client.get(f"/reservations/book/{isbn}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["isbn"] == isbn
    
    @pytest.mark.asyncio
    async def test_get_book_pending_reservations(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取图书的等待预约记录"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        # 获取图书的等待预约记录
        isbn = borrowed_book_setup["isbn"]
        response = await client.get(f"/reservations/book/{isbn}/pending")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["status"] == "等待中"
    
    @pytest.mark.asyncio
    async def test_cancel_reservation(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试取消预约"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        response = await client.post("/reservations/", json=reservation_data)
        reservation_record = response.json()
        reservation_id = reservation_record["reservation_id"]
        
        # 取消预约
        response = await client.post(f"/reservations/{reservation_id}/cancel")
        assert response.status_code == 200
        
        data = response.json()
        assert "取消" in data["message"]
    
    @pytest.mark.asyncio
    async def test_cancel_reservation_not_found(self, client: AsyncClient):
        """测试取消不存在的预约记录"""
        response = await client.post("/reservations/INVALID_RESERVATION_ID/cancel")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_notify_reservation_ready(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试通知预约可借阅"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        response = await client.post("/reservations/", json=reservation_data)
        reservation_record = response.json()
        reservation_id = reservation_record["reservation_id"]
        
        # 通知预约可借阅
        response = await client.post(f"/reservations/{reservation_id}/notify")
        assert response.status_code == 200
        
        data = response.json()
        assert "通知" in data["message"]
    
    @pytest.mark.asyncio
    async def test_complete_reservation(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试完成预约"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        response = await client.post("/reservations/", json=reservation_data)
        reservation_record = response.json()
        reservation_id = reservation_record["reservation_id"]
        
        # 先通知可借阅
        await client.post(f"/reservations/{reservation_id}/notify")
        
        # 完成预约
        response = await client.post(f"/reservations/{reservation_id}/complete")
        assert response.status_code == 200
        
        data = response.json()
        assert "完成" in data["message"]
    
    @pytest.mark.asyncio
    async def test_get_reservation_queue_position(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取预约队列位置"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        # 获取队列位置
        reader_id = created_reader["reader_id"]
        isbn = borrowed_book_setup["isbn"]
        response = await client.get(f"/reservations/queue/{reader_id}/{isbn}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["reader_id"] == reader_id
        assert data["isbn"] == isbn
        assert data["has_reservation"] is True
        assert "queue_position" in data
    
    @pytest.mark.asyncio
    async def test_get_reservation_queue_position_no_reservation(self, client: AsyncClient, created_book, created_reader):
        """测试获取无预约的队列位置"""
        reader_id = created_reader["reader_id"]
        isbn = created_book["isbn"]
        response = await client.get(f"/reservations/queue/{reader_id}/{isbn}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["reader_id"] == reader_id
        assert data["isbn"] == isbn
        assert data["has_reservation"] is False
        assert data["queue_position"] is None
    
    @pytest.mark.asyncio
    async def test_get_ready_reservations(self, client: AsyncClient):
        """测试获取可借阅状态的预约记录"""
        response = await client.get("/reservations/ready/list")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_process_book_return(self, client: AsyncClient, borrowed_book_setup):
        """测试处理图书归还后的预约通知"""
        isbn = borrowed_book_setup["isbn"]
        response = await client.post(f"/reservations/process/book-return/{isbn}")
        assert response.status_code == 200
        
        data = response.json()
        assert "notified_count" in data
        assert isinstance(data["notified_count"], int)
    
    @pytest.mark.asyncio
    async def test_process_expired_reservations(self, client: AsyncClient):
        """测试处理过期的预约"""
        response = await client.post("/reservations/process/expired")
        assert response.status_code == 200
        
        data = response.json()
        assert "processed_count" in data
        assert isinstance(data["processed_count"], int)
    
    @pytest.mark.asyncio
    async def test_get_reservation_statistics(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试获取预约统计信息"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        response = await client.get("/reservations/stats/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_reservations" in data
        assert data["total_reservations"] >= 1
    
    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient, borrowed_book_setup, created_reader):
        """测试分页功能"""
        # 先预约一本书
        reservation_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": borrowed_book_setup["isbn"]
        }
        await client.post("/reservations/", json=reservation_data)
        
        # 测试第一页
        response = await client.get("/reservations/?skip=0&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        
        # 测试第二页
        response = await client.get("/reservations/?skip=5&limit=5")
        assert response.status_code == 200
"""
借阅API测试
"""
import pytest
from httpx import AsyncClient


class TestBorrowsAPI:
    """借阅API测试类"""
    
    @pytest.mark.asyncio
    async def test_borrow_book(self, client: AsyncClient, created_book, created_reader):
        """测试借阅图书"""
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        
        response = await client.post("/borrows/", json=borrow_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["reader_id"] == created_reader["reader_id"]
        assert data["isbn"] == created_book["isbn"]
        assert data["status"] == "借阅中"
        assert "borrow_id" in data
        assert "borrow_date" in data
        assert "due_date" in data
    
    @pytest.mark.asyncio
    async def test_borrow_book_simple(self, client: AsyncClient, created_book, created_reader):
        """测试借阅图书（简化接口）"""
        reader_id = created_reader["reader_id"]
        isbn = created_book["isbn"]
        
        response = await client.post(f"/borrows/simple?reader_id={reader_id}&isbn={isbn}")
        assert response.status_code == 201
        
        data = response.json()
        assert data["reader_id"] == reader_id
        assert data["isbn"] == isbn
        assert data["status"] == "借阅中"
    
    @pytest.mark.asyncio
    async def test_borrow_nonexistent_book(self, client: AsyncClient, created_reader):
        """测试借阅不存在的图书"""
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": "9999999999999"
        }
        
        response = await client.post("/borrows/", json=borrow_data)
        assert response.status_code == 400
        assert "不可借阅" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_borrow_with_invalid_reader(self, client: AsyncClient, created_book):
        """测试无效读者借阅图书"""
        borrow_data = {
            "reader_id": "INVALID_READER",
            "isbn": created_book["isbn"]
        }
        
        response = await client.post("/borrows/", json=borrow_data)
        assert response.status_code == 400
        assert "读者" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_duplicate_borrow(self, client: AsyncClient, created_book, created_reader):
        """测试重复借阅同一本书"""
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        
        # 第一次借阅
        response = await client.post("/borrows/", json=borrow_data)
        assert response.status_code == 201
        
        # 第二次借阅同一本书
        response = await client.post("/borrows/", json=borrow_data)
        assert response.status_code == 400
        assert "重复借阅" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_borrow_record(self, client: AsyncClient, created_book, created_reader):
        """测试获取借阅记录"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        response = await client.post("/borrows/", json=borrow_data)
        borrow_record = response.json()
        borrow_id = borrow_record["borrow_id"]
        
        # 获取借阅记录
        response = await client.get(f"/borrows/{borrow_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["borrow_id"] == borrow_id
        assert data["reader_id"] == created_reader["reader_id"]
        assert data["isbn"] == created_book["isbn"]
    
    @pytest.mark.asyncio
    async def test_get_borrow_record_not_found(self, client: AsyncClient):
        """测试获取不存在的借阅记录"""
        response = await client.get("/borrows/INVALID_BORROW_ID")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_all_borrows(self, client: AsyncClient, created_book, created_reader):
        """测试获取所有借阅记录"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        await client.post("/borrows/", json=borrow_data)
        
        # 获取所有借阅记录
        response = await client.get("/borrows/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_reader_borrows(self, client: AsyncClient, created_book, created_reader):
        """测试获取读者的借阅记录"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        await client.post("/borrows/", json=borrow_data)
        
        # 获取读者的借阅记录
        reader_id = created_reader["reader_id"]
        response = await client.get(f"/borrows/reader/{reader_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["reader_id"] == reader_id
    
    @pytest.mark.asyncio
    async def test_get_reader_active_borrows(self, client: AsyncClient, created_book, created_reader):
        """测试获取读者的活跃借阅记录"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        await client.post("/borrows/", json=borrow_data)
        
        # 获取读者的活跃借阅记录
        reader_id = created_reader["reader_id"]
        response = await client.get(f"/borrows/reader/{reader_id}/active")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["status"] in ["借阅中", "已逾期"]
    
    @pytest.mark.asyncio
    async def test_get_book_borrows(self, client: AsyncClient, created_book, created_reader):
        """测试获取图书的借阅记录"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        await client.post("/borrows/", json=borrow_data)
        
        # 获取图书的借阅记录
        isbn = created_book["isbn"]
        response = await client.get(f"/borrows/book/{isbn}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["isbn"] == isbn
    
    @pytest.mark.asyncio
    async def test_return_book(self, client: AsyncClient, created_book, created_reader):
        """测试归还图书"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        response = await client.post("/borrows/", json=borrow_data)
        borrow_record = response.json()
        borrow_id = borrow_record["borrow_id"]
        
        # 归还图书
        response = await client.post(f"/borrows/{borrow_id}/return")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "已归还"
        assert data["return_date"] is not None
    
    @pytest.mark.asyncio
    async def test_return_book_not_found(self, client: AsyncClient):
        """测试归还不存在的借阅记录"""
        response = await client.post("/borrows/INVALID_BORROW_ID/return")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_renew_book(self, client: AsyncClient, created_book, created_reader):
        """测试续借图书"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        response = await client.post("/borrows/", json=borrow_data)
        borrow_record = response.json()
        borrow_id = borrow_record["borrow_id"]
        original_due_date = borrow_record["due_date"]
        
        # 续借图书
        response = await client.post(f"/borrows/{borrow_id}/renew")
        assert response.status_code == 200
        
        data = response.json()
        assert data["renew_count"] == 1
        assert data["due_date"] != original_due_date  # 应还日期应该延后
    
    @pytest.mark.asyncio
    async def test_renew_book_not_found(self, client: AsyncClient):
        """测试续借不存在的借阅记录"""
        response = await client.post("/borrows/INVALID_BORROW_ID/renew")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_mark_overdue(self, client: AsyncClient, created_book, created_reader):
        """测试标记为逾期"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        response = await client.post("/borrows/", json=borrow_data)
        borrow_record = response.json()
        borrow_id = borrow_record["borrow_id"]
        
        # 标记为逾期
        response = await client.post(f"/borrows/{borrow_id}/overdue")
        assert response.status_code == 200
        
        data = response.json()
        assert "逾期" in data["message"]
    
    @pytest.mark.asyncio
    async def test_mark_lost(self, client: AsyncClient, created_book, created_reader):
        """测试标记为丢失"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        response = await client.post("/borrows/", json=borrow_data)
        borrow_record = response.json()
        borrow_id = borrow_record["borrow_id"]
        
        # 标记为丢失
        fine = 50.0
        response = await client.post(f"/borrows/{borrow_id}/lost?fine={fine}")
        assert response.status_code == 200
        
        data = response.json()
        assert "丢失" in data["message"]
    
    @pytest.mark.asyncio
    async def test_get_overdue_borrows(self, client: AsyncClient):
        """测试获取逾期的借阅记录"""
        response = await client.get("/borrows/overdue/list")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_process_overdue_books(self, client: AsyncClient):
        """测试处理逾期图书"""
        response = await client.post("/borrows/process/overdue")
        assert response.status_code == 200
        
        data = response.json()
        assert "processed_count" in data
        assert isinstance(data["processed_count"], int)
    
    @pytest.mark.asyncio
    async def test_get_borrow_statistics(self, client: AsyncClient, created_book, created_reader):
        """测试获取借阅统计信息"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        await client.post("/borrows/", json=borrow_data)
        
        response = await client.get("/borrows/stats/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_borrows" in data
        assert data["total_borrows"] >= 1
    
    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient, created_book, created_reader):
        """测试分页功能"""
        # 先借阅一本书
        borrow_data = {
            "reader_id": created_reader["reader_id"],
            "isbn": created_book["isbn"]
        }
        await client.post("/borrows/", json=borrow_data)
        
        # 测试第一页
        response = await client.get("/borrows/?skip=0&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        
        # 测试第二页
        response = await client.get("/borrows/?skip=5&limit=5")
        assert response.status_code == 200
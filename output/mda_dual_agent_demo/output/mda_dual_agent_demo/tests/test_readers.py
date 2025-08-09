"""
读者API测试
"""
import pytest
from httpx import AsyncClient


class TestReadersAPI:
    """读者API测试类"""
    
    @pytest.mark.asyncio
    async def test_register_reader(self, client: AsyncClient, sample_reader_data):
        """测试注册读者"""
        response = await client.post("/readers/", json=sample_reader_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == sample_reader_data["name"]
        assert data["id_card"] == sample_reader_data["id_card"]
        assert data["phone"] == sample_reader_data["phone"]
        assert data["reader_type"] == sample_reader_data["reader_type"]
        assert data["status"] == "正常"
        assert data["credit_score"] == 100
        assert "reader_id" in data
    
    @pytest.mark.asyncio
    async def test_register_reader_duplicate_id_card(self, client: AsyncClient, sample_reader_data):
        """测试注册重复身份证号的读者"""
        # 先注册一个读者
        response = await client.post("/readers/", json=sample_reader_data)
        assert response.status_code == 201
        
        # 再次注册相同身份证号的读者
        duplicate_data = sample_reader_data.copy()
        duplicate_data["name"] = "李四"
        duplicate_data["phone"] = "13800138001"
        
        response = await client.post("/readers/", json=duplicate_data)
        assert response.status_code == 400
        assert "已被注册" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_reader_duplicate_phone(self, client: AsyncClient, sample_reader_data):
        """测试注册重复手机号的读者"""
        # 先注册一个读者
        response = await client.post("/readers/", json=sample_reader_data)
        assert response.status_code == 201
        
        # 再次注册相同手机号的读者
        duplicate_data = sample_reader_data.copy()
        duplicate_data["name"] = "李四"
        duplicate_data["id_card"] = "110101199001011235"
        
        response = await client.post("/readers/", json=duplicate_data)
        assert response.status_code == 400
        assert "已被注册" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_reader_invalid_data(self, client: AsyncClient):
        """测试注册读者时数据验证"""
        invalid_data = {
            "name": "",  # 姓名为空
            "id_card": "123",  # 身份证号太短
            "phone": "123",  # 手机号太短
            "email": "invalid-email",  # 邮箱格式错误
            "reader_type": "学生"
        }
        
        response = await client.post("/readers/", json=invalid_data)
        assert response.status_code == 422  # 验证错误
    
    @pytest.mark.asyncio
    async def test_get_reader(self, client: AsyncClient, created_reader):
        """测试获取读者信息"""
        reader_id = created_reader["reader_id"]
        response = await client.get(f"/readers/{reader_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["reader_id"] == reader_id
        assert data["name"] == created_reader["name"]
    
    @pytest.mark.asyncio
    async def test_get_reader_not_found(self, client: AsyncClient):
        """测试获取不存在的读者"""
        response = await client.get("/readers/INVALID_ID")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_readers_list(self, client: AsyncClient, created_reader):
        """测试获取读者列表"""
        response = await client.get("/readers/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["reader_id"] == created_reader["reader_id"]
    
    @pytest.mark.asyncio
    async def test_get_readers_by_type(self, client: AsyncClient, created_reader):
        """测试根据类型获取读者"""
        reader_type = created_reader["reader_type"]
        response = await client.get(f"/readers/type/{reader_type}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert data[0]["reader_type"] == reader_type
    
    @pytest.mark.asyncio
    async def test_get_readers_by_status(self, client: AsyncClient, created_reader):
        """测试根据状态获取读者"""
        status = "正常"
        response = await client.get(f"/readers/status/{status}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert data[0]["status"] == status
    
    @pytest.mark.asyncio
    async def test_search_readers_by_name(self, client: AsyncClient, created_reader):
        """测试根据姓名搜索读者"""
        name_keyword = "张"
        response = await client.get(f"/readers/search/name?name={name_keyword}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_update_reader(self, client: AsyncClient, created_reader):
        """测试更新读者信息"""
        reader_id = created_reader["reader_id"]
        update_data = {
            "name": "更新后的姓名",
            "id_card": created_reader["id_card"],
            "phone": created_reader["phone"],
            "email": "updated@example.com",
            "reader_type": created_reader["reader_type"]
        }
        
        response = await client.put(f"/readers/{reader_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "更新后的姓名"
        assert data["email"] == "updated@example.com"
    
    @pytest.mark.asyncio
    async def test_update_reader_not_found(self, client: AsyncClient):
        """测试更新不存在的读者"""
        update_data = {
            "name": "姓名",
            "id_card": "110101199001011234",
            "phone": "13800138000",
            "reader_type": "学生"
        }
        
        response = await client.put("/readers/INVALID_ID", json=update_data)
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_freeze_reader(self, client: AsyncClient, created_reader):
        """测试冻结读者"""
        reader_id = created_reader["reader_id"]
        response = await client.post(f"/readers/{reader_id}/freeze")
        assert response.status_code == 200
        
        data = response.json()
        assert "冻结" in data["message"]
        
        # 验证读者状态已更改
        response = await client.get(f"/readers/{reader_id}")
        assert response.status_code == 200
        reader_data = response.json()
        assert reader_data["status"] == "冻结"
    
    @pytest.mark.asyncio
    async def test_unfreeze_reader(self, client: AsyncClient, created_reader):
        """测试解冻读者"""
        reader_id = created_reader["reader_id"]
        
        # 先冻结
        await client.post(f"/readers/{reader_id}/freeze")
        
        # 再解冻
        response = await client.post(f"/readers/{reader_id}/unfreeze")
        assert response.status_code == 200
        
        data = response.json()
        assert "解冻" in data["message"]
        
        # 验证读者状态已恢复
        response = await client.get(f"/readers/{reader_id}")
        assert response.status_code == 200
        reader_data = response.json()
        assert reader_data["status"] == "正常"
    
    @pytest.mark.asyncio
    async def test_delete_reader(self, client: AsyncClient, created_reader):
        """测试注销读者"""
        reader_id = created_reader["reader_id"]
        response = await client.delete(f"/readers/{reader_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "注销" in data["message"]
    
    @pytest.mark.asyncio
    async def test_check_reader_status(self, client: AsyncClient, created_reader):
        """测试检查读者状态"""
        reader_id = created_reader["reader_id"]
        response = await client.get(f"/readers/{reader_id}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["reader_id"] == reader_id
        assert "is_active" in data
        assert "is_valid" in data
        assert "can_borrow" in data
        assert "credit_score" in data
    
    @pytest.mark.asyncio
    async def test_update_credit_score(self, client: AsyncClient, created_reader):
        """测试更新信用分"""
        reader_id = created_reader["reader_id"]
        score_change = -10
        
        response = await client.post(f"/readers/{reader_id}/credit?score_change={score_change}")
        assert response.status_code == 200
        
        data = response.json()
        assert str(score_change) in data["message"]
        
        # 验证信用分已更新
        response = await client.get(f"/readers/{reader_id}")
        assert response.status_code == 200
        reader_data = response.json()
        assert reader_data["credit_score"] == 90  # 100 + (-10)
    
    @pytest.mark.asyncio
    async def test_get_reader_statistics(self, client: AsyncClient, created_reader):
        """测试获取读者统计信息"""
        response = await client.get("/readers/stats/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_readers" in data
        assert data["total_readers"] >= 1
    
    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient, created_reader):
        """测试分页功能"""
        # 测试第一页
        response = await client.get("/readers/?skip=0&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        
        # 测试第二页
        response = await client.get("/readers/?skip=5&limit=5")
        assert response.status_code == 200
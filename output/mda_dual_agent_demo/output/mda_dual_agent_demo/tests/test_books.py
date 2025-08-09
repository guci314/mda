"""
图书API测试
"""
import pytest
from httpx import AsyncClient


class TestBooksAPI:
    """图书API测试类"""
    
    @pytest.mark.asyncio
    async def test_create_book(self, client: AsyncClient, sample_book_data):
        """测试创建图书"""
        response = await client.post("/books/", json=sample_book_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["isbn"] == sample_book_data["isbn"]
        assert data["title"] == sample_book_data["title"]
        assert data["author"] == sample_book_data["author"]
        assert data["status"] == "在架"
    
    @pytest.mark.asyncio
    async def test_create_book_duplicate_isbn(self, client: AsyncClient, sample_book_data):
        """测试创建重复ISBN的图书"""
        # 先创建一本图书
        response = await client.post("/books/", json=sample_book_data)
        assert response.status_code == 201
        
        # 再次创建相同ISBN的图书
        response = await client.post("/books/", json=sample_book_data)
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_book_invalid_data(self, client: AsyncClient):
        """测试创建图书时数据验证"""
        invalid_data = {
            "isbn": "123",  # ISBN太短
            "title": "",    # 标题为空
            "author": "作者",
            "publisher": "出版社",
            "publish_year": 1800,  # 年份太早
            "category": "分类",
            "total_quantity": -1,  # 负数
            "available_quantity": 5,
            "location": "位置"
        }
        
        response = await client.post("/books/", json=invalid_data)
        assert response.status_code == 422  # 验证错误
    
    @pytest.mark.asyncio
    async def test_get_book(self, client: AsyncClient, created_book):
        """测试获取图书信息"""
        isbn = created_book["isbn"]
        response = await client.get(f"/books/{isbn}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["isbn"] == isbn
        assert data["title"] == created_book["title"]
    
    @pytest.mark.asyncio
    async def test_get_book_not_found(self, client: AsyncClient):
        """测试获取不存在的图书"""
        response = await client.get("/books/9999999999999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_books_list(self, client: AsyncClient, created_book):
        """测试获取图书列表"""
        response = await client.get("/books/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["isbn"] == created_book["isbn"]
    
    @pytest.mark.asyncio
    async def test_search_books_by_title(self, client: AsyncClient, created_book):
        """测试根据书名搜索图书"""
        title_keyword = "计算机"
        response = await client.get(f"/books/search/title?title={title_keyword}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if data:  # 如果有结果
            assert title_keyword in data[0]["title"]
    
    @pytest.mark.asyncio
    async def test_search_books_by_author(self, client: AsyncClient, created_book):
        """测试根据作者搜索图书"""
        author_keyword = "Bryant"
        response = await client.get(f"/books/search/author?author={author_keyword}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_search_books_by_category(self, client: AsyncClient, created_book):
        """测试根据分类搜索图书"""
        category = "计算机科学"
        response = await client.get(f"/books/search/category?category={category}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_available_books(self, client: AsyncClient, created_book):
        """测试获取可借阅图书"""
        response = await client.get("/books/available/list")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert data[0]["available_quantity"] > 0
    
    @pytest.mark.asyncio
    async def test_update_book(self, client: AsyncClient, created_book):
        """测试更新图书信息"""
        isbn = created_book["isbn"]
        update_data = {
            "title": "更新后的书名",
            "author": created_book["author"],
            "publisher": created_book["publisher"],
            "publish_year": created_book["publish_year"],
            "category": created_book["category"],
            "total_quantity": 15,
            "available_quantity": 12,
            "location": created_book["location"],
            "description": "更新后的描述"
        }
        
        response = await client.put(f"/books/{isbn}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "更新后的书名"
        assert data["total_quantity"] == 15
    
    @pytest.mark.asyncio
    async def test_update_book_not_found(self, client: AsyncClient):
        """测试更新不存在的图书"""
        update_data = {
            "title": "书名",
            "author": "作者",
            "publisher": "出版社",
            "publish_year": 2020,
            "category": "分类",
            "total_quantity": 10,
            "available_quantity": 8,
            "location": "位置"
        }
        
        response = await client.put("/books/9999999999999", json=update_data)
        assert response.status_code == 400  # 图书不存在
    
    @pytest.mark.asyncio
    async def test_remove_book(self, client: AsyncClient, created_book):
        """测试下架图书"""
        isbn = created_book["isbn"]
        response = await client.delete(f"/books/{isbn}")
        assert response.status_code == 200
        
        data = response.json()
        assert "下架" in data["message"]
        
        # 验证图书已下架
        response = await client.get(f"/books/{isbn}")
        if response.status_code == 200:
            book_data = response.json()
            assert book_data["status"] == "已下架"
    
    @pytest.mark.asyncio
    async def test_check_book_availability(self, client: AsyncClient, created_book):
        """测试检查图书可借状态"""
        isbn = created_book["isbn"]
        response = await client.get(f"/books/{isbn}/availability")
        assert response.status_code == 200
        
        data = response.json()
        assert data["isbn"] == isbn
        assert "is_available" in data
        assert "available_quantity" in data
        assert "total_quantity" in data
    
    @pytest.mark.asyncio
    async def test_get_book_statistics(self, client: AsyncClient, created_book):
        """测试获取图书统计信息"""
        response = await client.get("/books/stats/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_books" in data
        assert data["total_books"] >= 1
    
    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient, created_book):
        """测试分页功能"""
        # 测试第一页
        response = await client.get("/books/?skip=0&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        
        # 测试第二页
        response = await client.get("/books/?skip=5&limit=5")
        assert response.status_code == 200
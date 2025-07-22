"""Test PIM to PSM converter with Gemini via LangChain (with caching)"""

import unittest
import asyncio
import yaml
from pathlib import Path
import tempfile
import shutil
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from converters.pim_to_psm_gemini_langchain import PIMtoPSMGeminiLangChainConverter

# 缓存配置
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache


class TestPIMtoPSMGeminiLangChainConverter(unittest.TestCase):
    """测试 PIM to PSM 转换器 (Gemini via LangChain with caching)"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 检查 API key
        if not (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_STUDIO_KEY')):
            raise unittest.SkipTest("需要设置 GEMINI_API_KEY 或 GOOGLE_AI_STUDIO_KEY 环境变量")
        
        # 使用测试专用的缓存文件
        cls.cache_path = ".langchain_test_cache.db"
        cls.converter = PIMtoPSMGeminiLangChainConverter(cache_path=cls.cache_path)
        cls.test_dir = Path(tempfile.mkdtemp())
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
        # 清理测试缓存文件
        cache_file = Path(cls.cache_path)
        if cache_file.exists():
            cache_file.unlink()
    
    def setUp(self):
        """每个测试前的设置"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """每个测试后的清理"""
        self.loop.close()
    
    def test_simple_pim_conversion(self):
        """测试简单的 PIM 模型转换"""
        # 创建测试 PIM 文件
        pim_content = """# 简单图书系统

## 系统概述
一个简单的图书管理系统，用于管理图书信息。

## 业务实体

### 图书
- **书名**（必填）- 图书的标题
- **作者**（必填）- 图书的作者
- **ISBN**（必填，唯一）- 国际标准书号
- **价格** - 图书价格
- **库存数量**（必填）- 可借阅的数量

## 业务规则
1. ISBN 必须是13位数字
2. 价格必须大于0
3. 库存数量不能为负数
"""
        
        pim_file = self.test_dir / "simple_book.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 执行转换
        async def run_test():
            psm_data = await self.converter.convert(pim_file, "fastapi")
            return psm_data
        
        psm_data = self.loop.run_until_complete(run_test())
        
        # 验证结果
        self.assertIsInstance(psm_data, dict)
        self.assertEqual(psm_data['platform'], 'fastapi')
        self.assertIn('entities', psm_data)
        self.assertIn('services', psm_data)
        
        # 验证实体
        entities = psm_data['entities']
        self.assertTrue(len(entities) > 0)
        
        # 查找图书实体
        book_entity = None
        for entity in entities:
            if entity['name'].lower() == 'book':
                book_entity = entity
                break
        
        self.assertIsNotNone(book_entity, "应该包含 Book 实体")
        
        # 验证属性
        assert book_entity is not None  # 告诉类型检查器这里不会是 None
        attributes = book_entity['attributes']
        attr_names = [attr['name'] for attr in attributes]
        
        # 应该包含基本属性
        self.assertIn('title', attr_names)
        self.assertIn('author', attr_names)
        self.assertIn('isbn', attr_names)
        self.assertIn('price', attr_names)
        # 库存数量可能被转换为 stock 或 stock_quantity
        self.assertTrue('stock' in attr_names or 'stock_quantity' in attr_names)
        
        # 验证 PSM 文件已保存
        psm_file = pim_file.parent / "simple_book_psm_fastapi.yaml"
        self.assertTrue(psm_file.exists())
    
    def test_cache_effectiveness(self):
        """测试缓存是否生效"""
        # 创建测试 PIM 文件
        pim_content = """# 缓存测试系统

## 业务实体

### 测试实体
- **名称**（必填）
- **描述**
"""
        
        pim_file = self.test_dir / "cache_test.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 第一次调用（会缓存）
        import time
        start_time = time.time()
        psm_data1 = self.converter.convert_sync(pim_file, "fastapi")
        first_call_time = time.time() - start_time
        
        # 第二次调用（应该从缓存读取，速度更快）
        start_time = time.time()
        psm_data2 = self.converter.convert_sync(pim_file, "fastapi")
        second_call_time = time.time() - start_time
        
        # 验证结果相同
        self.assertEqual(psm_data1, psm_data2)
        
        # 第二次调用应该明显更快（至少快10倍）
        # 注意：这个测试可能会因为网络波动而不稳定
        if first_call_time > 1:  # 只有当第一次调用超过1秒时才检查
            self.assertLess(second_call_time, first_call_time / 10, 
                          f"缓存应该使第二次调用更快。第一次: {first_call_time:.2f}s, 第二次: {second_call_time:.2f}s")
        
        print(f"缓存效果: 第一次调用 {first_call_time:.2f}s, 第二次调用 {second_call_time:.2f}s")
    
    def test_sync_conversion(self):
        """测试同步版本的转换"""
        pim_content = """# 用户系统

## 业务实体

### 用户
- **用户名**（必填，唯一）
- **密码**（必填）
- **邮箱**（必填，唯一）
- **注册时间**
"""
        
        pim_file = self.test_dir / "user_system_sync.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 执行同步转换
        psm_data = self.converter.convert_sync(pim_file, "fastapi")
        
        # 验证结果
        self.assertIsInstance(psm_data, dict)
        self.assertEqual(psm_data['platform'], 'fastapi')
        self.assertIn('entities', psm_data)
        self.assertIn('services', psm_data)
        
        # 验证实体
        entities = psm_data['entities']
        self.assertTrue(len(entities) > 0)
        
        # 查找用户实体
        user_entity = None
        for entity in entities:
            if 'user' in entity['name'].lower():
                user_entity = entity
                break
        
        self.assertIsNotNone(user_entity, "应该包含 User 实体")
        
        # 验证 PSM 文件已保存
        psm_file = pim_file.parent / "user_system_sync_psm_fastapi.yaml"
        self.assertTrue(psm_file.exists())
    
    def test_complex_pim_with_relationships(self):
        """测试包含关系的复杂 PIM 模型"""
        pim_content = """# 借阅管理系统

## 业务实体

### 读者
- **姓名**（必填）
- **借书证号**（必填，唯一）
- **电话**（必填）

### 图书
- **书名**（必填）
- **ISBN**（必填，唯一）

### 借阅记录
- **读者**（关联到读者）
- **图书**（关联到图书）
- **借阅日期**（必填）
- **归还日期**

## 业务流程

### 借书流程
1. 验证读者身份
2. 检查图书可用性
3. 创建借阅记录
4. 更新图书状态
"""
        
        pim_file = self.test_dir / "borrow_system.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 执行转换
        async def run_test():
            psm_data = await self.converter.convert(pim_file, "fastapi")
            return psm_data
        
        psm_data = self.loop.run_until_complete(run_test())
        
        # 验证实体数量
        entities = psm_data['entities']
        self.assertEqual(len(entities), 3, "应该有3个实体")
        
        # 验证借阅记录的关联关系
        borrow_record = None
        for entity in entities:
            if 'borrow' in entity['name'].lower() or 'record' in entity['name'].lower():
                borrow_record = entity
                break
        
        self.assertIsNotNone(borrow_record, "应该包含借阅记录实体")
        
        # 检查外键关系
        assert borrow_record is not None  # 告诉类型检查器这里不会是 None
        attributes = borrow_record['attributes']
        has_reader_ref = False
        has_book_ref = False
        
        for attr in attributes:
            if 'reader' in attr['name'].lower() or 'borrower' in attr['name'].lower():
                has_reader_ref = True
            if 'book' in attr['name'].lower():
                has_book_ref = True
        
        self.assertTrue(has_reader_ref, "借阅记录应该关联到读者")
        self.assertTrue(has_book_ref, "借阅记录应该关联到图书")


if __name__ == '__main__':
    unittest.main()
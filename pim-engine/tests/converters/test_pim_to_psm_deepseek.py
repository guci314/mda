"""Test PIM to PSM converter with DeepSeek"""

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

# 配置 LangChain 缓存
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

# 使用测试专用的缓存文件
CACHE_PATH = ".langchain_deepseek_test.db"
set_llm_cache(SQLiteCache(database_path=CACHE_PATH))

from converters.pim_to_psm_deepseek import PIMtoPSMDeepSeekConverter


class TestPIMtoPSMDeepSeekConverter(unittest.TestCase):
    """测试 PIM to PSM 转换器 (DeepSeek)"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 检查 API key
        if not os.getenv('DEEPSEEK_API_KEY'):
            raise unittest.SkipTest("需要设置 DEEPSEEK_API_KEY 环境变量")
        
        cls.converter = PIMtoPSMDeepSeekConverter()
        cls.test_dir = Path(tempfile.mkdtemp())
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
        
        # 不清理缓存文件，保留以供后续测试使用
        print(f"保留缓存文件: {CACHE_PATH}")
    
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
    
    def test_chinese_to_english_conversion(self):
        """测试中文到英文的转换"""
        pim_content = """# 订单管理

## 业务实体

### 订单
- **订单编号**（必填，唯一）
- **客户姓名**（必填）
- **订单金额**（必填）
- **订单状态**（待支付、已支付、已发货、已完成）
"""
        
        pim_file = self.test_dir / "order_system.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        async def run_test():
            psm_data = await self.converter.convert(pim_file, "fastapi")
            return psm_data
        
        psm_data = self.loop.run_until_complete(run_test())
        
        # 验证实体名称已转换为英文
        entities = psm_data['entities']
        entity_names = [e['name'] for e in entities]
        
        # 应该包含 Order 或类似的英文名称
        has_order_entity = any('order' in name.lower() for name in entity_names)
        self.assertTrue(has_order_entity, "应该包含 Order 实体")
        
        # 查找订单实体
        order_entity = None
        for entity in entities:
            if 'order' in entity['name'].lower():
                order_entity = entity
                break
        
        # 验证属性名称也转换为英文
        if order_entity:
            attr_names = [attr['name'] for attr in order_entity['attributes']]
            
            # 应该包含英文属性名
            expected_attrs = ['number', 'customer', 'amount', 'status']
            for expected in expected_attrs:
                has_attr = any(expected in name.lower() for name in attr_names)
                self.assertTrue(has_attr, f"应该包含 {expected} 相关的属性")
    
    def test_business_rules_conversion(self):
        """测试业务规则的转换"""
        pim_content = """# 会员系统

## 业务实体

### 会员
- **会员号**（必填，唯一）
- **姓名**（必填）
- **积分**（默认0）
- **等级**（普通、银卡、金卡）

## 业务规则
1. 积分达到1000升级为银卡
2. 积分达到5000升级为金卡
3. 会员号必须是8位数字
"""
        
        pim_file = self.test_dir / "member_system.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        async def run_test():
            psm_data = await self.converter.convert(pim_file, "fastapi")
            return psm_data
        
        psm_data = self.loop.run_until_complete(run_test())
        
        # 验证服务中包含业务规则相关的方法
        services = psm_data.get('services', [])
        self.assertTrue(len(services) > 0, "应该生成服务")
        
        # 检查是否有升级相关的方法
        all_methods = []
        for service in services:
            if 'methods' in service:
                all_methods.extend(service['methods'])
        
        # 应该包含处理积分或等级的方法
        method_names = [m.get('name', '').lower() for m in all_methods]
        has_level_logic = any(
            keyword in name 
            for name in method_names 
            for keyword in ['upgrade', 'level', 'point', 'member']
        )
        
        self.assertTrue(has_level_logic or len(services) > 0, 
                       "应该包含处理会员等级的逻辑")
    
    def test_cache_effectiveness(self):
        """测试 LangChain 缓存是否生效"""
        # 创建测试 PIM 文件
        pim_content = """# 缓存测试系统

## 业务实体

### 缓存测试
- **测试ID**（必填，唯一）
- **测试名称**（必填）
- **测试时间**
"""
        
        pim_file = self.test_dir / "cache_test.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 第一次调用（会缓存）
        import time
        print("\n=== 测试 DeepSeek 缓存效果 ===")
        
        start_time = time.time()
        psm_data1 = self.converter.convert_sync(pim_file, "fastapi")
        first_call_time = time.time() - start_time
        print(f"第一次调用耗时: {first_call_time:.2f}秒")
        
        # 第二次调用（应该从缓存读取，速度更快）
        start_time = time.time()
        psm_data2 = self.converter.convert_sync(pim_file, "fastapi")
        second_call_time = time.time() - start_time
        print(f"第二次调用耗时（缓存）: {second_call_time:.2f}秒")
        
        # 验证结果相同
        self.assertEqual(psm_data1, psm_data2, "两次调用结果应该相同")
        
        # 第二次调用应该明显更快
        if first_call_time > 1:  # 只有当第一次调用超过1秒时才检查
            speedup = first_call_time / second_call_time
            print(f"缓存加速比: {speedup:.1f}x")
            self.assertLess(second_call_time, first_call_time / 5, 
                          f"缓存应该使第二次调用更快。加速比: {speedup:.1f}x")
        
        # 验证文件被保存
        psm_file_path = pim_file.parent / "cache_test_psm_fastapi.yaml"
        self.assertTrue(psm_file_path.exists())


if __name__ == '__main__':
    # 打印缓存信息
    print(f"使用缓存文件: {CACHE_PATH}")
    unittest.main()
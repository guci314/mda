"""Test PIM to PSM converter - comparing Gemini CLI vs LangChain with cache"""

import unittest
import asyncio
import yaml
from pathlib import Path
import tempfile
import shutil
import sys
import os
import time
from dotenv import load_dotenv

# 加载环境变量
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from converters.pim_to_psm_gemini import PIMtoPSMGeminiConverter
from converters.pim_to_psm_gemini_langchain import PIMtoPSMGeminiLangChainConverter


class TestPIMtoPSMGeminiComparison(unittest.TestCase):
    """比较 Gemini CLI 和 LangChain 版本的性能"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 检查 API key
        if not (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_STUDIO_KEY')):
            raise unittest.SkipTest("需要设置 GEMINI_API_KEY 或 GOOGLE_AI_STUDIO_KEY 环境变量")
        
        cls.cli_converter = PIMtoPSMGeminiConverter()
        cls.langchain_converter = PIMtoPSMGeminiLangChainConverter(cache_path=".test_cache.db")
        cls.test_dir = Path(tempfile.mkdtemp())
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
        # 清理测试缓存文件
        cache_file = Path(".test_cache.db")
        if cache_file.exists():
            cache_file.unlink()
    
    def setUp(self):
        """每个测试前的设置"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """每个测试后的清理"""
        self.loop.close()
    
    def test_performance_comparison(self):
        """比较 CLI 和 LangChain 版本的性能"""
        # 创建测试 PIM 文件
        pim_content = """# 性能测试系统

## 业务实体

### 产品
- **产品名称**（必填）
- **产品编码**（必填，唯一）
- **价格**（必填）
- **库存**（必填）

### 订单
- **订单号**（必填，唯一）
- **客户名称**（必填）
- **订单金额**（必填）
- **订单状态**

## 业务规则
1. 产品编码必须是唯一的
2. 价格必须大于0
3. 库存不能为负数
4. 订单状态只能是：待支付、已支付、已发货、已完成
"""
        
        pim_file = self.test_dir / "performance_test.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 测试 CLI 版本
        print("\n=== 测试 Gemini CLI 版本 ===")
        async def test_cli():
            start_time = time.time()
            psm_data = await self.cli_converter.convert(pim_file, "fastapi")
            elapsed = time.time() - start_time
            print(f"CLI 版本耗时: {elapsed:.2f}秒")
            return psm_data, elapsed
        
        cli_data, cli_time = self.loop.run_until_complete(test_cli())
        
        # 测试 LangChain 版本（第一次，无缓存）
        print("\n=== 测试 LangChain 版本（第一次） ===")
        async def test_langchain_first():
            start_time = time.time()
            psm_data = await self.langchain_converter.convert(pim_file, "fastapi")
            elapsed = time.time() - start_time
            print(f"LangChain 版本（第一次）耗时: {elapsed:.2f}秒")
            return psm_data, elapsed
        
        langchain_data1, langchain_time1 = self.loop.run_until_complete(test_langchain_first())
        
        # 测试 LangChain 版本（第二次，有缓存）
        print("\n=== 测试 LangChain 版本（第二次，使用缓存） ===")
        async def test_langchain_cached():
            start_time = time.time()
            psm_data = await self.langchain_converter.convert(pim_file, "fastapi")
            elapsed = time.time() - start_time
            print(f"LangChain 版本（缓存）耗时: {elapsed:.2f}秒")
            return psm_data, elapsed
        
        langchain_data2, langchain_time2 = self.loop.run_until_complete(test_langchain_cached())
        
        # 验证结果一致性
        # 由于 LLM 的随机性，我们只验证基本结构
        self.assertEqual(cli_data['platform'], langchain_data1['platform'])
        self.assertEqual(langchain_data1['platform'], langchain_data2['platform'])
        
        # 打印性能总结
        print("\n=== 性能总结 ===")
        print(f"CLI 版本: {cli_time:.2f}秒")
        print(f"LangChain 第一次: {langchain_time1:.2f}秒")
        print(f"LangChain 缓存: {langchain_time2:.2f}秒")
        print(f"缓存加速比: {langchain_time1/langchain_time2:.1f}x")
        
        # 验证缓存确实生效了
        self.assertLess(langchain_time2, langchain_time1 / 10, "缓存应该显著提升性能")
    
    def test_migration_guide(self):
        """展示如何从 CLI 迁移到 LangChain"""
        print("\n=== 迁移指南 ===")
        print("1. 原始 CLI 用法:")
        print("   converter = PIMtoPSMGeminiConverter()")
        print("   psm_data = await converter.convert(pim_file, 'fastapi')")
        print()
        print("2. LangChain 用法（带缓存）:")
        print("   converter = PIMtoPSMGeminiLangChainConverter()")
        print("   psm_data = await converter.convert(pim_file, 'fastapi')")
        print()
        print("3. 主要优势:")
        print("   - 自动缓存重复请求")
        print("   - 更好的错误处理")
        print("   - 支持更多 LLM 配置选项")
        print("   - 统一的 LangChain 生态系统")
        
        # 实际测试迁移
        pim_content = """# 迁移测试

## 业务实体

### 测试
- **名称**（必填）
"""
        
        pim_file = self.test_dir / "migration_test.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 两种方式应该产生相似的结果
        async def test_both():
            cli_result = await self.cli_converter.convert(pim_file, "fastapi")
            langchain_result = await self.langchain_converter.convert(pim_file, "fastapi")
            return cli_result, langchain_result
        
        cli_result, langchain_result = self.loop.run_until_complete(test_both())
        
        # 验证基本结构相同
        self.assertEqual(cli_result['platform'], langchain_result['platform'])
        self.assertIn('entities', cli_result)
        self.assertIn('entities', langchain_result)


if __name__ == '__main__':
    unittest.main()
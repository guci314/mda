"""End-to-End tests for MDA flow"""

import unittest
import asyncio
import tempfile
import subprocess
import shutil
from pathlib import Path
import yaml
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from converters.pim_to_psm_gemini import PIMtoPSMGeminiConverter
from converters.psm_to_code_gemini import PSMtoCodeGeminiGenerator
from mda_orchestrator import MDAOrchestrator


class TestMDAEndToEnd(unittest.TestCase):
    """端到端测试 MDA 流程"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.has_api_key = bool(os.getenv("GEMINI_API_KEY"))
        cls.test_dir = Path(tempfile.mkdtemp())
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """每个测试前的设置"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """每个测试后的清理"""
        self.loop.close()
    
    def create_test_pim(self, name: str, content: str) -> Path:
        """创建测试 PIM 文件"""
        pim_file = self.test_dir / f"{name}.md"
        pim_file.write_text(content, encoding='utf-8')
        return pim_file
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "Requires GEMINI_API_KEY")
    def test_simple_crud_system_e2e(self):
        """测试简单 CRUD 系统的端到端流程"""
        # 创建 PIM
        pim_content = """# 产品管理系统

## 系统概述
简单的产品信息管理系统。

## 业务实体

### 产品
- **产品名称**（必填）- 产品的名称
- **产品编码**（必填，唯一）- 产品的唯一编码
- **价格**（必填）- 产品单价
- **库存数量**（必填）- 当前库存
- **描述** - 产品描述

## 业务规则
1. 产品编码必须唯一
2. 价格必须大于0
3. 库存数量不能为负数
4. 产品名称长度在1-100字符之间
"""
        
        pim_file = self.create_test_pim("product_system", pim_content)
        
        async def run_test():
            # 步骤1: PIM → PSM
            psm_converter = PIMtoPSMGeminiConverter()
            psm_data = await psm_converter.convert(pim_file, "fastapi")
            
            # 验证 PSM
            self.assertEqual(psm_data['platform'], 'fastapi')
            self.assertIn('entities', psm_data)
            self.assertIn('services', psm_data)
            
            # 查找产品实体
            product_entity = None
            for entity in psm_data['entities']:
                if 'product' in entity['name'].lower():
                    product_entity = entity
                    break
            
            self.assertIsNotNone(product_entity)
            
            # 验证属性转换
            attr_names = [attr['name'] for attr in product_entity['attributes']]
            self.assertTrue(any('name' in n or 'title' in n for n in attr_names))
            self.assertTrue(any('code' in n or 'id' in n for n in attr_names))
            self.assertTrue(any('price' in n for n in attr_names))
            self.assertTrue(any('stock' in n or 'quantity' in n for n in attr_names))
            
            # 步骤2: PSM → Code
            psm_file = pim_file.parent / f"{pim_file.stem}_psm_fastapi.yaml"
            self.assertTrue(psm_file.exists())
            
            code_generator = PSMtoCodeGeminiGenerator()
            output_dir = self.test_dir / "product_code"
            generated_files = await code_generator.generate(psm_file, output_dir)
            
            # 验证生成的文件
            expected_files = [
                'models.py', 'schemas.py', 'database.py',
                'services.py', 'api.py', 'main.py',
                'requirements.txt'
            ]
            
            for file in expected_files:
                self.assertIn(file, generated_files)
                self.assertTrue((output_dir / file).exists())
            
            # 步骤3: 验证生成的代码质量
            # 检查语法
            for py_file in output_dir.glob("*.py"):
                result = subprocess.run(
                    ["python", "-m", "py_compile", str(py_file)],
                    capture_output=True
                )
                self.assertEqual(result.returncode, 0,
                               f"Syntax error in {py_file.name}")
            
            # 验证关键内容
            models_content = (output_dir / "models.py").read_text()
            self.assertIn("Product", models_content)
            self.assertIn("SQLAlchemy", models_content.lower())
            
            api_content = (output_dir / "api.py").read_text()
            self.assertIn("router", api_content)
            self.assertIn("POST", api_content)
            self.assertIn("GET", api_content)
            
            return output_dir
        
        output_dir = self.loop.run_until_complete(run_test())
        
        # 清理
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "Requires GEMINI_API_KEY")
    def test_complex_business_flow_e2e(self):
        """测试包含复杂业务流程的端到端流程"""
        pim_content = """# 订单处理系统

## 业务实体

### 客户
- **客户名称**（必填）
- **联系电话**（必填）
- **地址**（必填）

### 订单
- **订单号**（必填，唯一）
- **客户**（关联到客户）
- **订单日期**（必填）
- **总金额**（必填）
- **状态**（待支付、已支付、已发货、已完成、已取消）

### 订单项
- **订单**（关联到订单）
- **产品名称**（必填）
- **数量**（必填）
- **单价**（必填）
- **小计**（自动计算）

## 业务流程

### 创建订单流程
1. 验证客户信息
2. 创建订单主记录
3. 添加订单项
4. 计算总金额
5. 设置初始状态为"待支付"

## 业务规则
1. 订单总金额等于所有订单项小计之和
2. 只有"待支付"状态的订单可以修改
3. 订单号格式：ORD + 年月日 + 序号
"""
        
        pim_file = self.create_test_pim("order_system", pim_content)
        
        async def run_test():
            orchestrator = MDAOrchestrator(deployment_base=str(self.test_dir))
            
            output_dir = await orchestrator.process_model(
                pim_file,
                platform='fastapi',
                deploy=False
            )
            
            # 验证实体关系
            models_content = (output_dir / "models.py").read_text()
            self.assertIn("Customer", models_content)
            self.assertIn("Order", models_content)
            self.assertIn("OrderItem", models_content)
            
            # 验证外键关系
            self.assertIn("ForeignKey", models_content)
            self.assertIn("relationship", models_content)
            
            # 验证业务逻辑
            services_content = (output_dir / "services.py").read_text()
            # 应该包含订单创建逻辑
            self.assertTrue(
                "order" in services_content.lower() or
                "Order" in services_content
            )
            
            return output_dir
        
        output_dir = self.loop.run_until_complete(run_test())
        
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    def test_mda_cli_integration(self):
        """测试 MDA CLI 工具集成"""
        # 创建测试 PIM
        pim_content = """# CLI 测试系统

## 业务实体

### 测试实体
- **名称**（必填）
- **值**（必填）
"""
        pim_file = self.create_test_pim("cli_test", pim_content)
        
        # 测试 CLI 命令（dry run）
        mda_script = Path(__file__).parent.parent.parent / "mda.py"
        
        if mda_script.exists():
            # 测试帮助命令
            result = subprocess.run(
                [sys.executable, str(mda_script), "--help"],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("MDA", result.stdout)
            self.assertIn("--platform", result.stdout)
    
    def test_generated_code_structure(self):
        """测试生成代码的结构（不需要 API key）"""
        # 创建模拟的生成代码结构
        output_dir = self.test_dir / "mock_generated"
        output_dir.mkdir()
        
        # 创建预期的文件结构
        files = {
            "models.py": """from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
""",
            "schemas.py": """from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    
    class Config:
        from_attributes = True
""",
            "main.py": """from fastapi import FastAPI
from api import router

app = FastAPI(title="Product API")
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
""",
            "requirements.txt": """fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
""",
            ".env": """DATABASE_URL=postgresql://postgres:postgres@localhost:5432/testdb
SECRET_KEY=test-secret-key
""",
            "docker-compose.yml": """version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: postgres
"""
        }
        
        # 创建文件
        for filename, content in files.items():
            (output_dir / filename).write_text(content)
        
        # 验证结构
        self.assertTrue((output_dir / "models.py").exists())
        self.assertTrue((output_dir / "schemas.py").exists())
        self.assertTrue((output_dir / "main.py").exists())
        self.assertTrue((output_dir / "requirements.txt").exists())
        self.assertTrue((output_dir / ".env").exists())
        self.assertTrue((output_dir / "docker-compose.yml").exists())
        
        # 验证可以作为 Python 模块导入（语法检查）
        for py_file in output_dir.glob("*.py"):
            result = subprocess.run(
                ["python", "-m", "py_compile", str(py_file)],
                capture_output=True
            )
            self.assertEqual(result.returncode, 0)


class TestMDAPerformance(unittest.TestCase):
    """MDA 性能测试"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "Requires GEMINI_API_KEY")
    def test_large_model_performance(self):
        """测试大型模型的处理性能"""
        # 创建包含多个实体的大型 PIM
        entities = []
        for i in range(10):
            entities.append(f"""
### 实体{i}
- **字段1**（必填）
- **字段2**（必填）
- **字段3**
- **字段4**
- **字段5**
""")
        
        pim_content = f"""# 大型系统

## 业务实体

{''.join(entities)}

## 业务规则
1. 所有实体的字段1必须唯一
2. 字段2不能为空
"""
        
        pim_file = self.test_dir / "large_system.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        import time
        
        async def run_performance_test():
            start_time = time.time()
            
            converter = PIMtoPSMGeminiConverter()
            psm_data = await converter.convert(pim_file, "fastapi")
            
            psm_time = time.time() - start_time
            
            # 验证所有实体都被转换
            self.assertGreaterEqual(len(psm_data.get('entities', [])), 10)
            
            # 性能基准：转换应该在合理时间内完成
            self.assertLess(psm_time, 60, "PSM conversion took too long")
            
            return psm_time
        
        psm_time = self.loop.run_until_complete(run_performance_test())
        print(f"\nPerformance: PSM conversion took {psm_time:.2f} seconds")


if __name__ == '__main__':
    unittest.main()
"""Test MDA Orchestrator"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mda_orchestrator import MDAOrchestrator
from unittest.mock import Mock, patch, AsyncMock


class TestMDAOrchestrator(unittest.TestCase):
    """测试 MDA 编排器"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.models_dir = cls.test_dir / "models"
        cls.models_dir.mkdir()
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """每个测试前的设置"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # 创建测试 PIM 文件
        self.pim_content = """# 测试系统

## 业务实体

### 用户
- **用户名**（必填，唯一）
- **密码**（必填）
- **邮箱**（必填，唯一）

## 业务规则
1. 用户名长度必须在3-20个字符之间
2. 密码必须包含字母和数字
3. 邮箱必须是有效格式
"""
        self.pim_file = self.models_dir / "test_system.md"
        self.pim_file.write_text(self.pim_content, encoding='utf-8')
    
    def tearDown(self):
        """每个测试后的清理"""
        self.loop.close()
        
        # 清理生成的文件
        for pattern in ["*_psm_*.yaml", "*_generated"]:
            for file in self.models_dir.glob(pattern):
                if file.is_dir():
                    shutil.rmtree(file)
                else:
                    file.unlink()
    
    def test_orchestrator_initialization(self):
        """测试编排器初始化"""
        orchestrator = MDAOrchestrator()
        
        self.assertIsNotNone(orchestrator.pim_to_psm)
        self.assertIsNotNone(orchestrator.psm_to_code)
        self.assertIsNotNone(orchestrator.deployment_base)
    
    @patch('mda_orchestrator.PIMtoPSMGeminiConverter')
    @patch('mda_orchestrator.PSMtoCodeGeminiGenerator')
    async def test_process_model_flow(self, mock_code_gen, mock_psm_gen):
        """测试模型处理流程（使用 Mock）"""
        # 设置 Mock
        mock_psm_converter = AsyncMock()
        mock_psm_converter.convert.return_value = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'entities': [{
                'name': 'User',
                'attributes': [
                    {'name': 'id', 'type': 'integer'},
                    {'name': 'username', 'type': 'string'},
                    {'name': 'email', 'type': 'string'}
                ]
            }],
            'services': [{
                'name': 'UserService',
                'methods': [
                    {'name': 'create', 'http_method': 'POST'},
                    {'name': 'get', 'http_method': 'GET'}
                ]
            }]
        }
        
        mock_code_generator = AsyncMock()
        mock_code_generator.generate.return_value = {
            'models.py': self.test_dir / 'models.py',
            'schemas.py': self.test_dir / 'schemas.py',
            'main.py': self.test_dir / 'main.py'
        }
        
        mock_psm_gen.return_value = mock_psm_converter
        mock_code_gen.return_value = mock_code_generator
        
        # 创建编排器并处理模型
        orchestrator = MDAOrchestrator(deployment_base=str(self.test_dir))
        
        output_dir = await orchestrator.process_model(
            self.pim_file,
            platform='fastapi',
            deploy=False
        )
        
        # 验证调用
        mock_psm_converter.convert.assert_called_once()
        mock_code_generator.generate.assert_called_once()
        
        # 验证输出目录
        self.assertIsInstance(output_dir, Path)
    
    @patch('subprocess.run')
    async def test_code_testing(self, mock_run):
        """测试代码验证功能"""
        # 模拟 subprocess 成功
        mock_run.return_value.returncode = 0
        
        orchestrator = MDAOrchestrator()
        
        # 创建测试代码目录
        code_dir = self.test_dir / "test_code"
        code_dir.mkdir()
        
        # 创建测试文件
        test_file = code_dir / "test.py"
        test_file.write_text("print('Hello, World!')")
        
        # 测试代码验证
        await orchestrator._test_generated_code(code_dir)
        
        # 验证 subprocess 被调用
        self.assertTrue(mock_run.called)
    
    async def test_deployment_directory_creation(self):
        """测试部署目录创建"""
        orchestrator = MDAOrchestrator(deployment_base=str(self.test_dir / "deploy"))
        
        code_dir = self.test_dir / "test_code"
        code_dir.mkdir()
        
        # 创建必要的文件
        (code_dir / "requirements.txt").write_text("fastapi==0.100.0")
        (code_dir / "main.py").write_text("print('test')")
        
        # 测试部署
        service_url = await orchestrator._deploy_service("test_service", code_dir)
        
        # 验证部署目录
        deploy_dir = Path(orchestrator.deployment_base) / "test_service"
        self.assertTrue(deploy_dir.exists())
        self.assertTrue((deploy_dir / "requirements.txt").exists())
        self.assertTrue((deploy_dir / "start.sh").exists())
    
    @patch('mda_orchestrator.PIMtoPSMGeminiConverter')
    @patch('mda_orchestrator.PSMtoCodeGeminiGenerator')
    async def test_batch_processing(self, mock_code_gen, mock_psm_gen):
        """测试批量处理"""
        # 创建多个 PIM 文件
        pim_files = []
        for i in range(3):
            pim_file = self.models_dir / f"test_system_{i}.md"
            pim_file.write_text(self.pim_content, encoding='utf-8')
            pim_files.append(pim_file)
        
        # 设置 Mock
        mock_psm_converter = AsyncMock()
        mock_psm_converter.convert.return_value = {'platform': 'fastapi'}
        
        mock_code_generator = AsyncMock()
        mock_code_generator.generate.return_value = {'main.py': Path('main.py')}
        
        mock_psm_gen.return_value = mock_psm_converter
        mock_code_gen.return_value = mock_code_generator
        
        # 批量处理
        orchestrator = MDAOrchestrator()
        await orchestrator.batch_process(pim_files)
        
        # 验证每个文件都被处理
        self.assertEqual(mock_psm_converter.convert.call_count, 3)
        self.assertEqual(mock_code_generator.generate.call_count, 3)
    
    def test_error_handling(self):
        """测试错误处理"""
        orchestrator = MDAOrchestrator()
        
        # 测试不存在的文件
        non_existent_file = self.test_dir / "non_existent.md"
        
        async def test_error():
            with self.assertRaises(Exception):
                await orchestrator.process_model(non_existent_file)
        
        self.loop.run_until_complete(test_error())


class TestMDAOrchestratorIntegration(unittest.TestCase):
    """MDA 编排器集成测试（需要 API key）"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 检查是否有 API key
        if not os.getenv("GEMINI_API_KEY"):
            cls.skip_integration = True
            return
        else:
            cls.skip_integration = False
        
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.models_dir = cls.test_dir / "models"
        cls.models_dir.mkdir()
    
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        if hasattr(cls, 'test_dir') and cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """每个测试前的设置"""
        if self.skip_integration:
            self.skipTest("GEMINI_API_KEY not set, skipping integration tests")
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """每个测试后的清理"""
        if hasattr(self, 'loop'):
            self.loop.close()
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "Requires GEMINI_API_KEY")
    def test_full_mda_flow_integration(self):
        """测试完整的 MDA 流程（真实 API 调用）"""
        # 创建简单的 PIM 模型
        pim_content = """# 简单任务系统

## 业务实体

### 任务
- **标题**（必填）- 任务标题
- **描述** - 任务描述
- **状态**（待办、进行中、已完成）- 任务状态
- **创建时间** - 创建时间

## 业务规则
1. 新任务的状态默认为"待办"
2. 任务标题不能为空
3. 只能按顺序改变状态：待办→进行中→已完成
"""
        
        pim_file = self.models_dir / "task_system.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        async def run_integration_test():
            orchestrator = MDAOrchestrator(deployment_base=str(self.test_dir))
            
            output_dir = await orchestrator.process_model(
                pim_file,
                platform='fastapi',
                deploy=False
            )
            
            # 验证生成的文件
            self.assertTrue(output_dir.exists())
            self.assertTrue((output_dir / "models.py").exists())
            self.assertTrue((output_dir / "schemas.py").exists())
            self.assertTrue((output_dir / "main.py").exists())
            self.assertTrue((output_dir / "requirements.txt").exists())
            
            # 验证 PSM 文件
            psm_file = pim_file.parent / "task_system_psm_fastapi.yaml"
            self.assertTrue(psm_file.exists())
            
            # 验证生成的代码包含预期内容
            models_content = (output_dir / "models.py").read_text()
            self.assertIn("Task", models_content)
            self.assertIn("title", models_content)
            self.assertIn("status", models_content)
            
            return output_dir
        
        output_dir = self.loop.run_until_complete(run_integration_test())
        
        # 清理
        if output_dir.exists():
            shutil.rmtree(output_dir)


if __name__ == '__main__':
    unittest.main()
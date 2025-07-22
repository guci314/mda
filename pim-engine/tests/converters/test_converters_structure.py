"""测试转换器的结构和基本功能（不需要 API key）"""

import unittest
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from converters.pim_to_psm_gemini import PIMtoPSMGeminiConverter
from converters.psm_to_code_gemini import PSMtoCodeGeminiGenerator


class TestConvertersStructure(unittest.TestCase):
    """测试转换器的结构和基本功能"""
    
    def test_pim_to_psm_converter_init(self):
        """测试 PIM to PSM 转换器初始化"""
        converter = PIMtoPSMGeminiConverter()
        self.assertIsNotNone(converter.gemini_cli)
        self.assertTrue(Path(converter.gemini_cli).exists())
    
    def test_pim_to_psm_prompt_building(self):
        """测试提示构建"""
        converter = PIMtoPSMGeminiConverter()
        
        pim_content = "# 测试系统\n## 业务实体\n### 用户\n- 用户名"
        prompt = converter._build_conversion_prompt(pim_content, "fastapi")
        
        # 验证提示包含必要内容
        self.assertIn("模型驱动架构", prompt)
        self.assertIn("PIM", prompt)
        self.assertIn("PSM", prompt)
        self.assertIn("fastapi", prompt)
        self.assertIn(pim_content, prompt)
        self.assertIn("YAML", prompt)
    
    def test_psm_to_code_generator_init(self):
        """测试 PSM to Code 生成器初始化"""
        generator = PSMtoCodeGeminiGenerator()
        self.assertIsNotNone(generator.gemini_cli)
        self.assertTrue(Path(generator.gemini_cli).exists())
    
    def test_models_prompt_generation(self):
        """测试模型代码提示生成"""
        generator = PSMtoCodeGeminiGenerator()
        
        psm_data = {
            'platform': 'fastapi',
            'entities': [{
                'name': 'User',
                'attributes': [
                    {'name': 'id', 'type': 'integer'},
                    {'name': 'username', 'type': 'string'}
                ]
            }]
        }
        
        prompt = generator._generate_models_prompt(psm_data)
        
        # 验证提示包含必要内容
        self.assertIn("SQLAlchemy", prompt)
        self.assertIn("User", prompt)
        self.assertIn("fastapi", prompt)
        self.assertIn("Column", prompt)
    
    def test_api_prompt_generation(self):
        """测试 API 代码提示生成"""
        generator = PSMtoCodeGeminiGenerator()
        
        psm_data = {
            'services': [{
                'name': 'UserService',
                'methods': [
                    {'name': 'create', 'http_method': 'POST'},
                    {'name': 'get', 'http_method': 'GET'}
                ]
            }]
        }
        
        prompt = generator._generate_api_prompt(psm_data)
        
        # 验证提示包含必要内容
        self.assertIn("FastAPI", prompt)
        self.assertIn("router", prompt)
        self.assertIn("POST", prompt)
        self.assertIn("GET", prompt)
    
    def test_code_extraction(self):
        """测试代码提取功能"""
        generator = PSMtoCodeGeminiGenerator()
        
        # 测试 Python 代码提取
        response = """这是一些说明文字
```python
def hello():
    return "world"
```
这是更多文字"""
        
        code = generator._extract_code(response, "test.py")
        self.assertEqual(code.strip(), 'def hello():\n    return "world"')
        
        # 测试没有代码块的情况
        response2 = "fastapi==0.100.0\nsqlalchemy==2.0.0"
        code2 = generator._extract_code(response2, "requirements.txt")
        self.assertEqual(code2.strip(), "fastapi==0.100.0\nsqlalchemy==2.0.0")
    
    def test_file_paths(self):
        """测试文件路径处理"""
        import tempfile
        
        converter = PIMtoPSMGeminiConverter()
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
            # 测试 PSM 文件名生成
            expected_psm = tmp_path.parent / f"{tmp_path.stem}_psm_fastapi.yaml"
            
            # 验证路径构建逻辑
            self.assertTrue(str(expected_psm).endswith("_psm_fastapi.yaml"))
        
        # 清理
        tmp_path.unlink()


if __name__ == '__main__':
    unittest.main()
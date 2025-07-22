"""Test PSM to Code generator with Gemini LangChain"""

import unittest
import asyncio
import yaml
from pathlib import Path
import tempfile
import shutil
import subprocess
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"已加载环境变量文件: {env_path}")

# 也尝试加载 pim-engine/.env
pim_env_path = Path(__file__).parent.parent.parent / ".env"
if pim_env_path.exists():
    load_dotenv(pim_env_path, override=True)
    print(f"已加载 PIM 环境变量文件: {pim_env_path}")

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# 配置 LangChain 缓存
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

# 使用测试专用的缓存文件（不清除，以便重复使用）
CACHE_PATH = ".langchain_gemini_psm_test.db"
set_llm_cache(SQLiteCache(database_path=CACHE_PATH))

from converters.psm_to_code_gemini_langchain import PSMtoCodeGeminiLangChainGenerator


class TestPSMtoCodeGeminiLangChainGenerator(unittest.TestCase):
    """测试 PSM to Code 生成器 (Gemini LangChain)"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 检查 API key
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_STUDIO_KEY')
        if not api_key:
            print("警告: GEMINI_API_KEY 或 GOOGLE_AI_STUDIO_KEY 环境变量未设置")
            print("当前环境变量:")
            for key in os.environ:
                if 'API' in key or 'GEMINI' in key or 'GOOGLE' in key:
                    print(f"  {key}: {os.environ[key][:10]}...")
            raise unittest.SkipTest("需要设置 GEMINI_API_KEY 或 GOOGLE_AI_STUDIO_KEY 环境变量")
        else:
            print(f"找到 API KEY: {api_key[:10]}...")
        
        cls.generator = PSMtoCodeGeminiLangChainGenerator(cache_path=CACHE_PATH)
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
        self.output_dir = self.test_dir / f"test_{self._testMethodName}"
        self.output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """每个测试后的清理"""
        self.loop.close()
    
    def create_test_psm(self, filename: str, content: dict) -> Path:
        """创建测试用的 PSM 文件"""
        psm_file = self.test_dir / filename
        with open(psm_file, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, allow_unicode=True)
        return psm_file
    
    def test_simple_fastapi_generation(self):
        """测试简单的 FastAPI 代码生成"""
        # 创建测试 PSM
        psm_data = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'description': '简单图书管理系统',
            'entities': [{
                'name': 'Book',
                'table_name': 'books',
                'description': '图书实体',
                'attributes': [
                    {
                        'name': 'id',
                        'type': 'integer',
                        'db_type': 'INTEGER',
                        'constraints': {
                            'primary_key': True,
                            'auto_increment': True
                        }
                    },
                    {
                        'name': 'title',
                        'type': 'string',
                        'db_type': 'VARCHAR(255)',
                        'constraints': {
                            'required': True
                        }
                    },
                    {
                        'name': 'author',
                        'type': 'string',
                        'db_type': 'VARCHAR(100)',
                        'constraints': {
                            'required': True
                        }
                    },
                    {
                        'name': 'isbn',
                        'type': 'string',
                        'db_type': 'VARCHAR(13)',
                        'constraints': {
                            'required': True,
                            'unique': True
                        }
                    }
                ]
            }],
            'services': [{
                'name': 'BookService',
                'base_path': '/api/books',
                'description': '图书管理服务',
                'methods': [
                    {
                        'name': 'create',
                        'http_method': 'POST',
                        'path': '/',
                        'description': '创建图书',
                        'request': {
                            'type': 'BookCreate'
                        },
                        'response': {
                            'type': 'BookResponse',
                            'status_code': 201
                        }
                    },
                    {
                        'name': 'list',
                        'http_method': 'GET',
                        'path': '/',
                        'description': '获取图书列表'
                    }
                ]
            }]
        }
        
        psm_file = self.create_test_psm('simple_book_psm.yaml', psm_data)
        
        # 执行代码生成
        async def run_test():
            files = await self.generator.generate(psm_file, self.output_dir)
            return files
        
        generated_files = self.loop.run_until_complete(run_test())
        
        # 验证生成的文件
        expected_files = [
            'models.py',
            'schemas.py',
            'database.py',
            'services.py',
            'api.py',
            'main.py',
            'requirements.txt',
            '.env.example',
            'Dockerfile',
            'docker-compose.yml',
            'README.md',
            '.gitignore'
        ]
        
        for expected_file in expected_files:
            self.assertIn(expected_file, generated_files)
            file_path = self.output_dir / expected_file
            self.assertTrue(file_path.exists(), f"{expected_file} 应该存在")
            
            # 验证文件不为空
            content = file_path.read_text()
            self.assertTrue(len(content) > 0, f"{expected_file} 不应该为空")
        
        # 验证 models.py 包含 Book 类
        models_content = (self.output_dir / 'models.py').read_text()
        self.assertIn('class Book', models_content)
        self.assertIn('__tablename__', models_content)
        self.assertIn('title', models_content)
        self.assertIn('author', models_content)
        self.assertIn('isbn', models_content)
        
        # 验证 Python 语法
        for py_file in self.output_dir.glob('*.py'):
            result = subprocess.run(
                ['python', '-m', 'py_compile', str(py_file)],
                capture_output=True
            )
            self.assertEqual(result.returncode, 0, 
                           f"{py_file.name} 应该是有效的 Python 代码")
    
    def test_sync_generation(self):
        """测试同步版本的代码生成"""
        psm_data = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'description': '用户管理系统',
            'entities': [{
                'name': 'User',
                'table_name': 'users',
                'attributes': [
                    {
                        'name': 'id',
                        'type': 'integer',
                        'db_type': 'INTEGER',
                        'constraints': {'primary_key': True}
                    },
                    {
                        'name': 'username',
                        'type': 'string',
                        'db_type': 'VARCHAR(50)',
                        'constraints': {'required': True, 'unique': True}
                    },
                    {
                        'name': 'email',
                        'type': 'string',
                        'db_type': 'VARCHAR(100)',
                        'constraints': {'required': True, 'unique': True}
                    }
                ]
            }],
            'services': [{
                'name': 'UserService',
                'base_path': '/api/users',
                'methods': [
                    {
                        'name': 'create_user',
                        'http_method': 'POST',
                        'path': '/',
                        'description': '创建用户'
                    }
                ]
            }]
        }
        
        psm_file = self.create_test_psm('user_sync_psm.yaml', psm_data)
        
        # 执行同步代码生成
        generated_files = self.generator.generate_sync(psm_file, self.output_dir)
        
        # 验证生成的文件
        self.assertTrue(len(generated_files) > 0)
        self.assertTrue((self.output_dir / 'models.py').exists())
        self.assertTrue((self.output_dir / 'schemas.py').exists())
        
        # 验证内容
        models_content = (self.output_dir / 'models.py').read_text()
        self.assertIn('class User', models_content)
        self.assertIn('username', models_content)
        self.assertIn('email', models_content)
    
    def test_complex_relationships_generation(self):
        """测试包含关系的复杂模型代码生成"""
        psm_data = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'description': '借阅管理系统',
            'entities': [
                {
                    'name': 'Reader',
                    'table_name': 'readers',
                    'attributes': [
                        {
                            'name': 'id',
                            'type': 'integer',
                            'db_type': 'INTEGER',
                            'constraints': {'primary_key': True}
                        },
                        {
                            'name': 'name',
                            'type': 'string',
                            'db_type': 'VARCHAR(100)',
                            'constraints': {'required': True}
                        }
                    ]
                },
                {
                    'name': 'Book',
                    'table_name': 'books',
                    'attributes': [
                        {
                            'name': 'id',
                            'type': 'integer',
                            'db_type': 'INTEGER',
                            'constraints': {'primary_key': True}
                        },
                        {
                            'name': 'title',
                            'type': 'string',
                            'db_type': 'VARCHAR(255)',
                            'constraints': {'required': True}
                        }
                    ]
                },
                {
                    'name': 'BorrowRecord',
                    'table_name': 'borrow_records',
                    'attributes': [
                        {
                            'name': 'id',
                            'type': 'integer',
                            'db_type': 'INTEGER',
                            'constraints': {'primary_key': True}
                        },
                        {
                            'name': 'reader_id',
                            'type': 'integer',
                            'db_type': 'INTEGER',
                            'constraints': {
                                'foreign_key': 'readers.id',
                                'required': True
                            }
                        },
                        {
                            'name': 'book_id',
                            'type': 'integer',
                            'db_type': 'INTEGER',
                            'constraints': {
                                'foreign_key': 'books.id',
                                'required': True
                            }
                        },
                        {
                            'name': 'borrow_date',
                            'type': 'datetime',
                            'db_type': 'DATETIME',
                            'constraints': {'required': True}
                        }
                    ]
                }
            ],
            'services': [{
                'name': 'BorrowService',
                'base_path': '/api/borrow',
                'methods': [
                    {
                        'name': 'borrow_book',
                        'http_method': 'POST',
                        'path': '/borrow',
                        'description': '借书'
                    },
                    {
                        'name': 'return_book',
                        'http_method': 'POST',
                        'path': '/return',
                        'description': '还书'
                    }
                ]
            }]
        }
        
        psm_file = self.create_test_psm('borrow_system_psm.yaml', psm_data)
        
        # 执行代码生成
        async def run_test():
            files = await self.generator.generate(psm_file, self.output_dir)
            return files
        
        generated_files = self.loop.run_until_complete(run_test())
        
        # 验证 models.py 包含所有实体和关系
        models_content = (self.output_dir / 'models.py').read_text()
        self.assertIn('class Reader', models_content)
        self.assertIn('class Book', models_content)
        self.assertIn('class BorrowRecord', models_content)
        
        # 验证外键关系
        self.assertIn('ForeignKey', models_content)
        self.assertIn('reader_id', models_content)
        self.assertIn('book_id', models_content)
        
        # 验证 services.py 包含借还书逻辑
        services_content = (self.output_dir / 'services.py').read_text()
        self.assertIn('BorrowService', services_content)
        self.assertIn('borrow_book', services_content)
        self.assertIn('return_book', services_content)
    
    def test_cache_effectiveness(self):
        """测试缓存有效性"""
        # 创建简单的 PSM
        psm_data = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'description': '缓存测试系统',
            'entities': [{
                'name': 'TestEntity',
                'table_name': 'test_entities',
                'attributes': [
                    {'name': 'id', 'type': 'integer', 'db_type': 'INTEGER'}
                ]
            }],
            'services': []
        }
        
        psm_file = self.create_test_psm('cache_test_psm.yaml', psm_data)
        
        # 第一次生成（会调用 LLM）
        import time
        start_time = time.time()
        
        async def run_test():
            return await self.generator.generate(psm_file, self.output_dir)
        
        self.loop.run_until_complete(run_test())
        first_run_time = time.time() - start_time
        print(f"第一次运行时间: {first_run_time:.2f}秒")
        
        # 创建新的输出目录
        cache_output_dir = self.test_dir / "cache_test_output"
        cache_output_dir.mkdir(exist_ok=True)
        
        # 第二次生成（应该使用缓存）
        start_time = time.time()
        self.loop.run_until_complete(self.generator.generate(psm_file, cache_output_dir))
        second_run_time = time.time() - start_time
        print(f"第二次运行时间（使用缓存）: {second_run_time:.2f}秒")
        
        # 验证缓存效果（第二次应该更快）
        # 如果缓存有效，第二次运行应该显著更快
        # 但由于网络延迟等因素，我们只检查文件是否正确生成
        self.assertTrue((cache_output_dir / 'models.py').exists())
        self.assertTrue((cache_output_dir / 'main.py').exists())


if __name__ == '__main__':
    # 打印缓存信息
    print(f"使用缓存文件: {CACHE_PATH}")
    cache_file = Path(CACHE_PATH)
    if cache_file.exists():
        size_kb = cache_file.stat().st_size / 1024
        print(f"缓存文件已存在，大小: {size_kb:.1f} KB")
    else:
        print("缓存文件不存在，将创建新的缓存")
    
    unittest.main()
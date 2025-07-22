"""Test PSM to Code generator with real Gemini CLI"""

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

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from converters.psm_to_code_gemini import PSMtoCodeGeminiGenerator


class TestPSMtoCodeGeminiGenerator(unittest.TestCase):
    """测试 PSM to Code 生成器"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.generator = PSMtoCodeGeminiGenerator()
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
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "需要设置 GEMINI_API_KEY 环境变量")
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
            'requirements.txt'
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
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "需要设置 GEMINI_API_KEY 环境变量")
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
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "需要设置 GEMINI_API_KEY 环境变量")
    def test_api_endpoints_generation(self):
        """测试 API 端点生成"""
        psm_data = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'entities': [{
                'name': 'User',
                'table_name': 'users',
                'attributes': [
                    {'name': 'id', 'type': 'integer', 'db_type': 'INTEGER'},
                    {'name': 'username', 'type': 'string', 'db_type': 'VARCHAR(50)'},
                    {'name': 'email', 'type': 'string', 'db_type': 'VARCHAR(100)'}
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
                    },
                    {
                        'name': 'get_user',
                        'http_method': 'GET',
                        'path': '/{id}',
                        'description': '获取用户'
                    },
                    {
                        'name': 'update_user',
                        'http_method': 'PUT',
                        'path': '/{id}',
                        'description': '更新用户'
                    },
                    {
                        'name': 'delete_user',
                        'http_method': 'DELETE',
                        'path': '/{id}',
                        'description': '删除用户'
                    }
                ]
            }]
        }
        
        psm_file = self.create_test_psm('user_api_psm.yaml', psm_data)
        
        # 执行代码生成
        async def run_test():
            files = await self.generator.generate(psm_file, self.output_dir)
            return files
        
        generated_files = self.loop.run_until_complete(run_test())
        
        # 验证 api.py 包含所有 CRUD 端点
        api_content = (self.output_dir / 'api.py').read_text()
        self.assertIn('@router.post', api_content)
        self.assertIn('@router.get', api_content)
        self.assertIn('@router.put', api_content)
        self.assertIn('@router.delete', api_content)
        
        # 验证路径参数
        self.assertIn('{id}', api_content)
        
        # 验证 main.py 包含路由注册
        main_content = (self.output_dir / 'main.py').read_text()
        self.assertIn('FastAPI', main_content)
        self.assertIn('include_router', main_content)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "需要设置 GEMINI_API_KEY 环境变量")
    def test_configuration_files_generation(self):
        """测试配置文件生成"""
        psm_data = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'description': '测试系统',
            'entities': [{
                'name': 'Test',
                'table_name': 'tests',
                'attributes': [
                    {'name': 'id', 'type': 'integer', 'db_type': 'INTEGER'}
                ]
            }],
            'services': []
        }
        
        psm_file = self.create_test_psm('config_test_psm.yaml', psm_data)
        
        # 执行代码生成
        async def run_test():
            files = await self.generator.generate(psm_file, self.output_dir)
            return files
        
        self.loop.run_until_complete(run_test())
        
        # 验证配置文件
        self.assertTrue((self.output_dir / '.env').exists())
        self.assertTrue((self.output_dir / 'docker-compose.yml').exists())
        self.assertTrue((self.output_dir / 'Dockerfile').exists())
        
        # 验证 .env 内容
        env_content = (self.output_dir / '.env').read_text()
        self.assertIn('DATABASE_URL', env_content)
        self.assertIn('SECRET_KEY', env_content)
        
        # 验证 docker-compose.yml
        docker_compose_content = (self.output_dir / 'docker-compose.yml').read_text()
        self.assertIn('services:', docker_compose_content)
        self.assertIn('postgres', docker_compose_content)
        
        # 验证 requirements.txt
        requirements_content = (self.output_dir / 'requirements.txt').read_text()
        self.assertIn('fastapi', requirements_content)
        self.assertIn('sqlalchemy', requirements_content)
        self.assertIn('uvicorn', requirements_content)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "需要设置 GEMINI_API_KEY 环境变量")
    def test_business_logic_generation(self):
        """测试业务逻辑代码生成"""
        psm_data = {
            'platform': 'fastapi',
            'version': '1.0.0',
            'entities': [{
                'name': 'Product',
                'table_name': 'products',
                'attributes': [
                    {'name': 'id', 'type': 'integer', 'db_type': 'INTEGER'},
                    {'name': 'name', 'type': 'string', 'db_type': 'VARCHAR(100)'},
                    {'name': 'price', 'type': 'decimal', 'db_type': 'DECIMAL(10,2)'},
                    {'name': 'stock', 'type': 'integer', 'db_type': 'INTEGER'}
                ]
            }],
            'services': [{
                'name': 'ProductService',
                'base_path': '/api/products',
                'methods': [
                    {
                        'name': 'check_stock',
                        'http_method': 'GET',
                        'path': '/{id}/stock',
                        'description': '检查库存',
                        'implementation_notes': '如果库存小于10，返回警告'
                    },
                    {
                        'name': 'update_stock',
                        'http_method': 'PUT',
                        'path': '/{id}/stock',
                        'description': '更新库存',
                        'implementation_notes': '库存不能为负数'
                    }
                ]
            }]
        }
        
        psm_file = self.create_test_psm('product_logic_psm.yaml', psm_data)
        
        # 执行代码生成
        async def run_test():
            files = await self.generator.generate(psm_file, self.output_dir)
            return files
        
        self.loop.run_until_complete(run_test())
        
        # 验证业务逻辑
        services_content = (self.output_dir / 'services.py').read_text()
        
        # 应该包含库存检查逻辑
        self.assertIn('stock', services_content.lower())
        # 应该包含验证逻辑（虽然具体实现依赖于 Gemini 的生成）
        self.assertTrue(
            'ProductService' in services_content,
            "应该包含 ProductService 类"
        )


if __name__ == '__main__':
    unittest.main()
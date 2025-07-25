"""PIM to PSM generator using DeepSeek LLM"""

import os
import yaml
import re
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import SecretStr


def generate_psm(pim: str) -> str:
    """
    Generate Platform Specific Model (PSM) from Platform Independent Model (PIM)
    
    Args:
        pim: PIM content in YAML or text format
        
    Returns:
        PSM content in YAML format
    """
    # Load environment variables
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    # Get API key
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
    
    # Create DeepSeek instance
    llm = ChatOpenAI(
        temperature=0,
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key=SecretStr(api_key)
    )
    
    # Create system message
    system_message = SystemMessage(content="""你是一个模型驱动架构（MDA）专家。你的任务是将平台无关模型（PIM）转换为平台特定模型（PSM）。

转换规则：
1. 理解中文业务描述，推断合适的技术实现
2. 根据业务含义选择合适的数据类型和约束
3. 生成符合平台最佳实践的技术规范
4. 为每个服务方法生成单元测试用例
5. 输出格式必须是有效的 YAML，不要包含其他内容

PSM 必须包含以下字段：
- platform: 目标平台（默认 fastapi）
- version: 版本号（默认 1.0.0）
- description: 系统描述
- entities: 实体定义列表
- services: 服务定义列表
- flows: 流程定义（包含技术实现细节）
- configurations: 平台特定配置
- unit_tests: 单元测试定义列表

实体定义格式：
```yaml
entities:
  - name: EntityName
    table_name: entity_names
    description: 实体描述
    attributes:
      - name: id
        type: integer
        db_type: INTEGER
        constraints:
          primary_key: true
          auto_increment: true
      - name: field_name
        type: string
        db_type: VARCHAR(255)
        constraints:
          required: true
          unique: false
      - name: created_at
        type: datetime
        db_type: TIMESTAMP
        constraints:
          default: CURRENT_TIMESTAMP
      - name: updated_at
        type: datetime
        db_type: TIMESTAMP
        constraints:
          default: CURRENT_TIMESTAMP
          on_update: CURRENT_TIMESTAMP
```

服务定义格式：
```yaml
services:
  - name: EntityService
    base_path: /api/entities
    description: 服务描述
    methods:
      - name: create
        http_method: POST
        path: /
        description: 创建实体
        request:
          type: EntityCreateRequest
          validation_rules:
            - field_name: required, min_length(1)
        response:
          type: EntityResponse
          status_code: 201
        implementation_notes: |
          1. 验证输入数据
          2. 检查业务规则
          3. 保存到数据库
          4. 返回创建的实体
      - name: list
        http_method: GET
        path: /
        description: 获取实体列表
        request:
          query_params:
            - name: page
              type: integer
              default: 1
            - name: page_size
              type: integer
              default: 20
        response:
          type: EntityListResponse
          status_code: 200
      - name: get
        http_method: GET
        path: /{id}
        description: 获取单个实体
        path_params:
          - name: id
            type: integer
        response:
          type: EntityResponse
          status_code: 200
      - name: update
        http_method: PUT
        path: /{id}
        description: 更新实体
        path_params:
          - name: id
            type: integer
        request:
          type: EntityUpdateRequest
        response:
          type: EntityResponse
          status_code: 200
      - name: delete
        http_method: DELETE
        path: /{id}
        description: 删除实体
        path_params:
          - name: id
            type: integer
        response:
          type: null
          status_code: 204
```

数据类型映射规则：
- 文本类：string -> VARCHAR(255), text -> TEXT
- 数字类：integer -> INTEGER, float -> FLOAT, decimal -> DECIMAL(10,2)
- 金额：使用 DECIMAL(10,2)
- 日期时间：date -> DATE, datetime -> TIMESTAMP
- 布尔：boolean -> BOOLEAN
- 枚举：enum -> VARCHAR(50) with CHECK constraint
- 邮箱：email -> VARCHAR(255) with email validation
- 电话：phone -> VARCHAR(20)
- URL：url -> VARCHAR(500)
- UUID：uuid -> CHAR(36)

单元测试定义格式：
```yaml
unit_tests:
  - name: test_create_entity_success
    service: EntityService
    method: create
    description: 测试成功创建实体
    test_cases:
      - name: 创建有效实体
        arrange:
          input_data:
            field_name: "Test Entity"
        act:
          method: create
          data: "{{ input_data }}"
        assert:
          status_code: 201
          response:
            field_name: "Test Entity"
            id: "{{ any_integer }}"
      
  - name: test_create_entity_validation_error
    service: EntityService
    method: create
    description: 测试创建实体时的验证错误
    test_cases:
      - name: 缺少必填字段
        arrange:
          input_data: {}
        act:
          method: create
          data: "{{ input_data }}"
        assert:
          status_code: 422
          error_type: ValidationError
          
  - name: test_get_entity_by_id
    service: EntityService
    method: get
    description: 测试根据ID获取实体
    test_cases:
      - name: 获取存在的实体
        arrange:
          entity_id: 1
          mock_data:
            id: 1
            field_name: "Test Entity"
        act:
          method: get
          path_params:
            id: "{{ entity_id }}"
        assert:
          status_code: 200
          response: "{{ mock_data }}"
      - name: 获取不存在的实体
        arrange:
          entity_id: 9999
        act:
          method: get
          path_params:
            id: "{{ entity_id }}"
        assert:
          status_code: 404
          error_type: NotFoundError
          
  - name: test_list_entities_pagination
    service: EntityService
    method: list
    description: 测试实体列表分页
    test_cases:
      - name: 获取第一页
        arrange:
          page: 1
          page_size: 10
        act:
          method: list
          query_params:
            page: "{{ page }}"
            page_size: "{{ page_size }}"
        assert:
          status_code: 200
          response:
            total: "{{ any_integer }}"
            page: 1
            page_size: 10
            items: "{{ list_of_entities }}"
```

请确保：
1. 所有中文名称都转换为合适的英文标识符（使用下划线命名法）
2. 每个实体都包含 id, created_at, updated_at 字段
3. 服务包含完整的 CRUD 操作（create, list, get, update, delete）
4. 添加必要的索引和约束
5. 服务方法符合 RESTful 规范
6. 为每个服务方法生成至少2个测试用例（正常情况和异常情况）
7. 测试用例要包含 arrange（准备）、act（执行）、assert（断言）三个阶段
8. 测试用例要覆盖主要的业务场景和边界条件

只输出 YAML 内容，不要包含 markdown 代码块标记或其他解释。""")
    
    # Create human message
    human_message = HumanMessage(content=f"""请将以下 PIM 模型转换为 fastapi 平台的 PSM：

{pim}""")
    
    # Create message list
    messages = [system_message, human_message]
    
    try:
        # Invoke the model
        result = llm.invoke(messages)
        
        # Extract content
        psm_content = str(result.content).strip()
        
        # Remove markdown code blocks if present
        if psm_content.startswith("```yaml"):
            yaml_match = re.search(r'```yaml\n(.*?)\n```', psm_content, re.DOTALL)
            if yaml_match:
                psm_content = yaml_match.group(1)
        elif psm_content.startswith("```"):
            code_match = re.search(r'```\n(.*?)\n```', psm_content, re.DOTALL)
            if code_match:
                psm_content = code_match.group(1)
        
        # Validate YAML
        try:
            psm_data = yaml.safe_load(psm_content)
            # Check required fields
            required_fields = ['platform', 'entities', 'services']
            for field in required_fields:
                if field not in psm_data:
                    raise ValueError(f"Missing required field: {field}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in generated PSM: {e}")
        
        return psm_content
        
    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        # Wrap other exceptions as RuntimeError
        raise RuntimeError(f"Failed to generate PSM: {str(e)}")


if __name__ == "__main__":
    # Test with a simple PIM
    test_pim = """
domain: user-management
version: 1.0.0
description: 用户管理系统

entities:
  - name: 用户
    attributes:
      - name: 邮箱
        type: email
        unique: true
        required: true
      - name: 姓名
        type: string
        required: true
      - name: 密码
        type: string
        required: true
      - name: 状态
        type: enum
        values: [活跃, 禁用]
        default: 活跃

services:
  - name: 用户服务
    operations:
      - 注册用户
      - 登录
      - 更新用户信息
      - 获取用户列表
"""
    
    try:
        psm = generate_psm(test_pim)
        print("Generated PSM:")
        print(psm)
        
        # Save to file
        with open("generated_psm.yaml", "w", encoding="utf-8") as f:
            f.write(psm)
        print("\nPSM saved to generated_psm.yaml")
        
    except Exception as e:
        print(f"Error: {e}")
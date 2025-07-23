"""PIM to PSM converter using DeepSeek"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import SecretStr

logger = logging.getLogger(__name__)


class PIMtoPSMDeepSeekConverter:
    """使用 DeepSeek 将 PIM 转换为 PSM"""
    
    def __init__(self):
        # 加载项目的 .env 文件
        project_root = Path(__file__).parent.parent.parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded .env from: {env_file}")
        
        # 初始化 DeepSeek LLM
        api_key = os.getenv('DEEPSEEK_API_KEY')
        self.llm = ChatOpenAI(
            temperature=0,
            model="deepseek-chat",  
            base_url="https://api.deepseek.com",
            api_key=SecretStr(api_key) if api_key else None
        )
    
    async def convert(self, pim_file: Path, platform: str = "fastapi") -> Dict[str, Any]:
        """将 PIM 模型转换为 PSM"""
        
        # 读取 PIM 内容
        pim_content = pim_file.read_text(encoding='utf-8')
        
        # 构建转换提示
        messages = self._build_conversion_messages(pim_content, platform)
        
        # 调用 DeepSeek
        result = await self.llm.ainvoke(messages)
        
        # 解析结果
        psm_data = self._parse_deepseek_response(str(result.content))
        
        # 保存 PSM 文件
        psm_file = pim_file.parent / f"{pim_file.stem}_psm_{platform}.yaml"
        with open(psm_file, 'w', encoding='utf-8') as f:
            yaml.dump(psm_data, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"PSM saved to: {psm_file}")
        return psm_data
    
    def convert_sync(self, pim_file: Path, platform: str = "fastapi") -> Dict[str, Any]:
        """同步版本的 PIM 转换"""
        
        # 读取 PIM 内容
        pim_content = pim_file.read_text(encoding='utf-8')
        
        # 构建转换提示
        messages = self._build_conversion_messages(pim_content, platform)
        
        # 调用 DeepSeek
        result = self.llm.invoke(messages)
        
        # 解析结果
        psm_data = self._parse_deepseek_response(str(result.content))
        
        # 保存 PSM 文件
        psm_file = pim_file.parent / f"{pim_file.stem}_psm_{platform}.yaml"
        with open(psm_file, 'w', encoding='utf-8') as f:
            yaml.dump(psm_data, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"PSM saved to: {psm_file}")
        return psm_data
    
    def _build_conversion_messages(self, pim_content: str, platform: str) -> list:
        """构建 DeepSeek 消息列表"""
        
        system_prompt = """你是一个模型驱动架构（MDA）专家。你的任务是将平台无关模型（PIM）转换为平台特定模型（PSM）。

转换规则：
1. 理解中文业务描述，推断合适的技术实现
2. 根据业务含义选择合适的数据类型和约束
3. 生成符合平台最佳实践的技术规范
4. 输出格式必须是有效的 YAML，不要包含其他内容"""

        user_prompt = f"""请将以下 PIM 模型转换为 {platform} 平台的 PSM：

{pim_content}

输出 PSM 必须包含：
- platform: {platform}
- version: 1.0.0
- description: 系统描述
- entities: 实体定义列表
- services: 服务定义列表
- flows: 流程定义（包含技术实现细节）
- configurations: 平台特定配置

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
```

请确保：
1. 所有中文名称都转换为合适的英文标识符
2. 选择适合的数据类型（如金额用 DECIMAL，日期用 DATE 等）
3. 添加必要的索引和约束
4. 包含 created_at 和 updated_at 时间戳字段
5. 服务方法符合 RESTful 规范

只输出 YAML 内容，不要有其他解释。"""

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
    
    def _parse_deepseek_response(self, response: str) -> Dict[str, Any]:
        """解析 DeepSeek 响应，提取 YAML 内容"""
        # 查找 YAML 代码块
        import re
        
        # 尝试找到 ```yaml 代码块
        yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
        else:
            # 如果没有代码块标记，假设整个响应都是 YAML
            yaml_content = response.strip()
        
        try:
            # 解析 YAML
            psm_data = yaml.safe_load(yaml_content)
            
            # 验证必要字段
            required_fields = ['platform', 'entities', 'services']
            for field in required_fields:
                if field not in psm_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return psm_data
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid YAML in DeepSeek response: {e}")


async def convert_pim_to_psm(pim_file: Path, platform: str = "fastapi") -> Path:
    """便捷函数：转换 PIM 到 PSM"""
    converter = PIMtoPSMDeepSeekConverter()
    psm_data = await converter.convert(pim_file, platform)
    psm_file = pim_file.parent / f"{pim_file.stem}_psm_{platform}.yaml"
    return psm_file


def convert_pim_to_psm_sync(pim_file: Path, platform: str = "fastapi") -> Path:
    """同步版本的便捷函数：转换 PIM 到 PSM"""
    converter = PIMtoPSMDeepSeekConverter()
    psm_data = converter.convert_sync(pim_file, platform)
    psm_file = pim_file.parent / f"{pim_file.stem}_psm_{platform}.yaml"
    return psm_file


if __name__ == "__main__":
    # 测试转换
    import sys
    import asyncio
    
    if len(sys.argv) < 2:
        print("Usage: python pim_to_psm_deepseek.py <pim_file> [platform]")
        sys.exit(1)
    
    pim_file = Path(sys.argv[1])
    platform = sys.argv[2] if len(sys.argv) > 2 else "fastapi"
    
    async def main():
        try:
            psm_file = await convert_pim_to_psm(pim_file, platform)
            print(f"✅ PSM generated: {psm_file}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(main())
"""OpenAI Function Schema for Semantic Memory Tools"""

SEMANTIC_MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_semantic_memory",
            "description": "写入或更新语义记忆（agent.md）文件，用于存储模块的核心知识、设计模式和注意事项",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "目录路径，如果为空则使用当前目录"
                    },
                    "content": {
                        "type": "string", 
                        "description": "要写入的内容，如果为空则生成默认模板"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "是否追加模式（默认为覆盖模式）",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_semantic_memory",
            "description": "读取语义记忆（agent.md）文件，支持级联读取当前目录和父目录的agent.md",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "目录路径，如果为空则使用当前目录"
                    }
                },
                "required": []
            }
        }
    }
]

# 如果需要单独的函数定义（兼容旧版OpenAI API）
SEMANTIC_MEMORY_FUNCTIONS = [
    {
        "name": "write_semantic_memory",
        "description": "写入或更新语义记忆（agent.md）文件，用于存储模块的核心知识、设计模式和注意事项",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": ["string", "null"],
                    "description": "目录路径，如果为null则使用当前目录"
                },
                "content": {
                    "type": ["string", "null"],
                    "description": "要写入的内容，如果为null则生成默认模板"
                },
                "append": {
                    "type": "boolean",
                    "description": "是否追加模式（默认为覆盖模式）",
                    "default": False
                }
            },
            "required": []
        }
    },
    {
        "name": "read_semantic_memory",
        "description": "读取语义记忆（agent.md）文件，支持级联读取当前目录和父目录的agent.md",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": ["string", "null"],
                    "description": "目录路径，如果为null则使用当前目录"
                }
            },
            "required": []
        }
    }
]

# 使用示例
"""
from openai import OpenAI
from semantic_memory_schema import SEMANTIC_MEMORY_TOOLS

client = OpenAI()

# 在API调用中使用
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "帮我保存这个模块的知识"}],
    tools=SEMANTIC_MEMORY_TOOLS,
    tool_choice="auto"
)

# 处理工具调用
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "write_semantic_memory":
            args = json.loads(tool_call.function.arguments)
            result = write_semantic_memory(**args)
        elif tool_call.function.name == "read_semantic_memory":
            args = json.loads(tool_call.function.arguments)
            result = read_semantic_memory(**args)
"""
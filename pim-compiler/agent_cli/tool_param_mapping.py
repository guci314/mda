"""
工具参数映射配置
解决 LangChain 工具参数名称与 Agent 期望参数不一致的问题
"""

# 工具参数映射表
TOOL_PARAM_MAPPING = {
    "write_file": {
        "filename": "path",      # filename -> path
        "file_path": "path",     # file_path -> path
        "content": "content"     # content 保持不变
    },
    "read_file": {
        "filename": "path",      # filename -> path
        "file_path": "path"      # file_path -> path
    },
    "python_repl": {
        "command": "code"        # command -> code
    }
}

def map_tool_params(tool_name: str, params: dict) -> dict:
    """
    将 Agent 生成的参数映射到 LangChain 工具需要的参数
    
    Args:
        tool_name: 工具名称
        params: 原始参数字典
        
    Returns:
        映射后的参数字典
    """
    if tool_name not in TOOL_PARAM_MAPPING:
        return params
    
    mapping = TOOL_PARAM_MAPPING[tool_name]
    mapped_params = {}
    
    for old_key, value in params.items():
        # 查找映射
        new_key = mapping.get(old_key, old_key)
        mapped_params[new_key] = value
    
    return mapped_params
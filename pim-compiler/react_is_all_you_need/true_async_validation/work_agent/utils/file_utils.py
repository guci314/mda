"""
文件处理工具库
提供常用的文件处理函数
"""

import os
import json
import pickle
from typing import Any, List, Optional, Union
from pathlib import Path


def read_file(file_path: Union[str, Path]) -> str:
    """
    读取文件内容为字符串
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件内容
        
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 读取文件时发生错误
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"文件未找到: {file_path}")
    except Exception as e:
        raise IOError(f"读取文件时发生错误: {e}")


def write_file(file_path: Union[str, Path], content: str) -> None:
    """
    将内容写入文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        
    Raises:
        IOError: 写入文件时发生错误
    """
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"写入文件时发生错误: {e}")


def append_to_file(file_path: Union[str, Path], content: str) -> None:
    """
    追加内容到文件末尾
    
    Args:
        file_path: 文件路径
        content: 要追加的内容
        
    Raises:
        IOError: 追加内容时发生错误
    """
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"追加内容到文件时发生错误: {e}")


def read_lines(file_path: Union[str, Path]) -> List[str]:
    """
    读取文件内容为行列表
    
    Args:
        file_path: 文件路径
        
    Returns:
        List[str]: 文件内容的行列表
        
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 读取文件时发生错误
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f.readlines()]
    except FileNotFoundError:
        raise FileNotFoundError(f"文件未找到: {file_path}")
    except Exception as e:
        raise IOError(f"读取文件时发生错误: {e}")


def write_lines(file_path: Union[str, Path], lines: List[str]) -> None:
    """
    将行列表写入文件
    
    Args:
        file_path: 文件路径
        lines: 要写入的行列表
        
    Raises:
        IOError: 写入文件时发生错误
    """
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')
    except Exception as e:
        raise IOError(f"写入文件时发生错误: {e}")


def file_exists(file_path: Union[str, Path]) -> bool:
    """
    检查文件是否存在
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件存在返回True，否则返回False
    """
    return Path(file_path).exists()


def delete_file(file_path: Union[str, Path]) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 删除成功返回True，否则返回False
    """
    try:
        if file_exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小（字节），文件不存在返回-1
        
    Examples:
        >>> size = get_file_size("example.txt")
        >>> print(f"文件大小: {size} 字节")
    """
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        return -1


def read_json(file_path: Union[str, Path]) -> Any:
    """
    读取JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        Any: JSON解析后的数据
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON格式错误
        IOError: 读取文件时发生错误
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件未找到: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON格式错误: {e}", e.doc, e.pos)
    except Exception as e:
        raise IOError(f"读取文件时发生错误: {e}")


def write_json(file_path: Union[str, Path], data: Any, indent: int = 2) -> None:
    """
    将数据写入JSON文件
    
    Args:
        file_path: JSON文件路径
        data: 要写入的数据
        indent: JSON缩进空格数
        
    Raises:
        IOError: 写入文件时发生错误
    """
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    except Exception as e:
        raise IOError(f"写入JSON文件时发生错误: {e}")


def read_pickle(file_path: Union[str, Path]) -> Any:
    """
    读取pickle文件
    
    Args:
        file_path: pickle文件路径
        
    Returns:
        Any: 反序列化后的对象
        
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 读取文件时发生错误
    """
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件未找到: {file_path}")
    except Exception as e:
        raise IOError(f"读取pickle文件时发生错误: {e}")


def write_pickle(file_path: Union[str, Path], obj: Any) -> None:
    """
    将对象序列化写入pickle文件
    
    Args:
        file_path: pickle文件路径
        obj: 要序列化的对象
        
    Raises:
        IOError: 写入文件时发生错误
    """
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            pickle.dump(obj, f)
    except Exception as e:
        raise IOError(f"写入pickle文件时发生错误: {e}")
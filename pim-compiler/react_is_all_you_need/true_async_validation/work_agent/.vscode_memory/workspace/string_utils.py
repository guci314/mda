"""
字符串处理工具库
提供常用的字符串处理函数
"""

import re
from typing import List, Optional


def is_empty(s: Optional[str]) -> bool:
    """
    检查字符串是否为空或None
    
    Args:
        s: 待检查的字符串
        
    Returns:
        bool: 如果字符串为空或None返回True，否则返回False
        
    Examples:
        >>> is_empty(None)
        True
        >>> is_empty("")
        True
        >>> is_empty(" ")
        False
        >>> is_empty("hello")
        False
    """
    return s is None or len(s) == 0


def is_blank(s: Optional[str]) -> bool:
    """
    检查字符串是否为空白（空、None或只包含空白字符）
    
    Args:
        s: 待检查的字符串
        
    Returns:
        bool: 如果字符串为空白返回True，否则返回False
        
    Examples:
        >>> is_blank(None)
        True
        >>> is_blank("")
        True
        >>> is_blank(" ")
        True
        >>> is_blank("\\t\\n")
        True
        >>> is_blank("hello")
        False
    """
    return s is None or len(s.strip()) == 0


def capitalize_first(s: str) -> str:
    """
    将字符串的第一个字符大写
    
    Args:
        s: 待处理的字符串
        
    Returns:
        str: 首字符大写的字符串
        
    Examples:
        >>> capitalize_first("hello")
        'Hello'
        >>> capitalize_first("HELLO")
        'HELLO'
        >>> capitalize_first("")
        ''
    """
    if is_empty(s):
        return s
    return s[0].upper() + s[1:]


def camel_to_snake(name: str) -> str:
    """
    将驼峰命名转换为下划线命名
    
    Args:
        name: 驼峰命名的字符串
        
    Returns:
        str: 下划线命名的字符串
        
    Examples:
        >>> camel_to_snake("camelCase")
        'camel_case'
        >>> camel_to_snake("HTMLParser")
        'html_parser'
        >>> camel_to_snake("XMLHttpRequest")
        'xml_http_request'
    """
    # 在大写字母前插入下划线，但不在字符串开头
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 在小写字母后跟大写字母前插入下划线
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """
    将下划线命名转换为驼峰命名
    
    Args:
        name: 下划线命名的字符串
        
    Returns:
        str: 驼峰命名的字符串
        
    Examples:
        >>> snake_to_camel("snake_case")
        'snakeCase'
        >>> snake_to_camel("xml_http_request")
        'xmlHttpRequest'
    """
    components = name.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def remove_prefix(s: str, prefix: str) -> str:
    """
    移除字符串的指定前缀
    
    Args:
        s: 原始字符串
        prefix: 要移除的前缀
        
    Returns:
        str: 移除前缀后的字符串
        
    Examples:
        >>> remove_prefix("unhappy", "un")
        'happy'
        >>> remove_prefix("hello", "xyz")
        'hello'
    """
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def remove_suffix(s: str, suffix: str) -> str:
    """
    移除字符串的指定后缀
    
    Args:
        s: 原始字符串
        suffix: 要移除的后缀
        
    Returns:
        str: 移除后缀后的字符串
        
    Examples:
        >>> remove_suffix("happiness", "ness")
        'happy'
        >>> remove_suffix("hello", "xyz")
        'hello'
    """
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串到指定长度
    
    Args:
        s: 原始字符串
        max_length: 最大长度
        suffix: 截断后添加的后缀
        
    Returns:
        str: 截断后的字符串
        
    Examples:
        >>> truncate("This is a long string", 10)
        'This is a...'
        >>> truncate("Short", 10)
        'Short'
    """
    if len(s) <= max_length:
        return s
    suffix_len = len(suffix)
    if suffix_len >= max_length:
        return suffix[:max_length]
    return s[:max_length - suffix_len] + suffix


def split_by_multiple_separators(s: str, separators: List[str]) -> List[str]:
    """
    使用多个分隔符分割字符串
    
    Args:
        s: 待分割的字符串
        separators: 分隔符列表
        
    Returns:
        List[str]: 分割后的字符串列表
        
    Examples:
        >>> split_by_multiple_separators("a,b;c:d", [",", ";", ":"])
        ['a', 'b', 'c', 'd']
    """
    import re
    pattern = '|'.join(re.escape(sep) for sep in separators)
    return re.split(pattern, s)
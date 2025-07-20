"""日志切面 - 纯技术关注点，与业务逻辑无关"""

import functools
import time
import json
from typing import Any, Callable
from datetime import datetime

from utils.logger import setup_logger


def log_aspect(
    level: str = "INFO",
    include_args: bool = True,
    include_result: bool = False,
    include_timing: bool = True
):
    """
    日志切面装饰器
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        include_args: 是否记录参数
        include_result: 是否记录返回值
        include_timing: 是否记录执行时间
    """
    def decorator(func: Callable) -> Callable:
        logger = setup_logger(func.__module__)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 构建日志上下文
            context = {
                "function": func.__name__,
                "module": func.__module__,
                "timestamp": datetime.now().isoformat()
            }
            
            if include_args:
                # 智能序列化参数（避免敏感信息）
                context["args"] = _sanitize_args(args)
                context["kwargs"] = _sanitize_kwargs(kwargs)
            
            # 前置日志
            logger.log(
                getattr(logger, level.lower()).__func__.__code__.co_consts[0],
                f"Executing {func.__name__}",
                extra={"context": context}
            )
            
            try:
                # 执行业务逻辑
                result = await func(*args, **kwargs)
                
                # 执行时间
                if include_timing:
                    context["duration_ms"] = (time.time() - start_time) * 1000
                
                if include_result:
                    context["result"] = _sanitize_result(result)
                
                # 成功日志
                logger.log(
                    getattr(logger, level.lower()).__func__.__code__.co_consts[0],
                    f"Completed {func.__name__}",
                    extra={"context": context}
                )
                
                return result
                
            except Exception as e:
                # 错误日志
                context["error"] = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "duration_ms": (time.time() - start_time) * 1000
                }
                
                logger.error(
                    f"Error in {func.__name__}",
                    extra={"context": context},
                    exc_info=True
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步版本的实现（类似逻辑）
            start_time = time.time()
            context = {
                "function": func.__name__,
                "module": func.__module__,
                "timestamp": datetime.now().isoformat()
            }
            
            if include_args:
                context["args"] = _sanitize_args(args)
                context["kwargs"] = _sanitize_kwargs(kwargs)
            
            logger.info(f"Executing {func.__name__}", extra={"context": context})
            
            try:
                result = func(*args, **kwargs)
                
                if include_timing:
                    context["duration_ms"] = (time.time() - start_time) * 1000
                
                if include_result:
                    context["result"] = _sanitize_result(result)
                
                logger.info(f"Completed {func.__name__}", extra={"context": context})
                return result
                
            except Exception as e:
                context["error"] = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "duration_ms": (time.time() - start_time) * 1000
                }
                
                logger.error(f"Error in {func.__name__}", extra={"context": context}, exc_info=True)
                raise
        
        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _sanitize_args(args: tuple) -> list:
    """清理参数，避免记录敏感信息"""
    sanitized = []
    for arg in args:
        if isinstance(arg, (str, int, float, bool, type(None))):
            sanitized.append(arg)
        elif hasattr(arg, '__dict__'):
            # 对象类型，只记录类名
            sanitized.append(f"<{type(arg).__name__}>")
        else:
            sanitized.append(f"<{type(arg).__name__}>")
    return sanitized


def _sanitize_kwargs(kwargs: dict) -> dict:
    """清理关键字参数，隐藏敏感字段"""
    sensitive_fields = {'password', 'token', 'secret', 'api_key', 'private_key'}
    sanitized = {}
    
    for key, value in kwargs.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            sanitized[key] = "***HIDDEN***"
        elif isinstance(value, (str, int, float, bool, type(None))):
            sanitized[key] = value
        else:
            sanitized[key] = f"<{type(value).__name__}>"
    
    return sanitized


def _sanitize_result(result: Any) -> Any:
    """清理返回值，避免记录敏感信息"""
    if isinstance(result, (str, int, float, bool, type(None))):
        return result
    elif isinstance(result, dict):
        return {k: "<value>" for k in result.keys()}
    elif isinstance(result, list):
        return f"<list[{len(result)}]>"
    else:
        return f"<{type(result).__name__}>"


# 导入异步支持
import asyncio
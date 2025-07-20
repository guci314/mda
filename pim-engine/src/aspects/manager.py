"""切面管理器 - 动态应用AOP切面保持业务纯洁性"""

import functools
import yaml
from typing import Dict, List, Callable, Any, Optional
from pathlib import Path

from utils.logger import setup_logger


class AspectManager:
    """
    切面管理器
    负责加载、配置和应用各种技术切面
    """
    
    def __init__(self, config_path: str = ".mda/aspects"):
        self.logger = setup_logger(__name__)
        self.config_path = Path(config_path)
        self.aspects = {}
        self.domain_aspects = {}
        self.loaded_decorators = {}
        
        # 加载内置切面装饰器
        self._load_builtin_aspects()
        
        # 加载配置
        self.load_configurations()
    
    def _load_builtin_aspects(self):
        """加载内置的切面装饰器"""
        from .logging import log_aspect
        from .security import security_aspect
        from .rate_limit import rate_limit_aspect
        from .cache import cache_aspect
        from .transaction import transaction_aspect
        from .monitoring import monitoring_aspect
        
        self.loaded_decorators = {
            "log_aspect": log_aspect,
            "security_aspect": security_aspect,
            "rate_limit_aspect": rate_limit_aspect,
            "cache_aspect": cache_aspect,
            "transaction_aspect": transaction_aspect,
            "monitoring_aspect": monitoring_aspect,
        }
    
    def load_configurations(self):
        """加载所有切面配置文件"""
        if not self.config_path.exists():
            self.logger.warning(f"Aspects config path not found: {self.config_path}")
            return
        
        # 加载默认配置
        default_config = self.config_path / "default.yaml"
        if default_config.exists():
            self._load_config_file(default_config, is_default=True)
        
        # 加载领域特定配置
        for config_file in self.config_path.glob("*.yaml"):
            if config_file.name != "default.yaml":
                self._load_config_file(config_file)
    
    def _load_config_file(self, config_file: Path, is_default: bool = False):
        """加载单个配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if is_default:
                self.aspects['default'] = config.get('aspects', {})
            else:
                domain = config_file.stem
                self.domain_aspects[domain] = config.get('aspects', {})
            
            self.logger.info(f"Loaded aspect configuration: {config_file.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load aspect config {config_file}: {e}")
    
    def apply_aspects(
        self, 
        func: Callable, 
        domain: Optional[str] = None,
        service: Optional[str] = None,
        method: Optional[str] = None
    ) -> Callable:
        """
        为函数应用配置的切面
        
        Args:
            func: 要包装的函数
            domain: 业务领域
            service: 服务名称
            method: 方法名称
        
        Returns:
            包装后的函数
        """
        # 收集要应用的切面配置
        aspect_configs = []
        
        # 1. 应用默认切面
        if 'default' in self.aspects:
            aspect_configs.extend(self._get_applicable_aspects(
                self.aspects['default'], 
                method or func.__name__
            ))
        
        # 2. 应用领域特定切面
        if domain and domain in self.domain_aspects:
            aspect_configs.extend(self._get_applicable_aspects(
                self.domain_aspects[domain],
                method or func.__name__
            ))
        
        # 3. 按顺序应用切面
        wrapped = func
        for aspect_config in reversed(aspect_configs):  # 反向应用保证执行顺序
            wrapped = self._apply_single_aspect(wrapped, aspect_config)
        
        return wrapped
    
    def _get_applicable_aspects(
        self, 
        aspects_config: Dict, 
        method_name: str
    ) -> List[Dict]:
        """获取适用于特定方法的切面配置"""
        applicable = []
        
        # 全局切面
        if 'all_methods' in aspects_config:
            applicable.extend(aspects_config['all_methods'])
        
        # 查询方法切面
        if method_name.startswith(('get', 'find', 'query', 'list')):
            if 'query_methods' in aspects_config:
                applicable.extend(aspects_config['query_methods'])
        
        # 变更方法切面
        if method_name.startswith(('create', 'update', 'delete', 'save')):
            if 'mutation_methods' in aspects_config:
                applicable.extend(aspects_config['mutation_methods'])
        
        # 特定方法切面
        if method_name in aspects_config:
            applicable.extend(aspects_config[method_name])
        
        return applicable
    
    def _apply_single_aspect(self, func: Callable, aspect_config: Dict) -> Callable:
        """应用单个切面"""
        aspect_type = aspect_config.get('type') or list(aspect_config.keys())[0]
        
        if aspect_type not in self.loaded_decorators:
            self.logger.warning(f"Unknown aspect type: {aspect_type}")
            return func
        
        # 获取装饰器和参数
        decorator = self.loaded_decorators[aspect_type]
        params = aspect_config.get(aspect_type, {})
        
        # 应用装饰器
        if isinstance(params, dict):
            return decorator(**params)(func)
        else:
            return decorator()(func)
    
    def create_domain_decorator(self, domain: str):
        """
        创建领域特定的装饰器
        
        Usage:
            @aspect_manager.create_domain_decorator("user-management")
            class UserService:
                pass
        """
        def class_decorator(cls):
            # 为类的所有方法应用切面
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    wrapped = self.apply_aspects(
                        attr,
                        domain=domain,
                        service=cls.__name__,
                        method=attr_name
                    )
                    setattr(cls, attr_name, wrapped)
            
            return cls
        
        return class_decorator
    
    def get_aspect_chain(
        self, 
        domain: str, 
        service: str, 
        method: str
    ) -> List[str]:
        """
        获取将要应用的切面链（用于调试）
        
        Returns:
            切面名称列表
        """
        aspect_configs = []
        
        if 'default' in self.aspects:
            aspect_configs.extend(self._get_applicable_aspects(
                self.aspects['default'], method
            ))
        
        if domain in self.domain_aspects:
            aspect_configs.extend(self._get_applicable_aspects(
                self.domain_aspects[domain], method
            ))
        
        return [
            list(config.keys())[0] for config in aspect_configs
        ]


# 全局实例
_aspect_manager = None


def get_aspect_manager() -> AspectManager:
    """获取全局切面管理器实例"""
    global _aspect_manager
    if _aspect_manager is None:
        _aspect_manager = AspectManager()
    return _aspect_manager


def apply_configured_aspects(domain: str):
    """
    便捷装饰器：应用配置的切面
    
    Usage:
        @apply_configured_aspects("user-management")
        class UserService:
            pass
    """
    manager = get_aspect_manager()
    return manager.create_domain_decorator(domain)
"""错误模式缓存机制"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class ErrorPattern:
    """错误模式定义"""
    pattern: str  # 正则表达式
    error_type: str  # 错误类型
    fix_template: str  # 修复模板
    description: str  # 描述
    success_rate: float = 1.0  # 成功率
    use_count: int = 0  # 使用次数
    last_used: Optional[str] = None  # 最后使用时间


@dataclass 
class CachedFix:
    """缓存的修复方案"""
    error_hash: str  # 错误内容的哈希
    fix_content: str  # 修复内容
    file_path: str  # 文件路径
    success: bool  # 是否成功
    timestamp: str  # 时间戳


class ErrorPatternCache:
    """错误模式缓存管理器"""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "pim-compiler"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.cache_dir / "error_patterns.json"
        self.fixes_file = self.cache_dir / "cached_fixes.json"
        
        self.patterns = self._load_patterns()
        self.fixes = self._load_fixes()
        
        # 初始化内置模式
        self._init_builtin_patterns()
    
    def _init_builtin_patterns(self):
        """初始化内置的错误模式"""
        builtin_patterns = [
            ErrorPattern(
                pattern=r"sqlalchemy\.exc\.InvalidRequestError.*async driver.*not async",
                error_type="async_driver_error",
                fix_template="""
# 修复异步驱动错误
# 将 create_engine 改为同步版本，或使用正确的异步驱动
# 例如：使用 asyncpg 代替 psycopg2
DATABASE_URL = "postgresql+asyncpg://..." # 使用异步驱动
# 或者使用同步引擎
from sqlalchemy import create_engine  # 不要用 create_async_engine
""",
                description="SQLAlchemy异步驱动配置错误"
            ),
            
            ErrorPattern(
                pattern=r'"Config" and "model_config" cannot be used together',
                error_type="pydantic_v2_config",
                fix_template="""
# 修复 Pydantic v2 配置错误
# 删除旧的 Config 类，使用 model_config
from pydantic import ConfigDict

class MyModel(BaseModel):
    # 删除 class Config:
    model_config = ConfigDict(from_attributes=True)
""",
                description="Pydantic v2配置冲突"
            ),
            
            ErrorPattern(
                pattern=r"AttributeError.*no attribute '(get_by_\w+|search)'",
                error_type="missing_crud_method",
                fix_template="""
# 添加缺失的CRUD方法
def {method_name}(self, db: Session, **kwargs):
    return db.query(self.model).filter_by(**kwargs).first()
""",
                description="CRUD方法缺失"
            ),
            
            ErrorPattern(
                pattern=r"from pydantic import.*BaseSettings.*ImportError",
                error_type="pydantic_settings_import",
                fix_template="""
# 修复 Pydantic v2 BaseSettings 导入
from pydantic_settings import BaseSettings, SettingsConfigDict
""",
                description="Pydantic v2 BaseSettings导入错误"
            ),
            
            ErrorPattern(
                pattern=r"@validator.*pydantic\.decorator",
                error_type="pydantic_validator",
                fix_template="""
# 修复 Pydantic v2 验证器
from pydantic import field_validator

@field_validator('field_name')
@classmethod
def validate_field(cls, v):
    return v
""",
                description="Pydantic v2验证器语法错误"
            )
        ]
        
        # 添加内置模式到缓存
        for pattern in builtin_patterns:
            if pattern.pattern not in self.patterns:
                self.patterns[pattern.pattern] = pattern
        
        self._save_patterns()
    
    def _load_patterns(self) -> Dict[str, ErrorPattern]:
        """加载错误模式"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        p['pattern']: ErrorPattern(**p) 
                        for p in data
                    }
            except Exception:
                pass
        return {}
    
    def _load_fixes(self) -> List[CachedFix]:
        """加载缓存的修复方案"""
        if self.fixes_file.exists():
            try:
                with open(self.fixes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [CachedFix(**fix) for fix in data]
            except Exception:
                pass
        return []
    
    def _save_patterns(self):
        """保存错误模式"""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(p) for p in self.patterns.values()],
                f,
                indent=2,
                ensure_ascii=False
            )
    
    def _save_fixes(self):
        """保存修复方案"""
        # 只保留最近1000个修复方案
        self.fixes = self.fixes[-1000:]
        with open(self.fixes_file, 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(fix) for fix in self.fixes],
                f,
                indent=2,
                ensure_ascii=False
            )
    
    def _compute_error_hash(self, error_text: str, file_path: str) -> str:
        """计算错误内容的哈希值"""
        # 规范化错误文本，去除行号等变化的部分
        normalized = re.sub(r'line \d+', 'line X', error_text)
        normalized = re.sub(r':\d+:', ':X:', normalized)
        
        content = f"{file_path}|{normalized}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def find_pattern_match(self, error_text: str) -> Optional[ErrorPattern]:
        """查找匹配的错误模式"""
        for pattern in self.patterns.values():
            if re.search(pattern.pattern, error_text, re.IGNORECASE | re.MULTILINE):
                # 更新使用统计
                pattern.use_count += 1
                pattern.last_used = datetime.now().isoformat()
                self._save_patterns()
                return pattern
        return None
    
    def find_cached_fix(self, error_text: str, file_path: str) -> Optional[CachedFix]:
        """查找缓存的修复方案"""
        error_hash = self._compute_error_hash(error_text, file_path)
        
        for fix in reversed(self.fixes):  # 从最新的开始查找
            if fix.error_hash == error_hash and fix.success:
                return fix
        return None
    
    def add_fix_result(self, error_text: str, file_path: str, 
                      fix_content: str, success: bool):
        """添加修复结果到缓存"""
        error_hash = self._compute_error_hash(error_text, file_path)
        
        cached_fix = CachedFix(
            error_hash=error_hash,
            fix_content=fix_content,
            file_path=file_path,
            success=success,
            timestamp=datetime.now().isoformat()
        )
        
        self.fixes.append(cached_fix)
        self._save_fixes()
    
    def update_pattern_success_rate(self, pattern: ErrorPattern, success: bool):
        """更新模式成功率"""
        # 使用指数移动平均
        alpha = 0.1  # 平滑因子
        pattern.success_rate = (1 - alpha) * pattern.success_rate + alpha * (1.0 if success else 0.0)
        self._save_patterns()
    
    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            "total_patterns": len(self.patterns),
            "total_cached_fixes": len(self.fixes),
            "successful_fixes": sum(1 for f in self.fixes if f.success),
            "most_used_patterns": sorted(
                self.patterns.values(),
                key=lambda p: p.use_count,
                reverse=True
            )[:5]
        }
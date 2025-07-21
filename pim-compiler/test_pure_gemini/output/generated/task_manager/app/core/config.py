"""
应用配置管理

此模块使用 Pydantic Settings 来管理应用的配置，可以方便地从环境变量或 .env 文件中加载配置。
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    应用配置类，定义了所有需要的环境变量。
    """
    PROJECT_NAME: str = "Task Manager API"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    # 支持 PostgreSQL (asyncpg) 和 SQLite (aiosqlite)
    # 示例:
    # DATABASE_URL="postgresql+asyncpg://user:password@host:port/dbname"
    # DATABASE_URL="sqlite+aiosqlite:///./task_manager.db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./task_manager.db"

    # 测试数据库URL，如果未设置，则在测试时动态创建
    TEST_DATABASE_URL: str | None = None

    # model_config 用于配置 Pydantic 的行为
    # case_sensitive=True 表示环境变量名���是大小写敏感的
    # env_file=".env" 指定从 .env 文件加载环境变量
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

# 创建一个全局可用的配置实例
settings = Settings()

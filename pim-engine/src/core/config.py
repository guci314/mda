"""Configuration management for PIM Engine"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Engine configuration settings"""
    
    # Application
    app_name: str = "PIM Execution Engine"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Database
    database_url: Optional[str] = Field(
        default="sqlite:///./pim_engine.db",
        env="DATABASE_URL"
    )
    db_pool_size: int = 20
    db_max_overflow: int = 40
    
    # Redis (optional)
    redis_url: Optional[str] = Field(
        default=None,
        env="REDIS_URL"
    )
    cache_ttl: int = 300  # 5 minutes
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Model Loading
    models_path: str = "./models"
    hot_reload: bool = True
    reload_interval: int = 5  # seconds
    
    # API Configuration
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_path: str = "/metrics"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    
    # LLM Configuration (for rule engine)
    llm_provider: Optional[str] = "anthropic"
    llm_api_key: Optional[str] = Field(default=None, env="LLM_API_KEY")
    llm_model: str = "claude-3-sonnet-20240229"
    llm_temperature: float = 0.3
    
    # Performance
    max_connections: int = 100
    connection_timeout: int = 30
    request_timeout: int = 60
    
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
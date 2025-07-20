# MDA-GENERATED-START: config
"""
Application configuration
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Project information
    PROJECT_NAME: str = "用户管理服务"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database configuration
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="userdb", env="POSTGRES_DB")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Database URL (can be set directly or computed)
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Pagination defaults
    DEFAULT_SKIP: int = 0
    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 100
    
    # Debug mode
    DEBUG_MODE: bool = Field(default=True, env="DEBUG_MODE")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If DATABASE_URL is not set, construct it
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
# MDA-GENERATED-END: config
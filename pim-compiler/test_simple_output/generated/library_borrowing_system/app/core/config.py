import os
from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "Library Borrowing System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Backend CORS origins
    # A comma-separated list of origins. e.g. `http://localhost,http://localhost:4200`
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database configuration
    DATABASE_URL: str = "sqlite:///./library.db"
    
    # Test database configuration
    TEST_DATABASE_URL: str = "sqlite:///./test.db"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

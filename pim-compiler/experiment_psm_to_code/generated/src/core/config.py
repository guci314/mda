from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "User Management API"
    API_V1_STR: str = "/api/v1"

    # Database configuration
    # To use PostgreSQL, change the URL format to:
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@host:port/db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"


settings = Settings()

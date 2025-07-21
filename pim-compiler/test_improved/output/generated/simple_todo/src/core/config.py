"""
Core application settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    Uses pydantic-settings to load from .env files or environment variables.
    """
    PROJECT_NAME: str = "Simple Todo API"
    API_V1_STR: str = "/api/v1"

    # Database configuration
    # The default value uses a local SQLite database.
    # For PostgreSQL, it would look like:
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@host:port/db"
    DATABASE_URL: str = "sqlite:///./simple_todo.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()

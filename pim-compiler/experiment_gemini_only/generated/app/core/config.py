from pydantic import AnyHttpUrl, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "Blog System API"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_env_file"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Database
    # Default to a local SQLite database for simplicity
    DATABASE_URL: str = "sqlite+aiosqlite:///./blog.db"

    # CORS
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []


settings = Settings()

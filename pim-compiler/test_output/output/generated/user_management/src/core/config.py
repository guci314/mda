"""
Application Configuration Management.

This module uses pydantic-settings to manage application configurations.
It loads settings from environment variables, allowing for a flexible
and secure way to configure the application.
"""
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Main application settings.
    """
    # Core settings
    PROJECT_NAME: str = "User Management API"
    API_V1_STR: str = "/api/v1"

    # Database settings
    # Using SQLite for simplicity. For production, use a robust database like PostgreSQL.
    # Example for PostgreSQL: "postgresql+asyncpg://user:password@host:port/db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./user_management.db"

    # Security settings
    # Generate a secure secret key using: openssl rand -hex 32
    SECRET_KEY: str = secrets.token_hex(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

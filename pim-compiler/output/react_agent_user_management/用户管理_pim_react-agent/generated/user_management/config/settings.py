from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/user_management"
    # Service port configuration
    API_PORT: int = 8000
    # Environment variable
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()
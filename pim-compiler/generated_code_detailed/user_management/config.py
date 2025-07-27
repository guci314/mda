from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./user_management.db"
    secret_key: str = "your-secret-key"
    
    class Config:
        env_file = ".env"

settings = Settings()
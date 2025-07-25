from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Blog Management API"
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
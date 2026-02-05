import os
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: int
    DATABASE_NAME: str

    class Config:
        # Construct absolute path to .env file in the backend root directory
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
        )
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

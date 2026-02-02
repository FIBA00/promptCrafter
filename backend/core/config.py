from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith("postgresql://") and not v.startswith("sqlite:///"):
            raise ValueError("DATABASE_URL must start with postgresql:// or sqlite:///")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

# app/core/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings


import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "API Monitoring K3 EPSON"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # Security / JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

    # WhatsApp Notification (Fonnte / Wablas / dll)
    WA_API_URL: str = ""
    WA_API_TOKEN: str = ""
    WA_DEFAULT_TARGET: str = ""  # Nomor tujuan default (format: 628xxx)
    WAHA_USERNAME: str = ""
    WAHA_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

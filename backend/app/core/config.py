from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Pronunciation Practice Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/pronunciation_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Azure Speech Service
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_REGION: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Dictionary API
    DICTIONARY_API_URL: str = "https://api.dictionaryapi.dev/api/v2/entries/en"

    # CORS - Allow all origins for development
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

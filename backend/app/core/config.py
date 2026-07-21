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

    # 讯飞语音评测(ISE)
    XF_APPID: Optional[str] = None
    XF_API_KEY: Optional[str] = None
    XF_API_SECRET: Optional[str] = None

    # 影子/降级 ML 模型地址
    SHADOW_ML_URL: Optional[str] = None

    # 境内评分节点
    SCORING_NODE_URL: Optional[str] = None
    SCORING_NODE_TOKEN: Optional[str] = None

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

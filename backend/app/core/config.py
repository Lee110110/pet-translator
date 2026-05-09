from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "AI宠物翻译官"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/pet_translator.db"

    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 72

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com/v1"
    LLM_MODEL: str = "deepseek-chat"
    LLM_MAX_TOKENS: int = 2048

    VISION_API_KEY: str = ""
    VISION_BASE_URL: str = "https://api.deepseek.com/v1"
    VISION_MODEL: str = "deepseek-chat"

    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024
    MAX_AUDIO_SIZE: int = 20 * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
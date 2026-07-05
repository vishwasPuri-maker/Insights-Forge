"""Application settings, loaded from .env via pydantic-settings.

Never hardcode secrets — everything sensitive is read from the environment.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://decisiq:decisiq@localhost:5432/decisiq"

    # JWT
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # S3 / MinIO
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "decisiq-landing"

    # LLM
    llm_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — read the .env once per process."""
    return Settings()


settings = get_settings()

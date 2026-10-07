from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "recipe-api"
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://app:change_me@localhost:5432/recipe_app"
    s3_endpoint: str = "http://localhost:4566"
    s3_public_endpoint: str = "http://localhost:4566"
    s3_access_key: str = "test"
    s3_secret_key: str = "test"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:14b"
    frontend_url: str = "http://localhost:5173"
    mailpit_smtp_host: str = "localhost"
    mailpit_smtp_port: int = 1025
    auth_session_ttl_seconds: int = Field(default=3600, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

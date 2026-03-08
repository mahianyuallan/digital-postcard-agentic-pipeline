from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "digital-postcard-agentic-pipeline"
    app_env: str = "dev"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./support_tickets.db"

    llm_mode: str = "mock"  # mock | openai
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    llm_timeout_seconds: float = Field(default=20.0, gt=0.0)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

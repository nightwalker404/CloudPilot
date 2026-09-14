from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(..., validation_alias="APP_NAME")
    debug_mode: bool = Field(default=False, validation_alias="DEBUG_MODE")
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    model: str = Field(..., validation_alias="MODEL")
    llm_base_url: str = Field(..., validation_alias="LLM_BASE_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
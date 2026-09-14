from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ### App Configuration ###
    app_name: str = Field(..., validation_alias="APP_NAME")
    debug_mode: bool = Field(default=False, validation_alias="DEBUG_MODE")

    ### AI Configuration ###
    model: str = Field(..., validation_alias="MODEL")
    llm_base_url: str = Field(..., validation_alias="LLM_BASE_URL")

    ### MongoDB Configuration ###
    mongo_uri: str = Field(..., validation_alias="MONGO_URI")
    mongo_initdb_root_username: str = Field(..., validation_alias="MONGO_INITDB_ROOT_USERNAME")
    mongo_initdb_root_password: str = Field(..., validation_alias="MONGO_INITDB_ROOT_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
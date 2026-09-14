from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

class Settings(BaseSettings):
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent

    ### Cert files
    CLIENT_CERT: Path = BASE_DIR / "certs" / "client.crt"
    CLIENT_KEY: Path = BASE_DIR / "certs" / "client.key"
    SERVER_CERT: Path = BASE_DIR / "certs" / "server.crt"
    
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

    ### Incus Configuration ###
    incus_url: str = Field(..., validation_alias="INCUS_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
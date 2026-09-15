from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar


class Settings(BaseSettings):
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent

    ### Cert files (configurable for Docker)
    client_cert_path: str = Field(default="", validation_alias="CLIENT_CERT_PATH")
    client_key_path: str = Field(default="", validation_alias="CLIENT_KEY_PATH")
    server_cert_path: str = Field(default="", validation_alias="SERVER_CERT_PATH")

    @property
    def CLIENT_CERT(self) -> Path:
        if self.client_cert_path:
            return Path(self.client_cert_path)
        return self.BASE_DIR / "certs" / "client.crt"

    @property
    def CLIENT_KEY(self) -> Path:
        if self.client_key_path:
            return Path(self.client_key_path)
        return self.BASE_DIR / "certs" / "client.key"

    @property
    def SERVER_CERT(self) -> Path:
        if self.server_cert_path:
            return Path(self.server_cert_path)
        return self.BASE_DIR / "certs" / "server.crt"

    ### App Configuration ###
    app_name: str = Field(..., validation_alias="APP_NAME")
    debug_mode: bool = Field(default=False, validation_alias="DEBUG_MODE")
    app_port: int = Field(..., validation_alias="APP_PORT")
    app_host: str = Field(..., validation_alias="APP_HOST")

    ### AI Configuration ###
    model: str = Field(..., validation_alias="MODEL")
    llm_base_url: str = Field(..., validation_alias="LLM_BASE_URL")

    ### MongoDB Configuration ###
    mongo_uri: str = Field(..., validation_alias="MONGO_URI")
    mongo_initdb_root_username: str = Field(..., validation_alias="MONGO_INITDB_ROOT_USERNAME")
    mongo_initdb_root_password: str = Field(..., validation_alias="MONGO_INITDB_ROOT_PASSWORD")
    mongo_db_name: str = Field(default="cloudpilot", validation_alias="MONGO_DB_NAME")

    ### Incus Configuration ###
    incus_url: str = Field(default="https://host.docker.internal:8443", validation_alias="INCUS_URL")

    ### Web Search Configuration ###
    searxng_url: str = Field(default="http://searxng:8080", validation_alias="SEARXNG_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
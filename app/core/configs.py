from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    app_name: str = Field(..., env="APP_NAME")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    database_url: str = Field(..., env="DATABASE_URL")
    llm_base_url: str = Field(..., env="LLM_BASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
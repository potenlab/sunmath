from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://sunmath:sunmath@localhost:5433/sunmath"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    llm_api_key: str = ""
    llm_model: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

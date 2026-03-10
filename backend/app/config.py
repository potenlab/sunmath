from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://sunmath:sunmath@localhost:5433/sunmath"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_timeout: float = 30.0
    benchmark_results_dir: str = "data/benchmark_results"
    vertex_api_key: str = ""
    google_application_credentials: str = ""
    gcp_project_id: str = ""
    gcp_location: str = "us-central1"
    gcs_bucket_name: str = "express-auth-414411-sunmath-ocr"
    baseline_model_endpoint: str = ""
    jwt_secret: str = "change-me-in-production"
    access_token_expire: int = 30       # minutes
    refresh_token_expire: int = 10080   # 7 days

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

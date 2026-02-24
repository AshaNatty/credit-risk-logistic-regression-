from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Banking Risk Multi-Agent System"
    app_version: str = "1.0.0"
    debug: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 3600

    # SQLite
    sqlite_db_path: str = "data/audit.db"

    # Chroma (Vector DB)
    chroma_persist_dir: str = "data/chroma"
    chroma_collection: str = "policy_documents"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Risk thresholds
    risk_score_low: float = 0.3
    risk_score_medium: float = 0.6
    risk_score_high: float = 0.8


settings = Settings()

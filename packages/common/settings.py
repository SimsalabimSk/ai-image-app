from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # Core
    environment: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # DB
    database_url: str = "postgresql+psycopg://app:app@postgres:5432/app"

    # Redis / Celery
    redis_url: str = "redis://redis:6379/0"

    # S3-compatible storage (MinIO)
    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "assets"
    s3_region: str = "us-east-1"

    # Assets
    temp_ttl_hours: int = 24


settings = Settings()

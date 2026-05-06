from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Operational settings
    service_name: str = "service-template"
    env: str = "production"
    log_level: str = "info"
    port: int = 8018
    trusted_proxy_hops: int = Field(default=1, ge=0)

    # Input validation settings
    max_content_length: int = Field(default=16_384, gt=0)

    # Authorization settings
    authorization_policies_dir: Path = Field(default=Path("policies"))
    authorization_policy_cache_ttl: int = Field(default=60, ge=0)
    
    # JWT authentication settings
    jwt_public_key: str = Field(default="DEFAULT_PUBLIC_KEY")
    jwt_issuer: str = Field(default="https://neosofia.com")
    jwt_audience: str = Field(default="api.neosofia.com")

    # Rate limit settings
    rate_limit_storage_uri: str = "memory://"
    health_rate_limit: str = "600 per minute"
    document_read_rate_limit: str = "60 per minute"
    document_delete_rate_limit: str = "10 per minute"

    # Gunicorn settings
    web_concurrency: int = Field(default=2, ge=1)
    gunicorn_threads: int = Field(default=2, ge=1)
    gunicorn_timeout: int = Field(default=30, ge=1)
    gunicorn_keepalive: int = Field(default=5, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="forbid",
    )


settings = Settings()  # type: ignore[call-arg]
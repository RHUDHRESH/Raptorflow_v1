"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Any

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Environment
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # Supabase Auth
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Razorpay
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: str | None = None

    # Google Gemini (Optional)
    GOOGLE_API_KEY: str | None = None

    # Perplexity (Optional)
    PERPLEXITY_API_KEY: str | None = None

    # Application URLs
    API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Security
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    CORS_ENABLED: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_IP: int = 100
    RATE_LIMIT_PER_USER: int = 1000

    # Observability
    LOG_LEVEL: str = "DEBUG"
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "local"

    # Feature Flags
    FEATURE_PAYMENTS_ENABLED: bool = True
    FEATURE_AI_AGENTS_ENABLED: bool = True

    # Worker (Celery)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_origins(cls, v: str) -> list[str]:
        """Parse comma-separated origins into list."""
        return [origin.strip() for origin in v.split(",")]

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS allowed origins."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()

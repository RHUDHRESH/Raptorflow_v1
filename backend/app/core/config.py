"""
Application configuration with Dev Mode (Local) and Cloud Mode support.
Single configuration file to toggle between local and cloud services.

Dev Mode (local):
  - Database: PostgreSQL local
  - LLM: Ollama (local) or open-source models
  - Embeddings: Ollama embeddings
  - Vector DB: ChromaDB
  - Cache: In-memory (Redis optional)
  - Search: Local tools
  - Auth: Basic/no Supabase

Cloud Mode:
  - Database: Supabase (PostgreSQL)
  - LLM: OpenAI GPT-4/4.5
  - Embeddings: OpenAI Ada
  - Vector DB: Supabase pgvector
  - Cache: Redis
  - Search: Perplexity API
  - Auth: Supabase
  - Payments: Razorpay
"""

from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExecutionMode(str, Enum):
    """Execution mode: dev (local) or cloud."""

    DEV = "dev"
    CLOUD = "cloud"


class LLMProvider(str, Enum):
    """LLM provider selection."""

    OLLAMA = "ollama"
    OPENAI = "openai"


class EmbeddingProvider(str, Enum):
    """Embedding provider selection."""

    OLLAMA = "ollama"
    OPENAI = "openai"


class VectorDBProvider(str, Enum):
    """Vector database provider."""

    CHROMADB = "chromadb"
    SUPABASE_PGVECTOR = "supabase_pgvector"


class CacheProvider(str, Enum):
    """Cache provider selection."""

    REDIS = "redis"
    IN_MEMORY = "in_memory"


class Settings(BaseSettings):
    """
    Application settings with mode-based configuration.

    All services automatically adapt based on EXECUTION_MODE setting.
    Change EXECUTION_MODE="dev" or EXECUTION_MODE="cloud" and everything else adjusts.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # ============================================================================
    # EXECUTION MODE - MASTER SWITCH
    # ============================================================================
    # Change this single value to switch entire app between local and cloud
    EXECUTION_MODE: ExecutionMode = Field(
        default=ExecutionMode.CLOUD,
        description="dev = local tools (Ollama, ChromaDB), cloud = cloud services (OpenAI, Supabase)"
    )

    # ============================================================================
    # ENVIRONMENT & DEBUG
    # ============================================================================
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # ============================================================================
    # DATABASE CONFIGURATION (Mode-Adaptive)
    # ============================================================================
    # Dev Mode: Local PostgreSQL (no Supabase)
    # Cloud Mode: Supabase PostgreSQL

    DATABASE_URL: Optional[PostgresDsn] = Field(
        default=None,
        description="PostgreSQL connection string (local or Supabase)"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=20,
        description="Connection pool size"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        description="Maximum overflow connections"
    )

    # Supabase Auth (Cloud Mode only)
    SUPABASE_URL: Optional[str] = Field(
        default=None,
        description="Supabase project URL (Cloud Mode)"
    )
    SUPABASE_ANON_KEY: Optional[str] = Field(
        default=None,
        description="Supabase anonymous key (Cloud Mode)"
    )
    SUPABASE_SERVICE_KEY: Optional[str] = Field(
        default=None,
        description="Supabase service role key (Cloud Mode)"
    )
    SUPABASE_JWT_SECRET: Optional[str] = Field(
        default=None,
        description="Supabase JWT secret (Cloud Mode)"
    )

    # ============================================================================
    # CACHE CONFIGURATION (Mode-Adaptive)
    # ============================================================================
    # Dev Mode: In-memory cache (default) or Redis
    # Cloud Mode: Redis (required)

    CACHE_PROVIDER: CacheProvider = Field(
        default=CacheProvider.IN_MEMORY,
        description="Cache provider: redis or in_memory"
    )
    REDIS_URL: Optional[str] = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    REDIS_MAX_CONNECTIONS: int = Field(
        default=50,
        description="Redis connection pool size"
    )

    # ============================================================================
    # LLM CONFIGURATION (Mode-Adaptive)
    # ============================================================================
    # Dev Mode: Ollama (local) - free, unlimited tokens
    # Cloud Mode: OpenAI GPT-4.5 Turbo - fast reasoning, low cost

    LLM_PROVIDER: Optional[LLMProvider] = Field(
        default=None,
        description="LLM provider: ollama (dev) or openai (cloud)"
    )

    # Ollama Configuration (Dev Mode)
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL (Dev Mode)"
    )
    OLLAMA_MODEL: str = Field(
        default="mistral",
        description="Ollama model name (Dev Mode): mistral, neural-chat, etc"
    )
    OLLAMA_EMBEDDING_MODEL: str = Field(
        default="nomic-embed-text",
        description="Ollama embedding model (Dev Mode)"
    )

    # OpenAI Configuration (Cloud Mode)
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key (Cloud Mode)"
    )
    OPENAI_ORG_ID: Optional[str] = Field(
        default=None,
        description="OpenAI organization ID (Cloud Mode)"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4-turbo",
        description="OpenAI model: gpt-4-turbo, gpt-4, gpt-3.5-turbo (Cloud Mode)"
    )
    OPENAI_FAST_MODEL: str = Field(
        default="gpt-4-turbo",
        description="OpenAI fast reasoning model (Cloud Mode)"
    )

    # ============================================================================
    # EMBEDDING CONFIGURATION (Mode-Adaptive)
    # ============================================================================
    # Dev Mode: Ollama embeddings (free, local)
    # Cloud Mode: OpenAI Ada embeddings

    EMBEDDING_PROVIDER: Optional[EmbeddingProvider] = Field(
        default=None,
        description="Embedding provider: ollama (dev) or openai (cloud)"
    )
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002",
        description="Embedding model name"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=1536,
        description="Embedding vector dimension"
    )

    # ============================================================================
    # VECTOR DATABASE CONFIGURATION (Mode-Adaptive)
    # ============================================================================
    # Dev Mode: ChromaDB (local, no server needed)
    # Cloud Mode: Supabase pgvector

    VECTOR_DB_PROVIDER: Optional[VectorDBProvider] = Field(
        default=None,
        description="Vector DB: chromadb (dev) or supabase_pgvector (cloud)"
    )

    # ChromaDB Configuration (Dev Mode)
    CHROMADB_PATH: str = Field(
        default="./chromadb_data",
        description="ChromaDB persistent storage path (Dev Mode)"
    )
    CHROMADB_HOST: Optional[str] = Field(
        default=None,
        description="ChromaDB server host (if using server mode)"
    )
    CHROMADB_PORT: Optional[int] = Field(
        default=None,
        description="ChromaDB server port (if using server mode)"
    )

    # ============================================================================
    # SEARCH & RESEARCH TOOLS
    # ============================================================================
    # Dev Mode: Local search tools only
    # Cloud Mode: Perplexity API + local tools

    PERPLEXITY_API_KEY: Optional[str] = Field(
        default=None,
        description="Perplexity API key (Cloud Mode)"
    )

    # Google Gemini (Optional, Cloud Mode)
    GOOGLE_API_KEY: Optional[str] = Field(
        default=None,
        description="Google API key for Gemini (Cloud Mode, optional)"
    )

    # ============================================================================
    # PAYMENT PROCESSING (Cloud Mode Only)
    # ============================================================================
    RAZORPAY_KEY_ID: Optional[str] = Field(
        default=None,
        description="Razorpay API key (Cloud Mode)"
    )
    RAZORPAY_KEY_SECRET: Optional[str] = Field(
        default=None,
        description="Razorpay API secret (Cloud Mode)"
    )
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = Field(
        default=None,
        description="Razorpay webhook secret (Cloud Mode)"
    )

    # ============================================================================
    # APPLICATION URLs
    # ============================================================================
    API_URL: str = Field(
        default="http://localhost:8000",
        description="API base URL"
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend base URL"
    )

    # ============================================================================
    # SECURITY
    # ============================================================================
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT and encryption"
    )
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated CORS allowed origins"
    )
    CORS_ENABLED: bool = Field(
        default=True,
        description="Enable CORS"
    )

    # ============================================================================
    # RATE LIMITING
    # ============================================================================
    RATE_LIMIT_PER_IP: int = Field(
        default=100,
        description="Rate limit per IP per minute"
    )
    RATE_LIMIT_PER_USER: int = Field(
        default=1000,
        description="Rate limit per user per month"
    )

    # ============================================================================
    # OBSERVABILITY & LOGGING
    # ============================================================================
    LOG_LEVEL: str = Field(
        default="DEBUG",
        description="Logging level"
    )
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN (Cloud Mode)"
    )
    SENTRY_ENVIRONMENT: str = Field(
        default="local",
        description="Sentry environment"
    )

    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    FEATURE_PAYMENTS_ENABLED: bool = Field(
        default=True,
        description="Enable payment processing"
    )
    FEATURE_AI_AGENTS_ENABLED: bool = Field(
        default=True,
        description="Enable AI agents"
    )

    # ============================================================================
    # WORKER / TASK QUEUE (Cloud Mode)
    # ============================================================================
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
        description="Celery result backend URL"
    )

    # ============================================================================
    # BUDGET CONTROL (Dev Mode)
    # ============================================================================
    # Dev Mode: Unlimited local compute
    # Cloud Mode: $15/month budget enforcement

    MONTHLY_BUDGET_CENTS: int = Field(
        default=1500,  # $15.00
        description="Monthly budget in cents (Cloud Mode)"
    )
    DAILY_BUDGET_CENTS: int = Field(
        default=50,  # $0.50/day avg
        description="Daily budget in cents (Cloud Mode)"
    )

    # ============================================================================
    # VALIDATORS & AUTO-CONFIGURATION
    # ============================================================================

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_origins(cls, v: str) -> list[str]:
        """Parse comma-separated origins into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("EXECUTION_MODE", mode="before")
    @classmethod
    def parse_mode(cls, v: Any) -> ExecutionMode:
        """Parse execution mode string."""
        if isinstance(v, str):
            return ExecutionMode(v.lower())
        return v

    def __init__(self, **data: Any) -> None:
        """Initialize settings and auto-configure based on mode."""
        super().__init__(**data)
        self._apply_mode_defaults()

    def _apply_mode_defaults(self) -> None:
        """Apply sensible defaults based on execution mode."""
        if self.EXECUTION_MODE == ExecutionMode.DEV:
            self._configure_dev_mode()
        else:
            self._configure_cloud_mode()

    def _configure_dev_mode(self) -> None:
        """Configure for dev mode (local tools)."""
        # LLM
        if not self.LLM_PROVIDER:
            self.LLM_PROVIDER = LLMProvider.OLLAMA

        # Embeddings
        if not self.EMBEDDING_PROVIDER:
            self.EMBEDDING_PROVIDER = EmbeddingProvider.OLLAMA

        # Vector DB
        if not self.VECTOR_DB_PROVIDER:
            self.VECTOR_DB_PROVIDER = VectorDBProvider.CHROMADB

        # Cache
        if not self.CACHE_PROVIDER:
            self.CACHE_PROVIDER = CacheProvider.IN_MEMORY

        # Database (use local PostgreSQL if not set)
        if not self.DATABASE_URL:
            self.DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/raptorflow"

        # Disable cloud-only features
        self.FEATURE_PAYMENTS_ENABLED = False
        self.SENTRY_DSN = None

    def _configure_cloud_mode(self) -> None:
        """Configure for cloud mode (cloud services)."""
        # LLM
        if not self.LLM_PROVIDER:
            self.LLM_PROVIDER = LLMProvider.OPENAI

        # Embeddings
        if not self.EMBEDDING_PROVIDER:
            self.EMBEDDING_PROVIDER = EmbeddingProvider.OPENAI

        # Vector DB
        if not self.VECTOR_DB_PROVIDER:
            self.VECTOR_DB_PROVIDER = VectorDBProvider.SUPABASE_PGVECTOR

        # Cache
        if not self.CACHE_PROVIDER:
            self.CACHE_PROVIDER = CacheProvider.REDIS

        # Require cloud credentials for cloud mode
        if not self.DATABASE_URL and not self.SUPABASE_URL:
            raise ValueError(
                "Cloud mode requires DATABASE_URL or SUPABASE_URL to be set. "
                "Please configure Supabase connection details."
            )

        if not self.OPENAI_API_KEY:
            raise ValueError(
                "Cloud mode requires OPENAI_API_KEY to be set. "
                "Please provide your OpenAI API key."
            )

    # ============================================================================
    # UTILITY PROPERTIES
    # ============================================================================

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS allowed origins."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS

    @property
    def is_dev_mode(self) -> bool:
        """Check if running in dev mode."""
        return self.EXECUTION_MODE == ExecutionMode.DEV

    @property
    def is_cloud_mode(self) -> bool:
        """Check if running in cloud mode."""
        return self.EXECUTION_MODE == ExecutionMode.CLOUD

    @property
    def is_local_storage(self) -> bool:
        """Check if using local storage (dev mode)."""
        return self.VECTOR_DB_PROVIDER == VectorDBProvider.CHROMADB

    @property
    def is_using_ollama(self) -> bool:
        """Check if using Ollama for LLM."""
        return self.LLM_PROVIDER == LLMProvider.OLLAMA

    @property
    def is_using_openai(self) -> bool:
        """Check if using OpenAI for LLM."""
        return self.LLM_PROVIDER == LLMProvider.OPENAI

    @property
    def is_in_memory_cache(self) -> bool:
        """Check if using in-memory cache."""
        return self.CACHE_PROVIDER == CacheProvider.IN_MEMORY

    @property
    def is_redis_cache(self) -> bool:
        """Check if using Redis cache."""
        return self.CACHE_PROVIDER == CacheProvider.REDIS

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on provider."""
        if self.is_using_ollama:
            return {
                "provider": "ollama",
                "base_url": self.OLLAMA_BASE_URL,
                "model": self.OLLAMA_MODEL,
                "embedding_model": self.OLLAMA_EMBEDDING_MODEL,
            }
        else:
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "fast_model": self.OPENAI_FAST_MODEL,
                "org_id": self.OPENAI_ORG_ID,
            }

    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get vector database configuration."""
        if self.VECTOR_DB_PROVIDER == VectorDBProvider.CHROMADB:
            return {
                "provider": "chromadb",
                "path": self.CHROMADB_PATH,
                "host": self.CHROMADB_HOST,
                "port": self.CHROMADB_PORT,
            }
        else:
            return {
                "provider": "supabase_pgvector",
                "url": self.SUPABASE_URL,
                "key": self.SUPABASE_SERVICE_KEY,
            }

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        if self.is_in_memory_cache:
            return {"provider": "in_memory"}
        else:
            return {
                "provider": "redis",
                "url": self.REDIS_URL,
                "max_connections": self.REDIS_MAX_CONNECTIONS,
            }

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": str(self.DATABASE_URL),
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
        }

    def log_configuration(self) -> str:
        """Log current configuration for debugging."""
        lines = [
            "=" * 80,
            f"RaptorFlow Configuration - {self.EXECUTION_MODE.value.upper()} MODE",
            "=" * 80,
            f"Execution Mode:    {self.EXECUTION_MODE.value}",
            f"Environment:       {self.ENVIRONMENT}",
            f"Debug:             {self.DEBUG}",
            "",
            "── LLM Configuration",
            f"Provider:          {self.LLM_PROVIDER.value}",
            f"Model:             {self.OLLAMA_MODEL if self.is_using_ollama else self.OPENAI_MODEL}",
            "",
            "── Embedding Configuration",
            f"Provider:          {self.EMBEDDING_PROVIDER.value}",
            f"Model:             {self.EMBEDDING_MODEL}",
            "",
            "── Vector Database Configuration",
            f"Provider:          {self.VECTOR_DB_PROVIDER.value}",
            "",
            "── Cache Configuration",
            f"Provider:          {self.CACHE_PROVIDER.value}",
            "",
            "── Database Configuration",
            f"Type:              PostgreSQL",
            f"Pool Size:         {self.DATABASE_POOL_SIZE}",
            "",
            "── Security",
            f"CORS Enabled:      {self.CORS_ENABLED}",
            f"Log Level:         {self.LOG_LEVEL}",
            "",
            "── Feature Flags",
            f"Payments Enabled:  {self.FEATURE_PAYMENTS_ENABLED}",
            f"Agents Enabled:    {self.FEATURE_AI_AGENTS_ENABLED}",
            "=" * 80,
        ]
        return "\n".join(lines)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()

# Log configuration on startup
if settings.DEBUG:
    import logging
    logger = logging.getLogger(__name__)
    logger.info(settings.log_configuration())

"""
GCP Secrets Manager Integration

Secure credential management for production deployment.

Handles:
- Retrieval of secrets from Google Cloud Secret Manager
- Local fallback to .env for development
- Caching with TTL
- Audit logging
"""

import logging
import os
from typing import Optional, Dict
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)


class SecretManager:
    """
    Manages secrets from GCP Secret Manager with fallback to environment variables.

    Production: Uses Google Cloud Secret Manager
    Development: Falls back to .env file via environment variables
    """

    def __init__(self, project_id: Optional[str] = None, use_gcp: bool = True):
        """
        Initialize Secret Manager.

        Args:
            project_id: GCP project ID (auto-detected if not provided)
            use_gcp: Whether to use GCP Secret Manager (default True)
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.use_gcp = use_gcp and self.project_id
        self._cache: Dict[str, tuple] = {}  # {secret_name: (value, timestamp)}
        self._cache_ttl = timedelta(hours=1)

        if self.use_gcp:
            try:
                from google.cloud import secretmanager
                self.secrets_client = secretmanager.SecretManagerServiceClient()
                logger.info(f"✅ GCP Secret Manager initialized for project {self.project_id}")
            except ImportError:
                logger.warning("google-cloud-secret-manager not installed, using env vars only")
                self.use_gcp = False
            except Exception as e:
                logger.warning(f"Failed to initialize GCP Secret Manager: {e}, falling back to env vars")
                self.use_gcp = False
        else:
            logger.info("Using environment variables for secrets (development mode)")

    def get_secret(self, secret_name: str) -> str:
        """
        Get a secret value.

        Tries in order:
        1. Check cache
        2. GCP Secret Manager (if enabled)
        3. Environment variable
        4. Raise error if not found

        Args:
            secret_name: Name of the secret (use snake_case like 'openai_api_key')

        Returns:
            Secret value as string

        Raises:
            ValueError: If secret not found in any source
        """
        # Check cache
        if secret_name in self._cache:
            value, timestamp = self._cache[secret_name]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                logger.debug(f"Using cached secret: {secret_name}")
                return value

        # Try GCP
        if self.use_gcp:
            try:
                value = self._get_from_gcp(secret_name)
                if value:
                    self._cache[secret_name] = (value, datetime.utcnow())
                    return value
            except Exception as e:
                logger.warning(f"Failed to get {secret_name} from GCP: {e}")

        # Try environment variable
        env_key = secret_name.upper()
        value = os.getenv(env_key)

        if value:
            self._cache[secret_name] = (value, datetime.utcnow())
            logger.debug(f"Retrieved {secret_name} from environment")
            return value

        # Not found
        raise ValueError(f"Secret '{secret_name}' not found in GCP Secret Manager or environment")

    def _get_from_gcp(self, secret_name: str) -> Optional[str]:
        """
        Retrieve secret from GCP Secret Manager.

        Args:
            secret_name: Secret name in GCP (use snake_case)

        Returns:
            Secret value or None if not found
        """
        if not self.use_gcp:
            return None

        try:
            # Format: projects/{project_id}/secrets/{secret_name}/versions/latest
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.secrets_client.access_secret_version(request={"name": name})
            value = response.payload.data.decode("UTF-8")

            logger.debug(f"Retrieved {secret_name} from GCP Secret Manager")
            return value

        except Exception as e:
            logger.debug(f"Secret {secret_name} not found in GCP: {e}")
            return None

    def get_secrets_dict(self, secret_names: list[str]) -> Dict[str, str]:
        """
        Get multiple secrets at once.

        Args:
            secret_names: List of secret names

        Returns:
            Dictionary of {secret_name: value}

        Raises:
            ValueError: If any secret is missing
        """
        secrets = {}
        for name in secret_names:
            secrets[name] = self.get_secret(name)
        return secrets

    def clear_cache(self):
        """Clear the secrets cache"""
        self._cache.clear()
        logger.info("Secrets cache cleared")


# Singleton instance
_secret_manager: Optional[SecretManager] = None


def get_secret_manager(project_id: Optional[str] = None) -> SecretManager:
    """Get or create singleton SecretManager instance"""
    global _secret_manager

    if _secret_manager is None:
        _secret_manager = SecretManager(project_id)

    return _secret_manager


# ============================================================================
# Pre-defined Secret Keys
# ============================================================================

class SecretKeys:
    """Standard secret key names for RaptorFlow"""

    # AI Provider Keys
    OPENAI_API_KEY = "openai_api_key"
    GEMINI_API_KEY = "gemini_api_key"
    PERPLEXITY_API_KEY = "perplexity_api_key"
    EXA_API_KEY = "exa_api_key"
    GOOGLE_API_KEY = "google_api_key"

    # Database
    SUPABASE_URL = "supabase_url"
    SUPABASE_KEY = "supabase_key"
    SUPABASE_SERVICE_KEY = "supabase_service_key"

    # Authentication
    JWT_SECRET_KEY = "jwt_secret_key"
    GOOGLE_OAUTH_CLIENT_ID = "google_oauth_client_id"
    GOOGLE_OAUTH_CLIENT_SECRET = "google_oauth_client_secret"

    # Integrations
    SLACK_WEBHOOK_URL = "slack_webhook_url"
    RAZORPAY_KEY_ID = "razorpay_key_id"
    RAZORPAY_KEY_SECRET = "razorpay_key_secret"
    RAZORPAY_WEBHOOK_SECRET = "razorpay_webhook_secret"

    # Redis (optional)
    REDIS_URL = "redis_url"


# ============================================================================
# Convenience Functions
# ============================================================================

def get_ai_keys() -> Dict[str, str]:
    """Get all AI provider keys"""
    manager = get_secret_manager()
    return {
        "openai": manager.get_secret(SecretKeys.OPENAI_API_KEY),
        "gemini": manager.get_secret(SecretKeys.GEMINI_API_KEY),
        "perplexity": manager.get_secret(SecretKeys.PERPLEXITY_API_KEY),
        "exa": manager.get_secret(SecretKeys.EXA_API_KEY),
    }


def get_database_keys() -> Dict[str, str]:
    """Get database credentials"""
    manager = get_secret_manager()
    return {
        "url": manager.get_secret(SecretKeys.SUPABASE_URL),
        "key": manager.get_secret(SecretKeys.SUPABASE_KEY),
        "service_key": manager.get_secret(SecretKeys.SUPABASE_SERVICE_KEY),
    }


def get_auth_keys() -> Dict[str, str]:
    """Get authentication keys"""
    manager = get_secret_manager()
    return {
        "jwt_secret": manager.get_secret(SecretKeys.JWT_SECRET_KEY),
        "google_oauth_client_id": manager.get_secret(SecretKeys.GOOGLE_OAUTH_CLIENT_ID),
        "google_oauth_client_secret": manager.get_secret(SecretKeys.GOOGLE_OAUTH_CLIENT_SECRET),
    }

"""
Unified Cloud AI Provider Service
==================================
Cloud-only architecture with environment-based provider switching.

Development Mode: Gemini (primary) → OpenRouter (fallback)
Production Mode: OpenAI GPT-5 series (primary) → OpenRouter (fallback)

NO LOCAL MODELS. NO OFFLINE MODE.
"""

import os
import logging
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass
import openai
import google.generativeai as genai
from openai import OpenAI

logger = logging.getLogger(__name__)

AppMode = Literal["dev", "prod"]


@dataclass
class ModelConfig:
    """GPT-5 series model configuration"""
    GPT5_NANO = "gpt-5-nano"
    GPT5_MINI = "gpt-5-mini"
    GPT5_STANDARD = "gpt-5"

    # Gemini models for development
    GEMINI_FLASH = "gemini-2.0-flash-exp"
    GEMINI_PRO = "gemini-pro"

    # OpenRouter models (fallback)
    OPENROUTER_GPT5_NANO = "openai/gpt-5-nano"
    OPENROUTER_GPT5_MINI = "openai/gpt-5-mini"
    OPENROUTER_GPT5 = "openai/gpt-5"


class CloudProviderError(Exception):
    """Base exception for cloud provider errors"""
    pass


class AllProvidersFailedError(CloudProviderError):
    """Raised when all configured providers fail"""
    pass


class CloudProviderService:
    """
    Unified cloud AI provider with automatic fallback.

    Modes:
    ------
    - dev: Uses Gemini as primary, OpenRouter as fallback
    - prod: Uses OpenAI GPT-5 series as primary, OpenRouter as fallback

    Environment Variables:
    ---------------------
    APP_MODE: "dev" or "prod"
    OPENAI_API_KEY: OpenAI API key (required for prod)
    GEMINI_API_KEY: Gemini API key (required for dev)
    OPENROUTER_API_KEY: OpenRouter API key (fallback for both modes)
    """

    def __init__(self):
        self.app_mode: AppMode = os.getenv("APP_MODE", "dev").lower()
        self.model_config = ModelConfig()

        # Validate mode
        if self.app_mode not in ["dev", "prod"]:
            raise ValueError(f"Invalid APP_MODE: {self.app_mode}. Must be 'dev' or 'prod'")

        # Initialize clients
        self._init_clients()

        logger.info(f"CloudProviderService initialized in {self.app_mode.upper()} mode")

    def _init_clients(self):
        """Initialize API clients based on app mode"""

        # OpenAI Client (Production mode)
        self.openai_client = None
        if self.app_mode == "prod":
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                logger.warning("OPENAI_API_KEY not set for production mode")
            else:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")

        # Gemini Client (Development mode)
        self.gemini_client = None
        if self.app_mode == "dev":
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                logger.warning("GEMINI_API_KEY not set for development mode")
            else:
                genai.configure(api_key=gemini_key)
                self.gemini_client = genai.GenerativeModel(self.model_config.GEMINI_FLASH)
                logger.info("Gemini client initialized")

        # OpenRouter Client (Universal fallback)
        self.openrouter_client = None
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            self.openrouter_client = OpenAI(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1"
            )
            logger.info("OpenRouter client initialized as fallback")
        else:
            logger.warning("OPENROUTER_API_KEY not set - no fallback available")

    def _select_model_for_complexity(self, task_complexity: str) -> str:
        """
        Select appropriate GPT-5 model based on task complexity.

        Args:
            task_complexity: One of ["simple", "moderate", "complex"]

        Returns:
            Model identifier string
        """
        if self.app_mode == "dev":
            return self.model_config.GEMINI_FLASH

        # Production mode - use GPT-5 series
        complexity_map = {
            "simple": self.model_config.GPT5_NANO,
            "moderate": self.model_config.GPT5_MINI,
            "complex": self.model_config.GPT5_STANDARD
        }

        return complexity_map.get(task_complexity, self.model_config.GPT5_MINI)

    def generate(
        self,
        prompt: str,
        task_complexity: str = "moderate",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate AI response with automatic provider fallback.

        Args:
            prompt: The input prompt
            task_complexity: "simple", "moderate", or "complex"
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional model-specific parameters

        Returns:
            Dict containing:
                - content: Generated text
                - model_used: Which model was used
                - provider: Which provider was used
                - usage: Token usage statistics
                - success: Boolean success status

        Raises:
            AllProvidersFailedError: When all providers fail
        """

        model = self._select_model_for_complexity(task_complexity)

        if self.app_mode == "dev":
            return self._generate_with_gemini_fallback(
                prompt, max_tokens, temperature, **kwargs
            )
        else:  # prod mode
            return self._generate_with_openai_fallback(
                prompt, model, max_tokens, temperature, **kwargs
            )

    def _generate_with_gemini_fallback(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Development mode: Gemini primary → OpenRouter fallback"""

        # Try Gemini first
        if self.gemini_client:
            try:
                logger.info(f"Attempting Gemini API call (dev mode)")
                response = self.gemini_client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature
                    )
                )

                content = response.text

                # Gemini doesn't provide token counts in the same way
                # Estimate based on content
                estimated_prompt_tokens = len(prompt.split()) * 1.3
                estimated_completion_tokens = len(content.split()) * 1.3

                logger.info("Gemini API call successful")
                return {
                    "success": True,
                    "content": content,
                    "model_used": self.model_config.GEMINI_FLASH,
                    "provider": "gemini",
                    "usage": {
                        "prompt_tokens": int(estimated_prompt_tokens),
                        "completion_tokens": int(estimated_completion_tokens),
                        "total_tokens": int(estimated_prompt_tokens + estimated_completion_tokens)
                    }
                }

            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                # Fall through to OpenRouter

        # Fallback to OpenRouter
        if self.openrouter_client:
            try:
                logger.info("Falling back to OpenRouter (dev mode)")
                return self._call_openrouter(
                    prompt,
                    self.model_config.OPENROUTER_GPT5_MINI,
                    max_tokens,
                    temperature,
                    **kwargs
                )
            except Exception as e:
                logger.error(f"OpenRouter fallback failed: {e}")

        raise AllProvidersFailedError("All providers failed in development mode")

    def _generate_with_openai_fallback(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Production mode: OpenAI GPT-5 series primary → OpenRouter fallback"""

        # Try OpenAI first
        if self.openai_client:
            try:
                logger.info(f"Attempting OpenAI API call with model: {model} (prod mode)")
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )

                content = response.choices[0].message.content
                usage = response.usage

                logger.info(f"OpenAI API call successful with {model}")
                return {
                    "success": True,
                    "content": content,
                    "model_used": model,
                    "provider": "openai",
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens
                    }
                }

            except Exception as e:
                logger.error(f"OpenAI API call failed with {model}: {e}")
                # Fall through to OpenRouter

        # Fallback to OpenRouter
        if self.openrouter_client:
            try:
                logger.info(f"Falling back to OpenRouter with {model} (prod mode)")

                # Map GPT-5 model to OpenRouter equivalent
                openrouter_model_map = {
                    self.model_config.GPT5_NANO: self.model_config.OPENROUTER_GPT5_NANO,
                    self.model_config.GPT5_MINI: self.model_config.OPENROUTER_GPT5_MINI,
                    self.model_config.GPT5_STANDARD: self.model_config.OPENROUTER_GPT5,
                }

                openrouter_model = openrouter_model_map.get(model, self.model_config.OPENROUTER_GPT5_MINI)

                return self._call_openrouter(
                    prompt,
                    openrouter_model,
                    max_tokens,
                    temperature,
                    **kwargs
                )
            except Exception as e:
                logger.error(f"OpenRouter fallback failed: {e}")

        raise AllProvidersFailedError(f"All providers failed in production mode for model {model}")

    def _call_openrouter(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Call OpenRouter API"""

        response = self.openrouter_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        content = response.choices[0].message.content
        usage = response.usage

        logger.info(f"OpenRouter API call successful with {model}")
        return {
            "success": True,
            "content": content,
            "model_used": model,
            "provider": "openrouter",
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
        }

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all configured providers"""

        status = {
            "app_mode": self.app_mode,
            "primary_provider": "gemini" if self.app_mode == "dev" else "openai",
            "fallback_provider": "openrouter",
            "providers": {}
        }

        # Check OpenAI
        status["providers"]["openai"] = {
            "configured": self.openai_client is not None,
            "active": self.app_mode == "prod",
            "models": [
                self.model_config.GPT5_NANO,
                self.model_config.GPT5_MINI,
                self.model_config.GPT5_STANDARD
            ]
        }

        # Check Gemini
        status["providers"]["gemini"] = {
            "configured": self.gemini_client is not None,
            "active": self.app_mode == "dev",
            "models": [self.model_config.GEMINI_FLASH, self.model_config.GEMINI_PRO]
        }

        # Check OpenRouter
        status["providers"]["openrouter"] = {
            "configured": self.openrouter_client is not None,
            "active": True,  # Always active as fallback
            "models": [
                self.model_config.OPENROUTER_GPT5_NANO,
                self.model_config.OPENROUTER_GPT5_MINI,
                self.model_config.OPENROUTER_GPT5
            ]
        }

        return status


# Global singleton instance
_cloud_provider_service: Optional[CloudProviderService] = None


def get_cloud_provider() -> CloudProviderService:
    """Get or create the global CloudProviderService instance"""
    global _cloud_provider_service

    if _cloud_provider_service is None:
        _cloud_provider_service = CloudProviderService()

    return _cloud_provider_service


def reinit_cloud_provider() -> CloudProviderService:
    """Reinitialize the cloud provider (useful for testing or mode switches)"""
    global _cloud_provider_service
    _cloud_provider_service = CloudProviderService()
    return _cloud_provider_service

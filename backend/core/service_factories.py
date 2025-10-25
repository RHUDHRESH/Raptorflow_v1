"""
Service Factory Module
Provides centralized initialization and caching of all backend services
"""

import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import os

logger = logging.getLogger(__name__)


class ServiceManager:
    """
    Singleton service manager for initializing and caching all backend services.
    Provides lazy initialization of LLM, embeddings, and other services.
    """

    _instance: Optional["ServiceManager"] = None
    _llm: Optional[object] = None
    _embeddings: Optional[object] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
        return cls._instance

    @property
    def llm(self):
        """Get or initialize the primary LLM (ChatOpenAI or ChatGoogleGenerativeAI)"""
        if self._llm is None:
            self._llm = self._init_llm()
        return self._llm

    @property
    def embeddings(self):
        """Get or initialize the embeddings service"""
        if self._embeddings is None:
            self._embeddings = self._init_embeddings()
        return self._embeddings

    @staticmethod
    def _init_llm():
        """Initialize the primary LLM based on configured providers"""
        app_mode = os.getenv("APP_MODE", "dev").lower()

        # Try OpenAI first if API key is available
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if openai_key:
            logger.info("Initializing ChatOpenAI LLM")
            return ChatOpenAI(
                model="gpt-4-turbo",
                api_key=openai_key,
                temperature=0.7,
                max_tokens=2000
            )

        # Fall back to Google Generative AI
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_key:
            logger.info("Initializing ChatGoogleGenerativeAI LLM")
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
                temperature=0.7
            )

        # If in dev mode, try Ollama (local)
        if app_mode == "dev":
            try:
                logger.info("Attempting to use local Ollama LLM")
                from langchain_ollama import OllamaLLM
                return OllamaLLM(model="mistral")
            except (ImportError, Exception) as e:
                logger.warning(f"Ollama not available: {e}")

        raise RuntimeError(
            "No LLM provider configured. Please set OPENAI_API_KEY, "
            "GEMINI_API_KEY, or ensure Ollama is running for development."
        )

    @staticmethod
    def _init_embeddings():
        """Initialize embeddings service"""
        try:
            from langchain_openai import OpenAIEmbeddings
            openai_key = os.getenv("OPENAI_API_KEY", "").strip()
            if openai_key:
                logger.info("Initializing OpenAI Embeddings")
                return OpenAIEmbeddings(api_key=openai_key)
        except Exception as e:
            logger.warning(f"OpenAI embeddings not available: {e}")

        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
            if gemini_key:
                logger.info("Initializing Google Generative AI Embeddings")
                return GoogleGenerativeAIEmbeddings(google_api_key=gemini_key)
        except Exception as e:
            logger.warning(f"Google embeddings not available: {e}")

        # Fallback to sentence-transformers
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            logger.info("Using HuggingFace Embeddings (CPU-based)")
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise RuntimeError("Could not initialize any embeddings service")

    def reset(self):
        """Reset all cached services (useful for testing)"""
        self._llm = None
        self._embeddings = None
        logger.info("ServiceManager services reset")


# Provide singleton instance
_service_manager = ServiceManager()


def get_service_manager() -> ServiceManager:
    """Get the singleton ServiceManager instance"""
    return _service_manager

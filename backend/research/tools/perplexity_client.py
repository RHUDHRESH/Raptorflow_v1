"""
Perplexity Sonar API Client

Integration with Perplexity's conversational search API.
Provides AI-powered answers with citations from real-time web search.
"""

import logging
import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PerplexityClient:
    """
    Client for Perplexity Sonar API.

    Provides conversational search with:
    - Real-time web search integration
    - Automatic citation and source tracking
    - Multi-turn conversation support
    - Configurable search domains
    """

    BASE_URL = "https://api.perplexity.ai"
    DEFAULT_MODEL = "sonar-pro"  # Latest available model

    def __init__(self, api_key: str):
        """
        Initialize Perplexity client.

        Args:
            api_key: Perplexity API key
        """
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """
        Ensure aiohttp session is initialized.

        Returns:
            Active aiohttp ClientSession
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        search_domain_filter: Optional[List[str]] = None,
        return_citations: bool = True,
        return_images: bool = False,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """
        Execute a chat completion request with Perplexity Sonar API.

        Args:
            messages: List of message dictionaries (role, content)
            model: Model to use (default: sonar-pro)
            search_domain_filter: Domains to prioritize (academic, news, technical)
            return_citations: Include citations in response
            return_images: Include images in response
            max_tokens: Maximum response tokens
            temperature: Response temperature (0-1)
            top_p: Top-p sampling parameter

        Returns:
            API response with answer and citations
        """
        session = await self._ensure_session()
        model = model or self.DEFAULT_MODEL

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "return_images": return_images,
            "search_recency_filter": "month",
            "search_domain_filter": search_domain_filter or ["academic", "news", "technical"]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            logger.debug(f"Calling Perplexity API with model={model}, messages={len(messages)}")

            async with session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Perplexity API error {response.status}: {error_text}")
                    raise Exception(f"Perplexity API error: {response.status}")

                data = await response.json()
                logger.debug(f"Perplexity response received: {len(data.get('citations', []))} citations")
                return data

        except asyncio.TimeoutError:
            logger.error("Perplexity API request timed out")
            raise
        except Exception as e:
            logger.error(f"Perplexity API request failed: {e}")
            raise

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Stream chat completion for real-time response.

        Args:
            messages: List of message dictionaries
            model: Model to use
            **kwargs: Additional parameters

        Yields:
            Streamed response chunks
        """
        session = await self._ensure_session()
        model = model or self.DEFAULT_MODEL

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Streaming API error: {response.status}")

                async for line in response.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str != "[DONE]":
                                try:
                                    data = json.loads(data_str)
                                    yield data
                                except json.JSONDecodeError:
                                    continue

        except Exception as e:
            logger.error(f"Streaming request failed: {e}")
            raise

    async def close(self):
        """
        Close the aiohttp session.
        """
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

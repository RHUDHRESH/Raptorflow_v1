"""
Exa.ai Neural Search Client

Integration with Exa's semantic/neural search API.
Uses embeddings to find semantically similar content beyond keyword matching.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ExaClient:
    """
    Client for Exa.ai neural search API.

    Features:
    - Neural/semantic search using embeddings
    - Auto-prompt for query optimization
    - Category filtering
    - Date range filtering
    - Real-time indexing
    """

    BASE_URL = "https://api.exa.ai"

    def __init__(self, api_key: str):
        """
        Initialize Exa client.

        Args:
            api_key: Exa API key
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

    async def search(
        self,
        query: str,
        num_results: int = 50,
        type: str = "neural",
        use_autoprompt: bool = True,
        category: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        domain_filter: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute neural search request.

        Args:
            query: Search query
            num_results: Number of results to return (1-100)
            type: Search type ('neural' or 'keyword')
            use_autoprompt: Let Exa optimize the query
            category: Content category filter
            start_published_date: Filter by publication date (ISO format)
            end_published_date: Filter by publication date (ISO format)
            domain_filter: Only search these domains
            exclude_domains: Exclude these domains

        Returns:
            Search results with metadata
        """
        session = await self._ensure_session()

        payload = {
            "query": query,
            "numResults": min(num_results, 100),
            "type": type,
            "useAutoprompt": use_autoprompt,
            "startPublishedDate": start_published_date,
            "endPublishedDate": end_published_date,
            "category": category
        }

        # Add domain filters if provided
        if domain_filter:
            payload["includeDomains"] = domain_filter
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            logger.debug(f"Calling Exa API with query='{query}', type={type}")

            async with session.post(
                f"{self.BASE_URL}/search",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Exa API error {response.status}: {error_text}")
                    raise Exception(f"Exa API error: {response.status}")

                data = await response.json()
                logger.debug(f"Exa returned {len(data.get('results', []))} results")
                return data

        except Exception as e:
            logger.error(f"Exa API request failed: {e}")
            raise

    async def find_similar(
        self,
        url: str,
        num_results: int = 20,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find semantically similar content to a URL.

        Args:
            url: URL to find similar content for
            num_results: Number of similar results
            category: Content category filter

        Returns:
            Similar content results
        """
        session = await self._ensure_session()

        payload = {
            "url": url,
            "numResults": min(num_results, 100),
            "category": category
        }

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            logger.debug(f"Finding similar content for: {url}")

            async with session.post(
                f"{self.BASE_URL}/findSimilar",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Find similar error: {response.status}")

                return await response.json()

        except Exception as e:
            logger.error(f"Find similar request failed: {e}")
            raise

    async def get_contents(
        self,
        urls: List[str],
        text: bool = True,
        highlights: bool = False
    ) -> Dict[str, Any]:
        """
        Get full content from URLs.

        Args:
            urls: URLs to fetch content from
            text: Extract text content
            highlights: Extract highlights matching search terms

        Returns:
            Content extraction results
        """
        session = await self._ensure_session()

        payload = {
            "urls": urls,
            "text": text,
            "highlights": highlights
        }

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            logger.debug(f"Getting contents for {len(urls)} URLs")

            async with session.post(
                f"{self.BASE_URL}/getContents",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Get contents error: {response.status}")

                return await response.json()

        except Exception as e:
            logger.error(f"Get contents request failed: {e}")
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

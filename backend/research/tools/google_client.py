"""
Google Custom Search Client

Integration with Google Custom Search API.
Traditional web search with ranking and snippets.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class GoogleSearchClient:
    """
    Client for Google Custom Search API.

    Features:
    - Custom search engine queries
    - Configurable result count
    - Safe search filtering
    - Result snippets and metadata
    """

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, api_key: str, search_engine_id: str):
        """
        Initialize Google Search client.

        Args:
            api_key: Google API key with Custom Search enabled
            search_engine_id: Custom search engine ID
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
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
        num_results: int = 20,
        start_index: int = 1,
        safe_search: str = "off",
        search_type: str = "web",
        filter_exact: Optional[str] = None,
        lr: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute custom search request.

        Args:
            query: Search query
            num_results: Number of results (1-10 per request)
            start_index: Starting index for pagination
            safe_search: Safe search level (off, medium, high)
            search_type: Type of search ('web', 'image', etc.)
            filter_exact: Filter for exact results
            lr: Language restriction (e.g., 'lang_en')

        Returns:
            Search results with metadata
        """
        session = await self._ensure_session()

        # Google Custom Search limits to 10 per request
        num_results = min(num_results, 10)

        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": num_results,
            "start": start_index,
            "safe": safe_search,
            "searchType": search_type
        }

        if filter_exact:
            params["filter"] = filter_exact
        if lr:
            params["lr"] = lr

        try:
            logger.debug(f"Calling Google Custom Search: {query}")

            async with session.get(
                f"{self.BASE_URL}?{urlencode(params)}",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Google API error {response.status}: {error_text}")
                    raise Exception(f"Google API error: {response.status}")

                data = await response.json()

                # Check for API errors
                if "error" in data:
                    logger.error(f"Google API returned error: {data['error']}")
                    raise Exception(f"Google API error: {data['error']}")

                logger.debug(f"Google returned {len(data.get('items', []))} results")
                return data

        except Exception as e:
            logger.error(f"Google search request failed: {e}")
            raise

    async def search_all(
        self,
        query: str,
        max_results: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Execute paginated search to get more results.

        Args:
            query: Search query
            max_results: Maximum results to retrieve
            **kwargs: Additional search parameters

        Returns:
            List of all search results
        """
        all_results = []
        start_index = 1

        # Google Custom Search limits to 100 queries per day
        max_pages = min((max_results + 9) // 10, 10)

        try:
            for page in range(max_pages):
                kwargs["num_results"] = min(10, max_results - len(all_results))
                kwargs["start_index"] = start_index

                response = await self.search(query, **kwargs)
                items = response.get("items", [])

                if not items:
                    break

                all_results.extend(items)

                if len(all_results) >= max_results:
                    break

                start_index += 10

            return all_results[:max_results]

        except Exception as e:
            logger.error(f"Paginated search failed: {e}")
            return all_results

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

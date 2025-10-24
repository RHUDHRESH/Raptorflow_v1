from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict

import httpx
from langchain.tools import BaseTool


class PerplexitySearchTool(BaseTool):
    name = "perplexity_search"
    description = """
    Deep research using Perplexity AI. Modes:
    - research: General research query (Sonar Pro model)
    - competitor: Competitor analysis (focused search)
    - trends: Latest trends in a topic (time-filtered)
    - news: Recent news about topic (last 7 days)
    
    Examples:
    perplexity_search(query='competitors of Tesla in EV market', mode='competitor')
    perplexity_search(query='sustainable fashion trends 2025', mode='trends')
    perplexity_search(query='latest AI news', mode='news', recency='day')
    """

    _BASE_URL = "https://api.perplexity.ai/chat/completions"
    _SYSTEM_PROMPTS: Dict[str, str] = {
        "research": "You are a research assistant. Provide comprehensive findings with authoritative sources.",
        "competitor": "You are a competitive analyst. Focus on market positioning, strengths, weaknesses, and unique value propositions.",
        "trends": "You are a trend analyst. Identify emerging patterns, growing topics, and future directions.",
        "news": "You are a news analyst. Summarize recent developments with key facts and implications.",
    }

    def __init__(self) -> None:
        super().__init__()
        self.api_key = os.getenv("PERPLEXITY_API_KEY", "").strip()

    def _build_payload(
        self,
        query: str,
        system_prompt: str,
        max_tokens: int,
        recency: str,
        return_images: bool,
        return_related: bool,
    ) -> Dict[str, Any]:
        return {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "return_images": return_images,
            "return_related_questions": return_related,
            "search_recency_filter": recency,
        }

    def _format_success(
        self,
        raw: Dict[str, Any],
        query: str,
        mode: str,
        return_images: bool,
        return_related: bool,
    ) -> Dict[str, Any]:
        return {
            "query": query,
            "mode": mode,
            "findings": raw["choices"][0]["message"]["content"],
            "citations": raw.get("citations", []),
            "images": raw.get("images", []) if return_images else [],
            "related_questions": raw.get("related_questions", []) if return_related else [],
            "timestamp": datetime.utcnow().isoformat(),
            "tokens_used": raw.get("usage", {}).get("total_tokens"),
        }

    def _error_payload(self, query: str, message: str) -> str:
        return json.dumps({"error": True, "message": message, "query": query})

    def _system_prompt(self, mode: str) -> str:
        return self._SYSTEM_PROMPTS.get(mode, self._SYSTEM_PROMPTS["research"])

    def _raise_for_api_key(self) -> None:
        if not self.api_key:
            raise RuntimeError("PERPLEXITY_API_KEY environment variable is not set")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _run(
        self,
        query: str,
        mode: str = "research",
        recency: str = "month",
        return_images: bool = False,
        return_related: bool = False,
        max_tokens: int = 1000,
    ) -> str:
        try:
            self._raise_for_api_key()
            payload = self._build_payload(
                query=query,
                system_prompt=self._system_prompt(mode),
                max_tokens=max_tokens,
                recency=recency,
                return_images=return_images,
                return_related=return_related,
            )

            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    self._BASE_URL,
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()

            result = self._format_success(
                response.json(),
                query=query,
                mode=mode,
                return_images=return_images,
                return_related=return_related,
            )
            return json.dumps(result, indent=2)
        except httpx.HTTPError as exc:
            return self._error_payload(query, f"Perplexity API error: {exc}")
        except Exception as exc:
            return self._error_payload(query, f"Unexpected error: {exc}")

    async def _arun(self, *args, **kwargs) -> str:
        query = kwargs.get("query")
        mode = kwargs.get("mode", "research")
        recency = kwargs.get("recency", "month")
        return_images = kwargs.get("return_images", False)
        return_related = kwargs.get("return_related", False)
        max_tokens = kwargs.get("max_tokens", 1000)

        try:
            self._raise_for_api_key()
            payload = self._build_payload(
                query=query,
                system_prompt=self._system_prompt(mode),
                max_tokens=max_tokens,
                recency=recency,
                return_images=return_images,
                return_related=return_related,
            )

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self._BASE_URL,
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()

            result = self._format_success(
                response.json(),
                query=query,
                mode=mode,
                return_images=return_images,
                return_related=return_related,
            )
            return json.dumps(result, indent=2)
        except httpx.HTTPError as exc:
            return self._error_payload(query, f"Perplexity API error: {exc}")
        except Exception as exc:
            return self._error_payload(query, f"Unexpected error: {exc}")

"""
Searcher Agent - Multi-Engine Search Orchestrator

Phase 3 of research workflow:
- Executes searches across multiple engines in parallel
- Perplexity Sonar API for conversational AI search
- Exa.ai for neural/semantic search
- Google Custom Search for traditional web search
- Aggregates and deduplicates results
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..state import ResearchState
from ..tools import (
    PerplexityClient,
    ExaClient,
    GoogleSearchClient
)

logger = logging.getLogger(__name__)


class SearcherAgent:
    """
    Executes parallel searches across multiple engines:
    - Perplexity Sonar API (conversational search with citations)
    - Exa.ai (neural/semantic search)
    - Google Custom Search (traditional web search)
    """

    def __init__(
        self,
        perplexity_api_key: str,
        exa_api_key: str,
        google_api_key: str,
        google_search_engine_id: str,
        llm: Optional[ChatOpenAI] = None
    ):
        """
        Initialize searcher with API clients.

        Args:
            perplexity_api_key: Perplexity API key
            exa_api_key: Exa.ai API key
            google_api_key: Google API key
            google_search_engine_id: Google Custom Search engine ID
            llm: Language model for query optimization
        """
        self.perplexity = PerplexityClient(perplexity_api_key)
        self.exa = ExaClient(exa_api_key)
        self.google = GoogleSearchClient(google_api_key, google_search_engine_id)
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.2)

    async def process(self, state: ResearchState) -> ResearchState:
        """
        Phase 3: Multi-Engine Search Execution

        Args:
            state: Current research state

        Returns:
            Updated state with search results from all engines
        """
        logger.info("Search phase started")

        sub_questions = state["sub_questions"]
        priority_order = state.get("priority_order", [f"q{i}" for i in range(len(sub_questions))])

        all_results = []
        perplexity_results = []
        exa_results = []
        google_results = []
        search_queries_executed = []

        state["current_phase"] = "searching"

        # Execute searches for each sub-question
        for question_idx, sub_question in enumerate(sub_questions):
            logger.info(f"Searching for: {sub_question[:80]}")

            # Optimize query for search engines
            optimized_query = await self._optimize_query(sub_question)

            # Execute parallel searches across all engines
            search_tasks = [
                self._search_perplexity(optimized_query, sub_question),
                self._search_exa(optimized_query, sub_question),
                self._search_google(optimized_query, sub_question)
            ]

            results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Collect results
            perplexity_batch = results[0] if not isinstance(results[0], Exception) else []
            exa_batch = results[1] if not isinstance(results[1], Exception) else []
            google_batch = results[2] if not isinstance(results[2], Exception) else []

            perplexity_results.extend(perplexity_batch)
            exa_results.extend(exa_batch)
            google_results.extend(google_batch)

            all_results.extend([
                r for batch in [perplexity_batch, exa_batch, google_batch]
                for r in batch
            ])

            # Record execution
            search_queries_executed.append({
                "sub_question_index": question_idx,
                "original_question": sub_question,
                "optimized_query": optimized_query,
                "timestamp": datetime.now().isoformat(),
                "perplexity_results": len(perplexity_batch),
                "exa_results": len(exa_batch),
                "google_results": len(google_batch),
                "total_results": len(perplexity_batch) + len(exa_batch) + len(google_batch)
            })

        logger.info(f"Search complete. Total results: {len(all_results)}")

        state["search_results"] = all_results
        state["perplexity_results"] = perplexity_results
        state["exa_results"] = exa_results
        state["google_results"] = google_results
        state["search_queries_executed"] = search_queries_executed

        # Calculate metadata
        state["search_metadata"] = {
            "total_results": len(all_results),
            "perplexity_results": len(perplexity_results),
            "exa_results": len(exa_results),
            "google_results": len(google_results),
            "unique_urls": len(set(
                r.get("url") for r in all_results if "url" in r
            )),
            "queries_executed": len(search_queries_executed),
            "timestamp": datetime.now().isoformat()
        }

        state["current_phase"] = "fetching"
        return state

    async def _optimize_query(self, question: str) -> str:
        """
        Optimize question for search engine queries.

        Args:
            question: Research sub-question

        Returns:
            Optimized search query
        """
        prompt = f"""
        Convert this research question into an optimized search query.
        Make it concise, keyword-focused, and search-engine friendly.

        Research Question: "{question}"

        Requirements:
        - Remove helper words like "what", "how", "why"
        - Focus on key concepts
        - Use quotes for phrases if needed
        - Keep it under 10 words
        - Include relevant keywords

        Return ONLY the optimized query (no JSON, no explanation).
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip().strip('"')
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            # Return simplified version
            return question.replace("?", "").lower()[:100]

    async def _search_perplexity(
        self,
        query: str,
        original_question: str
    ) -> List[Dict[str, Any]]:
        """
        Perplexity Sonar API search with citations.

        Args:
            query: Optimized search query
            original_question: Original sub-question for reference

        Returns:
            List of search results with citations
        """
        try:
            logger.debug(f"Searching Perplexity: {query}")

            response = await self.perplexity.chat_completion(
                model="sonar-pro",  # Use pro for better quality, sonar for speed
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research assistant providing detailed, comprehensive answers with proper citations."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                search_domain_filter=["academic", "news", "technical"],
                return_citations=True,
                return_images=False,
                max_tokens=4000
            )

            answer = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = response.get("citations", [])

            results = []

            # Add aggregated result
            if answer:
                results.append({
                    "engine": "perplexity",
                    "type": "aggregated_answer",
                    "question": original_question,
                    "answer": answer,
                    "citations": citations,
                    "timestamp": datetime.now().isoformat(),
                    "score": 0.95  # High score for Perplexity's synthesized answers
                })

            # Add individual citation sources
            for i, citation in enumerate(citations):
                results.append({
                    "engine": "perplexity",
                    "type": "citation",
                    "question": original_question,
                    "url": citation.get("url", ""),
                    "title": citation.get("title", ""),
                    "snippet": citation.get("snippet", "")[:500],
                    "source_index": i,
                    "timestamp": datetime.now().isoformat(),
                    "score": 0.85
                })

            logger.debug(f"Perplexity returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Perplexity search failed: {e}")
            return []

    async def _search_exa(
        self,
        query: str,
        original_question: str
    ) -> List[Dict[str, Any]]:
        """
        Exa.ai neural/semantic search.

        Args:
            query: Search query
            original_question: Original sub-question for reference

        Returns:
            List of semantically similar results
        """
        try:
            logger.debug(f"Searching Exa: {query}")

            response = await self.exa.search(
                query=query,
                num_results=50,
                type="neural",  # Neural search for semantic understanding
                use_autoprompt=True,  # Let Exa optimize the query
                category="research paper|blog|news|article",
                start_published_date="2023-01-01"  # Recent content
            )

            results = []

            for result in response.get("results", []):
                results.append({
                    "engine": "exa",
                    "type": "search_result",
                    "question": original_question,
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "text": result.get("text", "")[:1000],
                    "published_date": result.get("publishedDate"),
                    "author": result.get("author"),
                    "score": result.get("score", 0),
                    "timestamp": datetime.now().isoformat()
                })

            logger.debug(f"Exa returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Exa search failed: {e}")
            return []

    async def _search_google(
        self,
        query: str,
        original_question: str
    ) -> List[Dict[str, Any]]:
        """
        Google Custom Search.

        Args:
            query: Search query
            original_question: Original sub-question for reference

        Returns:
            List of Google search results
        """
        try:
            logger.debug(f"Searching Google: {query}")

            response = await self.google.search(
                query=query,
                num_results=20,
                safe_search="off"
            )

            results = []

            for i, item in enumerate(response.get("items", [])):
                results.append({
                    "engine": "google",
                    "type": "search_result",
                    "question": original_question,
                    "url": item.get("link", ""),
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", "")[:500],
                    "index": i,
                    "timestamp": datetime.now().isoformat(),
                    "score": 0.8 - (i * 0.05)  # Decay score by position
                })

            logger.debug(f"Google returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []

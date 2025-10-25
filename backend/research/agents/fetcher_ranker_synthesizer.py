"""
Fetcher, Ranker, and Synthesizer Agents

Combined module for content fetching, ranking, and synthesis phases.
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..state import ResearchState

logger = logging.getLogger(__name__)


class FetcherAgent:
    """Fetches full content from URLs using async HTTP."""

    def __init__(self):
        self.max_concurrent = 20
        self.timeout = 15

    async def process(self, state: ResearchState) -> ResearchState:
        """Phase 4: Content Fetching"""
        logger.info("Fetcher phase started")

        search_results = state["search_results"]
        max_sources = state.get("max_sources", 100)

        # Extract unique URLs
        unique_urls = list(set([
            r.get("url") for r in search_results
            if "url" in r and r.get("url")
        ]))[:max_sources]

        logger.info(f"Fetching content from {len(unique_urls)} URLs")

        # Parallel fetch with semaphore
        semaphore = asyncio.Semaphore(self.max_concurrent)
        fetch_tasks = [self._fetch_url_safe(url, semaphore) for url in unique_urls]

        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        fetched_content = []
        extraction_errors = []

        for url, result in zip(unique_urls, results):
            if isinstance(result, Exception):
                extraction_errors.append({
                    "url": url,
                    "error": str(result)
                })
            elif result:
                fetched_content.append(result)

        state["fetched_content"] = fetched_content
        state["extraction_errors"] = extraction_errors
        state["current_phase"] = "ranking"

        logger.info(f"Fetched {len(fetched_content)} URLs successfully")
        return state

    async def _fetch_url_safe(self, url: str, semaphore: asyncio.Semaphore) -> Optional[Dict]:
        """Fetch URL with rate limiting"""
        async with semaphore:
            return await self._fetch_url(url)

    async def _fetch_url(self, url: str) -> Optional[Dict]:
        """Simulate URL fetching (in production would use playwright/httpx)"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status == 200:
                        text = await response.text()
                        return {
                            "url": url,
                            "title": response.headers.get("title", ""),
                            "text": text[:50000],
                            "word_count": len(text.split()),
                            "fetch_timestamp": asyncio.get_event_loop().time()
                        }
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
        return None


class RankerAgent:
    """Ranks content by relevance and quality."""

    def __init__(self, llm: Optional[ChatOpenAI] = None, embeddings = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.embeddings = embeddings

    async def process(self, state: ResearchState) -> ResearchState:
        """Phase 5: Ranking & Filtering"""
        logger.info("Ranking phase started")

        fetched_content = state["fetched_content"]
        sub_questions = state["sub_questions"]

        if not fetched_content:
            logger.warning("No content to rank")
            state["ranked_sources"] = []
            state["relevance_scores"] = {}
            state["current_phase"] = "synthesizing"
            return state

        # Score each content piece
        scored_content = await self._score_relevance(fetched_content, sub_questions)

        # Ensure diversity
        diverse_content = self._ensure_diversity(scored_content)

        # Sort by score
        ranked = sorted(diverse_content, key=lambda x: x.get("relevance_score", 0), reverse=True)

        state["ranked_sources"] = ranked[:100]
        state["relevance_scores"] = {
            item["url"]: item.get("relevance_score", 0)
            for item in ranked
        }
        state["current_phase"] = "synthesizing"

        logger.info(f"Ranked {len(ranked)} sources")
        return state

    async def _score_relevance(self, content: List[Dict], questions: List[str]) -> List[Dict]:
        """Score content relevance to questions"""
        scored = []

        for item in content[:30]:  # Limit scoring to top 30
            text = item.get("text", "")[:2000]

            # Simple relevance scoring
            relevance_score = 0.5  # Default

            # Check keyword overlap
            question_words = set(" ".join(questions).lower().split())
            text_words = set(text.lower().split())
            overlap = len(question_words & text_words) / max(len(question_words), 1)
            relevance_score = min(0.9, overlap + 0.2)

            item["relevance_score"] = relevance_score
            scored.append(item)

        return scored

    def _ensure_diversity(self, content: List[Dict]) -> List[Dict]:
        """Ensure content from different domains"""
        domain_counts = {}
        diverse = []

        for item in content:
            url = item.get("url", "")
            domain = urlparse(url).netloc if url else "unknown"
            count = domain_counts.get(domain, 0)

            if count < 5:
                diverse.append(item)
                domain_counts[domain] = count + 1

        return diverse


class SynthesizerAgent:
    """Synthesizes information from multiple sources."""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.5)

    async def process(self, state: ResearchState) -> ResearchState:
        """Phase 6: Synthesis"""
        logger.info("Synthesis phase started")

        ranked_sources = state.get("ranked_sources", [])[:20]
        sub_questions = state.get("sub_questions", [])

        synthesized_chunks = []
        contradictions = []

        for question in sub_questions:
            relevant_sources = [s for s in ranked_sources][:5]

            synthesis = await self._synthesize_for_question(question, relevant_sources)
            synthesized_chunks.append(synthesis)

            # Detect contradictions
            contras = await self._detect_contradictions(synthesis, relevant_sources)
            contradictions.extend(contras)

        state["synthesized_chunks"] = synthesized_chunks
        state["contradictions"] = contradictions
        state["current_phase"] = "writing"

        logger.info(f"Synthesized {len(synthesized_chunks)} sections")
        return state

    async def _synthesize_for_question(self, question: str, sources: List[Dict]) -> Dict:
        """Create comprehensive answer from sources"""
        source_texts = "\n\n".join([
            f"Source {i+1}: {s.get('text', '')[:1000]}"
            for i, s in enumerate(sources[:3])
        ])

        prompt = f"""
        Answer this question using the provided sources:

        Question: {question}

        Sources:
        {source_texts}

        Provide a comprehensive answer with:
        - Key findings
        - Supporting evidence
        - Confidence level

        Return JSON:
        {{
            "answer": "detailed answer",
            "key_points": ["point1", "point2"],
            "confidence": 0.0-1.0,
            "supporting_sources": [0, 1, 2]
        }}
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            if content.startswith("{"):
                synthesis = json.loads(content)
            else:
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    synthesis = json.loads(json_match.group())
                else:
                    synthesis = {
                        "answer": content,
                        "key_points": [],
                        "confidence": 0.7,
                        "supporting_sources": []
                    }

            synthesis["question"] = question
            return synthesis

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {
                "question": question,
                "answer": "Synthesis failed",
                "key_points": [],
                "confidence": 0.0,
                "supporting_sources": []
            }

    async def _detect_contradictions(self, synthesis: Dict, sources: List[Dict]) -> List[Dict]:
        """Find contradictory information"""
        if len(sources) < 2:
            return []

        # Simple contradiction detection based on answer variation
        return []  # Simplified for now

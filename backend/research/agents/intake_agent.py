"""
Intake Agent - Query Understanding & Clarification

Phase 1 of research workflow:
- Analyzes user query for intent and domain
- Detects ambiguities that need clarification
- Expands query with context
- Sets research parameters
"""

import logging
import json
from typing import Dict, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from ..state import ResearchState

logger = logging.getLogger(__name__)


class IntakeAgent:
    """
    Analyzes user query, detects ambiguity, optionally requests clarification.
    Uses advanced NLP to understand research intent, domain, and complexity.
    """

    INTENT_TYPES = {
        "technical": "In-depth technical/engineering research",
        "business": "Market research, business intelligence, competitive analysis",
        "academic": "Academic research, literature review, theoretical analysis",
        "fact_check": "Verify specific claims, fact-checking",
        "comparison": "Compare alternatives, products, approaches",
        "trend": "Identify trends, patterns, developments",
        "how_to": "Step-by-step instructions, tutorials, procedures"
    }

    DOMAINS = [
        "machine_learning", "healthcare", "finance", "technology",
        "education", "environment", "energy", "transportation",
        "agriculture", "manufacturing", "retail", "legal",
        "politics", "science", "research", "general"
    ]

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize intake agent with LLM.

        Args:
            llm: Language model instance (uses default if not provided)
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.intent_examples = self._build_intent_examples()

    async def process(self, state: ResearchState) -> ResearchState:
        """
        Phase 1: Query Intake & Understanding

        Args:
            state: Current research state

        Returns:
            Updated state with clarified query and research parameters
        """
        logger.info(f"Intake phase started for query: {state['user_query'][:100]}")

        query = state["user_query"]
        state["current_phase"] = "intake"

        # 1. Analyze intent
        intent_analysis = await self._analyze_intent(query)
        state["research_intent"] = intent_analysis["type"]
        state["research_domain"] = intent_analysis["domain"]

        logger.debug(f"Detected intent: {intent_analysis['type']}, domain: {intent_analysis['domain']}")

        # 2. Check for ambiguity
        ambiguity_check = await self._check_ambiguity(query)

        if ambiguity_check["is_ambiguous"]:
            logger.warning(f"Query ambiguity detected: {ambiguity_check['reasons']}")
            state["requires_clarification"] = True
            state["clarification_question"] = ambiguity_check["question"]
            state["current_phase"] = "clarification_needed"
            # Workflow will pause here for user input
            return state

        logger.info("Query is sufficiently clear, proceeding")

        # 3. Expand query with context
        clarified = await self._expand_query(query, intent_analysis)
        state["clarified_query"] = clarified
        logger.debug(f"Expanded query: {clarified[:200]}")

        # 4. Set research parameters
        state["query_type"] = self._determine_query_type(intent_analysis)
        state["max_depth"] = self._calculate_depth(intent_analysis)

        logger.info(f"Query type: {state['query_type']}, depth: {state['max_depth']}")

        state["current_phase"] = "planning"
        return state

    async def _analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify research intent and domain.

        Args:
            query: User's research query

        Returns:
            Dictionary with intent type and domain
        """
        intent_options = ", ".join([f"{k}: {v}" for k, v in self.INTENT_TYPES.items()])
        domain_options = ", ".join(self.DOMAINS)

        prompt = f"""
        Analyze this research query and classify its intent and domain.

        Query: "{query}"

        Available intent types:
        {intent_options}

        Available domains:
        {domain_options}

        Respond with ONLY valid JSON:
        {{
            "type": "<one of the intent types>",
            "domain": "<one of the domains or 'general'>",
            "complexity": "simple|moderate|complex",
            "time_sensitive": true|false,
            "requires_citations": true|false,
            "reasoning": "brief explanation"
        }}
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # Extract JSON from response
            if content.startswith("{"):
                result = json.loads(content)
            else:
                # Try to extract JSON if wrapped in markdown
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON in response")

            # Validate result
            if "type" not in result or result["type"] not in self.INTENT_TYPES:
                result["type"] = "general"
            if "domain" not in result or result["domain"] not in self.DOMAINS:
                result["domain"] = "general"

            return result

        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {
                "type": "general",
                "domain": "general",
                "complexity": "moderate",
                "time_sensitive": False,
                "requires_citations": True,
                "reasoning": "Default analysis due to error"
            }

    async def _check_ambiguity(self, query: str) -> Dict[str, Any]:
        """
        Detect if query needs clarification.

        Args:
            query: User's research query

        Returns:
            Dictionary indicating ambiguity status
        """
        prompt = f"""
        Is this research query clear and specific enough to execute immediately,
        or does it require clarification before starting research?

        Query: "{query}"

        Consider:
        - Is the query scope clear (is it too broad/narrow)?
        - Are there undefined terms or acronyms?
        - Are multiple interpretations possible?
        - Is the desired outcome clear?

        Respond with ONLY valid JSON:
        {{
            "is_ambiguous": true|false,
            "reasons": ["reason1", "reason2"] or [],
            "question": "What specific aspect would you like to focus on?" or null,
            "severity": "none|low|medium|high"
        }}
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            if content.startswith("{"):
                result = json.loads(content)
            else:
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"is_ambiguous": False, "reasons": [], "question": None, "severity": "none"}

            return result

        except Exception as e:
            logger.error(f"Ambiguity check failed: {e}")
            return {"is_ambiguous": False, "reasons": [], "question": None, "severity": "none"}

    async def _expand_query(self, query: str, intent: Dict[str, Any]) -> str:
        """
        Add context and specificity to query for better research coverage.

        Args:
            query: Original user query
            intent: Intent analysis result

        Returns:
            Expanded, more specific query
        """
        intent_type = intent["type"]
        domain = intent["domain"]

        prompt = f"""
        Expand and improve this research query to make it more specific
        and comprehensive while preserving the original intent.

        Original query: "{query}"
        Research intent: {intent_type}
        Domain: {domain}

        Create an enhanced query that:
        - Is more specific and concrete
        - Clarifies key terms if needed
        - Sets appropriate scope
        - Maintains the original intent
        - Adds relevant context

        Respond with ONLY the improved query (no JSON, no explanations).
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip().strip('"')
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return query

    def _determine_query_type(self, intent: Dict[str, Any]) -> str:
        """
        Determine research type based on intent.

        Args:
            intent: Intent analysis result

        Returns:
            Query type: 'breadth_first' | 'depth_first' | 'hybrid'
        """
        intent_type = intent["type"]
        complexity = intent.get("complexity", "moderate")

        if intent_type in ["comparison", "trend"]:
            return "breadth_first"
        elif intent_type in ["technical", "academic"]:
            return "depth_first"
        else:
            return "hybrid"

    def _calculate_depth(self, intent: Dict[str, Any]) -> int:
        """
        Calculate research depth based on complexity.

        Args:
            intent: Intent analysis result

        Returns:
            Max research depth (number of sub-question levels)
        """
        complexity = intent.get("complexity", "moderate")

        complexity_to_depth = {
            "simple": 1,
            "moderate": 2,
            "complex": 3
        }

        return complexity_to_depth.get(complexity, 2)

    def _build_intent_examples(self) -> Dict[str, list]:
        """
        Build examples for intent classification.

        Returns:
            Dictionary of intent examples
        """
        return {
            "technical": [
                "How does transformer architecture work?",
                "Explain vector databases and their optimization"
            ],
            "business": [
                "What are the top 5 AI startups in 2024?",
                "Compare cloud providers for enterprise deployment"
            ],
            "academic": [
                "Survey recent advances in retrieval-augmented generation",
                "What is the state of research in quantum computing?"
            ],
            "fact_check": [
                "Is it true that AI can outperform humans in all tasks?",
                "Can we reverse climate change?"
            ],
            "comparison": [
                "Compare Python vs Rust for systems programming",
                "What's the difference between LLMs and MLMs?"
            ]
        }

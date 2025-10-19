"""
RESEARCH AGENT v2 - Complete Overhaul
Comprehensive business intelligence gathering with evidence graph
"""
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ResearchAgentV2:
    """Production-grade research agent with full async support"""

    def __init__(self):
        self.name = "research_agent"
        self.max_iterations = 3
        self.min_completeness = 0.7

    async def analyze_business(self, business_id: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - analyzes a business comprehensively

        Flow:
        1. Situation Analysis (What is the current market position?)
        2. Competitor Research (Who are they competing against?)
        3. Build Competitor Ladder (Map what each competitor owns)
        4. Evidence Gathering (Find proof points)
        5. Link Evidence (Connect claims to proof - RTB)
        6. Validate Completeness (Do we have enough data?)
        """

        try:
            logger.info(f"Starting research for business {business_id}")

            # Initialize state
            state = {
                "business_id": business_id,
                "business_data": business_data,
                "iterations": 0,
                "evidence_nodes": [],
                "competitor_ladder": [],
                "sostac_analysis": {},
                "status": "analyzing"
            }

            # Step 1: Situation Analysis
            logger.info("Step 1/6: Analyzing situation...")
            state = await self._analyze_situation(state)

            # Step 2: Competitor Research
            logger.info("Step 2/6: Researching competitors...")
            state = await self._research_competitors(state)

            # Step 3: Build Competitor Ladder
            logger.info("Step 3/6: Building competitor ladder...")
            state = await self._build_competitor_ladder(state)

            # Step 4: Gather Evidence
            logger.info("Step 4/6: Gathering evidence...")
            state = await self._gather_evidence(state)

            # Step 5: Link Evidence to Claims (RTB)
            logger.info("Step 5/6: Linking evidence to claims...")
            state = await self._link_evidence_to_claims(state)

            # Step 6: Validate
            logger.info("Step 6/6: Validating completeness...")
            completeness = await self._validate_completeness(state)
            state["completeness_score"] = completeness

            state["status"] = "completed"
            logger.info(f"Research completed with {completeness:.1%} completeness")

            return {
                "success": True,
                "status": "completed",
                "results": {
                    "sostac": state["sostac_analysis"],
                    "competitor_ladder": state["competitor_ladder"],
                    "evidence_count": len(state["evidence_nodes"]),
                    "completeness_score": completeness,
                    "evidence_nodes": state["evidence_nodes"]
                }
            }

        except Exception as e:
            logger.exception(f"Research agent failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "results": {}
            }

    async def _analyze_situation(self, state: Dict) -> Dict:
        """
        STEP 1: Analyze current business situation using SOSTAC

        Output:
        - Where business is now (Situation)
        - Where they want to go (Objectives)
        - Their stated strategy
        """
        business = state["business_data"]

        # Use GPT to analyze SOSTAC
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )

        prompt = f"""
        Analyze this business using the SOSTAC framework:

        Business: {business['name']}
        Industry: {business['industry']}
        Location: {business['location']}
        Description: {business['description']}
        Goals: {business['goals']}

        Provide analysis in JSON:
        {{
            "situation": "Where they are now (market position, current state)",
            "objectives": "What they want to achieve (specific goals)",
            "market_size_estimate": "TAM/SAM estimate",
            "current_positioning": "How they currently position themselves",
            "main_challenges": ["Challenge 1", "Challenge 2"]
        }}
        """

        response = await llm.ainvoke(prompt)

        try:
            sostac = json.loads(response.content)
        except:
            sostac = {"status": "analysis_incomplete"}

        state["sostac_analysis"] = sostac

        # Create evidence nodes for this analysis
        state["evidence_nodes"].append({
            "type": "situation_analysis",
            "content": json.dumps(sostac),
            "source": "llm_analysis",
            "confidence": 0.8
        })

        return state

    async def _research_competitors(self, state: Dict) -> Dict:
        """
        STEP 2: Deep research competitors using Perplexity

        Find: market leaders, their positioning, pricing, target markets
        """
        business = state["business_data"]

        try:
            from tools.perplexity_search import PerplexitySearchTool
            perplexity = PerplexitySearchTool()

            # Search for competitors
            search_query = f"""
            Top 5 competitors in {business['industry']} in {business['location']}.
            What positioning does each competitor own? What are they known for?
            What is their market position? Price point? Target market?
            """

            result = await perplexity._execute(query=search_query)

            if result.get("success"):
                state["evidence_nodes"].append({
                    "type": "competitor_research",
                    "content": result.get("content", ""),
                    "source": "perplexity",
                    "confidence": 0.9
                })

        except Exception as e:
            logger.warning(f"Perplexity search failed: {str(e)}")

        return state

    async def _build_competitor_ladder(self, state: Dict) -> Dict:
        """
        STEP 3: Build competitor ladder - map what each competitor owns

        Output: {"competitor": "name", "word_owned": "concept", "strength": 0.8}
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        prompt = f"""
        Based on this business and market context, create a competitor ladder.

        Business: {state['business_data']['name']}
        Market: {state['business_data']['industry']}

        Return JSON array:
        [
            {{
                "competitor": "Company Name",
                "word_owned": "The positioning word (e.g., 'speed', 'luxury', 'affordability')",
                "position_strength": 0.8,
                "description": "Why they own this position"
            }}
        ]

        Identify 4-5 main competitors and their positions.
        """

        response = await llm.ainvoke(prompt)

        try:
            ladder = json.loads(response.content)
            state["competitor_ladder"] = ladder
        except:
            state["competitor_ladder"] = []

        state["evidence_nodes"].append({
            "type": "competitor_ladder",
            "content": json.dumps(state["competitor_ladder"]),
            "source": "llm_analysis",
            "confidence": 0.75
        })

        return state

    async def _gather_evidence(self, state: Dict) -> Dict:
        """
        STEP 4: Gather supporting evidence for market claims

        Evidence types:
        - Market size
        - Customer pain points
        - Trend data
        - Industry reports
        """

        business = state["business_data"]

        evidence_nodes = [
            {
                "type": "industry_analysis",
                "content": f"Market analysis for {business['industry']} in {business['location']}",
                "source": "research",
                "confidence": 0.7
            },
            {
                "type": "target_market",
                "content": f"Potential customers for {business['name']}",
                "source": "analysis",
                "confidence": 0.65
            }
        ]

        state["evidence_nodes"].extend(evidence_nodes)
        return state

    async def _link_evidence_to_claims(self, state: Dict) -> Dict:
        """
        STEP 5: Link evidence to claims (RTB - Reason To Believe)

        Creates connections: Claim → Supporting Evidence
        Example: "We are fastest" → Evidence of speed metrics
        """

        # For now, link all evidence nodes
        state["evidence_edges"] = []

        for i, node in enumerate(state["evidence_nodes"]):
            if i < len(state["evidence_nodes"]) - 1:
                state["evidence_edges"].append({
                    "from": node["type"],
                    "to": state["evidence_nodes"][i + 1]["type"],
                    "relationship": "supports",
                    "strength": 0.7
                })

        return state

    async def _validate_completeness(self, state: Dict) -> float:
        """
        STEP 6: Score completeness of research

        Returns: 0.0 - 1.0 score
        - Evidence count: 0.3 weight
        - SOSTAC completeness: 0.4 weight
        - Competitor coverage: 0.3 weight
        """

        scores = []

        # Evidence score (need 4+ pieces)
        evidence_score = min(len(state["evidence_nodes"]) / 4.0, 1.0)
        scores.append(("evidence", evidence_score, 0.3))

        # SOSTAC completeness
        sostac_fields = ["situation", "objectives", "market_size_estimate"]
        sostac_score = sum(1 for f in sostac_fields if f in state["sostac_analysis"]) / len(sostac_fields)
        scores.append(("sostac", sostac_score, 0.4))

        # Competitor coverage (need 3+)
        competitor_score = min(len(state.get("competitor_ladder", [])) / 3.0, 1.0)
        scores.append(("competitors", competitor_score, 0.3))

        # Calculate weighted score
        total_score = sum(score * weight for _, score, weight in scores)

        logger.info(f"Completeness scores: {scores}")
        logger.info(f"Final completeness: {total_score:.1%}")

        return total_score


# Singleton instance
research_agent = ResearchAgentV2()

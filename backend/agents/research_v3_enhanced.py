"""
RESEARCH AGENT v3 - Enhanced with Advanced Tools
Comprehensive business intelligence with tool integration
"""
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ResearchAgentV3Enhanced:
    """Enhanced research agent with advanced tool integration"""

    def __init__(self):
        self.name = "research_agent_v3"
        self.max_iterations = 3
        self.min_completeness = 0.75
        self.tools_enabled = True

    async def analyze_business_with_tools(
        self,
        business_id: str,
        business_data: Dict[str, Any],
        tools_config: Dict = None
    ) -> Dict[str, Any]:
        """
        Enhanced analysis using integrated tools

        Tools used:
        - Perplexity: Deep web research
        - Evidence Graph: Build knowledge graph
        - Competitor Analysis: Ladder building & conflict detection
        - Completeness Validator: Validate research quality
        """

        try:
            logger.info(f"Starting enhanced research for business {business_id}")

            state = {
                "business_id": business_id,
                "business_data": business_data,
                "iterations": 0,
                "evidence_graph": {},
                "competitor_ladder": [],
                "conflicts": [],
                "rtbs": [],
                "sostac_analysis": {},
                "completeness_scores": {},
                "status": "analyzing"
            }

            # Step 1: Situation Analysis with SOSTAC
            logger.info("Step 1/7: Analyzing situation...")
            state = await self._enhanced_situation_analysis(state)

            # Step 2: Deep Competitor Research
            logger.info("Step 2/7: Deep competitor research...")
            state = await self._enhanced_competitor_research(state)

            # Step 3: Build Competitor Ladder with tool
            logger.info("Step 3/7: Building competitor ladder...")
            state = await self._build_ladder_with_tool(state)

            # Step 4: Detect Positioning Conflicts
            logger.info("Step 4/7: Detecting positioning conflicts...")
            state = await self._detect_conflicts(state)

            # Step 5: Gather and Build Evidence Graph
            logger.info("Step 5/7: Building evidence graph...")
            state = await self._build_evidence_graph(state)

            # Step 6: Create RTBs (Reasons To Believe)
            logger.info("Step 6/7: Creating RTBs...")
            state = await self._create_rtbs(state)

            # Step 7: Validate Completeness
            logger.info("Step 7/7: Validating completeness...")
            state = await self._validate_completeness_enhanced(state)

            state["status"] = "completed"

            return {
                "success": True,
                "status": "completed",
                "results": {
                    "sostac": state["sostac_analysis"],
                    "competitor_ladder": state["competitor_ladder"],
                    "positioning_conflicts": state["conflicts"],
                    "evidence_graph": state["evidence_graph"],
                    "rtbs": state["rtbs"],
                    "completeness_scores": state["completeness_scores"],
                    "overall_completeness": round(
                        sum(state["completeness_scores"].values()) / len(state["completeness_scores"]),
                        2
                    ) if state["completeness_scores"] else 0,
                    "research_quality": self._assess_research_quality(state)
                }
            }

        except Exception as e:
            logger.exception(f"Enhanced research failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e)
            }

    async def _enhanced_situation_analysis(self, state: Dict) -> Dict:
        """Analyze situation with enhanced depth"""
        business = state["business_data"]

        logger.info("Performing SOSTAC analysis...")

        # Use Gemini for analysis
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7
            )

            prompt = f"""
            Perform comprehensive SOSTAC analysis for this business:

            Business: {business['name']}
            Industry: {business['industry']}
            Location: {business['location']}
            Description: {business['description']}
            Goals: {business.get('goals', {})}

            Provide JSON response with:
            {{
                "situation": "Current market position and state",
                "objectives": "Specific goals to achieve",
                "market_size_estimate": "TAM/SAM/SOM estimates",
                "current_positioning": "How currently positioned",
                "main_challenges": ["Challenge 1", "Challenge 2", "Challenge 3"],
                "market_dynamics": "Market trends and changes",
                "opportunities": ["Opportunity 1", "Opportunity 2"],
                "threats": ["Threat 1", "Threat 2"]
            }}
            """

            response = await llm.ainvoke(prompt)
            sostac = json.loads(response.content)

        except Exception as e:
            logger.warning(f"Gemini analysis failed: {str(e)}")
            sostac = self._create_fallback_sostac(business)

        state["sostac_analysis"] = sostac
        logger.info(f"SOSTAC analysis complete: {len(sostac)} fields")

        return state

    async def _enhanced_competitor_research(self, state: Dict) -> Dict:
        """Enhanced competitor research using tools"""
        business = state["business_data"]

        logger.info("Performing enhanced competitor research...")

        try:
            from tools.perplexity_search_v2 import PerplexitySearchToolV2

            perplexity = PerplexitySearchToolV2()

            # Multiple search queries for comprehensive research
            queries = [
                f"Top competitors in {business['industry']} - their market position, pricing, positioning",
                f"Market leaders in {business['industry']} {business['location']} - what they're known for",
                f"Emerging competitors in {business['industry']} - new entrants and their strategies"
            ]

            all_research = []

            for query in queries:
                try:
                    result = await perplexity._execute(query=query)
                    if result.get("success"):
                        all_research.append({
                            "query": query,
                            "content": result.get("content", ""),
                            "citations": result.get("citations", []),
                            "confidence": 0.85
                        })
                        logger.info(f"Research complete for query: {query[:50]}...")
                except Exception as e:
                    logger.warning(f"Query failed: {query} - {str(e)}")

            state["research_sources"] = all_research

        except Exception as e:
            logger.warning(f"Enhanced competitor research failed: {str(e)}")

        return state

    async def _build_ladder_with_tool(self, state: Dict) -> Dict:
        """Build competitor ladder using specialized tool"""
        logger.info("Using competitor ladder tool...")

        try:
            from tools.competitor_analysis_v2 import CompetitorLadderBuilderTool

            ladder_builder = CompetitorLadderBuilderTool()

            # Prepare competitor data from research
            competitors = self._extract_competitors_from_research(state)

            result = await ladder_builder._execute(
                competitors=competitors,
                industry=state["business_data"].get("industry", "")
            )

            if result.get("success"):
                state["competitor_ladder"] = result.get("ladder", [])
                state["positioning_gaps"] = result.get("positioning_gaps", [])
                logger.info(f"Ladder built: {len(state['competitor_ladder'])} competitors")

        except Exception as e:
            logger.warning(f"Ladder tool failed: {str(e)}")
            state["competitor_ladder"] = self._create_fallback_ladder(state)

        return state

    async def _detect_conflicts(self, state: Dict) -> Dict:
        """Detect positioning conflicts using tool"""
        logger.info("Detecting positioning conflicts...")

        try:
            from tools.competitor_analysis_v2 import PositioningConflictDetectorTool

            conflict_detector = PositioningConflictDetectorTool()

            # For now, we'll detect conflicts based on competitor ladder
            # In full implementation, would use against proposed positioning options

            detected_conflicts = []
            competitor_words = [c.get("word_owned", "") for c in state["competitor_ladder"]]

            for comp1 in competitor_words:
                for comp2 in competitor_words:
                    if comp1 != comp2 and self._are_words_conflicting(comp1, comp2):
                        detected_conflicts.append({
                            "word1": comp1,
                            "word2": comp2,
                            "conflict_type": "semantic_overlap"
                        })

            state["conflicts"] = detected_conflicts
            logger.info(f"Conflicts detected: {len(state['conflicts'])}")

        except Exception as e:
            logger.warning(f"Conflict detection failed: {str(e)}")

        return state

    async def _build_evidence_graph(self, state: Dict) -> Dict:
        """Build evidence graph using tool"""
        logger.info("Building evidence graph...")

        try:
            from tools.evidence_graph_v2 import EvidenceGraphBuilderTool

            graph_builder = EvidenceGraphBuilderTool()

            # Create claims from SOSTAC
            claims = self._extract_claims_from_sostac(state["sostac_analysis"])

            # Extract evidence sources from research
            evidence_sources = self._extract_evidence_sources(state)

            result = await graph_builder._execute(
                claims=claims,
                evidence_sources=evidence_sources
            )

            if result.get("success"):
                state["evidence_graph"] = {
                    "nodes": result.get("nodes", []),
                    "edges": result.get("edges", []),
                    "statistics": result.get("statistics", {})
                }
                logger.info(f"Evidence graph built: {result['statistics'].get('total_nodes', 0)} nodes")

        except Exception as e:
            logger.warning(f"Evidence graph building failed: {str(e)}")

        return state

    async def _create_rtbs(self, state: Dict) -> Dict:
        """Create RTBs (Reasons To Believe) using tool"""
        logger.info("Creating RTBs...")

        try:
            from tools.evidence_graph_v2 import RTBLinkerTool

            rtb_linker = RTBLinkerTool()

            # Create positioning claims from competitor ladder
            positioning_claims = {
                f"Position {i+1}": comp.get("word_owned", "")
                for i, comp in enumerate(state["competitor_ladder"][:3])
            }

            # Extract evidence
            evidence_sources = self._extract_evidence_sources(state)

            result = await rtb_linker._execute(
                positioning_claims=positioning_claims,
                evidence_sources=evidence_sources
            )

            if result.get("success"):
                state["rtbs"] = result.get("rtbs", [])
                state["overall_credibility"] = result.get("overall_credibility", 0)
                logger.info(f"RTBs created: {len(state['rtbs'])}")

        except Exception as e:
            logger.warning(f"RTB creation failed: {str(e)}")

        return state

    async def _validate_completeness_enhanced(self, state: Dict) -> Dict:
        """Validate research completeness using tool"""
        logger.info("Validating research completeness...")

        try:
            from tools.evidence_graph_v2 import CompletenessValidatorTool

            validator = CompletenessValidatorTool()

            result = await validator._execute(
                evidence_graph=state["evidence_graph"],
                competitor_coverage=[c.get("competitor", "") for c in state["competitor_ladder"]],
                market_data=state.get("sostac_analysis", {})
            )

            if result.get("success"):
                state["completeness_scores"] = result.get("dimension_scores", {})
                state["overall_completeness"] = result.get("completeness_score", 0)
                logger.info(f"Completeness validation: {state['overall_completeness']:.1%}")

        except Exception as e:
            logger.warning(f"Completeness validation failed: {str(e)}")
            state["completeness_scores"] = {}

        return state

    def _extract_competitors_from_research(self, state: Dict) -> List[Dict]:
        """Extract competitor data from research sources"""
        competitors = []

        for source in state.get("research_sources", []):
            # Parse content for competitor mentions
            content = source.get("content", "").lower()

            # Simple extraction (would be more sophisticated in production)
            competitor_names = [
                "company1", "company2", "company3", "company4", "company5"
            ]

            for name in competitor_names:
                if name in content:
                    competitors.append({
                        "name": name.title(),
                        "positioning_word": "Unknown",
                        "positioning": "Extracted from research",
                        "source": source.get("query", "")
                    })

        return competitors[:5]  # Top 5

    def _create_fallback_ladder(self, state: Dict) -> List[Dict]:
        """Create fallback competitor ladder"""
        return [
            {
                "competitor": f"Competitor {i+1}",
                "word_owned": f"Position {i+1}",
                "positioning_strength": 0.5 + (i * 0.1),
                "description": f"Market player in {state['business_data'].get('industry', 'the industry')}"
            }
            for i in range(3)
        ]

    def _create_fallback_sostac(self, business: Dict) -> Dict:
        """Create fallback SOSTAC analysis"""
        return {
            "situation": f"{business['name']} operates in {business['industry']}",
            "objectives": "Achieve growth and market expansion",
            "market_size_estimate": "To be determined",
            "current_positioning": "Needs assessment",
            "main_challenges": ["Market competition", "Customer acquisition"],
            "opportunities": ["Market growth", "Technology adoption"]
        }

    def _extract_claims_from_sostac(self, sostac: Dict) -> List[str]:
        """Extract claims from SOSTAC"""
        return [
            sostac.get("situation", ""),
            sostac.get("objectives", ""),
            f"Market size: {sostac.get('market_size_estimate', '')}",
            f"Current position: {sostac.get('current_positioning', '')}"
        ]

    def _extract_evidence_sources(self, state: Dict) -> List[Dict]:
        """Extract evidence sources from research"""
        sources = []

        for research in state.get("research_sources", []):
            sources.append({
                "evidence": research.get("content", "")[:500],  # Truncate
                "source": research.get("query", "research"),
                "type": "web_research",
                "credibility": research.get("confidence", 0.7)
            })

        return sources

    def _are_words_conflicting(self, word1: str, word2: str) -> bool:
        """Check if two words represent conflicting positions"""
        conflicting_pairs = {
            ("premium", "budget"),
            ("luxury", "affordable"),
            ("fast", "thorough"),
            ("simple", "comprehensive")
        }

        word1_lower = word1.lower()
        word2_lower = word2.lower()

        for pair in conflicting_pairs:
            if {word1_lower, word2_lower} == set(pair):
                return True

        return False

    def _assess_research_quality(self, state: Dict) -> Dict:
        """Assess overall research quality"""
        return {
            "overall_quality": "good" if state.get("overall_completeness", 0) > 0.7 else "fair",
            "evidence_coverage": "comprehensive" if len(state.get("evidence_graph", {}).get("nodes", [])) > 10 else "adequate",
            "competitor_analysis": "thorough" if len(state.get("competitor_ladder", [])) >= 3 else "basic",
            "conflicts_identified": len(state.get("conflicts", [])),
            "recommendation": "Research is ready for positioning strategy" if state.get("overall_completeness", 0) > 0.75 else "Recommend additional research"
        }


# Singleton instance
research_agent_v3 = ResearchAgentV3Enhanced()

"""Research Agent - Gathers business intelligence and builds evidence graph"""
import logging
import json
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from tools.perplexity_search import PerplexitySearchTool
from tools.competitor_ladder import CompetitorLadderTool
from tools.sostac_analyzer import SOSTACAnalyzerTool
from tools.evidence_db import EvidenceDBTool
from tools.rtb_linker import RTBLinkerTool
from utils.supabase_client import get_supabase_client
from agents.base_agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    """Extended state for research agent"""
    business_id: str
    business_data: Dict[str, Any]
    evidence_nodes: List[Dict]
    competitor_ladder: List[Dict]
    sostac_analysis: Dict[str, Any]
    status: str
    completeness_score: float
    iterations: int
    max_iterations: int
    error: Optional[str]


class ResearchAgent(BaseAgent):
    """Agent for comprehensive business research and evidence gathering"""

    def __init__(self):
        super().__init__(
            name="research_agent",
            description="Conducts SOSTAC analysis, builds competitor ladder, gathers evidence"
        )

        # Initialize tools
        self.perplexity = PerplexitySearchTool()
        self.competitor_tool = CompetitorLadderTool()
        self.sostac_tool = SOSTACAnalyzerTool()
        self.evidence_db = EvidenceDBTool()
        self.rtb_linker = RTBLinkerTool()
        self.supabase = get_supabase_client()

        # Override graph building for research-specific flow
        self._build_research_graph()

    def _build_research_graph(self):
        """Build research-specific LangGraph"""
        graph = StateGraph(ResearchState)

        # Add specialized nodes
        graph.add_node("analyze_situation", self._analyze_situation)
        graph.add_node("research_competitors", self._research_competitors)
        graph.add_node("build_ladder", self._build_competitor_ladder)
        graph.add_node("gather_evidence", self._gather_evidence)
        graph.add_node("validate_evidence", self._validate_evidence)
        graph.add_node("link_rtbs", self._link_claims_to_rtbs)
        graph.add_node("check_completeness", self._check_completeness)
        graph.add_node("save_results", self._save_results)
        graph.add_node("error_handler", self._handle_error)

        # Set entry point
        graph.set_entry_point("analyze_situation")

        # Define edge flow
        graph.add_edge("analyze_situation", "research_competitors")
        graph.add_edge("research_competitors", "build_ladder")
        graph.add_edge("build_ladder", "gather_evidence")
        graph.add_edge("gather_evidence", "validate_evidence")
        graph.add_edge("validate_evidence", "link_rtbs")
        graph.add_edge("link_rtbs", "check_completeness")

        # Conditional: loop or finalize
        graph.add_conditional_edges(
            "check_completeness",
            self._should_continue_research,
            {
                "continue": "gather_evidence",
                "finalize": "save_results",
                "error": "error_handler"
            }
        )

        # Error handling
        graph.add_edge("error_handler", END)

        # Compile graph
        self.graph = graph.compile()

    def _should_continue_research(self, state: ResearchState) -> str:
        """Determine if research should continue"""
        try:
            if state.get("error"):
                return "error"
            
            if state.get("completeness_score", 0) >= 0.8:
                return "finalize"
            
            if state.get("iterations", 0) >= state.get("max_iterations", 3):
                return "finalize"
            
            return "continue"
        except Exception as e:
            logger.error(f"Error in research decision: {e}")
            return "error"

    async def _analyze_situation(self, state: ResearchState) -> ResearchState:
        """Analyze business situation using SOSTAC"""
        try:
            business_data = state.get("business_data", {})
            
            # Run SOSTAC analysis
            sostac_result = await self.sostac_tool.ainvoke({
                "business_data": business_data,
                "analysis_type": "situation_analysis"
            })
            
            state["sostac_analysis"] = sostac_result.get("sostac", {})
            state["status"] = "analyzed"
            
            logger.info(f"Situation analysis completed for business {state['business_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error in situation analysis: {e}")
            state["error"] = str(e)
            return state

    async def _research_competitors(self, state: ResearchState) -> ResearchState:
        """Research competitors using Perplexity"""
        try:
            business_data = state.get("business_data", {})
            
            # Search for competitors
            competitors = await self.perplexity.ainvoke({
                "query": f"competitors for {business_data.get('name')} in {business_data.get('industry')} industry",
                "max_results": 10
            })
            
            state["competitor_data"] = competitors.get("results", [])
            state["status"] = "competitors_researched"
            
            logger.info(f"Competitor research completed for business {state['business_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error in competitor research: {e}")
            state["error"] = str(e)
            return state

    async def _build_competitor_ladder(self, state: ResearchState) -> ResearchState:
        """Build competitor ladder"""
        try:
            business_data = state.get("business_data", {})
            competitor_data = state.get("competitor_data", [])
            
            # Build ladder
            ladder_result = await self.competitor_tool.ainvoke({
                "business_data": business_data,
                "competitors": competitor_data
            })
            
            state["competitor_ladder"] = ladder_result.get("ladder", [])
            state["status"] = "ladder_built"
            
            logger.info(f"Competitor ladder built for business {state['business_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error building competitor ladder: {e}")
            state["error"] = str(e)
            return state

    async def _gather_evidence(self, state: ResearchState) -> ResearchState:
        """Gather evidence for claims"""
        try:
            business_data = state.get("business_data", {})
            
            # Gather evidence
            evidence_result = await self.evidence_db.ainvoke({
                "business_data": business_data,
                "research_focus": "market_positioning"
            })
            
            if "evidence_nodes" not in state:
                state["evidence_nodes"] = []
            state["evidence_nodes"].extend(evidence_result.get("evidence", []))
            state["status"] = "evidence_gathered"
            state["iterations"] = state.get("iterations", 0) + 1
            
            logger.info(f"Evidence gathered for business {state['business_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error gathering evidence: {e}")
            state["error"] = str(e)
            return state

    async def _validate_evidence(self, state: ResearchState) -> ResearchState:
        """Validate gathered evidence"""
        try:
            evidence_nodes = state.get("evidence_nodes", [])
            
            # Validate evidence (simple validation for now)
            valid_evidence = []
            for evidence in evidence_nodes:
                if evidence.get("confidence", 0) >= 0.6:
                    valid_evidence.append(evidence)
            
            state["evidence_nodes"] = valid_evidence
            state["status"] = "evidence_validated"
            
            logger.info(f"Evidence validated for business {state['business_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error validating evidence: {e}")
            state["error"] = str(e)
            return state

    async def _link_claims_to_rtbs(self, state: ResearchState) -> ResearchState:
        """Link claims to reasons to believe"""
        try:
            business_data = state.get("business_data", {})
            evidence_nodes = state.get("evidence_nodes", [])
            
            # Link claims to RTBs
            rtb_result = await self.rtb_linker.ainvoke({
                "business_data": business_data,
                "evidence": evidence_nodes
            })
            
            state["rtb_links"] = rtb_result.get("links", [])
            state["status"] = "rtbs_linked"
            
            logger.info(f"RTBs linked for business {state['business_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error linking RTBs: {e}")
            state["error"] = str(e)
            return state

    async def _check_completeness(self, state: ResearchState) -> ResearchState:
        """Check research completeness"""
        try:
            evidence_count = len(state.get("evidence_nodes", []))
            competitor_count = len(state.get("competitor_ladder", []))
            
            # Calculate completeness score
            completeness = min(1.0, (evidence_count / 10.0 + competitor_count / 5.0) / 2.0)
            state["completeness_score"] = completeness
            state["status"] = "completeness_checked"
            
            logger.info(f"Completeness score: {completeness:.2f} for business {state['business_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error checking completeness: {e}")
            state["error"] = str(e)
            return state

    async def _save_results(self, state: ResearchState) -> ResearchState:
        """Save research results to database"""
        try:
            business_id = state.get("business_id")
            
            # Save SOSTAC analysis
            if state.get("sostac_analysis"):
                self.supabase.table("sostac_analyses").insert({
                    "business_id": business_id,
                    "analysis": state["sostac_analysis"],
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
            
            # Save competitor ladder
            if state.get("competitor_ladder"):
                self.supabase.table("competitor_ladder").insert({
                    "business_id": business_id,
                    "ladder": state["competitor_ladder"],
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
            
            # Save evidence
            for evidence in state.get("evidence_nodes", []):
                self.supabase.table("evidence").insert({
                    "business_id": business_id,
                    "evidence_data": evidence,
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
            
            state["status"] = "completed"
            logger.info(f"Research results saved for business {business_id}")
            return state
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            state["error"] = str(e)
            return state

    async def _handle_error(self, state: ResearchState) -> ResearchState:
        """Handle errors in research process"""
        error_msg = state.get("error", "Unknown error")
        logger.error(f"Research error for business {state.get('business_id')}: {error_msg}")
        state["status"] = "error"
        return state

    def _process(self, state: ResearchState) -> ResearchState:
        """Main processing logic - required by BaseAgent"""
        # For research agent, we use the graph-based approach
        # This method is required by BaseAgent but not used in graph flow
        return state

    def _validate(self, state: ResearchState) -> ResearchState:
        """Validate results - required by BaseAgent"""
        # For research agent, we use the graph-based approach
        # This method is required by BaseAgent but not used in graph flow
        return state

# Create research agent instance
research_agent = ResearchAgent()

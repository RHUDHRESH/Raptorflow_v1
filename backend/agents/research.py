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
            "calculate_completeness",

from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from tools.perplexity_search import PerplexitySearchTool
from tools.competitor_ladder import CompetitorLadderTool
from tools.sostac_analyzer import SOSTACAnalyzerTool
from tools.evidence_db import EvidenceDBTool
from tools.rtb_linker import RTBLinkerTool
from utils.supabase_client import get_supabase_client
import asyncio

class ResearchState(TypedDict):
    business_id: str
    business_data: Dict
    evidence: List[Dict]
    competitor_ladder: List[Dict]
    sostac: Dict
    status: str
    completeness_score: float

class ResearchAgent:
    def __init__(self):
        self.perplexity = PerplexitySearchTool()
        self.competitor_tool = CompetitorLadderTool()
        self.sostac_tool = SOSTACAnalyzerTool()
        self.evidence_db = EvidenceDBTool()
        self.rtb_linker = RTBLinkerTool()
        self.supabase = get_supabase_client()
        
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self):
        graph = StateGraph(ResearchState)
        
        # Add nodes
        graph.add_node("run_sostac", self._run_sostac_analysis)
        graph.add_node("build_competitor_ladder", self._build_competitor_ladder)
        graph.add_node("gather_evidence", self._gather_evidence)
        graph.add_node("link_claims_to_rtbs", self._link_claims_to_rtbs)
        graph.add_node("calculate_completeness", self._calculate_completeness)
        
        # Add edges
        graph.set_entry_point("run_sostac")
        graph.add_edge("run_sostac", "build_competitor_ladder")
        graph.add_edge("build_competitor_ladder", "gather_evidence")
        graph.add_edge("gather_evidence", "link_claims_to_rtbs")
        graph.add_edge("link_claims_to_rtbs", "calculate_completeness")
        
        # Conditional: loop back if not complete enough
        graph.add_conditional_edges(
            "calculate_completeness",

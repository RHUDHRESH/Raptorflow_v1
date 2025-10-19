from typing import TypedDict, Dict
from langgraph.graph import StateGraph, END
from tools.amec_evaluator import AMECEvaluatorTool
from tools.clv_calculator import CLVCalculatorTool
from tools.route_back_logic import RouteBackLogicTool
from utils.supabase_client import get_supabase_client
import json

class AnalyticsState(TypedDict):
    business_id: str
    campaign_data: Dict
    performance_data: Dict
    amec_analysis: Dict
    clv_analysis: Dict
    route_back_decision: Dict
    status: str

class AnalyticsAgent:
    def __init__(self):
        self.amec = AMECEvaluatorTool()
        self.clv = CLVCalculatorTool()
        self.route_back = RouteBackLogicTool()
        self.supabase = get_supabase_client()
        
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self):
        graph = StateGraph(AnalyticsState)
        
        graph.add_node("run_amec", self._run_amec_evaluation)
        graph.add_node("calculate_clv", self._calculate_clv)
        graph.add_node("evaluate_route_back", self._evaluate_route_back)
        graph.add_node("update_knowledge_graph", self._update_knowledge_graph)
        
        graph.set_entry_point("run_amec")
        graph.add_edge("run_amec", "calculate_clv")
        graph.add_edge("calculate_clv", "evaluate_route_back")
        graph.add_edge("evaluate_route_back", "update_knowledge_graph")
        graph.add_edge("update_knowledge_graph", END)
        
        return graph
    
    async def _run_amec_evaluation(self, state: AnalyticsState) -> AnalyticsState:
        """Run AMEC ladder evaluation"""
        result = self.amec._run(
            campaign_data=state['campaign_data'],
            performance_data=state['performance_data']
        )
        
        state['amec_analysis'] = json.loads(result)
        return state
    
    async def _calculate_clv(self, state: AnalyticsState) -> AnalyticsState:
        """Calculate Customer Lifetime Value"""
        # Get purchase data from performance
        purchase_data = state['performance_data'].get('purchase_data', {})
        acquisition_cost = state['campaign_data'].get('budget', 0) / max(state['performance_data'].get('conversions', 1), 1)
        
        result = self.clv._run(
            action='calculate',
            purchase_data=purchase_data,
            acquisition_cost=acquisition_cost
        )
        
        state['clv_analysis'] = json.loads(result)
        return state
    
    async def _evaluate_route_back(self, state: AnalyticsState) -> AnalyticsState:
        """Determine if route-back is needed"""
        result = self.route_back._run(
            business_id=state['business_id'],
            performance_data=state['performance_data'],
            campaign_data=state['campaign_data']
        )
        
        state['route_back_decision'] = json.loads(result)
        return state
    
    async def _update_knowledge_graph(self, state: AnalyticsState) -> AnalyticsState:
        """Update knowledge graph with learnings"""
        # Store learnings in database
        self.supabase.table('performance_metrics').insert({
            'business_id': state['business_id'],
            'entity_type': 'campaign',
            'entity_id': state['campaign_data'].get('move_id'),
            'metric_name': 'amec_overall_score',
            'metric_value': state['amec_analysis']['overall_score']
        }).execute()
        
        state['status'] = 'complete'
        return state

# Create singleton
analytics_agent = AnalyticsAgent().app

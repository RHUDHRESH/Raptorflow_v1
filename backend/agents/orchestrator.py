from typing import TypedDict, Literal, Dict, Any
from langgraph.graph import StateGraph, END
from tools.state_manager import StateManagerTool
from tools.tier_validator import TierValidatorTool
from utils.supabase_client import get_supabase_client
import json

# Import specialist agents
from agents.research import research_agent
from agents.positioning import positioning_agent
from agents.icp import icp_agent
from agents.strategy import strategy_agent
from agents.content import content_agent
from agents.analytics import analytics_agent

class OrchestratorState(TypedDict):
    business_id: str
    current_stage: str
    user_input: Dict
    context: Dict
    route_back_needed: bool
    route_back_to: str
    subscription_tier: str
    specialist_results: Dict
    error: str

class OrchestratorAgent:
    def __init__(self):
        self.state_manager = StateManagerTool()
        self.tier_validator = TierValidatorTool()
        self.supabase = get_supabase_client()
        
        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self):
        graph = StateGraph(OrchestratorState)
        
        # Add nodes
        graph.add_node("initialize", self._initialize)
        graph.add_node("check_tier", self._check_tier_access)
        graph.add_node("determine_stage", self._determine_stage)
        graph.add_node("check_prerequisites", self._check_prerequisites)
        graph.add_node("delegate_research", self._delegate_research)
        graph.add_node("delegate_positioning", self._delegate_positioning)
        graph.add_node("delegate_icp", self._delegate_icp)
        graph.add_node("delegate_strategy", self._delegate_strategy)
        graph.add_node("delegate_content", self._delegate_content)
        graph.add_node("delegate_analytics", self._delegate_analytics)
        graph.add_node("handle_route_back", self._handle_route_back)
        graph.add_node("finalize", self._finalize)
        
        # Add edges
        graph.set_entry_point("initialize")
        graph.add_edge("initialize", "check_tier")
        graph.add_edge("check_tier", "determine_stage")
        
        # Conditional routing based on stage
        graph.add_conditional_edges(
            "determine_stage",
            self._route_by_stage,
            {
                "research": "check_prerequisites",
                "positioning": "check_prerequisites",
                "icp": "check_prerequisites",
                "strategy": "check_prerequisites",
                "content": "check_prerequisites",
                "analytics": "check_prerequisites",
                "error": END
            }
        )
        
        # Prerequisites check
        graph.add_conditional_edges(
            "check_prerequisites",
            self._check_prereq_results,
            {
                "research": "delegate_research",
                "positioning": "delegate_positioning",
                "icp": "delegate_icp",
                "strategy": "delegate_strategy",
                "content": "delegate_content",
                "analytics": "delegate_analytics",
                "route_back": "handle_route_back"
            }
        )
        
        # After delegation
        graph.add_edge("delegate_research", "finalize")
        graph.add_edge("delegate_positioning", "finalize")
        graph.add_edge("delegate_icp", "finalize")
        graph.add_edge("delegate_strategy", "finalize")
        graph.add_edge("delegate_content", "finalize")
        graph.add_edge("delegate_analytics", "finalize")
        graph.add_edge("handle_route_back", "finalize")
        graph.add_edge("finalize", END)
        
        return graph
    
    def _initialize(self, state: OrchestratorState) -> OrchestratorState:
        """Load business context and subscription tier"""
        business_id = state['business_id']
        
        # Get subscription
        sub = self.supabase.table('subscriptions')\
            .select('*')\
            .eq('business_id', business_id)\
            .single()\
            .execute()
        
        state['subscription_tier'] = sub.data['tier']
        state['context'] = state.get('context', {})
        state['specialist_results'] = {}
        
        return state
    
    def _check_tier_access(self, state: OrchestratorState) -> OrchestratorState:
        """Verify tier allows requested operation"""
        feature = state['user_input'].get('feature', 'basic')
        
        validation = json.loads(self.tier_validator._run(
            business_id=state['business_id'],
            feature=feature
        ))
        
        if not validation['has_access']:
            state['error'] = f"Upgrade to {validation['tier']} required for {feature}"
        
        return state
    
    def _determine_stage(self, state: OrchestratorState) -> OrchestratorState:
        """Determine which specialist agent to call"""
        user_input = state['user_input']
        action = user_input.get('action', '')
        
        # Map actions to stages
        stage_map = {
            'run_research': 'research',
            'analyze_sostac': 'research',
            'build_competitor_ladder': 'research',
            'generate_positioning': 'positioning',
            'select_positioning': 'positioning',
            'create_icps': 'icp',
            'build_strategy': 'strategy',
            'create_move': 'content',
            'generate_calendar': 'content',
            'measure_performance': 'analytics',
            'evaluate_campaign': 'analytics'
        }
        
        state['current_stage'] = stage_map.get(action, 'research')
        return state
    
    def _check_prerequisites(self, state: OrchestratorState) -> OrchestratorState:
        """Check if prerequisites are met for current stage"""
        stage = state['current_stage']
        business_id = state['business_id']
        
        # Define prerequisites for each stage
        prerequisites = {
            'positioning': ['sostac_analyses', 'competitor_ladder'],
            'icp': ['positioning_analyses'],
            'strategy': ['positioning_analyses', 'icps'],
            'content': ['strategies', 'icps'],
            'analytics': ['moves']
        }
        
        if stage not in prerequisites:
            return state  # No prerequisites
        
        # Check each prerequisite
        missing = []
        for table in prerequisites[stage]:
            result = self.supabase.table(table)\
                .select('id')\
                .eq('business_id', business_id)\
                .limit(1)\
                .execute()
            
            if not result.data:
                missing.append(table)
        
        if missing:
            state['route_back_needed'] = True
            # Determine which stage to route back to
            if 'positioning_analyses' in missing:
                state['route_back_to'] = 'positioning'
            elif 'icps' in missing:
                state['route_back_to'] = 'icp'
            else:
                state['route_back_to'] = 'research'
        
        return state
    
    def _route_by_stage(self, state: OrchestratorState) -> str:
        """Route to appropriate delegation node"""
        if state.get('error'):
            return "error"
        return state['current_stage']
    
    def _check_prereq_results(self, state: OrchestratorState) -> str:
        """Route based on prerequisite check"""
        if state.get('route_back_needed'):
            return "route_back"
        return state['current_stage']
    
    async def _delegate_research(self, state: OrchestratorState) -> OrchestratorState:
        """Delegate to Research Agent"""
        business = self.supabase.table('businesses')\
            .select('*')\
            .eq('id', state['business_id'])\
            .single()\
            .execute()
        
        result = await research_agent.ainvoke({
            'business_id': state['business_id'],
            'business_data': business.data,
            'evidence': [],
            'competitor_ladder': [],
            'sostac': {},
            'status': 'running'
        })
        
        state['specialist_results']['research'] = result
        return state
    
    async def _delegate_positioning(self, state: OrchestratorState) -> OrchestratorState:
        """Delegate to Positioning Agent"""
        business = self.supabase.table('businesses')\
            .select('*')\
            .eq('id', state['business_id'])\
            .single()\
            .execute()
        
        comps = self.supabase.table('competitor_ladder')\
            .select('*')\
            .eq('business_id', state['business_id'])\
            .execute()
        
        result = await positioning_agent.ainvoke({
            'business_id': state['business_id'],
            'business_data': business.data,
            'competitor_ladder': comps.data,
            'options': [],
            'status': 'running'
        })
        
        state['specialist_results']['positioning'] = result
        return state
    
    async def _delegate_icp(self, state: OrchestratorState) -> OrchestratorState:
        """Delegate to ICP Agent"""
        sub = self.supabase.table('subscriptions')\
            .select('*')\
            .eq('business_id', state['business_id'])\
            .single()\
            .execute()
        
        pos = self.supabase.table('positioning_analyses')\
            .select('*')\
            .eq('business_id', state['business_id'])\
            .single()\
            .execute()
        
        result = await icp_agent.ainvoke({
            'business_id': state['business_id'],
            'positioning': pos.data['selected_option'],
            'max_icps': sub.data['max_icps'],
            'icps': [],
            'status': 'running'
        })
        
        state['specialist_results']['icp'] = result
        return state
    
    async def _delegate_strategy(self, state: OrchestratorState) -> OrchestratorState:
        """Delegate to Strategy Agent"""
        # Implementation similar to above
        state['specialist_results']['strategy'] = {}
        return state
    
    async def _delegate_content(self, state: OrchestratorState) -> OrchestratorState:
        """Delegate to Content Agent"""
        # Implementation similar to above
        state['specialist_results']['content'] = {}
        return state
    
    async def _delegate_analytics(self, state: OrchestratorState) -> OrchestratorState:
        """Delegate to Analytics Agent"""
        # Implementation similar to above
        state['specialist_results']['analytics'] = {}
        return state
    
    def _handle_route_back(self, state: OrchestratorState) -> OrchestratorState:
        """Handle route-back scenario"""
        state['specialist_results']['route_back'] = {
            'needed': True,
            'to_stage': state['route_back_to'],
            'message': f"Prerequisites missing. Please complete {state['route_back_to']} first."
        }
        return state
    
    def _finalize(self, state: OrchestratorState) -> OrchestratorState:
        """Prepare final response"""
        return state

# Create singleton instance
orchestrator = OrchestratorAgent()

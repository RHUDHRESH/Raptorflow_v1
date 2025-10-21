from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from tools.persona_generator import PersonaGeneratorTool
from tools.jtbd_mapper import JTBDMapperTool
from tools.tag_extractor import TagExtractorTool
from tools.segment_scorer import SegmentScorerTool
from utils.embeddings import generate_embedding
from utils.supabase_client import get_supabase_client
from .base_agent import BaseAgent, AgentState
import json

class ICPState(AgentState):
    positioning: Dict
    max_icps: int
    personas: List[Dict]
    icps: List[Dict]

class ICPAgent(BaseAgent):
    def __init__(self):
        super().__init__("ICP Agent", "Generates Ideal Customer Profiles with budget-controlled AI")
        self.persona_gen = PersonaGeneratorTool()
        self.jtbd = JTBDMapperTool()
        self.tag_extractor = TagExtractorTool()
        self.scorer = SegmentScorerTool()
        self.supabase = get_supabase_client()
        
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self):
        graph = StateGraph(ICPState)
        
        graph.add_node("generate_personas", self._generate_personas)
        graph.add_node("map_jtbd", self._map_jtbd)
        graph.add_node("create_value_props", self._create_value_props)
        graph.add_node("score_segments", self._score_segments)
        graph.add_node("select_top_icps", self._select_top_icps)
        graph.add_node("extract_tags", self._extract_monitoring_tags)
        graph.add_node("generate_embeddings", self._generate_embeddings)
        
        graph.set_entry_point("generate_personas")
        graph.add_edge("generate_personas", "map_jtbd")
        graph.add_edge("map_jtbd", "create_value_props")
        graph.add_edge("create_value_props", "score_segments")
        graph.add_edge("score_segments", "select_top_icps")
        graph.add_edge("select_top_icps", "extract_tags")
        graph.add_edge("extract_tags", "generate_embeddings")
        graph.add_edge("generate_embeddings", END)
        
        return graph
    
    async def _generate_personas(self, state: ICPState) -> ICPState:
        """Generate detailed customer personas"""
        count = state['max_icps']
        
        result = self.persona_gen._run(
            action='generate',
            positioning=state['positioning'],
            count=count
        )
        
        personas_data = json.loads(result)
        state['personas'] = personas_data['personas']
        
        return state
    
    async def _map_jtbd(self, state: ICPState) -> ICPState:
        """Map Jobs-to-be-Done for each persona"""
        for persona in state['personas']:
            jtbd_result = self.jtbd._run(
                action='map',
                persona=persona
            )
            
            jtbd_data = json.loads(jtbd_result)
            persona['jtbd'] = jtbd_data['jtbd_map']
        
        return state
    
    async def _create_value_props(self, state: ICPState) -> ICPState:
        """Create value propositions for each persona using budget-controlled AI"""
        positioning = state['positioning']
        
        for persona in state['personas']:
            prompt = f"""Create value proposition for this persona.

PERSONA: {persona['name']}
JTBD: {json.dumps(persona['jtbd'])}

POSITIONING: {positioning.get('word')}

Value Proposition Canvas:
1. Customer Jobs (from JTBD)
2. Pains (what frustrates them)
3. Gains (what they desire)
4. Pain Relievers (how we solve pains)
5. Gain Creators (how we create gains)
6. Products & Services (what we offer)

Return JSON with these sections."""
            
            # Use budget-controlled AI call
            ai_result = self.call_ai_with_budget_control(
                prompt=prompt,
                task_complexity="medium",  # Value props need some reasoning but not GPT-5
                estimated_tokens=800
            )
            
            if ai_result["success"]:
                try:
                    vp_data = json.loads(ai_result["content"])
                    persona['value_proposition'] = vp_data
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    persona['value_proposition'] = {
                        "customer_jobs": "Jobs extracted from JTBD",
                        "pains": "Common pain points identified",
                        "gains": "Desired outcomes defined",
                        "pain_relievers": "Solutions offered",
                        "gain_creators": "Value created",
                        "products_services": "Services provided"
                    }
            else:
                # Use fallback if budget exhausted
                persona['value_proposition'] = {
                    "customer_jobs": "Jobs extracted from JTBD",
                    "pains": "Common pain points identified",
                    "gains": "Desired outcomes defined",
                    "pain_relievers": "Solutions offered",
                    "gain_creators": "Value created",
                    "products_services": "Services provided",
                    "budget_fallback": True
                }
        
        return state
    
    async def _score_segments(self, state: ICPState) -> ICPState:
        """Score each segment on fit, urgency, accessibility"""
        for persona in state['personas']:
            # Score using SegmentScorerTool (would need to implement this)
            # For now, simplified scoring
            
            # Fit score: How well does positioning match needs?
            fit_score = 0.8  # Placeholder
            
            # Urgency score: How badly do they need this now?
            urgency_score = 0.7  # Placeholder
            
            # Accessibility score: Can we reach them efficiently?
            accessibility_score = 0.75  # Placeholder
            
            persona['scores'] = {
                'fit': fit_score,
                'urgency': urgency_score,
                'accessibility': accessibility_score,
                'overall': (fit_score + urgency_score + accessibility_score) / 3
            }
        
        return state
    
    async def _select_top_icps(self, state: ICPState) -> ICPState:
        """Select top N ICPs based on scores"""
        # Sort by overall score
        state['personas'].sort(key=lambda x: x['scores']['overall'], reverse=True)
        
        # Select top N
        state['icps'] = state['personas'][:state['max_icps']]
        state['status'] = 'complete'
        
        return state
    
    async def _extract_monitoring_tags(self, state: ICPState) -> ICPState:
        """Extract tags for Perplexity monitoring"""
        for icp in state['icps']:
            tag_result = self.tag_extractor._run(
                action='extract',
                icp=icp,
                count=10
            )
            
            tag_data = json.loads(tag_result)
            icp['monitoring_tags'] = tag_data['tags']
        
        return state
    
    async def _generate_embeddings(self, state: ICPState) -> ICPState:
        """Generate vector embeddings for semantic search"""
        for icp in state['icps']:
            # Create text representation
            text = f"{icp['name']} {json.dumps(icp.get('demographics', {}))} {json.dumps(icp.get('psychographics', {}))}"
            
            # Generate embedding
            embedding = generate_embedding(text)
            icp['embedding'] = embedding
            
            # Save to database
            self.supabase.table('icps').insert({
                'business_id': state['business_id'],
                'name': icp['name'],
                'demographics': icp.get('demographics'),
                'psychographics': icp.get('psychographics'),
                'jtbd': icp.get('jtbd'),
                'value_proposition': icp.get('value_proposition'),
                'platforms': icp.get('behaviors', {}).get('social_media_usage', []),
                'monitoring_tags': icp['monitoring_tags'],
                'embedding': embedding
            }).execute()
        
        return state

    def _process(self, state: ICPState) -> ICPState:
        """Main processing logic for ICP generation"""
        try:
            # Initialize state
            state['stage'] = 'processing'
            state['personas'] = []
            state['icps'] = []
            
            # Run the ICP generation workflow
            # For now, we'll run synchronously for simplicity
            # In production, this should be async
            import asyncio
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the workflow
            result = loop.run_until_complete(
                self._run_icp_workflow(state)
            )
            
            state.update(result)
            state['stage'] = 'completed'
            
        except Exception as e:
            state['error'] = str(e)
            state['stage'] = 'failed'
        
        return state

    def _validate(self, state: ICPState) -> ICPState:
        """Validate ICP results"""
        if state.get('error'):
            return state
        
        # Check if we have valid ICPs
        if not state.get('icps') or len(state['icps']) == 0:
            state['error'] = "No ICPs generated"
            return state
        
        # Validate each ICP has required fields
        required_fields = ['name', 'demographics', 'psychographics', 'value_proposition']
        for icp in state['icps']:
            for field in required_fields:
                if field not in icp or not icp[field]:
                    state['error'] = f"ICP missing required field: {field}"
                    return state
        
        return state

    async def _run_icp_workflow(self, state: ICPState) -> ICPState:
        """Run the complete ICP generation workflow"""
        # Generate personas
        state = await self._generate_personas(state)
        
        # Map JTBD
        state = await self._map_jtbd(state)
        
        # Create value propositions
        state = await self._create_value_props(state)
        
        # Score segments
        state = await self._score_segments(state)
        
        # Select top ICPs
        state = await self._select_top_icps(state)
        
        # Extract monitoring tags
        state = await self._extract_monitoring_tags(state)
        
        # Generate embeddings
        state = await self._generate_embeddings(state)
        
        return state

# Create singleton
icp_agent = ICPAgent().app

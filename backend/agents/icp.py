from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from tools.persona_generator import PersonaGeneratorTool
from tools.jtbd_mapper import JTBDMapperTool
from tools.tag_extractor import TagExtractorTool
from tools.segment_scorer import SegmentScorerTool
from utils.embeddings import generate_embedding
from utils.supabase_client import get_supabase_client
import json

class ICPState(TypedDict):
    business_id: str
    positioning: Dict
    max_icps: int
    personas: List[Dict]
    icps: List[Dict]
    status: str

class ICPAgent:
    def __init__(self):
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
        """Create value propositions for each persona"""
        positioning = state['positioning']
        
        for persona in state['personas']:
            # Use Gemini to create value prop
            from utils.gemini_client import get_gemini_client
            gemini = get_gemini_client()
            
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
            
            response = gemini.generate_content(prompt)
            vp_data = json.loads(response.text)
            
            persona['value_proposition'] = vp_data
        
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

# Create singleton
icp_agent = ICPAgent().app

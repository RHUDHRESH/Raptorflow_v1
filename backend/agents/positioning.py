from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from tools.positioning_kb import PositioningKnowledgeBaseTool
from tools.differentiation import DifferentiationAnalyzerTool
from tools.sacrifice_calculator import SacrificeCalculatorTool
from tools.visual_hammer import VisualHammerTool
from utils.gemini_client import get_gemini_client
from utils.supabase_client import get_supabase_client
import json

class PositioningState(TypedDict):
    business_id: str
    business_data: Dict
    competitor_ladder: List[Dict]
    options: List[Dict]
    selected_option: Dict
    status: str
    validation_score: float

class PositioningAgent:
    def __init__(self):
        self.kb = PositioningKnowledgeBaseTool()
        self.differentiation = DifferentiationAnalyzerTool()
        self.sacrifice_calc = SacrificeCalculatorTool()
        self.visual_hammer = VisualHammerTool()
        self.gemini = get_gemini_client()
        self.supabase = get_supabase_client()
        
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self):
        graph = StateGraph(PositioningState)
        
        graph.add_node("identify_inherent_drama", self._identify_inherent_drama)
        graph.add_node("generate_options", self._generate_positioning_options)
        graph.add_node("evaluate_differentiation", self._evaluate_differentiation)
        graph.add_node("calculate_sacrifices", self._calculate_sacrifices)
        graph.add_node("create_visual_hammers", self._create_visual_hammers)
        graph.add_node("validate_options", self._validate_options)
        
        graph.set_entry_point("identify_inherent_drama")
        graph.add_edge("identify_inherent_drama", "generate_options")
        graph.add_edge("generate_options", "evaluate_differentiation")
        graph.add_edge("evaluate_differentiation", "calculate_sacrifices")
        graph.add_edge("calculate_sacrifices", "create_visual_hammers")
        graph.add_edge("create_visual_hammers", "validate_options")
        
        graph.add_conditional_edges(
            "validate_options",
            lambda state: "approved" if state['validation_score'] > 0.75 else "rework",
            {
                "approved": END,
                "rework": "generate_options"
            }
        )
        
        return graph
    
    async def _identify_inherent_drama(self, state: PositioningState) -> PositioningState:
        """Identify inherent drama (Leo Burnett concept)"""
        business = state['business_data']
        
        # Get positioning knowledge
        kb_content = self.kb._run(action='get_principle', principle='inherent_drama')
        
        prompt = f"""Using Leo Burnett's "Inherent Drama" concept:

{kb_content}

Business: {business['name']}
Industry: {business['industry']}
Description: {business['description']}

What is the INHERENT DRAMA in this product/service?
- What human truth does it tap into?
- What emotional need does it fulfill?
- What's the natural story here?

Return JSON:
{{
  "inherent_drama": "The core human truth",
  "emotional_need": "What need it fulfills",
  "natural_story": "The narrative angle"
}}"""
        
        response = self.gemini.generate_content(prompt)
        drama_data = json.loads(response.text)
        
        state['business_data']['inherent_drama'] = drama_data
        return state
    
    async def _generate_positioning_options(self, state: PositioningState) -> PositioningState:
        """Generate 3 distinct positioning options"""
        business = state['business_data']
        competitors = state['competitor_ladder']
        
        # Get positioning principles
        law_of_focus = self.kb._run(action='get_principle', principle='law_of_focus')
        purple_cow = self.kb._run(action='get_principle', principle='purple_cow')
        
        prompt = f"""Generate 3 DISTINCT positioning options for this business.

BUSINESS:
Name: {business['name']}
Industry: {business['industry']}
Description: {business['description']}
Inherent Drama: {json.dumps(business.get('inherent_drama', {}))}

COMPETITORS OWN THESE WORDS:
{', '.join([f"{c['competitor_name']}: {c['word_owned']}" for c in competitors])}

POSITIONING PRINCIPLES:
{law_of_focus}

{purple_cow}

For EACH of 3 options, provide:
1. Word to Own: Single word or short phrase (2-3 words max)
2. Rationale: Why this positioning makes strategic sense
3. Category: Are we competing in existing category or creating new one?
4. Big Idea: Simple creative concept that makes brand unforgettable
5. Purple Cow Moment: The remarkable element

Make options DIFFERENT from each other and from competitors.

Return JSON:
{{
  "options": [
    {{
      "word": "speed|quality|innovation|etc",
      "rationale": "Why this works",
      "category": "existing|new",
      "big_idea": "Creative concept",
      "purple_cow": "Remarkable element",
      "target_emotion": "What emotion we trigger"
    }}
  ]
}}"""
        
        response = self.gemini.generate_content(prompt)
        options_data = json.loads(response.text)
        
        state['options'] = options_data['options']
        return state
    
    async def _evaluate_differentiation(self, state: PositioningState) -> PositioningState:
        """Score each option for differentiation"""
        for option in state['options']:
            diff_result = self.differentiation._run(
                action='analyze',
                positioning=option['word'],
                competitor_ladder=state['competitor_ladder']
            )
            
            diff_data = json.loads(diff_result)
            option['differentiation_score'] = diff_data['differentiation_score']
            option['conflicts'] = diff_data['conflicts']
        
        return state
    
    async def _calculate_sacrifices(self, state: PositioningState) -> PositioningState:
        """Calculate required sacrifices for each option"""
        for option in state['options']:
            sacrifice_result = self.sacrifice_calc._run(
                action='calculate',
                positioning=option,
                business_data=state['business_data']
            )
            
            sacrifice_data = json.loads(sacrifice_result)
            option['sacrifices'] = sacrifice_data['sacrifices']
            option['sacrifice_score'] = sacrifice_data['sacrifice_score']
        
        return state
    
    async def _create_visual_hammers(self, state: PositioningState) -> PositioningState:
        """Generate visual hammer concepts for each option"""
        for option in state['options']:
            hammer_result = self.visual_hammer._run(
                action='generate',
                positioning=option,
                business_data=state['business_data']
            )
            
            hammer_data = json.loads(hammer_result)
            option['visual_hammers'] = hammer_data['hammers'][:3]  # Top 3
            option['recommended_hammer'] = hammer_data['recommended']
        
        return state
    
    async def _validate_options(self, state: PositioningState) -> PositioningState:
        """Validate overall quality of options"""
        scores = []
        
        for option in state['options']:
            # Calculate composite score
            diff_score = option.get('differentiation_score', 0)
            sacrifice_score = option.get('sacrifice_score', 0)
            
            # Has visual hammer?
            has_hammer = len(option.get('visual_hammers', [])) > 0
            hammer_score = 1.0 if has_hammer else 0.0
            
            composite = (diff_score * 0.5) + (sacrifice_score * 0.3) + (hammer_score * 0.2)
            option['composite_score'] = composite
            scores.append(composite)
        
        # Overall validation
        state['validation_score'] = sum(scores) / len(scores) if scores else 0
        
        if state['validation_score'] > 0.75:
            state['status'] = 'approved'
        else:
            state['status'] = 'needs_rework'
        
        # Sort options by score
        state['options'].sort(key=lambda x: x['composite_score'], reverse=True)
        
        return state

# Create singleton
positioning_agent = PositioningAgent().app

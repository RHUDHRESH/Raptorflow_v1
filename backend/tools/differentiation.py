from langchain.tools import BaseTool
from typing import List, Dict
from utils.embeddings import generate_embedding
from utils.supabase_client import get_supabase_client
import numpy as np
import json

class DifferentiationAnalyzerTool(BaseTool):
    name = "differentiation_analyzer"
    description = """
    Analyze how differentiated a positioning is from competitors.
    
    Operations:
    - analyze: Score positioning against competitor ladder
    - compare: Compare multiple positioning options
    - find_conflicts: Identify positioning conflicts
    - recommend: Suggest improvements for differentiation
    
    Examples:
    differentiation_analyzer(action='analyze', positioning='fastest delivery', competitor_ladder=[...])
    differentiation_analyzer(action='compare', options=[{}, {}, {}], competitor_ladder=[...])
    """
    
    def __init__(self):
        super().__init__()
        self.supabase = get_supabase_client()
    
    def _run(
        self,
        action: str,
        positioning: Optional[str] = None,
        options: Optional[List[Dict]] = None,
        competitor_ladder: Optional[List[Dict]] = None,
        business_id: Optional[str] = None
    ) -> str:
        
        # Load competitor ladder if not provided
        if not competitor_ladder and business_id:
            result = self.supabase.table('competitor_ladder')\
                .select('*')\
                .eq('business_id', business_id)\
                .execute()
            competitor_ladder = result.data
        
        if not competitor_ladder:
            raise ValueError("competitor_ladder or business_id required")
        
        if action == 'analyze':
            if not positioning:
                raise ValueError("analyze requires: positioning")
            
            conflicts = []
            position_embedding = generate_embedding(positioning)
            
            for competitor in competitor_ladder:
                word_owned = competitor['word_owned']
                comp_embedding = generate_embedding(word_owned)
                
                # Calculate semantic similarity
                similarity = self._cosine_similarity(position_embedding, comp_embedding)
                
                if similarity > 0.7:  # High similarity = conflict
                    conflicts.append({
                        'competitor': competitor['competitor_name'],
                        'their_position': word_owned,
                        'similarity_score': round(similarity, 3),
                        'position_strength': competitor['position_strength'],
                        'conflict_severity': round(similarity * competitor['position_strength'], 3)
                    })
            
            # Calculate overall differentiation score
            if conflicts:
                max_conflict = max(c['conflict_severity'] for c in conflicts)
                differentiation_score = max(0, 1.0 - max_conflict)
            else:
                differentiation_score = 1.0
            
            # Categorize differentiation
            if differentiation_score >= 0.8:
                category = "HIGHLY_DIFFERENTIATED"
                recommendation = "Strong positioning with clear differentiation."
            elif differentiation_score >= 0.6:
                category = "MODERATELY_DIFFERENTIATED"
                recommendation = "Good differentiation, but watch for competitor overlap."
            elif differentiation_score >= 0.4:
                category = "WEAKLY_DIFFERENTIATED"
                recommendation = "Significant overlap with competitors. Consider pivoting."
            else:
                category = "NOT_DIFFERENTIATED"
                recommendation = "Direct conflict with existing players. Must choose different positioning."
            
            return json.dumps({
                'positioning': positioning,
                'differentiation_score': round(differentiation_score, 3),
                'category': category,
                'conflicts': conflicts,
                'recommendation': recommendation,
                'is_unique': len(conflicts) == 0
            })
        
        elif action == 'compare':
            if not options:
                raise ValueError("compare requires: options")
            
            results = []
            for i, option in enumerate(options):
                word = option.get('word', option.get('positioning', ''))
                analysis = json.loads(self._run(
                    action='analyze',
                    positioning=word,
                    competitor_ladder=competitor_ladder
                ))
                results.append({
                    'option_index': i,
                    'option': option,
                    'analysis': analysis
                })
            
            # Rank by differentiation score
            results.sort(key=lambda x: x['analysis']['differentiation_score'], reverse=True)
            
            return json.dumps({
                'options_analyzed': len(options),
                'ranked_results': results,
                'best_option': results[0]['option_index'],
                'best_differentiation_score': results[0]['analysis']['differentiation_score']
            })
        
        elif action == 'find_conflicts':
            if not positioning:
                raise ValueError("find_conflicts requires: positioning")
            
            analysis = json.loads(self._run(
                action='analyze',
                positioning=positioning,
                competitor_ladder=competitor_ladder
            ))
            
            return json.dumps({
                'positioning': positioning,
                'conflicts': analysis['conflicts'],
                'conflict_count': len(analysis['conflicts']),
                'has_conflicts': len(analysis['conflicts']) > 0
            })
        
        elif action == 'recommend':
            if not positioning:
                raise ValueError("recommend requires: positioning")
            
            analysis = json.loads(self._run(
                action='analyze',
                positioning=positioning,
                competitor_ladder=competitor_ladder
            ))
            
            if analysis['differentiation_score'] >= 0.8:
                recommendations = [
                    "Your positioning is strong. Maintain consistency.",
                    "Build brand assets around this positioning.",
                    "Create content that reinforces this unique position."
                ]
            elif analysis['conflicts']:
                main_conflict = analysis['conflicts'][0]
                recommendations = [
                    f"Avoid direct conflict with {main_conflict['competitor']} who owns '{main_conflict['their_position']}'",
                    "Consider positioning as the opposite (Law of Opposite)",
                    f"Try narrowing to a niche (e.g., 'fastest delivery for busy professionals' vs just 'fastest')",
                    "Explore adjacent attributes that are unowned"
                ]
            else:
                recommendations = [
                    "Strengthen your position with specific evidence",
                    "Make your positioning more concrete and memorable",
                    "Add a visual hammer to reinforce the position"
                ]
            
            return json.dumps({
                'positioning': positioning,
                'differentiation_score': analysis['differentiation_score'],
                'recommendations': recommendations
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)

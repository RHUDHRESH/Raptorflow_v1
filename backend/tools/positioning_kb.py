from langchain.tools import BaseTool
from typing import Optional
import os
from utils.embeddings import generate_embedding
import numpy as np

class PositioningKnowledgeBaseTool(BaseTool):
    name = "positioning_kb"
    description = """
    Access marketing positioning principles from Ries, Trout, Godin, Burnett, Ogilvy.
    
    Operations:
    - get_principle: Get specific principle by name
    - search: Semantic search for relevant principles
    - get_all: Get all principles
    - get_by_author: Get principles by author
    
    Examples:
    positioning_kb(action='get_principle', principle='law_of_focus')
    positioning_kb(action='search', query='how to differentiate from competitors')
    positioning_kb(action='get_by_author', author='Seth Godin')
    """
    
    def __init__(self):
        super().__init__()
        self.knowledge = self._load_knowledge()
        self.principles_map = self._build_principles_map()
    
    def _load_knowledge(self) -> str:
        knowledge_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'positioning_principles.txt')
        with open(knowledge_path, 'r') as f:
            return f.read()
    
    def _build_principles_map(self) -> dict:
        """Map principle names to their content"""
        return {
            'law_of_focus': 'LAW OF FOCUS',
            'law_of_sacrifice': 'LAW OF SACRIFICE',
            'law_of_category': 'LAW OF CATEGORY',
            'law_of_ladder': 'LAW OF LADDER',
            'law_of_opposite': 'LAW OF OPPOSITE',
            'purple_cow': 'PURPLE COW',
            'permission_marketing': 'PERMISSION MARKETING',
            'inherent_drama': 'INHERENT DRAMA',
            'big_idea': 'BIG IDEA',
            'visual_hammer': 'VISUAL HAMMER',
            'research_first': 'RESEARCH FIRST',
            'benefits_over_features': 'BENEFITS > FEATURES'
        }
    
    def _run(
        self,
        action: str = 'get_all',
        principle: Optional[str] = None,
        query: Optional[str] = None,
        author: Optional[str] = None
    ) -> str:
        
        if action == 'get_principle':
            if not principle:
                raise ValueError("get_principle requires: principle")
            
            # Find the section
            search_term = self.principles_map.get(principle, principle.upper())
            lines = self.knowledge.split('\n')
            section = []
            capture = False
            
            for line in lines:
                if search_term in line:
                    capture = True
                elif capture and line.startswith('##'):
                    break
                
                if capture:
                    section.append(line)
            
            if section:
                return '\n'.join(section)
            else:
                return f"Principle '{principle}' not found. Available: {', '.join(self.principles_map.keys())}"
        
        elif action == 'search':
            if not query:
                raise ValueError("search requires: query")
            
            # Split knowledge into chunks
            chunks = self.knowledge.split('\n\n')
            
            # Generate query embedding
            query_embedding = generate_embedding(query)
            
            # Find best matches
            best_matches = []
            for chunk in chunks:
                if len(chunk.strip()) < 20:  # Skip very short chunks
                    continue
                
                chunk_embedding = generate_embedding(chunk)
                similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                
                if similarity > 0.5:  # Threshold
                    best_matches.append({
                        'content': chunk,
                        'similarity': similarity
                    })
            
            # Sort by similarity
            best_matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top 3
            return '\n\n---\n\n'.join([m['content'] for m in best_matches[:3]])
        
        elif action == 'get_by_author':
            if not author:
                raise ValueError("get_by_author requires: author")
            
            lines = self.knowledge.split('\n')
            author_content = []
            capture = False
            
            for line in lines:
                if author.lower() in line.lower():
                    capture = True
                elif capture and any(name in line for name in ['Ries', 'Trout', 'Godin', 'Burnett', 'Ogilvy']) and author.lower() not in line.lower():
                    break
                
                if capture:
                    author_content.append(line)
            
            return '\n'.join(author_content) if author_content else f"No content found for author: {author}"
        
        elif action == 'get_all':
            return self.knowledge
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)

# Additional tools to implement:
# - Differentiation analyzer
# - Sacrifice calculator
# - Visual hammer generator
# - Persona generator
# - JTBD mapper
# - Tag extractor
# - 7Ps builder
# - Calendar generator
# - Platform validator
# - All remaining tools (30+ more)
# - Complete agent implementations
# - Complete API endpoints
# - Frontend components
# - Deployment scripts

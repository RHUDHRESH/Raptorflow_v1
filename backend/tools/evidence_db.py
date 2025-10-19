from langchain.tools import BaseTool
from typing import List, Dict, Optional
from utils.supabase_client import get_supabase_client
from utils.embeddings import generate_embedding
import json

class EvidenceDBTool(BaseTool):
    name = "evidence_db"
    description = """
    Query and manipulate evidence graph. Operations:
    - create_node: Add evidence/claim/insight node
    - create_edge: Link two nodes
    - search: Text search in evidence
    - semantic_search: Vector similarity search
    - get_subgraph: Get node and all connected nodes
    - get_claims: Get all claims for business
    - get_rtbs: Get all RTBs supporting a claim
    - calculate_confidence: Compute claim confidence from evidence
    
    Examples:
    evidence_db(action='create_node', business_id='uuid', type='claim', content='We are fastest')
    evidence_db(action='create_edge', from_id='uuid1', to_id='uuid2', type='supports', strength=0.9)
    evidence_db(action='semantic_search', query='fast delivery', threshold=0.8)
    """
    
    def __init__(self):
        super().__init__()
        self.supabase = get_supabase_client()
    
    def _run(
        self,
        action: str,
        business_id: Optional[str] = None,
        node_type: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict] = None,
        confidence_score: float = 1.0,
        source: str = 'agent',
        from_id: Optional[str] = None,
        to_id: Optional[str] = None,
        relationship_type: Optional[str] = None,
        strength: float = 1.0,
        query: Optional[str] = None,
        threshold: float = 0.7,
        limit: int = 10,
        node_id: Optional[str] = None
    ) -> str:
        
        if action == 'create_node':
            if not business_id or not node_type or not content:
                raise ValueError("create_node requires: business_id, node_type, content")
            
            # Generate embedding for semantic search
            embedding = generate_embedding(content)
            
            result = self.supabase.table('evidence_nodes').insert({
                'business_id': business_id,
                'node_type': node_type,  # claim, rtb, insight, competitor
                'content': content,
                'metadata': metadata or {},
                'confidence_score': confidence_score,
                'source': source,
                'embedding': embedding
            }).execute()
            
            return json.dumps({
                'success': True,
                'node_id': result.data[0]['id'],
                'node': result.data[0]
            })
        
        elif action == 'create_edge':
            if not from_id or not to_id or not relationship_type:
                raise ValueError("create_edge requires: from_id, to_id, relationship_type")
            
            result = self.supabase.table('evidence_edges').insert({
                'from_node': from_id,
                'to_node': to_id,
                'relationship_type': relationship_type,  # supports, contradicts, relates_to
                'strength': strength,
                'created_by_agent': source
            }).execute()
            
            return json.dumps({
                'success': True,
                'edge_id': result.data[0]['id']
            })
        
        elif action == 'search':
            if not query:
                raise ValueError("search requires: query")
            
            result = self.supabase.table('evidence_nodes')\
                .select('*')\
                .ilike('content', f'%{query}%')
            
            if business_id:
                result = result.eq('business_id', business_id)
            
            result = result.limit(limit).execute()
            
            return json.dumps(result.data)
        
        elif action == 'semantic_search':
            if not query:
                raise ValueError("semantic_search requires: query")
            
            # Generate query embedding
            query_embedding = generate_embedding(query)
            
            # Call Supabase RPC function for vector similarity
            result = self.supabase.rpc('match_evidence', {
                'query_embedding': query_embedding,
                'match_threshold': threshold,
                'match_count': limit,
                'business_id_filter': business_id
            }).execute()
            
            return json.dumps(result.data)
        
        elif action == 'get_subgraph':
            if not node_id:
                raise ValueError("get_subgraph requires: node_id")
            
            # Get the node
            node = self.supabase.table('evidence_nodes')\
                .select('*')\
                .eq('id', node_id)\
                .single()\
                .execute()
            
            # Get all outgoing edges
            outgoing = self.supabase.table('evidence_edges')\
                .select('*, to_node:evidence_nodes!to_node(*)')\
                .eq('from_node', node_id)\
                .execute()
            
            # Get all incoming edges
            incoming = self.supabase.table('evidence_edges')\
                .select('*, from_node:evidence_nodes!from_node(*)')\
                .eq('to_node', node_id)\
                .execute()
            
            return json.dumps({
                'node': node.data,
                'outgoing': outgoing.data,
                'incoming': incoming.data
            })
        
        elif action == 'get_claims':
            if not business_id:
                raise ValueError("get_claims requires: business_id")
            
            result = self.supabase.table('evidence_nodes')\
                .select('*')\
                .eq('business_id', business_id)\
                .eq('node_type', 'claim')\
                .execute()
            
            return json.dumps(result.data)
        
        elif action == 'get_rtbs':
            if not node_id:
                raise ValueError("get_rtbs requires: node_id (claim node)")
            
            # Get all RTBs supporting this claim
            result = self.supabase.table('evidence_edges')\
                .select('*, to_node:evidence_nodes!to_node(*)')\
                .eq('from_node', node_id)\
                .eq('relationship_type', 'supported_by')\
                .execute()
            
            return json.dumps([edge['to_node'] for edge in result.data])
        
        elif action == 'calculate_confidence':
            if not node_id:
                raise ValueError("calculate_confidence requires: node_id")
            
            # Get all supporting evidence
            rtbs = json.loads(self._run(action='get_rtbs', node_id=node_id))
            
            if not rtbs:
                confidence = 0.0
            else:
                # Average confidence of all supporting evidence
                confidence = sum(rtb['confidence_score'] for rtb in rtbs) / len(rtbs)
            
            # Update the claim's confidence
            self.supabase.table('evidence_nodes')\
                .update({'confidence_score': confidence})\
                .eq('id', node_id)\
                .execute()
            
            return json.dumps({
                'node_id': node_id,
                'confidence': confidence,
                'supporting_evidence_count': len(rtbs)
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)

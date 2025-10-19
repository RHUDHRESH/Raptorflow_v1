from langchain.tools import BaseTool
from typing import Optional, Dict, Any
from utils.supabase_client import get_supabase_client
import json
from datetime import datetime

class StateManagerTool(BaseTool):
    name = "state_manager"
    description = """
    Manage agent state in database. Operations:
    - save: Store agent state and context
    - load: Retrieve agent state by session_id
    - update: Update existing state
    - list: Get all sessions for a business
    - delete: Remove old sessions
    
    Examples:
    state_manager(action='save', agent='research', business_id='uuid', state={'step': 1}, context={'findings': []})
    state_manager(action='load', session_id='uuid')
    state_manager(action='update', session_id='uuid', state={'step': 2})
    """
    
    def __init__(self):
        super().__init__()
        self.supabase = get_supabase_client()
    
    def _run(
        self, 
        action: str,
        agent: Optional[str] = None,
        business_id: Optional[str] = None,
        state: Optional[Dict] = None,
        context: Optional[Dict] = None,
        session_id: Optional[str] = None,
        status: str = 'running'
    ) -> str:
        
        if action == 'save':
            if not agent or not business_id or not state:
                raise ValueError("save requires: agent, business_id, state")
            
            result = self.supabase.table('agent_sessions').insert({
                'business_id': business_id,
                'agent_name': agent,
                'state': state,
                'context': context or {},
                'status': status,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
            
            return json.dumps({
                'success': True,
                'session_id': result.data[0]['id'],
                'message': f'State saved for {agent}'
            })
        
        elif action == 'load':
            if not session_id:
                raise ValueError("load requires: session_id")
            
            result = self.supabase.table('agent_sessions')\
                .select('*')\
                .eq('id', session_id)\
                .single()\
                .execute()
            
            return json.dumps(result.data)
        
        elif action == 'update':
            if not session_id:
                raise ValueError("update requires: session_id")
            
            update_data = {'updated_at': datetime.utcnow().isoformat()}
            if state is not None:
                update_data['state'] = state
            if context is not None:
                update_data['context'] = context
            if status:
                update_data['status'] = status
            
            result = self.supabase.table('agent_sessions')\
                .update(update_data)\
                .eq('id', session_id)\
                .execute()
            
            return json.dumps({
                'success': True,
                'message': 'State updated'
            })
        
        elif action == 'list':
            if not business_id:
                raise ValueError("list requires: business_id")
            
            result = self.supabase.table('agent_sessions')\
                .select('*')\
                .eq('business_id', business_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return json.dumps(result.data)
        
        elif action == 'delete':
            if not session_id:
                raise ValueError("delete requires: session_id")
            
            self.supabase.table('agent_sessions')\
                .delete()\
                .eq('id', session_id)\
                .execute()
            
            return json.dumps({
                'success': True,
                'message': 'Session deleted'
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)

from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from tools.calendar_generator import CalendarGeneratorTool
from tools.platform_validator import PlatformValidatorTool
from tools.asset_factory import AssetFactoryTool
from tools.multi_channel_adapter import MultiChannelAdapterTool
from utils.supabase_client import get_supabase_client
import json

class ContentState(TypedDict):
    business_id: str
    goal: str
    platform: str
    duration_days: int
    icps: List[Dict]
    positioning: Dict
    calendar: Dict
    status: str

class ContentAgent:
    def __init__(self):
        self.calendar_gen = CalendarGeneratorTool()
        self.validator = PlatformValidatorTool()
        self.asset_factory = AssetFactoryTool()
        self.multi_channel = MultiChannelAdapterTool()
        self.supabase = get_supabase_client()
        
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self):
        graph = StateGraph(ContentState)
        
        graph.add_node("generate_calendar", self._generate_calendar)
        graph.add_node("validate_content", self._validate_all_content)
        graph.add_node("create_asset_briefs", self._create_asset_briefs)
        graph.add_node("finalize", self._finalize_calendar)
        
        graph.set_entry_point("generate_calendar")
        graph.add_edge("generate_calendar", "validate_content")
        graph.add_edge("validate_content", "create_asset_briefs")
        graph.add_edge("create_asset_briefs", "finalize")
        graph.add_edge("finalize", END)
        
        return graph
    
    async def _generate_calendar(self, state: ContentState) -> ContentState:
        """Generate complete content calendar"""
        result = self.calendar_gen._run(
            duration_days=state['duration_days'],
            platform=state['platform'],
            goal=state['goal'],
            icps=state['icps'],
            positioning=state.get('positioning')
        )
        
        calendar_data = json.loads(result)
        state['calendar'] = calendar_data
        
        return state
    
    async def _validate_all_content(self, state: ContentState) -> ContentState:
        """Validate all posts against platform specs"""
        calendar = state['calendar']
        platform = state['platform']
        
        for day in calendar['calendar']:
            for post in day['posts']:
                if not post.get('valid', True):
                    # Auto-fix if possible
                    fix_result = self.validator._run(
                        action='suggest_fix',
                        platform=platform,
                        content={
                            'text': post['text'],
                            'hashtags': post.get('hashtags', [])
                        }
                    )
                    
                    fix_data = json.loads(fix_result)
                    if 'fixed_content' in fix_data:
                        post['text'] = fix_data['fixed_content']['text']
                        post['hashtags'] = fix_data['fixed_content'].get('hashtags', [])
                        post['valid'] = True
                        post['auto_fixed'] = True
        
        return state
    
    async def _create_asset_briefs(self, state: ContentState) -> ContentState:
        """Create asset briefs for visual content"""
        calendar = state['calendar']
        
        for day in calendar['calendar']:
            for post in day['posts']:
                if post.get('format') in ['video', 'carousel', 'image']:
                    brief_result = self.asset_factory._run(
                        action='generate_brief',
                        post=post
                    )
                    
                    post['asset_brief'] = json.loads(brief_result)
        
        return state
    
    async def _finalize_calendar(self, state: ContentState) -> ContentState:
        """Finalize and save calendar"""
        # Save to database
        move_result = self.supabase.table('moves').insert({
            'business_id': state['business_id'],
            'goal': state['goal'],
            'platform': state['platform'],
            'duration_days': state['duration_days'],
            'calendar': state['calendar'],
            'status': 'active'
        }).execute()
        
        state['calendar']['move_id'] = move_result.data[0]['id']
        state['status'] = 'complete'
        
        return state

# Create singleton
content_agent = ContentAgent().app

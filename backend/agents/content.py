from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from ..tools.calendar_generator import CalendarGeneratorTool
from ..tools.platform_validator import PlatformValidatorTool
from ..tools.asset_factory import AssetFactoryTool
from ..tools.multi_channel_adapter import MultiChannelAdapterTool
from ..utils.supabase_client import get_supabase_client
from .base_agent import BaseAgent, AgentState
import json

class ContentState(AgentState):
    goal: str
    platform: str
    duration_days: int
    icps: List[Dict]
    positioning: Dict
    calendar: Dict

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Content Agent", "Generates content calendars with budget-controlled AI")
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

    def _process(self, state: ContentState) -> ContentState:
        """Main processing logic for content calendar generation"""
        try:
            # Initialize state
            state['stage'] = 'processing'
            state['calendar'] = {}
            
            # Run the content generation workflow
            import asyncio
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the workflow
            result = loop.run_until_complete(
                self._run_content_workflow(state)
            )
            
            state.update(result)
            state['stage'] = 'completed'
            
        except Exception as e:
            state['error'] = str(e)
            state['stage'] = 'failed'
        
        return state

    def _validate(self, state: ContentState) -> ContentState:
        """Validate content calendar results"""
        if state.get('error'):
            return state
        
        # Check if we have a valid calendar
        if not state.get('calendar') or 'calendar' not in state['calendar']:
            state['error'] = "No calendar generated"
            return state
        
        # Validate calendar structure
        calendar = state['calendar']['calendar']
        if not isinstance(calendar, list) or len(calendar) == 0:
            state['error'] = "Invalid calendar structure"
            return state
        
        # Check each day has posts
        for day in calendar:
            if 'posts' not in day or not isinstance(day['posts'], list):
                state['error'] = "Invalid day structure in calendar"
                return state
        
        return state

    async def _run_content_workflow(self, state: ContentState) -> ContentState:
        """Run the complete content generation workflow"""
        # Generate calendar
        state = await self._generate_calendar(state)
        
        # Validate content
        state = await self._validate_all_content(state)
        
        # Create asset briefs
        state = await self._create_asset_briefs(state)
        
        # Finalize calendar
        state = await self._finalize_calendar(state)
        
        return state

    def _enhance_posts_with_ai(self, posts: List[Dict], platform: str, goal: str) -> List[Dict]:
        """Enhance posts with budget-controlled AI for better quality"""
        enhanced_posts = []
        
        for post in posts:
            # Use budget-controlled AI to enhance post content
            prompt = f"""Enhance this social media post for {platform}.

GOAL: {goal}
PLATFORM: {platform}
CURRENT POST: {json.dumps(post)}

Enhancement requirements:
1. Make it more engaging and compelling
2. Ensure it follows platform best practices
3. Optimize for the target audience
4. Add relevant hashtags if missing
5. Keep the core message intact

Return enhanced post as JSON with the same structure."""
            
            ai_result = self.call_ai_with_budget_control(
                prompt=prompt,
                task_complexity="simple",  # Post enhancement is relatively simple
                estimated_tokens=600
            )
            
            if ai_result["success"]:
                try:
                    enhanced_post = json.loads(ai_result["content"])
                    enhanced_post['ai_enhanced'] = True
                    enhanced_post['enhancement_cost'] = ai_result['cost']
                    enhanced_posts.append(enhanced_post)
                except json.JSONDecodeError:
                    # Use original post if enhancement fails
                    post['ai_enhanced'] = False
                    post['enhancement_failed'] = True
                    enhanced_posts.append(post)
            else:
                # Use original post if budget exhausted
                post['ai_enhanced'] = False
                post['budget_fallback'] = True
                enhanced_posts.append(post)
        
        return enhanced_posts

# Create singleton
content_agent = ContentAgent().app

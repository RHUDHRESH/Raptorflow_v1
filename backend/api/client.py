"""
API Client Layer - Handles all communication between frontend and backend
Provides clean, typed interfaces for frontend consumption
"""
import logging
import json
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class RaptorflowAPIClient:
    """Main API client for frontend integration"""

    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.timeout = 60.0

    # ==================== INTAKE FLOW ====================

    async def intake_business(
        self,
        name: str,
        industry: str,
        location: str,
        description: str,
        goals: str
    ) -> Dict[str, Any]:
        """
        Create new business and start research flow

        Returns: {business_id, subscription_tier, subscription_id}
        """
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            # Save business
            result = supabase.table('businesses').insert({
                'name': name,
                'industry': industry,
                'location': location,
                'description': description,
                'goals': {'text': goals}
            }).execute()

            business_id = result.data[0]['id']

            # Create trial subscription
            sub_result = supabase.table('subscriptions').insert({
                'business_id': business_id,
                'tier': 'trial',
                'max_icps': 3,
                'max_moves': 5,
                'status': 'trial'
            }).execute()

            return {
                "success": True,
                "business_id": business_id,
                "subscription_tier": "trial",
                "subscription_id": sub_result.data[0]['id']
            }

        except Exception as e:
            logger.error(f"Intake failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # ==================== RESEARCH FLOW ====================

    async def run_research(self, business_id: str) -> AsyncGenerator:
        """
        Run research analysis with streaming progress updates

        Yields: {stage, status, progress, data}
        """
        from agents.research_v2 import research_agent
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            # Get business
            biz_result = supabase.table('businesses').select('*').eq('id', business_id).single().execute()
            business_data = biz_result.data

            # Stage 1: SOSTAC Analysis
            yield {
                "stage": "sostac_analysis",
                "status": "running",
                "progress": 0.15,
                "message": "Analyzing business situation..."
            }

            # Stage 2: Competitor Research
            yield {
                "stage": "competitor_research",
                "status": "running",
                "progress": 0.35,
                "message": "Researching competitors..."
            }

            # Stage 3: Build Ladder
            yield {
                "stage": "build_ladder",
                "status": "running",
                "progress": 0.50,
                "message": "Building competitor ladder..."
            }

            # Stage 4: Gather Evidence
            yield {
                "stage": "gather_evidence",
                "status": "running",
                "progress": 0.70,
                "message": "Gathering evidence..."
            }

            # Stage 5: Validate
            yield {
                "stage": "validate",
                "status": "running",
                "progress": 0.90,
                "message": "Validating research..."
            }

            # Run actual research
            result = await research_agent.analyze_business(business_id, business_data)

            if result.get("success"):
                # Save results
                research_data = result.get("results", {})

                supabase.table('sostac_analyses').insert({
                    'business_id': business_id,
                    'situation': research_data.get('sostac', {}).get('situation'),
                    'objectives': research_data.get('sostac', {}).get('objectives'),
                    'strategy': research_data.get('sostac', {}).get('strategy'),
                    'tactics': {},
                    'action': {},
                    'control': {}
                }).execute()

                supabase.table('competitor_ladder').insert(
                    [{"business_id": business_id, **comp} for comp in research_data.get('competitor_ladder', [])]
                ).execute()

                yield {
                    "stage": "complete",
                    "status": "completed",
                    "progress": 1.0,
                    "data": research_data
                }
            else:
                yield {
                    "stage": "error",
                    "status": "failed",
                    "error": result.get("error")
                }

        except Exception as e:
            logger.exception(f"Research failed: {str(e)}")
            yield {
                "stage": "error",
                "status": "failed",
                "error": str(e)
            }

    # ==================== POSITIONING FLOW ====================

    async def generate_positioning(self, business_id: str) -> AsyncGenerator:
        """Generate 3 positioning options with streaming"""
        from agents.positioning_v2 import positioning_agent
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            yield {
                "stage": "start",
                "status": "running",
                "progress": 0.1,
                "message": "Initializing positioning analysis..."
            }

            # Get business data
            biz = supabase.table('businesses').select('*').eq('id', business_id).single().execute()
            business_data = biz.data

            # Get research results
            sostac = supabase.table('sostac_analyses').select('*').eq('business_id', business_id).single().execute()
            competitor_ladder = supabase.table('competitor_ladder').select('*').eq('business_id', business_id).execute()

            yield {
                "stage": "analyzing",
                "status": "running",
                "progress": 0.4,
                "message": "Analyzing drama and positioning..."
            }

            # Generate positioning
            result = await positioning_agent.generate_positioning(
                business_id,
                business_data,
                competitor_ladder.data,
                sostac.data if sostac.data else {}
            )

            if result.get("success"):
                options = result.get("results", {}).get("options", [])

                # Save to database
                supabase.table('positioning_analyses').insert({
                    'business_id': business_id,
                    'options': options,
                    'inherent_drama': result.get("results", {}).get("inherent_drama")
                }).execute()

                yield {
                    "stage": "complete",
                    "status": "completed",
                    "progress": 1.0,
                    "data": {
                        "options": options,
                        "inherent_drama": result.get("results", {}).get("inherent_drama")
                    }
                }
            else:
                yield {
                    "stage": "error",
                    "status": "failed",
                    "error": result.get("error")
                }

        except Exception as e:
            logger.exception(f"Positioning generation failed: {str(e)}")
            yield {
                "stage": "error",
                "status": "failed",
                "error": str(e)
            }

    async def select_positioning(self, business_id: str, option_index: int) -> Dict[str, Any]:
        """Select a positioning option"""
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            analysis = supabase.table('positioning_analyses').select('*').eq('business_id', business_id).single().execute()

            if not analysis.data or not analysis.data.get('options'):
                return {"success": False, "error": "No positioning analysis found"}

            options = analysis.data['options']

            if option_index < 0 or option_index >= len(options):
                return {"success": False, "error": "Invalid option index"}

            selected = options[option_index]

            supabase.table('positioning_analyses').update({
                'selected_option': selected
            }).eq('id', analysis.data['id']).execute()

            return {
                "success": True,
                "selected_positioning": selected
            }

        except Exception as e:
            logger.error(f"Selection failed: {str(e)}")
            return {"success": False, "error": str(e)}

    # ==================== ICP FLOW ====================

    async def generate_icps(self, business_id: str, max_icps: int = 3) -> AsyncGenerator:
        """Generate ICPs with streaming"""
        from agents.icp_v2 import icp_agent
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            # Check tier
            sub = supabase.table('subscriptions').select('*').eq('business_id', business_id).single().execute()
            tier_max = sub.data.get('max_icps', 3)
            max_icps = min(max_icps, tier_max)

            yield {
                "stage": "start",
                "status": "running",
                "progress": 0.1,
                "message": f"Generating {max_icps} customer profiles..."
            }

            # Get business and positioning
            biz = supabase.table('businesses').select('*').eq('id', business_id).single().execute()
            pos = supabase.table('positioning_analyses').select('*').eq('business_id', business_id).single().execute()

            if not pos.data or not pos.data.get('selected_option'):
                yield {
                    "stage": "error",
                    "status": "failed",
                    "error": "No positioning selected"
                }
                return

            yield {
                "stage": "analyzing",
                "status": "running",
                "progress": 0.5,
                "message": "Creating detailed personas..."
            }

            # Generate ICPs
            result = await icp_agent.generate_icps(
                business_id,
                biz.data,
                pos.data['selected_option'],
                max_icps
            )

            if result.get("success"):
                icps = result.get("results", {}).get("icps", [])

                # Save to database
                for icp in icps:
                    supabase.table('icps').insert({
                        'business_id': business_id,
                        'name': icp.get('name'),
                        'demographics': icp.get('demographics'),
                        'psychographics': icp.get('psychographics'),
                        'jtbd': icp.get('jtbd'),
                        'platforms': icp.get('behavior', {}).get('top_platforms', []),
                        'content_preferences': icp.get('behavior', {}).get('content_preferences'),
                        'trending_topics': icp.get('monitoring_tags', []),
                        'tags': icp.get('monitoring_tags', [])
                    }).execute()

                yield {
                    "stage": "complete",
                    "status": "completed",
                    "progress": 1.0,
                    "data": {
                        "icps": icps,
                        "count": len(icps)
                    }
                }
            else:
                yield {
                    "stage": "error",
                    "status": "failed",
                    "error": result.get("error")
                }

        except Exception as e:
            logger.exception(f"ICP generation failed: {str(e)}")
            yield {
                "stage": "error",
                "status": "failed",
                "error": str(e)
            }

    # ==================== DATA RETRIEVAL ====================

    async def get_business(self, business_id: str) -> Dict[str, Any]:
        """Get business details"""
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            result = supabase.table('businesses').select('*').eq('id', business_id).single().execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_research_data(self, business_id: str) -> Dict[str, Any]:
        """Get research analysis"""
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            sostac = supabase.table('sostac_analyses').select('*').eq('business_id', business_id).single().execute()
            competitors = supabase.table('competitor_ladder').select('*').eq('business_id', business_id).execute()

            return {
                "success": True,
                "data": {
                    "sostac": sostac.data if sostac.data else {},
                    "competitors": competitors.data
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_positioning(self, business_id: str) -> Dict[str, Any]:
        """Get positioning analysis"""
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            result = supabase.table('positioning_analyses').select('*').eq('business_id', business_id).single().execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_icps(self, business_id: str) -> Dict[str, Any]:
        """Get all ICPs for business"""
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            result = supabase.table('icps').select('*').eq('business_id', business_id).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_subscription(self, business_id: str) -> Dict[str, Any]:
        """Get subscription tier"""
        from utils.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        try:
            result = supabase.table('subscriptions').select('*').eq('business_id', business_id).single().execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
api_client = RaptorflowAPIClient()

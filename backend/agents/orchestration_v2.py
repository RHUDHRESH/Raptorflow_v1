"""
RaptorFlow Orchestration v2: 3-Tier AI with LangGraph

Complete marketing strategy generation workflow with:
- Intelligent model routing (nano/mini/full)
- Real-time progress streaming
- Budget tracking and enforcement
- Comprehensive error handling
"""

import logging
from typing import TypedDict, List, Dict, Optional, Annotated
import operator
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.constants import Annotated

logger = logging.getLogger(__name__)


# ============================================================================
# State Definitions
# ============================================================================

class ResearchOutput(TypedDict):
    """Research task outputs"""
    situation_analysis: Optional[str]
    competitor_ladder: Optional[List[Dict]]
    evidence: Optional[List[Dict]]
    cost: float
    duration: float


class PositioningOutput(TypedDict):
    """Positioning task outputs"""
    options: Optional[List[Dict]]
    selected_option: Optional[Dict]
    validation_score: float
    cost: float


class MarketingState(TypedDict):
    """
    Shared state across all agents in the orchestration.

    Accumulates results as workflow progresses.
    """
    # Business context
    business_id: str
    business_data: Dict
    industry: str
    description: str
    goals: List[str]

    # Research phase outputs
    situation_analysis: Optional[str]
    competitor_ladder: Optional[List[Dict]]
    evidence: Optional[List[Dict]]
    sostac: Optional[Dict]

    # Strategy phase outputs
    positioning_options: Optional[List[Dict]]
    selected_positioning: Optional[Dict]
    icps: Optional[List[Dict]]
    marketing_7ps: Optional[Dict]
    north_star_metrics: Optional[Dict]

    # Campaign phase outputs
    content_calendar: Optional[Dict]
    asset_templates: Optional[List[Dict]]

    # Analytics phase outputs
    amec_analysis: Optional[Dict]
    clv_analysis: Optional[Dict]

    # Tracking
    total_cost: Annotated[float, operator.add]
    total_duration: Annotated[float, operator.add]
    models_used: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    workflow_stage: str


class RaptorFlowOrchestrator:
    """
    LangGraph orchestrator for complete marketing strategy.

    Workflow:
    1. Business Intake (validation)
    2. Deep Research (situation + competitor intelligence)
    3. SOSTAC Analysis
    4. Positioning Strategy
    5. ICP Generation
    6. Marketing Mix (7Ps)
    7. Content Calendar
    8. Analytics Framework
    """

    def __init__(self, ai_provider_manager, cost_controller, connection_manager=None):
        """
        Initialize orchestrator.

        Args:
            ai_provider_manager: AIProviderManager for intelligent routing
            cost_controller: CostController for budget enforcement
            connection_manager: WebSocket connection manager for streaming
        """
        self.ai = ai_provider_manager
        self.cost = cost_controller
        self.ws_manager = connection_manager
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Construct LangGraph workflow"""
        workflow = StateGraph(MarketingState)

        # Define nodes (agents)
        workflow.add_node("intake", self.intake_node)
        workflow.add_node("research", self.research_node)
        workflow.add_node("sostac", self.sostac_node)
        workflow.add_node("positioning", self.positioning_node)
        workflow.add_node("icp", self.icp_node)
        workflow.add_node("strategy", self.strategy_node)
        workflow.add_node("content", self.content_node)
        workflow.add_node("analytics", self.analytics_node)

        # Define edges (flow)
        workflow.set_entry_point("intake")
        workflow.add_edge("intake", "research")
        workflow.add_edge("research", "sostac")
        workflow.add_edge("sostac", "positioning")
        workflow.add_edge("positioning", "icp")
        workflow.add_edge("icp", "strategy")
        workflow.add_edge("strategy", "content")
        workflow.add_edge("content", "analytics")
        workflow.add_edge("analytics", END)

        return workflow.compile()

    async def emit_progress(
        self,
        business_id: str,
        stage: str,
        progress: int,
        details: Optional[dict] = None
    ):
        """Emit progress update via WebSocket if connected"""
        if self.ws_manager:
            try:
                from .websocket_routes import emit_progress
                await emit_progress(business_id, "strategy", stage, progress, details)
            except Exception as e:
                logger.warning(f"Failed to emit progress: {e}")

    async def intake_node(self, state: MarketingState) -> MarketingState:
        """
        Intake Node: Validate business data

        Uses: GPT-5 Nano (input validation)
        Cost: ~$0.001
        """
        logger.info(f"📋 Starting intake for {state['business_id']}")

        state["workflow_stage"] = "intake"
        await self.emit_progress(state["business_id"], "intake", 5, {
            "step": "validating_input"
        })

        try:
            # Validate business data
            messages = [
                {
                    "role": "system",
                    "content": "You are a data validation specialist. Validate the business data and identify any missing or invalid fields."
                },
                {
                    "role": "user",
                    "content": f"""
                    Validate this business profile:
                    Name: {state['business_data'].get('name')}
                    Industry: {state['business_data'].get('industry')}
                    Description: {state['business_data'].get('description')}
                    Goals: {state['business_data'].get('goals')}

                    Return: valid (true/false), issues (list)
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="input_validation",
                messages=messages
            )

            state["models_used"] = [result["model_used"]]
            state["total_cost"] += result["cost"]

            await self.emit_progress(state["business_id"], "intake", 100)

            logger.info(f"✅ Intake complete for {state['business_id']}")
            return state

        except Exception as e:
            logger.error(f"Intake error: {e}")
            state["errors"].append(f"Intake failed: {str(e)}")
            raise

    async def research_node(self, state: MarketingState) -> MarketingState:
        """
        Research Node: Deep business and competitive research

        Uses: GPT-5 (deep reasoning for complex analysis)
        Cost: $0.50 - 2.00
        """
        logger.info(f"🔬 Starting research for {state['business_id']}")

        state["workflow_stage"] = "research"
        await self.emit_progress(state["business_id"], "research", 10, {
            "step": "situation_analysis"
        })

        try:
            # Check budget before expensive operation
            can_proceed, budget_info = await self.cost.check_budget_before_task(
                state["business_id"],
                "situation_analysis",
                len(state["description"]) + len(" ".join(state["goals"]))
            )

            if not can_proceed:
                logger.error(f"Budget check failed: {budget_info}")
                state["errors"].append(f"Budget limit exceeded: {budget_info.get('reason')}")
                raise Exception("Budget limit exceeded")

            # Situation Analysis
            messages = [
                {
                    "role": "system",
                    "content": "You are a strategic market analyst. Provide deep insights about market dynamics."
                },
                {
                    "role": "user",
                    "content": f"""
                    Analyze the market situation for:
                    Industry: {state['industry']}
                    Business: {state['description']}
                    Goals: {', '.join(state['goals'])}

                    Provide:
                    1. Market size and growth trends
                    2. Key industry drivers
                    3. Technology landscape
                    4. Customer behavior patterns
                    5. Regulatory environment
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="situation_analysis",
                messages=messages,
                reasoning_effort="high"
            )

            state["situation_analysis"] = result["response"]
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]
            state["total_duration"] += result["latency"]

            await self.emit_progress(state["business_id"], "research", 50, {
                "step": "competitor_analysis",
                "cost_so_far": state["total_cost"]
            })

            # Competitor Intelligence
            messages = [
                {
                    "role": "system",
                    "content": "You are a competitive intelligence specialist."
                },
                {
                    "role": "user",
                    "content": f"""
                    Build a competitor ladder for {state['industry']}.

                    Context: {state['situation_analysis'][:1000]}

                    Identify top 15 competitors and rank by market position.
                    For each: positioning, strengths, weaknesses, estimated market share.
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="competitor_intelligence",
                messages=messages,
                reasoning_effort="high"
            )

            state["competitor_ladder"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            await self.emit_progress(state["business_id"], "research", 100, {
                "step": "complete",
                "competitors_found": len(state["competitor_ladder"])
            })

            logger.info(f"✅ Research complete for {state['business_id']}")
            return state

        except Exception as e:
            logger.error(f"Research error: {e}")
            state["errors"].append(f"Research failed: {str(e)}")
            raise

    async def sostac_node(self, state: MarketingState) -> MarketingState:
        """
        SOSTAC Node: Strategic framework analysis

        Uses: GPT-5 (deep reasoning)
        Cost: $1.00 - 3.00
        """
        logger.info(f"📊 Starting SOSTAC for {state['business_id']}")

        state["workflow_stage"] = "sostac"
        await self.emit_progress(state["business_id"], "strategy", 20, {
            "step": "sostac_analysis"
        })

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a strategic marketing planner expert in SOSTAC framework."
                },
                {
                    "role": "user",
                    "content": f"""
                    Create comprehensive SOSTAC analysis:

                    Situation: {state['situation_analysis'][:500]}
                    Competitors: {str(state['competitor_ladder'][:3])}

                    Provide detailed analysis for:
                    1. Situation - Market, customer, competitive analysis
                    2. Objectives - What you want to achieve
                    3. Strategy - How to compete and win
                    4. Tactics - Specific actions and channels
                    5. Action - Implementation details
                    6. Control - Measurement and KPIs

                    Output as JSON with nested structure.
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="sostac_analysis",
                messages=messages,
                reasoning_effort="high"
            )

            state["sostac"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            await self.emit_progress(state["business_id"], "strategy", 40)

            logger.info(f"✅ SOSTAC complete for {state['business_id']}")
            return state

        except Exception as e:
            logger.error(f"SOSTAC error: {e}")
            state["errors"].append(f"SOSTAC failed: {str(e)}")
            raise

    async def positioning_node(self, state: MarketingState) -> MarketingState:
        """
        Positioning Node: Generate positioning options

        Uses: GPT-5 (deep reasoning for strategic positioning)
        Cost: $0.60 - 1.20
        """
        logger.info(f"🎯 Starting positioning for {state['business_id']}")

        state["workflow_stage"] = "positioning"
        await self.emit_progress(state["business_id"], "strategy", 50, {
            "step": "positioning_generation"
        })

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a brand positioning strategist."
                },
                {
                    "role": "user",
                    "content": f"""
                    Generate 3 distinct positioning options for {state['industry']} business:

                    Market: {state['industry']}
                    Strategy: {state['sostac'].get('strategy', 'N/A')}

                    For each option provide:
                    1. Core positioning statement
                    2. Target audience definition
                    3. Key differentiators
                    4. Value proposition
                    5. Brand personality
                    6. Competitive advantage

                    Output as JSON array with option_1, option_2, option_3.
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="positioning_strategy",
                messages=messages,
                reasoning_effort="high"
            )

            state["positioning_options"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            # Auto-select best option based on strategy alignment
            state["selected_positioning"] = state["positioning_options"][0]

            await self.emit_progress(state["business_id"], "strategy", 60, {
                "step": "positioning_selected"
            })

            logger.info(f"✅ Positioning complete for {state['business_id']}")
            return state

        except Exception as e:
            logger.error(f"Positioning error: {e}")
            state["errors"].append(f"Positioning failed: {str(e)}")
            raise

    async def icp_node(self, state: MarketingState) -> MarketingState:
        """
        ICP Node: Generate Ideal Customer Profiles

        Uses: GPT-5 Mini (balanced reasoning)
        Cost: $0.20 - 0.50
        """
        logger.info(f"👥 Starting ICP generation for {state['business_id']}")

        state["workflow_stage"] = "icp"
        await self.emit_progress(state["business_id"], "strategy", 65, {
            "step": "icp_generation"
        })

        try:
            # Get tier limit for ICPs
            feature_limits = await self.cost.get_feature_limits(state["business_id"])
            max_icps = feature_limits["max_icps"]

            messages = [
                {
                    "role": "system",
                    "content": "You are a buyer persona strategist."
                },
                {
                    "role": "user",
                    "content": f"""
                    Create {max_icps} detailed Ideal Customer Profiles aligned with positioning:

                    Positioning: {state['selected_positioning']}
                    Market: {state['industry']}

                    For each ICP provide:
                    1. Name and role
                    2. Demographics (age, income, location, education)
                    3. Psychographics (values, fears, aspirations)
                    4. Challenges and pain points
                    5. Information sources and platforms
                    6. Buying process and criteria
                    7. Content preferences
                    8. Trending topics they follow

                    Output as JSON array with {max_icps} profiles.
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="icp_generation",
                messages=messages,
                reasoning_effort="medium"
            )

            state["icps"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            await self.emit_progress(state["business_id"], "strategy", 75, {
                "step": "icps_created",
                "count": len(state["icps"])
            })

            logger.info(f"✅ ICP complete for {state['business_id']}")
            return state

        except Exception as e:
            logger.error(f"ICP error: {e}")
            state["errors"].append(f"ICP generation failed: {str(e)}")
            raise

    async def strategy_node(self, state: MarketingState) -> MarketingState:
        """
        Strategy Node: Marketing mix and metrics

        Uses: GPT-5 Mini (balanced reasoning)
        Cost: $0.40 - 0.80
        """
        logger.info(f"📈 Starting strategy for {state['business_id']}")

        state["workflow_stage"] = "strategy"
        await self.emit_progress(state["business_id"], "strategy", 80, {
            "step": "marketing_mix"
        })

        try:
            # 7Ps Marketing Mix
            messages = [
                {
                    "role": "system",
                    "content": "You are a marketing strategist expert in the 7Ps framework."
                },
                {
                    "role": "user",
                    "content": f"""
                    Create 7Ps Marketing Mix for {state['industry']} business:

                    Positioning: {state['selected_positioning']}
                    ICPs: {state['icps']}

                    Define detailed strategy for:
                    1. Product - Features, quality, innovation
                    2. Price - Pricing strategy, positioning
                    3. Place - Distribution channels
                    4. Promotion - Marketing communications
                    5. People - Team, training, culture
                    6. Process - Operations, customer journey
                    7. Physical Evidence - Branding, materials

                    Output as JSON with nested 7ps object.
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="7ps_marketing_mix",
                messages=messages,
                reasoning_effort="medium"
            )

            state["marketing_7ps"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            # North Star Metrics
            messages = [
                {
                    "role": "system",
                    "content": "You are a metrics strategist."
                },
                {
                    "role": "user",
                    "content": f"""
                    Define North Star metrics for {state['industry']} business:

                    Goals: {state['goals']}
                    Strategy: {state['sostac'].get('control', 'N/A')}

                    Identify:
                    1. Primary North Star metric
                    2. Supporting metrics (5-7)
                    3. Lagging indicators (results)
                    4. Leading indicators (activity)
                    5. Measurement frequency
                    6. Targets (3mo, 6mo, 12mo)
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="north_star_metrics",
                messages=messages,
                reasoning_effort="medium"
            )

            state["north_star_metrics"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            await self.emit_progress(state["business_id"], "strategy", 90)

            logger.info(f"✅ Strategy complete for {state['business_id']}")
            return state

        except Exception as e:
            logger.error(f"Strategy error: {e}")
            state["errors"].append(f"Strategy failed: {str(e)}")
            raise

    async def content_node(self, state: MarketingState) -> MarketingState:
        """
        Content Node: Content calendar and assets

        Uses: GPT-5 Mini (creative generation)
        Cost: $0.40 - 0.90
        """
        logger.info(f"📝 Starting content for {state['business_id']}")

        state["workflow_stage"] = "content"
        await self.emit_progress(state["business_id"], "strategy", 92, {
            "step": "content_calendar"
        })

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a content strategist and calendar planner."
                },
                {
                    "role": "user",
                    "content": f"""
                    Create 30-day content calendar for {state['industry']} business:

                    ICPs: {state['icps']}
                    Positioning: {state['selected_positioning']}
                    Channels: LinkedIn, Twitter, TikTok, Blog

                    For each day provide:
                    - Platform
                    - Content type (post, video, article, infographic)
                    - Topic/headline
                    - Key message aligned with positioning
                    - CTA
                    - Mix: 30% promotional, 50% educational, 20% entertaining

                    Output as JSON array with 30 day objects.
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="content_calendar_creation",
                messages=messages,
                reasoning_effort="medium"
            )

            state["content_calendar"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            await self.emit_progress(state["business_id"], "strategy", 96)

            logger.info(f"✅ Content complete for {state['business_id']}")
            return state

        except Exception as e:
            logger.error(f"Content error: {e}")
            state["errors"].append(f"Content generation failed: {str(e)}")
            raise

    async def analytics_node(self, state: MarketingState) -> MarketingState:
        """
        Analytics Node: Measurement framework

        Uses: GPT-5 (deep reasoning for ROI analysis)
        Cost: $0.20 - 0.50
        """
        logger.info(f"📊 Starting analytics for {state['business_id']}")

        state["workflow_stage"] = "analytics"
        await self.emit_progress(state["business_id"], "strategy", 98, {
            "step": "analytics_framework"
        })

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an analytics and ROI specialist."
                },
                {
                    "role": "user",
                    "content": f"""
                    Create AMEC ROI measurement framework:

                    Strategy: {state['sostac'].get('control', 'N/A')}
                    Metrics: {state['north_star_metrics']}

                    Provide:
                    1. AMEC framework alignment
                    2. Customer Lifetime Value calculation method
                    3. Attribution model (multi-touch)
                    4. ROI calculation formula
                    5. Reporting cadence
                    6. Dashboard KPIs
                    """
                }
            ]

            result = await self.ai.execute_with_fallback(
                task_type="amec_roi_analysis",
                messages=messages,
                reasoning_effort="high"
            )

            state["amec_analysis"] = json.loads(result["response"])
            state["models_used"].append(result["model_used"])
            state["total_cost"] += result["cost"]

            await self.emit_progress(state["business_id"], "strategy", 100, {
                "step": "complete",
                "total_cost": state["total_cost"],
                "duration": state["total_duration"]
            })

            logger.info(
                f"✅ Orchestration complete for {state['business_id']} | "
                f"Cost: ${state['total_cost']:.2f} | Models: {len(set(state['models_used']))}"
            )
            return state

        except Exception as e:
            logger.error(f"Analytics error: {e}")
            state["errors"].append(f"Analytics failed: {str(e)}")
            raise

    async def run_workflow(self, initial_state: MarketingState) -> MarketingState:
        """
        Execute complete workflow from intake to analytics.

        Args:
            initial_state: Initial marketing state

        Returns:
            Final state with all results
        """
        logger.info(f"🚀 Starting RaptorFlow orchestration for {initial_state['business_id']}")

        try:
            final_state = await self.graph.ainvoke(initial_state)
            return final_state

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            raise


# Helper for usage in main.py
def create_orchestrator(ai_manager, cost_controller, ws_manager=None):
    """Factory to create orchestrator instance"""
    return RaptorFlowOrchestrator(ai_manager, cost_controller, ws_manager)


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """
    Example of how to use the orchestrator.

    In main.py route:
    ```
    @app.post("/api/analyze/{business_id}")
    async def analyze_business(business_id: str):
        orchestrator = create_orchestrator(ai_manager, cost_controller)

        initial_state = {
            "business_id": business_id,
            "business_data": {...},
            "industry": "SaaS",
            "description": "...",
            "goals": ["..."],
            "total_cost": 0.0,
            "total_duration": 0.0,
            "models_used": [],
            "errors": [],
            "workflow_stage": "init"
        }

        final_state = await orchestrator.run_workflow(initial_state)

        return {
            "success": len(final_state["errors"]) == 0,
            "total_cost": final_state["total_cost"],
            "results": {
                "positioning": final_state["selected_positioning"],
                "icps": final_state["icps"],
                "calendar": final_state["content_calendar"]
            }
        }
    ```
    """
    pass


# Import json for parsing responses
import json

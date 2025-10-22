"""ChannelMapperAgent - Maps marketing channels and AISAS stages"""
import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..core.service_factories import ServiceManager
from ..base_agent import BaseAgent, AgentState
from ..middleware.budget_controller import check_budget_before_api_call

logger = logging.getLogger(__name__)

# Platform specifications and physics
PLATFORM_SPECS = {
    "YouTube": {
        "content_types": ["Hero", "Hub", "Help"],
        "cadence": "1-2 per week",
        "posting_times": ["Tuesday 2PM", "Thursday 10AM"],
        "content_length": "8-15 minutes long-form or 15-60 seconds shorts",
        "tone": "Educational, authentic, personality-driven",
        "hero_aisas": 70,  # Better for Action/Share
        "hub_aisas": 60,   # Good for Interest/Search
        "help_aisas": 40,  # Good for Attention/Interest
    },
    "LinkedIn": {
        "content_types": ["Hub", "Help"],
        "cadence": "3-5 per week",
        "posting_times": ["Tuesday 8AM", "Thursday 10AM", "Wednesday 2PM"],
        "content_length": "150-300 words, images/carousel",
        "tone": "Professional, thought-leadership, insights",
        "hero_aisas": 50,
        "hub_aisas": 70,
        "help_aisas": 60,
    },
    "Instagram": {
        "content_types": ["Hero", "Hub"],
        "cadence": "4-6 per week",
        "posting_times": ["Tuesday 11AM", "Thursday 1PM", "Saturday 9AM"],
        "content_length": "High-quality visuals, 1-3 sentences",
        "tone": "Brand voice, visually consistent, lifestyle",
        "hero_aisas": 75,
        "hub_aisas": 65,
        "help_aisas": 35,
    },
    "TikTok": {
        "content_types": ["Hero", "Hub"],
        "cadence": "5-7 per week",
        "posting_times": ["6-9AM", "12-1PM", "7-11PM"],
        "content_length": "15-60 seconds, trend-aware",
        "tone": "Authentic, trending, entertaining",
        "hero_aisas": 80,  # Very high for awareness
        "hub_aisas": 70,
        "help_aisas": 40,
    },
    "X (Twitter)": {
        "content_types": ["Hub", "Help"],
        "cadence": "5-10 per day",
        "posting_times": ["9AM", "12PM", "3PM", "6PM"],
        "content_length": "280 characters, punchy",
        "tone": "Conversational, witty, timely",
        "hero_aisas": 45,
        "hub_aisas": 65,
        "help_aisas": 70,
    },
    "Threads": {
        "content_types": ["Hub", "Help"],
        "cadence": "2-5 per day",
        "posting_times": ["9AM", "12PM", "6PM"],
        "content_length": "500 character limit, threaded",
        "tone": "Casual, conversational, community-focused",
        "hero_aisas": 50,
        "hub_aisas": 60,
        "help_aisas": 65,
    },
    "Facebook": {
        "content_types": ["Hero", "Hub"],
        "cadence": "2-5 per week",
        "posting_times": ["1-3PM on weekdays", "11AM-1PM weekends"],
        "content_length": "Varied, community-focused",
        "tone": "Friendly, community-oriented",
        "hero_aisas": 60,
        "hub_aisas": 60,
        "help_aisas": 50,
    },
    "Email": {
        "content_types": ["Help"],
        "cadence": "1-3 per week",
        "posting_times": ["Tuesday 9AM", "Thursday 9AM"],
        "content_length": "500-1000 words, scannable",
        "tone": "Personal, helpful, clear",
        "hero_aisas": 30,
        "hub_aisas": 50,
        "help_aisas": 80,
    },
}


class ChannelMapperAgent(BaseAgent):
    """
    Stage 4 Agent: Map marketing channels and AISAS stages
    - Uses Platform Physics Library to fetch channel constraints
    - Recommends channels for each ICP/JTBD combination
    - Assigns content types (Hero, Hub, Help)
    - Calculates AISAS stage recommendations (0-100)
    """

    def __init__(self):
        super().__init__(
            name="ChannelMapper",
            description="Maps marketing channels and AISAS stages for ICP/JTBD combinations"
        )
        self.services = ServiceManager()

    async def _process(self, state: AgentState) -> AgentState:
        """Map channels for ICP/JTBD matrix"""
        try:
            state["stage"] = "mapping_channels"

            workspace_id = state["context"].get("workspace_id")
            icps = state["context"].get("built_icps", [])
            jtbds = state["context"].get("extracted_jtbds", [])

            if not icps or not jtbds:
                state["error"] = "Missing ICPs or JTBDs for channel mapping"
                return state

            # Check budget
            if not check_budget_before_api_call("channel_mapping"):
                state["error"] = "Budget limit reached for channel mapping"
                return state

            mapped_channels = []

            # For each ICP/JTBD combination, recommend channels
            for icp in icps:
                for jtbd in jtbds:
                    logger.info(f"Mapping channels for ICP {icp.get('name')} × JTBD {jtbd.get('why')[:50]}")

                    # Get channel recommendations for this pairing
                    recommendations = await self._recommend_channels(icp, jtbd)

                    for recommendation in recommendations:
                        channel = {
                            "id": str(uuid.uuid4()),
                            "workspace_id": workspace_id,
                            "icp_id": icp.get("id"),
                            "jtbd_id": jtbd.get("id"),
                            "channel_name": recommendation.get("channel_name"),
                            "content_type": recommendation.get("content_type"),
                            "aisas_stage": recommendation.get("aisas_stage", 50),
                            "aisas_attention": recommendation.get("aisas_attention", 0),
                            "aisas_interest": recommendation.get("aisas_interest", 0),
                            "aisas_search": recommendation.get("aisas_search", 0),
                            "aisas_action": recommendation.get("aisas_action", 0),
                            "aisas_share": recommendation.get("aisas_share", 0),
                            "cadence": recommendation.get("cadence"),
                            "posting_times": recommendation.get("posting_times"),
                            "content_length": recommendation.get("content_length"),
                            "tone": recommendation.get("tone"),
                            "confidence_score": recommendation.get("confidence_score", 0.8),
                            "reasoning": recommendation.get("reasoning"),
                            "created_at": datetime.utcnow().isoformat(),
                        }

                        mapped_channels.append(channel)

            state["results"]["mapped_channels"] = mapped_channels
            state["results"]["channel_count"] = len(mapped_channels)

            logger.info(f"Mapped {len(mapped_channels)} channel recommendations")

        except Exception as e:
            logger.exception(f"Error in channel mapping: {str(e)}")
            state["error"] = str(e)

        return state

    async def _recommend_channels(
        self,
        icp: Dict[str, Any],
        jtbd: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend channels for an ICP/JTBD combination"""
        try:
            llm = self.services.llm

            # Build context about the ICP and JTBD
            icp_traits = ", ".join(
                [f"{k}: {v}" for k, v in icp.get("traits", {}).items()][:3]
            )
            pain_points = ", ".join(icp.get("pain_points", [])[:2])

            prompt = f"""Recommend the 3 best marketing channels for this ICP and JTBD combination.

ICP: {icp.get('name')}
Traits: {icp_traits}
Pain Points: {pain_points}

JTBD:
Why: {jtbd.get('why')}
Circumstances: {jtbd.get('circumstances')}

Available channels: YouTube, LinkedIn, Instagram, TikTok, X (Twitter), Threads, Facebook, Email

For each recommendation, provide JSON:
[{{
  "channel_name": "Channel name",
  "content_type": "Hero/Hub/Help",
  "aisas_stage": 65,  // 0-100 where to position in customer journey
  "aisas_attention": 20,  // breakdown of AISAS
  "aisas_interest": 15,
  "aisas_search": 15,
  "aisas_action": 10,
  "aisas_share": 5,
  "reasoning": "Why this channel is ideal for this audience and job",
  "confidence_score": 0.85
}}]

Return ONLY valid JSON array. Prioritize channels where this ICP actually spends time."""

            response = await llm.invoke(prompt)
            recommendations = json.loads(response)

            # Enrich with platform specs
            for rec in recommendations:
                channel_name = rec.get("channel_name")
                if channel_name in PLATFORM_SPECS:
                    specs = PLATFORM_SPECS[channel_name]
                    rec["cadence"] = specs.get("cadence")
                    rec["posting_times"] = specs.get("posting_times")
                    rec["content_length"] = specs.get("content_length")
                    rec["tone"] = specs.get("tone")

            return recommendations

        except json.JSONDecodeError:
            logger.warning("Failed to parse channel recommendations as JSON")
            return []
        except Exception as e:
            logger.error(f"Channel recommendation error: {str(e)}")
            return []

    async def _validate(self, state: AgentState) -> AgentState:
        """Validate mapped channels"""
        try:
            state["stage"] = "validating_channels"

            mapped_channels = state["results"].get("mapped_channels", [])

            if not mapped_channels:
                logger.warning("No channels were mapped")
                state["status"] = "completed"
                return state

            # Validate each channel has required fields
            required_fields = ["channel_name", "aisas_stage", "icp_id", "jtbd_id"]
            valid_count = 0

            for channel in mapped_channels:
                if all(field in channel for field in required_fields):
                    valid_count += 1
                else:
                    logger.warning(f"Channel {channel.get('id')} missing required fields")

            logger.info(f"Validated {valid_count}/{len(mapped_channels)} channels")

            state["status"] = "completed"

        except Exception as e:
            logger.exception(f"Validation error: {str(e)}")
            state["error"] = str(e)

        return state

    async def _finalize(self, state: AgentState) -> AgentState:
        """Finalize channel mapping results"""
        state["stage"] = "finalized"

        channel_count = state["results"].get("channel_count", 0)
        logger.info(f"Channel Mapping finalized with {channel_count} recommendations")

        return state


# Factory function
def create_channel_mapper_agent() -> ChannelMapperAgent:
    """Create a new ChannelMapperAgent instance"""
    return ChannelMapperAgent()

"""ExplanationAgent - Generates rationales and evidence citations for strategic decisions"""
import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..core.service_factories import ServiceManager
from ..base_agent import BaseAgent, AgentState
from ..middleware.budget_controller import check_budget_before_api_call

logger = logging.getLogger(__name__)


class ExplanationAgent(BaseAgent):
    """
    Stage 5 Agent: Generate explanations with evidence
    - Generates human-readable rationales for each strategic decision
    - Creates evidence citations linking back to context
    - Identifies which Wisdom Engine rules fired
    - Calculates confidence scores for recommendations
    - Provides actionable insights with reasoning
    """

    def __init__(self):
        super().__init__(
            name="ExplanationGenerator",
            description="Generates rationales and evidence citations for strategic decisions"
        )
        self.services = ServiceManager()

    async def _process(self, state: AgentState) -> AgentState:
        """Generate explanations for all strategic entities"""
        try:
            state["stage"] = "generating_explanations"

            workspace_id = state["context"].get("workspace_id")
            context_items = state["context"].get("processed_context_items", [])
            jtbds = state["context"].get("extracted_jtbds", [])
            icps = state["context"].get("built_icps", [])
            channels = state["context"].get("mapped_channels", [])

            if not all([jtbds, icps, channels]):
                state["error"] = "Missing required entities for explanation generation"
                return state

            # Check budget
            if not check_budget_before_api_call("explanation_generation"):
                state["error"] = "Budget limit reached for explanation generation"
                return state

            explanations = []

            # Generate explanations for JTBD
            logger.info("Generating JTBD explanations...")
            for jtbd in jtbds:
                jtbd_explanation = await self._generate_jtbd_explanation(
                    jtbd, context_items
                )
                if jtbd_explanation:
                    explanations.extend(jtbd_explanation)

            # Generate explanations for ICP
            logger.info("Generating ICP explanations...")
            for icp in icps:
                icp_explanation = await self._generate_icp_explanation(
                    icp, context_items
                )
                if icp_explanation:
                    explanations.extend(icp_explanation)

            # Generate explanations for channel recommendations
            logger.info("Generating channel explanations...")
            for channel in channels:
                channel_explanation = await self._generate_channel_explanation(
                    channel, jtbds, icps, context_items
                )
                if channel_explanation:
                    explanations.extend(channel_explanation)

            state["results"]["explanations"] = explanations
            state["results"]["explanation_count"] = len(explanations)

            logger.info(f"Generated {len(explanations)} explanations with citations")

        except Exception as e:
            logger.exception(f"Error in explanation generation: {str(e)}")
            state["error"] = str(e)

        return state

    async def _generate_jtbd_explanation(
        self,
        jtbd: Dict[str, Any],
        context_items: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Generate explanations for a JTBD statement"""
        try:
            llm = self.services.llm

            # Get evidence citations for this JTBD
            citations = self._create_citations(
                jtbd.get("evidence_citations", []),
                context_items,
                "jtbd",
                jtbd.get("id")
            )

            # Generate rationale
            prompt = f"""Explain why this Job-to-be-Done is important and what it means for strategy.

JTBD:
Why: {jtbd.get('why')}
Circumstances: {jtbd.get('circumstances')}
Forces: {jtbd.get('forces')}
Anxieties: {jtbd.get('anxieties')}

Provide 2-3 actionable insights about this job in plain language. Focus on:
1. What this job reveals about customer needs
2. How to better serve this job
3. What messaging might resonate

Return plain text explanation, 2-3 sentences max."""

            rationale = await llm.invoke(prompt)

            return [
                {
                    "id": str(uuid.uuid4()),
                    "entity_type": "jtbd",
                    "entity_id": jtbd.get("id"),
                    "title": f"About: {jtbd.get('why')[:50]}...",
                    "rationale": rationale,
                    "explanation_type": "context_summary",
                    "citation_ids": [c.get("id") for c in citations],
                    "confidence_score": jtbd.get("confidence_score", 0.8),
                    "created_at": datetime.utcnow().isoformat(),
                }
            ] + citations

        except Exception as e:
            logger.error(f"JTBD explanation error: {str(e)}")
            return None

    async def _generate_icp_explanation(
        self,
        icp: Dict[str, Any],
        context_items: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Generate explanations for an ICP"""
        try:
            llm = self.services.llm

            # Get evidence citations
            citations = self._create_citations(
                icp.get("evidence_citations", []),
                context_items,
                "icp",
                icp.get("id")
            )

            # Generate trait breakdown explanation
            traits_text = ", ".join(
                [f"{k}: {v}" for k, v in icp.get("traits", {}).items()]
            )

            prompt = f"""Explain the characteristics of this customer segment and why they matter.

ICP: {icp.get('name')}
Traits: {traits_text}
Pain Points: {', '.join(icp.get('pain_points', []))}

Provide insights about:
1. Who this customer is and what drives them
2. What makes them distinct from other segments
3. How to reach and serve them effectively

Return plain text, 2-3 sentences max."""

            rationale = await llm.invoke(prompt)

            return [
                {
                    "id": str(uuid.uuid4()),
                    "entity_type": "icp",
                    "entity_id": icp.get("id"),
                    "title": f"Profile: {icp.get('name')}",
                    "rationale": rationale,
                    "explanation_type": "customer_summary",
                    "citation_ids": [c.get("id") for c in citations],
                    "confidence_score": icp.get("confidence_score", 0.8),
                    "created_at": datetime.utcnow().isoformat(),
                }
            ] + citations

        except Exception as e:
            logger.error(f"ICP explanation error: {str(e)}")
            return None

    async def _generate_channel_explanation(
        self,
        channel: Dict[str, Any],
        jtbds: List[Dict[str, Any]],
        icps: List[Dict[str, Any]],
        context_items: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Generate explanations for a channel recommendation"""
        try:
            llm = self.services.llm

            # Find the related JTBD and ICP
            jtbd = next((j for j in jtbds if j.get("id") == channel.get("jtbd_id")), None)
            icp = next((i for i in icps if i.get("id") == channel.get("icp_id")), None)

            if not jtbd or not icp:
                return None

            # Create citations
            citations = self._create_citations(
                [],  # Channel citations are implicit from ICP/JTBD
                context_items,
                "channel",
                channel.get("id")
            )

            # Generate explanation for why this channel
            prompt = f"""Explain why {channel.get('channel_name')} is the right channel for this customer/job combination.

Customer: {icp.get('name')}
Job: {jtbd.get('why')}
Content Type: {channel.get('content_type')}

Explain:
1. Why this audience is on this platform
2. What type of content works here
3. Specific strategy for reaching them

Return plain text, 2-3 sentences max. Be specific and actionable."""

            channel_rationale = await llm.invoke(prompt)

            explanations = [
                {
                    "id": str(uuid.uuid4()),
                    "entity_type": "channel",
                    "entity_id": channel.get("id"),
                    "title": f"{channel.get('channel_name')} for {icp.get('name')}",
                    "rationale": channel_rationale,
                    "explanation_type": "platform_strategy",
                    "confidence_score": channel.get("confidence_score", 0.8),
                    "created_at": datetime.utcnow().isoformat(),
                }
            ]

            # Add AISAS stage explanation
            aisas_explanation = self._explain_aisas_stage(
                channel.get("aisas_stage", 50),
                icp.get("name"),
                channel.get("channel_name")
            )
            explanations.append(aisas_explanation)

            # Add confidence reasoning
            confidence_explanation = self._explain_confidence(
                channel.get("confidence_score", 0.8),
                icp.get("name"),
                jtbd.get("why")
            )
            explanations.append(confidence_explanation)

            return explanations + citations

        except Exception as e:
            logger.error(f"Channel explanation error: {str(e)}")
            return None

    def _create_citations(
        self,
        context_ids: List[str],
        context_items: List[Dict[str, Any]],
        entity_type: str,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """Create citation records linking to context"""
        citations = []

        for context_id in context_ids[:3]:  # Limit to top 3 citations
            context_item = next(
                (c for c in context_items if c.get("id") == context_id),
                None
            )

            if context_item:
                citation = {
                    "id": str(uuid.uuid4()),
                    "context_item_id": context_id,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "quote": context_item.get("extracted_text", "")[:200],
                    "relevance_score": 0.8,
                    "created_at": datetime.utcnow().isoformat(),
                }
                citations.append(citation)

        return citations

    def _explain_aisas_stage(
        self,
        aisas_stage: float,
        icp_name: str,
        channel_name: str
    ) -> Dict[str, Any]:
        """Generate explanation for AISAS stage positioning"""
        if aisas_stage < 30:
            stage = "Attention"
            strategy = "Focus on awareness and initial interest"
        elif aisas_stage < 50:
            stage = "Interest/Search"
            strategy = "Build consideration and help with evaluation"
        elif aisas_stage < 70:
            stage = "Action"
            strategy = "Drive conversion and purchase intent"
        else:
            stage = "Share"
            strategy = "Encourage advocacy and community building"

        return {
            "id": str(uuid.uuid4()),
            "entity_type": "aisas",
            "entity_id": f"{icp_name}_{channel_name}_aisas",
            "title": f"AISAS Stage: {stage}",
            "rationale": f"Position {icp_name} on {channel_name} at the {stage} stage. {strategy}.",
            "explanation_type": "aisas_positioning",
            "confidence_score": 0.85,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _explain_confidence(
        self,
        confidence_score: float,
        icp_name: str,
        job_why: str
    ) -> Dict[str, Any]:
        """Generate explanation for confidence scoring"""
        if confidence_score >= 0.9:
            level = "Very High"
            reasoning = "Strong evidence in context supports this recommendation"
        elif confidence_score >= 0.8:
            level = "High"
            reasoning = "Good evidence supports this recommendation"
        elif confidence_score >= 0.7:
            level = "Medium"
            reasoning = "Reasonable hypothesis, but limited evidence"
        else:
            level = "Low"
            reasoning = "Exploratory hypothesis, test with small audience"

        return {
            "id": str(uuid.uuid4()),
            "entity_type": "confidence",
            "entity_id": f"{icp_name}_confidence",
            "title": f"Confidence: {level}",
            "rationale": f"{reasoning}. Start with a small test to validate assumptions about {icp_name}'s interest in {job_why}.",
            "explanation_type": "confidence_assessment",
            "confidence_score": confidence_score,
            "created_at": datetime.utcnow().isoformat(),
        }

    async def _validate(self, state: AgentState) -> AgentState:
        """Validate generated explanations"""
        try:
            state["stage"] = "validating_explanations"

            explanations = state["results"].get("explanations", [])

            if not explanations:
                logger.warning("No explanations were generated")
                state["status"] = "completed"
                return state

            # Validate each explanation has required fields
            required_fields = ["entity_type", "entity_id", "rationale"]
            valid_count = 0

            for explanation in explanations:
                if all(field in explanation for field in required_fields):
                    valid_count += 1

            logger.info(f"Validated {valid_count}/{len(explanations)} explanations")

            state["status"] = "completed"

        except Exception as e:
            logger.exception(f"Validation error: {str(e)}")
            state["error"] = str(e)

        return state

    async def _finalize(self, state: AgentState) -> AgentState:
        """Finalize explanation generation"""
        state["stage"] = "finalized"

        explanation_count = state["results"].get("explanation_count", 0)
        logger.info(f"Explanation generation finalized with {explanation_count} items")

        return state


# Factory function
def create_explanation_agent() -> ExplanationAgent:
    """Create a new ExplanationAgent instance"""
    return ExplanationAgent()

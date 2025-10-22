"""Strategy Orchestrator - Coordinates the 5-stage analysis pipeline"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .context_processor_agent import create_context_processor_agent
from .jtbd_extraction_agent import create_jtbd_extraction_agent
from .icp_builder_agent import create_icp_builder_agent
from .channel_mapper_agent import create_channel_mapper_agent
from .explanation_agent import create_explanation_agent

logger = logging.getLogger(__name__)


class StrategyOrchestrator:
    """
    Orchestrates the 5-stage Strategy Workspace analysis pipeline.

    Pipeline Stages:
    1. ContextProcessorAgent - Extracts and analyzes context
    2. JTBDExtractionAgent - Identifies Jobs-to-be-Done
    3. ICPBuilderAgent - Creates customer profiles
    4. ChannelMapperAgent - Maps marketing channels
    5. ExplanationAgent - Generates rationales with evidence

    Each stage feeds into the next, progressively building the strategy.
    """

    def __init__(self):
        """Initialize orchestrator with all agents"""
        self.context_processor = create_context_processor_agent()
        self.jtbd_extractor = create_jtbd_extraction_agent()
        self.icp_builder = create_icp_builder_agent()
        self.channel_mapper = create_channel_mapper_agent()
        self.explanation_agent = create_explanation_agent()

        self.pipeline_state = {}

    async def analyze_strategy(
        self,
        workspace_id: str,
        context_items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run complete 5-stage strategy analysis pipeline.

        Args:
            workspace_id: Unique workspace identifier
            context_items: List of context items to analyze

        Returns:
            Dict with analysis results from all 5 stages
        """
        try:
            logger.info(f"Starting strategy analysis for workspace: {workspace_id}")
            start_time = datetime.now()

            # Stage 1: Process context
            logger.info("Stage 1/5: Processing context...")
            context_result = await self._stage_1_process_context(workspace_id, context_items)

            if context_result.get("error"):
                return {
                    "success": False,
                    "error": f"Context processing failed: {context_result.get('error')}",
                    "stage": 1
                }

            # Stage 2: Extract JTBD
            logger.info("Stage 2/5: Extracting JTBDs...")
            jtbd_result = await self._stage_2_extract_jtbd(
                workspace_id,
                context_result.get("processed_context_items", [])
            )

            if jtbd_result.get("error"):
                return {
                    "success": False,
                    "error": f"JTBD extraction failed: {jtbd_result.get('error')}",
                    "stage": 2
                }

            # Stage 3: Build ICPs
            logger.info("Stage 3/5: Building ICPs...")
            icp_result = await self._stage_3_build_icps(
                workspace_id,
                context_result.get("processed_context_items", []),
                jtbd_result.get("extracted_jtbds", [])
            )

            if icp_result.get("error"):
                return {
                    "success": False,
                    "error": f"ICP building failed: {icp_result.get('error')}",
                    "stage": 3
                }

            # Stage 4: Map channels
            logger.info("Stage 4/5: Mapping channels...")
            channel_result = await self._stage_4_map_channels(
                workspace_id,
                icp_result.get("built_icps", []),
                jtbd_result.get("extracted_jtbds", [])
            )

            if channel_result.get("error"):
                return {
                    "success": False,
                    "error": f"Channel mapping failed: {channel_result.get('error')}",
                    "stage": 4
                }

            # Stage 5: Generate explanations
            logger.info("Stage 5/5: Generating explanations...")
            explanation_result = await self._stage_5_generate_explanations(
                workspace_id,
                context_result.get("processed_context_items", []),
                jtbd_result.get("extracted_jtbds", []),
                icp_result.get("built_icps", []),
                channel_result.get("mapped_channels", [])
            )

            if explanation_result.get("error"):
                return {
                    "success": False,
                    "error": f"Explanation generation failed: {explanation_result.get('error')}",
                    "stage": 5
                }

            # Compile complete results
            elapsed_time = (datetime.now() - start_time).total_seconds()

            complete_analysis = {
                "success": True,
                "workspace_id": workspace_id,
                "analysis": {
                    "context_items_processed": context_result.get("item_count", 0),
                    "jtbds_extracted": jtbd_result.get("jtbd_count", 0),
                    "icps_built": icp_result.get("icp_count", 0),
                    "channels_mapped": channel_result.get("channel_count", 0),
                    "explanations_generated": explanation_result.get("explanation_count", 0),
                },
                "details": {
                    "processed_context": context_result.get("processed_context_items", []),
                    "extracted_jtbds": jtbd_result.get("extracted_jtbds", []),
                    "built_icps": icp_result.get("built_icps", []),
                    "mapped_channels": channel_result.get("mapped_channels", []),
                    "explanations": explanation_result.get("explanations", []),
                },
                "metadata": {
                    "elapsed_seconds": elapsed_time,
                    "stages_completed": 5,
                    "timestamp": datetime.now().isoformat(),
                }
            }

            logger.info(f"Strategy analysis completed in {elapsed_time:.2f} seconds")
            logger.info(f"  - Context items processed: {context_result.get('item_count', 0)}")
            logger.info(f"  - JTBDs extracted: {jtbd_result.get('jtbd_count', 0)}")
            logger.info(f"  - ICPs built: {icp_result.get('icp_count', 0)}")
            logger.info(f"  - Channels mapped: {channel_result.get('channel_count', 0)}")
            logger.info(f"  - Explanations generated: {explanation_result.get('explanation_count', 0)}")

            return complete_analysis

        except Exception as e:
            logger.exception(f"Error in strategy orchestration: {str(e)}")
            return {
                "success": False,
                "error": f"Orchestration failed: {str(e)}",
                "stage": "unknown"
            }

    async def _stage_1_process_context(
        self,
        workspace_id: str,
        context_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute Stage 1: Context Processing"""
        try:
            state = {
                "context": {
                    "workspace_id": workspace_id,
                    "context_items": context_items
                }
            }

            result = await self.context_processor.app.ainvoke(state)

            return result.get("results", {})

        except Exception as e:
            logger.exception(f"Stage 1 error: {str(e)}")
            return {"error": str(e)}

    async def _stage_2_extract_jtbd(
        self,
        workspace_id: str,
        processed_context_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute Stage 2: JTBD Extraction"""
        try:
            state = {
                "context": {
                    "workspace_id": workspace_id,
                    "processed_context_items": processed_context_items
                }
            }

            result = await self.jtbd_extractor.app.ainvoke(state)

            return result.get("results", {})

        except Exception as e:
            logger.exception(f"Stage 2 error: {str(e)}")
            return {"error": str(e)}

    async def _stage_3_build_icps(
        self,
        workspace_id: str,
        processed_context_items: List[Dict[str, Any]],
        extracted_jtbds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute Stage 3: ICP Building"""
        try:
            state = {
                "context": {
                    "workspace_id": workspace_id,
                    "processed_context_items": processed_context_items,
                    "extracted_jtbds": extracted_jtbds
                }
            }

            result = await self.icp_builder.app.ainvoke(state)

            return result.get("results", {})

        except Exception as e:
            logger.exception(f"Stage 3 error: {str(e)}")
            return {"error": str(e)}

    async def _stage_4_map_channels(
        self,
        workspace_id: str,
        built_icps: List[Dict[str, Any]],
        extracted_jtbds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute Stage 4: Channel Mapping"""
        try:
            state = {
                "context": {
                    "workspace_id": workspace_id,
                    "built_icps": built_icps,
                    "extracted_jtbds": extracted_jtbds
                }
            }

            result = await self.channel_mapper.app.ainvoke(state)

            return result.get("results", {})

        except Exception as e:
            logger.exception(f"Stage 4 error: {str(e)}")
            return {"error": str(e)}

    async def _stage_5_generate_explanations(
        self,
        workspace_id: str,
        processed_context_items: List[Dict[str, Any]],
        extracted_jtbds: List[Dict[str, Any]],
        built_icps: List[Dict[str, Any]],
        mapped_channels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute Stage 5: Explanation Generation"""
        try:
            state = {
                "context": {
                    "workspace_id": workspace_id,
                    "processed_context_items": processed_context_items,
                    "extracted_jtbds": extracted_jtbds,
                    "built_icps": built_icps,
                    "mapped_channels": mapped_channels
                }
            }

            result = await self.explanation_agent.app.ainvoke(state)

            return result.get("results", {})

        except Exception as e:
            logger.exception(f"Stage 5 error: {str(e)}")
            return {"error": str(e)}

    async def analyze_single_stage(
        self,
        stage: int,
        workspace_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a single stage in isolation (for debugging/testing).

        Args:
            stage: Stage number (1-5)
            workspace_id: Workspace identifier
            **kwargs: Stage-specific parameters

        Returns:
            Results from the specified stage
        """
        try:
            if stage == 1:
                return await self._stage_1_process_context(
                    workspace_id,
                    kwargs.get("context_items", [])
                )
            elif stage == 2:
                return await self._stage_2_extract_jtbd(
                    workspace_id,
                    kwargs.get("processed_context_items", [])
                )
            elif stage == 3:
                return await self._stage_3_build_icps(
                    workspace_id,
                    kwargs.get("processed_context_items", []),
                    kwargs.get("extracted_jtbds", [])
                )
            elif stage == 4:
                return await self._stage_4_map_channels(
                    workspace_id,
                    kwargs.get("built_icps", []),
                    kwargs.get("extracted_jtbds", [])
                )
            elif stage == 5:
                return await self._stage_5_generate_explanations(
                    workspace_id,
                    kwargs.get("processed_context_items", []),
                    kwargs.get("extracted_jtbds", []),
                    kwargs.get("built_icps", []),
                    kwargs.get("mapped_channels", [])
                )
            else:
                return {"error": f"Invalid stage number: {stage}"}

        except Exception as e:
            logger.exception(f"Error running stage {stage}: {str(e)}")
            return {"error": str(e)}


# Factory function
def create_strategy_orchestrator() -> StrategyOrchestrator:
    """Create a new StrategyOrchestrator instance"""
    return StrategyOrchestrator()

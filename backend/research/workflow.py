"""
LangGraph Deep Research Workflow

Complete orchestration of the multi-agent research system using LangGraph.
Handles state management, checkpointing, and human-in-the-loop interactions.
"""

import logging
import time
import uuid
import os
from typing import Dict, Optional, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ResearchState
from .agents import (
    IntakeAgent,
    PlannerAgent,
    SearcherAgent,
    FetcherAgent,
    RankerAgent,
    SynthesizerAgent,
    WriterAgent
)

logger = logging.getLogger(__name__)


class DeepResearchGraph:
    """
    Main LangGraph workflow orchestrator.

    Manages:
    - State checkpointing for fault tolerance
    - Parallel agent execution
    - Human-in-the-loop interventions
    - Real-time progress tracking
    """

    def __init__(
        self,
        perplexity_api_key: str,
        exa_api_key: str,
        google_api_key: str,
        google_search_engine_id: str,
        llm: Optional[ChatOpenAI] = None,
        use_memory_checkpoint: bool = True
    ):
        """
        Initialize research graph with API keys and LLM.

        Args:
            perplexity_api_key: Perplexity API key
            exa_api_key: Exa.ai API key
            google_api_key: Google API key
            google_search_engine_id: Google Custom Search engine ID
            llm: Language model instance
            use_memory_checkpoint: Use in-memory checkpointing (production: use PostgreSQL)
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.3)

        # Initialize agents
        self.intake_agent = IntakeAgent(self.llm)
        self.planner_agent = PlannerAgent(self.llm)
        self.searcher_agent = SearcherAgent(
            perplexity_api_key=perplexity_api_key,
            exa_api_key=exa_api_key,
            google_api_key=google_api_key,
            google_search_engine_id=google_search_engine_id,
            llm=self.llm
        )
        self.fetcher_agent = FetcherAgent()
        self.ranker_agent = RankerAgent(self.llm)
        self.synthesizer_agent = SynthesizerAgent(self.llm)
        self.writer_agent = WriterAgent(self.llm)

        # Setup checkpointer
        self.checkpointer = MemorySaver() if use_memory_checkpoint else None

        # Build graph
        self.graph = self._build_graph()
        self.compiled_graph = None

    def _build_graph(self) -> StateGraph:
        """
        Construct the LangGraph workflow.

        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(ResearchState)

        # Add agent nodes
        workflow.add_node("intake", self._node_intake)
        workflow.add_node("planner", self._node_planner)
        workflow.add_node("searcher", self._node_searcher)
        workflow.add_node("fetcher", self._node_fetcher)
        workflow.add_node("ranker", self._node_ranker)
        workflow.add_node("synthesizer", self._node_synthesizer)
        workflow.add_node("writer", self._node_writer)

        # Define workflow edges
        workflow.set_entry_point("intake")

        # Conditional: intake might need clarification
        workflow.add_conditional_edges(
            "intake",
            self._should_clarify,
            {
                "clarify": END,  # Pause for user input
                "continue": "planner"
            }
        )

        # Linear flow
        workflow.add_edge("planner", "searcher")
        workflow.add_edge("searcher", "fetcher")
        workflow.add_edge("fetcher", "ranker")
        workflow.add_edge("ranker", "synthesizer")
        workflow.add_edge("synthesizer", "writer")
        workflow.add_edge("writer", END)

        # Compile with checkpointer
        return workflow.compile(checkpointer=self.checkpointer)

    # Node wrapper functions - each wraps agent processing and tracks timing
    async def _node_intake(self, state: ResearchState) -> ResearchState:
        """Intake node with timing"""
        start = time.time()
        state["execution_time"] = state.get("execution_time", {})
        result = await self.intake_agent.process(state)
        result["execution_time"]["intake"] = time.time() - start
        return result

    async def _node_planner(self, state: ResearchState) -> ResearchState:
        """Planner node with timing"""
        start = time.time()
        state["execution_time"] = state.get("execution_time", {})
        result = await self.planner_agent.process(state)
        result["execution_time"]["planner"] = time.time() - start
        return result

    async def _node_searcher(self, state: ResearchState) -> ResearchState:
        """Searcher node with timing"""
        start = time.time()
        state["execution_time"] = state.get("execution_time", {})
        result = await self.searcher_agent.process(state)
        result["execution_time"]["searcher"] = time.time() - start
        return result

    async def _node_fetcher(self, state: ResearchState) -> ResearchState:
        """Fetcher node with timing"""
        start = time.time()
        state["execution_time"] = state.get("execution_time", {})
        result = await self.fetcher_agent.process(state)
        result["execution_time"]["fetcher"] = time.time() - start
        return result

    async def _node_ranker(self, state: ResearchState) -> ResearchState:
        """Ranker node with timing"""
        start = time.time()
        state["execution_time"] = state.get("execution_time", {})
        result = await self.ranker_agent.process(state)
        result["execution_time"]["ranker"] = time.time() - start
        return result

    async def _node_synthesizer(self, state: ResearchState) -> ResearchState:
        """Synthesizer node with timing"""
        start = time.time()
        state["execution_time"] = state.get("execution_time", {})
        result = await self.synthesizer_agent.process(state)
        result["execution_time"]["synthesizer"] = time.time() - start
        return result

    async def _node_writer(self, state: ResearchState) -> ResearchState:
        """Writer node with timing"""
        start = time.time()
        state["execution_time"] = state.get("execution_time", {})
        result = await self.writer_agent.process(state)
        result["execution_time"]["writer"] = time.time() - start
        return result

    def _should_clarify(self, state: ResearchState) -> str:
        """
        Routing function: determine if clarification is needed.

        Returns:
            "clarify" to pause for user input, "continue" to proceed
        """
        return "clarify" if state.get("requires_clarification") else "continue"

    async def research(
        self,
        query: str,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute complete research workflow.

        Args:
            query: User's research question
            thread_id: Optional session ID (generated if not provided)
            user_id: Optional user ID for tracking
            **kwargs: Additional research parameters

        Returns:
            Final research state with report and metadata
        """
        thread_id = thread_id or str(uuid.uuid4())
        logger.info(f"Starting research workflow: {thread_id}")

        # Initialize state
        initial_state = ResearchState(
            thread_id=thread_id,
            user_id=user_id,
            created_at=datetime.now().isoformat(),
            user_query=query,
            query_type=kwargs.get("query_type", "hybrid"),
            max_depth=kwargs.get("max_depth", 3),
            max_sources=kwargs.get("max_sources", 100),
            focus_areas=kwargs.get("focus_areas"),
            clarified_query=None,
            research_intent=None,
            research_domain=None,
            context_requirements=None,
            research_plan=None,
            sub_questions=[],
            dependencies={},
            priority_order=[],
            research_strategy=None,
            search_results=[],
            perplexity_results=[],
            exa_results=[],
            google_results=[],
            search_metadata={},
            search_queries_executed=[],
            fetched_content=[],
            extraction_errors=[],
            content_metadata={},
            skipped_urls=[],
            ranked_sources=[],
            relevance_scores={},
            diversity_score=0.0,
            quality_metrics={},
            synthesized_chunks=[],
            cross_references=[],
            contradictions=[],
            synthesis_notes=[],
            knowledge_gaps=[],
            final_report=None,
            report_sections=None,
            citations=[],
            confidence_scores={},
            bibliography=[],
            messages=[],
            current_phase="intake",
            phase_history=[],
            errors=[],
            warnings=[],
            execution_time={},
            total_tokens_used=0,
            api_calls_made={},
            requires_clarification=False,
            clarification_question=None,
            user_feedback=None,
            cache_hits=0,
            embedding_cache={},
            research_complete=False,
            output_format="markdown",
            summary=None
        )

        # Run graph
        config = {"configurable": {"thread_id": thread_id}} if self.checkpointer else None

        try:
            # Compile if not yet compiled
            if self.compiled_graph is None:
                self.compiled_graph = self.graph.compile(checkpointer=self.checkpointer)

            final_state = await self.compiled_graph.ainvoke(
                initial_state,
                config=config
            )

            logger.info(f"Research completed: {thread_id}")

            return {
                "thread_id": thread_id,
                "report": final_state.get("final_report", ""),
                "summary": final_state.get("summary", ""),
                "citations": final_state.get("citations", []),
                "bibliography": final_state.get("bibliography", []),
                "confidence": final_state.get("confidence_scores", {}),
                "metadata": {
                    "execution_time": final_state.get("execution_time", {}),
                    "total_sources": len(final_state.get("ranked_sources", [])),
                    "total_results_found": len(final_state.get("search_results", [])),
                    "contradictions": len(final_state.get("contradictions", [])),
                    "phase": final_state.get("current_phase", "complete"),
                    "research_complete": final_state.get("research_complete", False)
                }
            }

        except Exception as e:
            logger.error(f"Research workflow failed: {e}")
            return {
                "thread_id": thread_id,
                "error": str(e),
                "report": "Research workflow encountered an error",
                "metadata": {"phase": "error"}
            }

    def get_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve current state for a research session.

        Args:
            thread_id: Research session ID

        Returns:
            Current state dictionary or None if not found
        """
        if not self.checkpointer:
            return None

        try:
            state = self.checkpointer.get(thread_id)
            return state
        except Exception as e:
            logger.error(f"Failed to retrieve state for {thread_id}: {e}")
            return None

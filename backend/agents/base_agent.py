"""Base agent class with common functionality for all agents - CLOUD ONLY"""
import json
import logging
from typing import TypedDict, Any, Dict, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from langgraph.graph import StateGraph, END
from backend.utils.cloud_provider import get_cloud_provider, AllProvidersFailedError

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Base state for all agents"""
    business_id: str
    agent_name: str
    stage: str
    status: str  # running, completed, failed, paused
    error: Optional[str]
    context: Dict[str, Any]
    results: Dict[str, Any]
    timestamp: str


class BaseAgent(ABC):
    """Base class for all LangGraph agents - CLOUD ONLY ARCHITECTURE"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.graph = None
        self.app = None
        self.cloud_provider = get_cloud_provider()
        self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state machine"""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("initialize", self._initialize)
        graph.add_node("process", self._process)
        graph.add_node("validate", self._validate)
        graph.add_node("finalize", self._finalize)
        graph.add_node("error_handler", self._handle_error)

        # Set entry point
        graph.set_entry_point("initialize")

        # Add edges
        graph.add_edge("initialize", "process")

        # Conditional routing after process
        graph.add_conditional_edges(
            "process",
            self._should_validate,
            {
                "validate": "validate",
                "error": "error_handler"
            }
        )

        graph.add_edge("validate", "finalize")
        graph.add_edge("error_handler", "finalize")
        graph.add_edge("finalize", END)

        self.graph = graph
        self.app = graph.compile()

    def _initialize(self, state: AgentState) -> AgentState:
        """Initialize agent state"""
        state["agent_name"] = self.name
        state["stage"] = "initializing"
        state["status"] = "running"
        state["timestamp"] = datetime.now().isoformat()
        state["results"] = {}

        logger.info(f"Agent {self.name} initialized for business {state['business_id']}")
        return state

    @abstractmethod
    def _process(self, state: AgentState) -> AgentState:
        """Main processing logic - implement in subclass"""
        pass

    @abstractmethod
    def _validate(self, state: AgentState) -> AgentState:
        """Validate results - implement in subclass"""
        pass

    def _should_validate(self, state: AgentState) -> str:
        """Determine if validation is needed"""
        if state.get("error"):
            return "error"
        return "validate"

    def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors gracefully"""
        logger.error(f"Error in {self.name}: {state.get('error')}")
        state["status"] = "failed"
        return state

    def _finalize(self, state: AgentState) -> AgentState:
        """Finalize and prepare results"""
        state["status"] = "completed"
        state["timestamp"] = datetime.now().isoformat()
        logger.info(f"Agent {self.name} completed for business {state['business_id']}")
        return state

    def call_ai(
        self,
        prompt: str,
        task_complexity: str = "moderate",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make AI call using cloud provider with automatic fallback.

        Cloud-only architecture:
        - Development mode: Gemini → OpenRouter
        - Production mode: OpenAI GPT-5 series → OpenRouter

        Args:
            prompt: The input prompt
            task_complexity: "simple", "moderate", or "complex"
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional model-specific parameters

        Returns:
            Dict containing:
                - success: Boolean
                - content: Generated text
                - model_used: Which model was used
                - provider: Which provider was used
                - usage: Token usage statistics
        """

        try:
            logger.info(
                f"Agent {self.name} making cloud AI call "
                f"(complexity: {task_complexity}, max_tokens: {max_tokens})"
            )

            result = self.cloud_provider.generate(
                prompt=prompt,
                task_complexity=task_complexity,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            if result["success"]:
                logger.info(
                    f"Agent {self.name} AI call successful - "
                    f"Provider: {result['provider']}, Model: {result['model_used']}, "
                    f"Tokens: {result['usage']['total_tokens']}"
                )

            return result

        except AllProvidersFailedError as e:
            logger.error(f"All cloud providers failed for agent {self.name}: {e}")
            return {
                "success": False,
                "error": "ALL_PROVIDERS_FAILED",
                "message": "All configured cloud providers failed. Please check API keys and try again.",
                "model_used": None,
                "provider": None
            }

        except Exception as e:
            logger.error(f"Unexpected error in AI call for agent {self.name}: {e}")
            return {
                "success": False,
                "error": "AI_CALL_FAILED",
                "message": str(e),
                "model_used": None,
                "provider": None
            }

    async def run(self, business_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent"""
        initial_state = AgentState(
            business_id=business_id,
            agent_name=self.name,
            stage="start",
            status="pending",
            error=None,
            context=context,
            results={},
            timestamp=datetime.now().isoformat()
        )

        try:
            final_state = self.app.invoke(initial_state)
            return {
                "success": final_state["status"] == "completed",
                "status": final_state["status"],
                "results": final_state["results"],
                "error": final_state.get("error")
            }
        except Exception as e:
            logger.exception(f"Agent {self.name} crashed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "results": {}
            }

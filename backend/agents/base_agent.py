"""Base agent class with common functionality for all agents"""
import json
import logging
from typing import TypedDict, Any, Dict, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from langgraph.graph import StateGraph, END
from ..middleware.budget_controller import budget_controller, get_optimal_model, check_budget_before_api_call

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
    """Base class for all LangGraph agents"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.graph = None
        self.app = None
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

    def call_ai_with_budget_control(self, prompt: str, task_complexity: str = "simple", estimated_tokens: int = 500) -> Dict[str, Any]:
        """
        Make AI call with automatic budget control and model selection
        """
        # Get optimal model based on task complexity and budget
        model = get_optimal_model(task_complexity, estimated_tokens)
        
        # Check budget before making call
        can_make, reason = budget_controller.can_make_request(model, estimated_tokens, estimated_tokens // 4)
        if not can_make:
            logger.warning(f"Budget limit exceeded for {self.name}: {reason}")
            return {
                "success": False,
                "error": "BUDGET_LIMIT_EXCEEDED",
                "message": reason,
                "model_used": None,
                "fallback_response": "Budget limit reached. Please try again tomorrow."
            }
        
        try:
            # This would be replaced with actual OpenAI client call
            # For now, simulate the call with budget tracking
            logger.info(f"Making AI call with model: {model} for agent: {self.name}")
            
            # Simulate API response (replace with actual OpenAI call)
            response = {
                "content": f"Simulated response from {model} for task: {task_complexity}",
                "model": model,
                "usage": {
                    "prompt_tokens": estimated_tokens,
                    "completion_tokens": estimated_tokens // 4,
                    "total_tokens": estimated_tokens + (estimated_tokens // 4)
                }
            }
            
            # Record actual usage
            budget_controller.record_usage(
                model,
                response["usage"]["prompt_tokens"],
                response["usage"]["completion_tokens"]
            )
            
            return {
                "success": True,
                "content": response["content"],
                "model_used": model,
                "usage": response["usage"],
                "cost": budget_controller.calculate_request_cost(
                    model,
                    response["usage"]["prompt_tokens"],
                    response["usage"]["completion_tokens"]
                )
            }
            
        except Exception as e:
            logger.error(f"AI call failed for {self.name}: {str(e)}")
            return {
                "success": False,
                "error": "AI_CALL_FAILED",
                "message": str(e),
                "model_used": model
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

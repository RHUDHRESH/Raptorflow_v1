"""Base agent class with common functionality for all agents"""
import json
import logging
from typing import TypedDict, Any, Dict, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from langgraph.graph import StateGraph, END

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

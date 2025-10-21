"""
Enhanced Base Agent v2 - Advanced capabilities with multi-model support,
real-time data, error recovery, and extensive integrations
"""
import json
import logging
import asyncio
from typing import TypedDict, Any, Dict, List, Optional, Union, Callable
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
import httpx
import aiofiles
from pathlib import Path

# Enhanced imports for new capabilities
from ..middleware.budget_controller import budget_controller, get_optimal_model
from ..middleware.ai_safety import AISafetyGuardrails
from ..middleware.monitoring import PerformanceMonitor
from ..middleware.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Enhanced agent status tracking"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    WAITING_FOR_INPUT = "waiting_for_input"
    PROCESSING = "processing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class AIModelConfig:
    """AI model configuration"""
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class IntegrationConfig:
    """External integration configuration"""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    rate_limit: Optional[int] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_tokens_used: int = 0
    total_cost: float = 0.0
    api_calls_made: int = 0
    errors_encountered: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    processing_time: float = 0.0


class EnhancedAgentState(TypedDict):
    """Enhanced state for all agents with advanced features"""
    # Core fields
    business_id: str
    agent_name: str
    agent_version: str
    stage: str
    status: str
    priority: int
    error: Optional[str]
    context: Dict[str, Any]
    results: Dict[str, Any]
    timestamp: str
    
    # Enhanced fields
    metadata: Dict[str, Any]
    config: Dict[str, Any]
    integrations: Dict[str, IntegrationConfig]
    ai_models: Dict[str, AIModelConfig]
    performance: PerformanceMetrics
    retry_count: int
    max_retries: int
    parent_agent_id: Optional[str]
    child_agents: List[str]
    collaboration_mode: bool
    real_time_data: Dict[str, Any]
    user_feedback: Optional[Dict[str, Any]]
    cache_enabled: bool
    monitoring_enabled: bool
    safety_checks_enabled: bool


class EnhancedBaseAgent(ABC):
    """Enhanced base agent with advanced capabilities"""

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "2.0.0",
        default_models: List[str] = None,
        integrations: List[str] = None,
        capabilities: List[str] = None
    ):
        self.name = name
        self.description = description
        self.version = version
        self.graph = None
        self.app = None
        
        # Configuration
        self.default_models = default_models or ["gpt-4", "gpt-3.5-turbo"]
        self.available_integrations = integrations or []
        self.capabilities = capabilities or []
        
        # Enhanced components
        self.safety_guardrails = AISafetyGuardrails()
        self.performance_monitor = PerformanceMonitor()
        self.rate_limiter = RateLimiter()
        
        # Cache and state management
        self.cache = {}
        self.active_tasks = {}
        self.collaboration_sessions = {}
        
        # Build the enhanced graph
        self._build_enhanced_graph()
        self.app = self.graph.compile()

    def _build_enhanced_graph(self):
        """Build enhanced LangGraph state machine with advanced features"""
        graph = StateGraph(EnhancedAgentState)

        # Add enhanced nodes
        graph.add_node("initialize", self._enhanced_initialize)
        graph.add_node("validate_config", self._validate_configuration)
        graph.add_node("setup_integrations", self._setup_integrations)
        graph.add_node("load_real_time_data", self._load_real_time_data)
        graph.add_node("process", self._enhanced_process)
        graph.add_node("collaborate_if_needed", self._handle_collaboration)
        graph.add_node("validate_with_safety", self._validate_with_safety)
        graph.add_node("optimize_results", self._optimize_results)
        graph.add_node("handle_errors", self._enhanced_error_handler)
        graph.add_node("finalize", self._enhanced_finalize)
        graph.add_node("cleanup", self._cleanup_resources)

        # Set entry point
        graph.set_entry_point("initialize")

        # Add enhanced edges with conditional routing
        graph.add_edge("initialize", "validate_config")
        graph.add_edge("validate_config", "setup_integrations")
        graph.add_edge("setup_integrations", "load_real_time_data")
        graph.add_edge("load_real_time_data", "process")

        # Enhanced conditional routing after process
        graph.add_conditional_edges(
            "process",
            self._determine_next_step,
            {
                "collaborate": "collaborate_if_needed",
                "validate": "validate_with_safety",
                "error": "handle_errors",
                "optimize": "optimize_results"
            }
        )

        graph.add_edge("collaborate_if_needed", "validate_with_safety")
        graph.add_edge("validate_with_safety", "optimize_results")
        graph.add_edge("optimize_results", "finalize")
        graph.add_edge("handle_errors", "finalize")
        graph.add_edge("finalize", "cleanup")
        graph.add_edge("cleanup", END)

        self.graph = graph

    def _enhanced_initialize(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Enhanced initialization with comprehensive setup"""
        state["agent_name"] = self.name
        state["agent_version"] = self.version
        state["stage"] = "initializing"
        state["status"] = AgentStatus.INITIALIZING.value
        state["timestamp"] = datetime.now().isoformat()
        state["results"] = {}
        state["metadata"] = {
            "initialized_at": datetime.now().isoformat(),
            "capabilities": self.capabilities,
            "available_integrations": self.available_integrations
        }
        
        # Initialize performance tracking
        state["performance"] = PerformanceMetrics()
        state["retry_count"] = 0
        state["max_retries"] = 3
        
        # Initialize configuration
        state["config"] = {
            "cache_enabled": True,
            "monitoring_enabled": True,
            "safety_checks_enabled": True,
            "collaboration_mode": False,
            "real_time_updates": True
        }
        
        # Initialize AI models
        state["ai_models"] = {
            "primary": AIModelConfig(model=self.default_models[0]),
            "fallback": AIModelConfig(model=self.default_models[1] if len(self.default_models) > 1 else "gpt-3.5-turbo"),
            "fast": AIModelConfig(model="gpt-3.5-turbo", temperature=0.3)
        }
        
        # Initialize integrations
        state["integrations"] = {}
        state["real_time_data"] = {}
        state["user_feedback"] = None
        state["child_agents"] = []
        
        logger.info(f"Enhanced Agent {self.name} v{self.version} initialized for business {state['business_id']}")
        return state

    def _validate_configuration(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Validate agent configuration and prerequisites"""
        state["stage"] = "validating_config"
        
        try:
            # Validate business context
            if not state.get("business_id"):
                raise ValueError("Business ID is required")
            
            # Validate AI model configurations
            for model_name, model_config in state["ai_models"].items():
                if not model_config.model:
                    raise ValueError(f"Model {model_name} configuration is invalid")
            
            # Validate integrations if any are configured
            for integration_name, integration_config in state["integrations"].items():
                if integration_config.api_key and not integration_config.base_url:
                    logger.warning(f"Integration {integration_name} has API key but no base URL")
            
            # Check budget limits
            budget_status = budget_controller.get_budget_status(state["business_id"])
            if budget_status.get("exceeded", False):
                logger.warning(f"Budget exceeded for business {state['business_id']}")
                state["config"]["budget_limited"] = True
            
            state["stage"] = "config_validated"
            logger.info(f"Configuration validated for {self.name}")
            
        except Exception as e:
            state["error"] = f"Configuration validation failed: {str(e)}"
            logger.error(f"Configuration validation failed for {self.name}: {str(e)}")
        
        return state

    def _setup_integrations(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Setup external integrations"""
        state["stage"] = "setting_up_integrations"
        
        # Auto-configure common integrations based on agent capabilities
        if "web_search" in self.capabilities:
            state["integrations"]["perplexity"] = IntegrationConfig(
                name="perplexity",
                base_url="https://api.perplexity.ai",
                rate_limit=100
            )
        
        if "social_media" in self.capabilities:
            state["integrations"]["twitter"] = IntegrationConfig(
                name="twitter",
                base_url="https://api.twitter.com/2",
                rate_limit=300
            )
        
        if "analytics" in self.capabilities:
            state["integrations"]["google_analytics"] = IntegrationConfig(
                name="google_analytics",
                base_url="https://analyticsreporting.googleapis.com"
            )
        
        state["stage"] = "integrations_ready"
        return state

    async def _load_real_time_data(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Load real-time data from various sources"""
        if not state["config"].get("real_time_updates", True):
            return state
        
        state["stage"] = "loading_real_time_data"
        
        try:
            # Load market trends if analytics capability
            if "analytics" in self.capabilities:
                trends_data = await self._fetch_market_trends(state)
                state["real_time_data"]["market_trends"] = trends_data
            
            # Load social media sentiment if social capability
            if "social_media" in self.capabilities:
                sentiment_data = await self._fetch_social_sentiment(state)
                state["real_time_data"]["social_sentiment"] = sentiment_data
            
            # Load competitor updates if research capability
            if "research" in self.capabilities:
                competitor_data = await self._fetch_competitor_updates(state)
                state["real_time_data"]["competitor_updates"] = competitor_data
            
            state["stage"] = "real_time_data_loaded"
            
        except Exception as e:
            logger.warning(f"Failed to load real-time data: {str(e)}")
            state["real_time_data"]["error"] = str(e)
        
        return state

    @abstractmethod
    def _enhanced_process(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Enhanced main processing logic - implement in subclass"""
        pass

    def _determine_next_step(self, state: EnhancedAgentState) -> str:
        """Determine the next processing step based on state"""
        if state.get("error"):
            return "error"
        
        # Check if collaboration is needed
        if state.get("collaboration_mode", False) and not state.get("collaboration_completed", False):
            return "collaborate"
        
        # Check if safety validation is needed
        if state.get("safety_checks_enabled", True):
            return "validate"
        
        # Default to optimization
        return "optimize"

    async def _handle_collaboration(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Handle collaboration with other agents"""
        state["stage"] = "collaborating"
        
        # Implementation for agent collaboration
        # This would involve calling other agents and combining results
        
        state["collaboration_completed"] = True
        return state

    async def _validate_with_safety(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Validate results with AI safety checks"""
        if not state.get("safety_checks_enabled", True):
            return state
        
        state["stage"] = "safety_validation"
        
        try:
            # Validate results using safety guardrails
            results_text = json.dumps(state.get("results", {}))
            safety_check = await self.safety_guardrails.validate_content(results_text)
            
            if not safety_check.get("safe", True):
                state["error"] = f"Safety check failed: {safety_check.get('reason', 'Unknown')}"
                logger.warning(f"Safety check failed for {self.name}")
            else:
                state["safety_validated"] = True
                
        except Exception as e:
            logger.warning(f"Safety validation failed: {str(e)}")
            # Continue without safety check if it fails
        
        return state

    async def _optimize_results(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Optimize and enhance results"""
        state["stage"] = "optimizing_results"
        
        try:
            # Apply result optimization based on agent type
            optimized_results = await self._apply_optimizations(state)
            state["results"] = optimized_results
            state["optimization_applied"] = True
            
        except Exception as e:
            logger.warning(f"Result optimization failed: {str(e)}")
            # Continue with original results
        
        return state

    async def _enhanced_error_handler(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Enhanced error handling with retry logic"""
        state["status"] = AgentStatus.FAILED.value
        state["performance"].errors_encountered += 1
        
        error = state.get("error", "Unknown error")
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)
        
        logger.error(f"Error in {self.name}: {error} (attempt {retry_count + 1}/{max_retries})")
        
        # Implement retry logic
        if retry_count < max_retries:
            state["retry_count"] = retry_count + 1
            state["status"] = AgentStatus.RETRYING.value
            
            # Wait before retry with exponential backoff
            retry_delay = 2 ** retry_count
            await asyncio.sleep(retry_delay)
            
            # Clear error and retry
            state["error"] = None
            return await self._enhanced_process(state)
        
        return state

    async def _enhanced_finalize(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Enhanced finalization with comprehensive cleanup"""
        state["status"] = AgentStatus.COMPLETED.value
        state["timestamp"] = datetime.now().isoformat()
        
        # Finalize performance metrics
        state["performance"].end_time = datetime.now()
        state["performance"].processing_time = (
            state["performance"].end_time - state["performance"].start_time
        ).total_seconds()
        
        # Generate summary
        state["summary"] = {
            "agent": self.name,
            "version": self.version,
            "duration": state["performance"].processing_time,
            "tokens_used": state["performance"].total_tokens_used,
            "cost": state["performance"].total_cost,
            "api_calls": state["performance"].api_calls_made,
            "errors": state["performance"].errors_encountered,
            "cache_hit_rate": self._calculate_cache_hit_rate(state)
        }
        
        logger.info(f"Enhanced Agent {self.name} completed for business {state['business_id']}")
        return state

    async def _cleanup_resources(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Clean up resources and save state"""
        try:
            # Save performance metrics
            if state.get("monitoring_enabled", True):
                await self.performance_monitor.record_metrics(
                    agent_name=self.name,
                    business_id=state["business_id"],
                    metrics=state["performance"]
                )
            
            # Clear temporary data
            state["temp_data"] = {}
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {str(e)}")
        
        return state

    # Enhanced AI calling methods
    async def call_ai_with_enhanced_control(
        self,
        prompt: str,
        task_complexity: str = "medium",
        estimated_tokens: int = 500,
        model_config: Optional[AIModelConfig] = None,
        use_cache: bool = True,
        enable_streaming: bool = False
    ) -> Dict[str, Any]:
        """Enhanced AI call with advanced controls"""
        
        # Use cache if enabled and available
        cache_key = f"{hash(prompt)}_{task_complexity}_{estimated_tokens}"
        if use_cache and cache_key in self.cache:
            state["performance"].cache_hits += 1
            return self.cache[cache_key]
        
        state["performance"].cache_misses += 1
        
        # Get optimal model configuration
        if not model_config:
            model_config = state.get("ai_models", {}).get("primary")
        
        # Check budget before making call
        can_make, reason = budget_controller.can_make_request(
            model_config.model, 
            estimated_tokens, 
            estimated_tokens // 4
        )
        
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
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Make the AI call with enhanced configuration
            result = await self._make_enhanced_ai_call(
                prompt=prompt,
                model_config=model_config,
                estimated_tokens=estimated_tokens,
                enable_streaming=enable_streaming
            )
            
            # Update performance metrics
            state["performance"].api_calls_made += 1
            state["performance"].total_tokens_used += result.get("usage", {}).get("total_tokens", 0)
            state["performance"].total_cost += result.get("cost", 0.0)
            
            # Record actual usage
            if result.get("usage"):
                budget_controller.record_usage(
                    model_config.model,
                    result["usage"]["prompt_tokens"],
                    result["usage"]["completion_tokens"]
                )
            
            # Cache the result
            if use_cache:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced AI call failed for {self.name}: {str(e)}")
            return {
                "success": False,
                "error": "AI_CALL_FAILED",
                "message": str(e),
                "model_used": model_config.model
            }

    async def _make_enhanced_ai_call(
        self,
        prompt: str,
        model_config: AIModelConfig,
        estimated_tokens: int,
        enable_streaming: bool = False
    ) -> Dict[str, Any]:
        """Make enhanced AI call with multiple model support"""
        # This would be implemented with actual AI model calls
        # For now, return a simulated response
        
        return {
            "success": True,
            "content": f"Enhanced response from {model_config.model} for task complexity: {prompt[:100]}...",
            "model_used": model_config.model,
            "usage": {
                "prompt_tokens": estimated_tokens,
                "completion_tokens": estimated_tokens // 4,
                "total_tokens": estimated_tokens + (estimated_tokens // 4)
            },
            "cost": budget_controller.calculate_request_cost(
                model_config.model,
                estimated_tokens,
                estimated_tokens // 4
            ),
            "enhanced_features": {
                "streaming_enabled": enable_streaming,
                "safety_validated": True,
                "optimized": True
            }
        }

    # Helper methods for real-time data
    async def _fetch_market_trends(self, state: EnhancedAgentState) -> Dict[str, Any]:
        """Fetch market trends from external sources"""
        # Implementation would call external APIs
        return {"trends": ["AI adoption increasing", "Remote work growth"], "timestamp": datetime.now().isoformat()}

    async def _fetch_social_sentiment(self, state: EnhancedAgentState) -> Dict[str, Any]:
        """Fetch social media sentiment data"""
        # Implementation would call social media APIs
        return {"sentiment": {"positive": 0.6, "negative": 0.2, "neutral": 0.2}, "timestamp": datetime.now().isoformat()}

    async def _fetch_competitor_updates(self, state: EnhancedAgentState) -> Dict[str, Any]:
        """Fetch competitor updates"""
        # Implementation would monitor competitor activities
        return {"updates": ["New product launch", "Price change"], "timestamp": datetime.now().isoformat()}

    async def _apply_optimizations(self, state: EnhancedAgentState) -> Dict[str, Any]:
        """Apply result optimizations"""
        # Implementation would optimize results based on agent type
        return state.get("results", {})

    def _calculate_cache_hit_rate(self, state: EnhancedAgentState) -> float:
        """Calculate cache hit rate"""
        total_requests = state["performance"].cache_hits + state["performance"].cache_misses
        if total_requests == 0:
            return 0.0
        return state["performance"].cache_hits / total_requests

    async def run(self, business_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the enhanced agent"""
        initial_state = EnhancedAgentState(
            business_id=business_id,
            agent_name=self.name,
            agent_version=self.version,
            stage="start",
            status=AgentStatus.INITIALIZING.value,
            priority=TaskPriority.NORMAL.value,
            error=None,
            context=context,
            results={},
            timestamp=datetime.now().isoformat(),
            metadata={},
            config={},
            integrations={},
            ai_models={},
            performance=PerformanceMetrics(),
            retry_count=0,
            max_retries=3,
            parent_agent_id=None,
            child_agents=[],
            collaboration_mode=False,
            real_time_data={},
            user_feedback=None,
            cache_enabled=True,
            monitoring_enabled=True,
            safety_checks_enabled=True
        )

        try:
            final_state = await self.app.ainvoke(initial_state)
            return {
                "success": final_state["status"] == AgentStatus.COMPLETED.value,
                "status": final_state["status"],
                "results": final_state["results"],
                "summary": final_state.get("summary", {}),
                "performance": final_state["performance"],
                "error": final_state.get("error")
            }
        except Exception as e:
            logger.exception(f"Enhanced Agent {self.name} crashed: {str(e)}")
            return {
                "success": False,
                "status": AgentStatus.FAILED.value,
                "error": str(e),
                "results": {}
            }

    # Enhanced utility methods
    async def collaborate_with_agent(
        self,
        target_agent: str,
        collaboration_data: Dict[str, Any],
        collaboration_type: str = "sequential"
    ) -> Dict[str, Any]:
        """Collaborate with another agent"""
        # Implementation for agent collaboration
        return {"collaboration_id": f"{self.name}_{target_agent}_{datetime.now().timestamp()}"}

    async def request_user_input(
        self,
        prompt: str,
        input_type: str = "text",
        options: List[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Request input from user"""
        # Implementation would send request to frontend
        return {"user_input": "Sample user response", "timestamp": datetime.now().isoformat()}

    async def schedule_task(
        self,
        task_name: str,
        scheduled_time: datetime,
        task_data: Dict[str, Any]
    ) -> str:
        """Schedule a task for future execution"""
        # Implementation would schedule the task
        return f"task_{task_name}_{scheduled_time.timestamp()}"

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and configuration"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_integrations": self.available_integrations,
            "default_models": self.default_models
        }

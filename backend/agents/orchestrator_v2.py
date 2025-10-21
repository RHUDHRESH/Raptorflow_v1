"""
Enhanced Orchestrator v2 - Advanced agent coordination with real-time monitoring,
collaborative workflows, and intelligent routing
"""
import json
import logging
import asyncio
from typing import TypedDict, Literal, Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Enhanced imports
from .base_agent_v2 import EnhancedBaseAgent, EnhancedAgentState, TaskPriority, AgentStatus
from ..tools.enhanced_tools_v2 import (
    real_time_data,
    advanced_analytics,
    automation_engine,
    collaboration_hub
)
from ..tools.state_manager import StateManagerTool
from ..tools.tier_validator import TierValidatorTool
from ..utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class OrchestratorMode(Enum):
    """Orchestrator operation modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    COLLABORATIVE = "collaborative"
    ADAPTIVE = "adaptive"


class RoutingStrategy(Enum):
    """Agent routing strategies"""
    PRIORITY_BASED = "priority_based"
    CAPABILITY_MATCH = "capability_match"
    LOAD_BALANCED = "load_balanced"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_DRIVEN = "performance_driven"


@dataclass
class AgentTask:
    """Agent task definition"""
    task_id: str
    agent_type: str
    priority: TaskPriority
    business_id: str
    context: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    retry_count: int = 0
    max_retries: int = 3
    estimated_cost: float = 0.0
    estimated_duration: int = 60


@dataclass
class WorkflowConfig:
    """Workflow configuration"""
    mode: OrchestratorMode = OrchestratorMode.HYBRID
    routing_strategy: RoutingStrategy = RoutingStrategy.CAPABILITY_MATCH
    enable_real_time_monitoring: bool = True
    enable_collaboration: bool = True
    enable_cost_optimization: bool = True
    enable_performance_tracking: bool = True
    max_parallel_tasks: int = 5
    timeout_multiplier: float = 1.5
    auto_retry_failed: bool = True


class EnhancedOrchestratorState(TypedDict):
    """Enhanced orchestrator state"""
    business_id: str
    workflow_id: str
    mode: str
    routing_strategy: str
    tasks: List[AgentTask]
    completed_tasks: List[str]
    failed_tasks: List[str]
    active_tasks: Dict[str, Dict[str, Any]]
    task_results: Dict[str, Dict[str, Any]]
    workflow_config: Dict[str, Any]
    real_time_metrics: Dict[str, Any]
    collaboration_sessions: Dict[str, Any]
    cost_tracking: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    error: Optional[str]
    status: str
    timestamp: str


class EnhancedOrchestratorAgent(EnhancedBaseAgent):
    """Enhanced orchestrator with advanced coordination capabilities"""

    def __init__(self):
        super().__init__(
            name="Enhanced Orchestrator",
            description="Advanced agent coordination with real-time monitoring and intelligent routing",
            version="2.0.0",
            default_models=["gpt-4", "gpt-3.5-turbo"],
            integrations=["slack", "teams", "monitoring", "analytics"],
            capabilities=[
                "intelligent_routing",
                "real_time_monitoring",
                "collaborative_workflows",
                "cost_optimization",
                "performance_tracking",
                "adaptive_execution",
                "error_recovery",
                "workflow_automation"
            ]
        )
        
        # Initialize tools
        self.state_manager = StateManagerTool()
        self.tier_validator = TierValidatorTool()
        self.supabase = get_supabase_client()
        
        # Workflow configuration
        self.workflow_config = WorkflowConfig()
        
        # Agent registry
        self.agent_registry = {
            "research": {
                "class": "ResearchAgent",
                "capabilities": ["market_research", "competitor_analysis", "trend_analysis"],
                "estimated_cost": 0.05,
                "estimated_duration": 120
            },
            "positioning": {
                "class": "PositioningAgent",
                "capabilities": ["positioning_strategy", "brand_analysis", "market_positioning"],
                "estimated_cost": 0.08,
                "estimated_duration": 180
            },
            "icp": {
                "class": "EnhancedICPAgent",
                "capabilities": ["persona_generation", "icp_analysis", "segmentation"],
                "estimated_cost": 0.12,
                "estimated_duration": 240
            },
            "strategy": {
                "class": "StrategyAgent",
                "capabilities": ["business_strategy", "growth_planning", "competitive_strategy"],
                "estimated_cost": 0.10,
                "estimated_duration": 200
            },
            "content": {
                "class": "ContentAgent",
                "capabilities": ["content_creation", "content_strategy", "content_calendar"],
                "estimated_cost": 0.06,
                "estimated_duration": 150
            },
            "analytics": {
                "class": "AnalyticsAgent",
                "capabilities": ["performance_analysis", "metrics_tracking", "reporting"],
                "estimated_cost": 0.04,
                "estimated_duration": 90
            }
        }
        
        # Active workflows tracking
        self.active_workflows = {}
        self.workflow_metrics = {}

    def _enhanced_process(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Enhanced main processing logic for orchestration"""
        try:
            # Initialize enhanced orchestration
            state["stage"] = "orchestrating"
            state["tasks"] = []
            state["completed_tasks"] = []
            state["failed_tasks"] = []
            state["active_tasks"] = {}
            state["task_results"] = {}
            state["real_time_metrics"] = {}
            state["collaboration_sessions"] = {}
            state["cost_tracking"] = {"total_estimated": 0.0, "total_actual": 0.0}
            state["performance_metrics"] = {}
            
            # Run the enhanced orchestration workflow
            import asyncio
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the enhanced workflow
            result = loop.run_until_complete(
                self._run_enhanced_orchestration(state)
            )
            
            state.update(result)
            state["stage"] = "completed"
            
        except Exception as e:
            state["error"] = str(e)
            state["stage"] = "failed"
            logger.error(f"Enhanced orchestration failed: {str(e)}")
        
        return state

    async def _run_enhanced_orchestration(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Run the complete enhanced orchestration workflow"""
        
        # Step 1: Analyze request and create task plan
        state = await self._analyze_and_plan_tasks(state)
        
        # Step 2: Optimize task execution plan
        state = await self._optimize_execution_plan(state)
        
        # Step 3: Setup real-time monitoring
        if self.workflow_config.enable_real_time_monitoring:
            state = await self._setup_real_time_monitoring(state)
        
        # Step 4: Execute tasks based on workflow mode
        if state["workflow_config"]["mode"] == OrchestratorMode.PARALLEL.value:
            state = await self._execute_parallel_tasks(state)
        elif state["workflow_config"]["mode"] == OrchestratorMode.SEQUENTIAL.value:
            state = await self._execute_sequential_tasks(state)
        elif state["workflow_config"]["mode"] == OrchestratorMode.HYBRID.value:
            state = await self._execute_hybrid_tasks(state)
        elif state["workflow_config"]["mode"] == OrchestratorMode.COLLABORATIVE.value:
            state = await self._execute_collaborative_tasks(state)
        else:  # ADAPTIVE
            state = await self._execute_adaptive_tasks(state)
        
        # Step 5: Aggregate and enhance results
        state = await self._aggregate_and_enhance_results(state)
        
        # Step 6: Generate workflow insights
        state = await self._generate_workflow_insights(state)
        
        # Step 7: Cleanup and finalize
        state = await self._cleanup_workflow(state)
        
        return state

    async def _analyze_and_plan_tasks(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Analyze user request and create optimal task plan"""
        logger.info("Analyzing request and planning tasks")
        
        user_input = state.get("context", {}).get("user_input", {})
        action = user_input.get("action", "")
        
        # Map actions to required agents
        action_agent_map = {
            "run_research": ["research"],
            "analyze_sostac": ["research"],
            "build_competitor_ladder": ["research"],
            "generate_positioning": ["research", "positioning"],
            "select_positioning": ["positioning"],
            "create_icps": ["research", "positioning", "icp"],
            "build_strategy": ["research", "positioning", "icp", "strategy"],
            "create_move": ["strategy", "content"],
            "generate_calendar": ["content"],
            "measure_performance": ["analytics"],
            "evaluate_campaign": ["analytics"],
            "comprehensive_analysis": ["research", "positioning", "icp", "strategy", "content", "analytics"]
        }
        
        required_agents = action_agent_map.get(action, ["research"])
        
        # Create tasks with intelligent prioritization
        tasks = []
        for i, agent_type in enumerate(required_agents):
            agent_info = self.agent_registry.get(agent_type, {})
            
            task = AgentTask(
                task_id=f"task_{agent_type}_{datetime.now().timestamp()}",
                agent_type=agent_type,
                priority=self._calculate_task_priority(agent_type, action),
                business_id=state["business_id"],
                context=state["context"],
                dependencies=required_agents[:i] if i > 0 else [],
                estimated_cost=agent_info.get("estimated_cost", 0.05),
                estimated_duration=agent_info.get("estimated_duration", 120)
            )
            tasks.append(task)
        
        state["tasks"] = tasks
        state["cost_tracking"]["total_estimated"] = sum(task.estimated_cost for task in tasks)
        
        return state

    async def _optimize_execution_plan(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Optimize task execution plan based on routing strategy"""
        logger.info(f"Optimizing execution plan with {state['workflow_config']['routing_strategy']} strategy")
        
        routing_strategy = state["workflow_config"]["routing_strategy"]
        tasks = state["tasks"]
        
        if routing_strategy == RoutingStrategy.PRIORITY_BASED.value:
            # Sort by priority
            tasks.sort(key=lambda x: x.priority.value, reverse=True)
        
        elif routing_strategy == RoutingStrategy.COST_OPTIMIZED.value:
            # Sort by cost (cheapest first for budget constraints)
            tasks.sort(key=lambda x: x.estimated_cost)
        
        elif routing_strategy == RoutingStrategy.PERFORMANCE_DRIVEN.value:
            # Sort by estimated duration (fastest first)
            tasks.sort(key=lambda x: x.estimated_duration)
        
        elif routing_strategy == RoutingStrategy.LOAD_BALANCED.value:
            # Distribute tasks evenly across time
            tasks = self._balance_task_load(tasks)
        
        # Apply routing-specific optimizations
        optimized_tasks = await self._apply_routing_optimizations(tasks, routing_strategy)
        
        state["tasks"] = optimized_tasks
        return state

    async def _setup_real_time_monitoring(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Setup real-time monitoring for workflow execution"""
        logger.info("Setting up real-time monitoring")
        
        # Create monitoring dashboard
        monitoring_config = {
            "workflow_id": state["workflow_id"],
            "business_id": state["business_id"],
            "tasks_count": len(state["tasks"]),
            "estimated_cost": state["cost_tracking"]["total_estimated"],
            "monitoring_metrics": [
                "task_progress",
                "cost_accumulation",
                "performance_metrics",
                "error_rates",
                "completion_times"
            ]
        }
        
        # Setup automation for monitoring
        automation_result = await automation_engine._execute(
            action="monitor_and_act",
            workflow_config={
                "conditions": [
                    {"metric": "cost_accumulation", "threshold": 0.8, "operator": ">"},
                    {"metric": "error_rates", "threshold": 0.1, "operator": ">"},
                    {"metric": "task_progress", "threshold": 0.9, "operator": "<", "duration": 300}
                ],
                "actions": ["send_alert", "adjust_strategy", "escalate"]
            }
        )
        
        if automation_result["success"]:
            state["real_time_monitoring"] = {
                "monitoring_id": automation_result["results"]["monitoring_id"],
                "config": monitoring_config,
                "active": True
            }
        
        return state

    async def _execute_parallel_tasks(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Execute tasks in parallel with dependency management"""
        logger.info("Executing tasks in parallel")
        
        tasks = state["tasks"]
        max_parallel = self.workflow_config.max_parallel_tasks
        completed_tasks = []
        failed_tasks = []
        task_results = {}
        
        # Group tasks by dependency level
        dependency_levels = self._group_tasks_by_dependencies(tasks)
        
        for level, level_tasks in dependency_levels.items():
            # Execute tasks at current level in parallel
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def execute_task(task):
                async with semaphore:
                    return await self._execute_single_task(task, state)
            
            # Execute all tasks at this level
            level_results = await asyncio.gather(
                *[execute_task(task) for task in level_tasks],
                return_exceptions=True
            )
            
            # Process results
            for i, result in enumerate(level_results):
                task = level_tasks[i]
                if isinstance(result, Exception):
                    failed_tasks.append(task.task_id)
                    logger.error(f"Task {task.task_id} failed: {str(result)}")
                else:
                    completed_tasks.append(task.task_id)
                    task_results[task.task_id] = result
            
            # Update state
            state["completed_tasks"] = completed_tasks
            state["failed_tasks"] = failed_tasks
            state["task_results"] = task_results
            
            # Check if we should continue (fail fast if critical tasks fail)
            if len(failed_tasks) > len(tasks) * 0.3:  # More than 30% failure rate
                logger.warning("High failure rate detected, stopping execution")
                break
        
        return state

    async def _execute_sequential_tasks(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Execute tasks sequentially with dependency checking"""
        logger.info("Executing tasks sequentially")
        
        tasks = state["tasks"]
        completed_tasks = []
        failed_tasks = []
        task_results = {}
        
        for task in tasks:
            # Check dependencies
            if task.dependencies:
                missing_deps = [dep for dep in task.dependencies if dep not in completed_tasks]
                if missing_deps:
                    logger.error(f"Task {task.task_id} has missing dependencies: {missing_deps}")
                    failed_tasks.append(task.task_id)
                    continue
            
            # Execute task
            try:
                result = await self._execute_single_task(task, state)
                completed_tasks.append(task.task_id)
                task_results[task.task_id] = result
                
                # Update state after each task
                state["completed_tasks"] = completed_tasks
                state["task_results"] = task_results
                
            except Exception as e:
                failed_tasks.append(task.task_id)
                logger.error(f"Task {task.task_id} failed: {str(e)}")
                
                # Stop on critical task failure
                if task.priority == TaskPriority.CRITICAL:
                    break
        
        state["failed_tasks"] = failed_tasks
        return state

    async def _execute_hybrid_tasks(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Execute tasks with hybrid approach (parallel where possible, sequential where needed)"""
        logger.info("Executing tasks with hybrid approach")
        
        # This is a simplified version - in production would use more sophisticated logic
        tasks = state["tasks"]
        
        # Separate independent and dependent tasks
        independent_tasks = [t for t in tasks if not t.dependencies]
        dependent_tasks = [t for t in tasks if t.dependencies]
        
        # Execute independent tasks in parallel
        if independent_tasks:
            state["tasks"] = independent_tasks
            state = await self._execute_parallel_tasks(state)
        
        # Execute dependent tasks sequentially
        if dependent_tasks:
            state["tasks"] = dependent_tasks
            state = await self._execute_sequential_tasks(state)
        
        return state

    async def _execute_collaborative_tasks(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Execute tasks with collaborative approach"""
        logger.info("Executing tasks with collaborative approach")
        
        # Create collaboration space
        collaboration_result = await collaboration_hub._execute(
            action="create_team_space",
            collaboration_data={
                "name": f"Workflow {state['workflow_id']} Collaboration",
                "members": state.get("context", {}).get("team_members", []),
                "purpose": "Collaborative task execution and review"
            }
        )
        
        if collaboration_result["success"]:
            space_id = collaboration_result["results"]["space_id"]
            state["collaboration_sessions"]["main"] = space_id
            
            # Execute tasks with collaboration checkpoints
            tasks = state["tasks"]
            for i, task in enumerate(tasks):
                # Notify team about task start
                await collaboration_hub._execute(
                    action="send_message",
                    collaboration_data={
                        "space_id": space_id,
                        "content": f"Starting task {i+1}/{len(tasks)}: {task.agent_type}",
                        "mentions": ["@team"]
                    }
                )
                
                # Execute task
                try:
                    result = await self._execute_single_task(task, state)
                    state["task_results"][task.task_id] = result
                    state["completed_tasks"].append(task.task_id)
                    
                    # Share results for review
                    await collaboration_hub._execute(
                        action="send_message",
                        collaboration_data={
                            "space_id": space_id,
                            "content": f"Completed {task.agent_type} task. Results ready for review.",
                            "attachments": [result]
                        }
                    )
                    
                    # Collect feedback (simulated brief delay)
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    state["failed_tasks"].append(task.task_id)
                    logger.error(f"Collaborative task {task.task_id} failed: {str(e)}")
        
        return state

    async def _execute_adaptive_tasks(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Execute tasks with adaptive approach based on real-time conditions"""
        logger.info("Executing tasks with adaptive approach")
        
        # Start with parallel execution
        initial_mode = state["workflow_config"]["mode"]
        state["workflow_config"]["mode"] = OrchestratorMode.PARALLEL.value
        
        # Monitor and adapt
        tasks_completed = 0
        total_tasks = len(state["tasks"])
        
        async def adaptive_monitor():
            while tasks_completed < total_tasks:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Get current metrics
                current_metrics = state.get("real_time_metrics", {})
                error_rate = current_metrics.get("error_rate", 0)
                cost_rate = current_metrics.get("cost_rate", 0)
                
                # Adapt strategy based on conditions
                if error_rate > 0.2:
                    # High error rate - switch to sequential
                    state["workflow_config"]["mode"] = OrchestratorMode.SEQUENTIAL.value
                    logger.info("Switching to sequential due to high error rate")
                
                elif cost_rate > 0.8:
                    # High cost - switch to cost-optimized
                    state["workflow_config"]["routing_strategy"] = RoutingStrategy.COST_OPTIMIZED.value
                    logger.info("Switching to cost-optimized routing")
        
        # Start monitoring
        monitor_task = asyncio.create_task(adaptive_monitor())
        
        try:
            # Execute with adaptive monitoring
            state = await self._execute_parallel_tasks(state)
        finally:
            monitor_task.cancel()
        
        # Restore original mode
        state["workflow_config"]["mode"] = initial_mode
        
        return state

    async def _execute_single_task(self, task: AgentTask, state: EnhancedOrchestratorState) -> Dict[str, Any]:
        """Execute a single task with enhanced error handling"""
        logger.info(f"Executing task {task.task_id}: {task.agent_type}")
        
        start_time = datetime.now()
        
        try:
            # Get agent instance
            agent = await self._get_agent_instance(task.agent_type)
            
            # Execute agent with timeout
            result = await asyncio.wait_for(
                agent.run(task.business_id, task.context),
                timeout=task.timeout
            )
            
            # Update cost tracking
            actual_cost = result.get("performance", {}).get("total_cost", task.estimated_cost)
            state["cost_tracking"]["total_actual"] += actual_cost
            
            # Update performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "task_id": task.task_id,
                "agent_type": task.agent_type,
                "success": result.get("success", False),
                "results": result.get("results", {}),
                "performance": result.get("performance", {}),
                "execution_time": execution_time,
                "actual_cost": actual_cost,
                "completed_at": datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Task {task.task_id} timed out")
            raise Exception(f"Task execution timed out after {task.timeout} seconds")
        
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count})")
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                return await self._execute_single_task(task, state)
            
            raise

    async def _aggregate_and_enhance_results(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Aggregate and enhance results from all tasks"""
        logger.info("Aggregating and enhancing results")
        
        task_results = state["task_results"]
        
        # Basic aggregation
        aggregated_results = {
            "summary": {
                "total_tasks": len(state["tasks"]),
                "completed_tasks": len(state["completed_tasks"]),
                "failed_tasks": len(state["failed_tasks"]),
                "success_rate": len(state["completed_tasks"]) / len(state["tasks"]) if state["tasks"] else 0
            },
            "cost_analysis": {
                "estimated_total": state["cost_tracking"]["total_estimated"],
                "actual_total": state["cost_tracking"]["total_actual"],
                "cost_variance": state["cost_tracking"]["total_actual"] - state["cost_tracking"]["total_estimated"]
            },
            "performance_analysis": {
                "total_execution_time": sum(r.get("execution_time", 0) for r in task_results.values()),
                "average_task_time": sum(r.get("execution_time", 0) for r in task_results.values()) / len(task_results) if task_results else 0,
                "fastest_task": min(task_results.items(), key=lambda x: x[1].get("execution_time", float('inf')))[0] if task_results else None,
                "slowest_task": max(task_results.items(), key=lambda x: x[1].get("execution_time", 0))[0] if task_results else None
            },
            "task_details": task_results
        }
        
        # AI-enhanced result analysis
        if len(task_results) > 1:
            enhanced_insights = await self._generate_result_insights(aggregated_results, state)
            aggregated_results["enhanced_insights"] = enhanced_insights
        
        state["aggregated_results"] = aggregated_results
        return state

    async def _generate_result_insights(self, results: Dict[str, Any], state: EnhancedOrchestratorState) -> Dict[str, Any]:
        """Generate AI-enhanced insights from aggregated results"""
        prompt = f"""Analyze these workflow execution results and provide strategic insights.

WORKFLOW RESULTS:
{json.dumps(results, indent=2)}

Provide analysis covering:
1. Performance Optimization Opportunities
2. Cost Efficiency Recommendations
3. Quality Improvement Suggestions
4. Workflow Optimization Ideas
5. Risk Assessment and Mitigation
6. Success Metrics and KPIs
7. Future Workflow Improvements

Return actionable insights with specific recommendations."""
        
        ai_result = await self.call_ai_with_enhanced_control(
            prompt=prompt,
            task_complexity="medium",
            estimated_tokens=800
        )
        
        if ai_result["success"]:
            try:
                return json.loads(ai_result["content"])
            except json.JSONDecodeError:
                return {"insights": ai_result["content"], "parse_error": True}
        
        return {"insights": "AI analysis failed", "fallback": True}

    async def _generate_workflow_insights(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Generate comprehensive workflow insights"""
        logger.info("Generating workflow insights")
        
        # Generate workflow summary
        workflow_summary = {
            "workflow_id": state["workflow_id"],
            "business_id": state["business_id"],
            "execution_mode": state["workflow_config"]["mode"],
            "routing_strategy": state["workflow_config"]["routing_strategy"],
            "total_duration": (datetime.now() - datetime.fromisoformat(state["timestamp"])).total_seconds(),
            "tasks_executed": len(state["completed_tasks"]) + len(state["failed_tasks"]),
            "success_rate": len(state["completed_tasks"]) / len(state["tasks"]) if state["tasks"] else 0,
            "cost_efficiency": state["cost_tracking"]["total_estimated"] / state["cost_tracking"]["total_actual"] if state["cost_tracking"]["total_actual"] > 0 else 1.0
        }
        
        # Performance analysis
        if "aggregated_results" in state:
            performance_analysis = await advanced_analytics._execute(
                analysis_type="regression",
                data=[
                    {
                        "task_type": result.get("agent_type"),
                        "execution_time": result.get("execution_time", 0),
                        "cost": result.get("actual_cost", 0),
                        "success": 1 if result.get("success", False) else 0
                    }
                    for result in state["aggregated_results"]["task_details"].values()
                ],
                target_column="success",
                features=["execution_time", "cost"]
            )
            
            if performance_analysis["success"]:
                workflow_summary["performance_analysis"] = performance_analysis["results"]
        
        state["workflow_insights"] = workflow_summary
        return state

    async def _cleanup_workflow(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Cleanup workflow resources and save metrics"""
        logger.info("Cleaning up workflow resources")
        
        # Save workflow metrics to database
        try:
            workflow_data = {
                "workflow_id": state["workflow_id"],
                "business_id": state["business_id"],
                "config": state["workflow_config"],
                "results": state.get("aggregated_results", {}),
                "insights": state.get("workflow_insights", {}),
                "cost_tracking": state["cost_tracking"],
                "performance_metrics": state.get("performance_metrics", {}),
                "status": "completed" if not state.get("error") else "failed",
                "completed_at": datetime.now().isoformat()
            }
            
            self.supabase.table("workflow_executions_v2").insert(workflow_data).execute()
            
        except Exception as e:
            logger.error(f"Failed to save workflow metrics: {str(e)}")
        
        # Cleanup collaboration sessions
        if "collaboration_sessions" in state:
            for session_id in state["collaboration_sessions"].values():
                # Archive collaboration space
                try:
                    await collaboration_hub._execute(
                        action="archive_space",
                        collaboration_data={"space_id": session_id}
                    )
                except Exception as e:
                    logger.warning(f"Failed to archive collaboration session {session_id}: {str(e)}")
        
        # Stop monitoring
        if "real_time_monitoring" in state:
            monitoring_id = state["real_time_monitoring"].get("monitoring_id")
            if monitoring_id:
                try:
                    await automation_engine._execute(
                        action="stop_monitoring",
                        workflow_config={"monitoring_id": monitoring_id}
                    )
                except Exception as e:
                    logger.warning(f"Failed to stop monitoring {monitoring_id}: {str(e)}")
        
        return state

    # Helper methods
    def _calculate_task_priority(self, agent_type: str, action: str) -> TaskPriority:
        """Calculate task priority based on agent type and action"""
        priority_map = {
            "research": TaskPriority.HIGH,
            "positioning": TaskPriority.HIGH,
            "icp": TaskPriority.CRITICAL,
            "strategy": TaskPriority.HIGH,
            "content": TaskPriority.NORMAL,
            "analytics": TaskPriority.NORMAL
        }
        
        return priority_map.get(agent_type, TaskPriority.NORMAL)

    def _group_tasks_by_dependencies(self, tasks: List[AgentTask]) -> Dict[int, List[AgentTask]]:
        """Group tasks by dependency level"""
        levels = {}
        task_dict = {task.task_id: task for task in tasks}
        
        # Simple dependency leveling - in production would use more sophisticated algorithm
        for task in tasks:
            level = len(task.dependencies)
            if level not in levels:
                levels[level] = []
            levels[level].append(task)
        
        return levels

    def _balance_task_load(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """Balance task load for even distribution"""
        # Simple load balancing - in production would use more sophisticated algorithms
        return sorted(tasks, key=lambda x: (x.estimated_duration, x.estimated_cost))

    async def _apply_routing_optimizations(self, tasks: List[AgentTask], strategy: str) -> List[AgentTask]:
        """Apply routing-specific optimizations"""
        # Apply strategy-specific optimizations
        if strategy == RoutingStrategy.CAPABILITY_MATCH.value:
            # Ensure tasks are ordered by capability requirements
            capability_order = ["research", "positioning", "icp", "strategy", "content", "analytics"]
            return sorted(tasks, key=lambda x: capability_order.index(x.agent_type) if x.agent_type in capability_order else 999)
        
        return tasks

    async def _get_agent_instance(self, agent_type: str):
        """Get agent instance for execution"""
        # This would dynamically import and instantiate agents
        # For now, return a mock agent
        class MockAgent:
            async def run(self, business_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "success": True,
                    "results": {"mock_data": f"Results for {agent_type}"},
                    "performance": {"total_cost": 0.05, "processing_time": 60}
                }
        
        return MockAgent()

    def _validate(self, state: EnhancedOrchestratorState) -> EnhancedOrchestratorState:
        """Validate orchestration results"""
        if state.get('error'):
            return state
        
        # Check if workflow completed successfully
        if not state.get('completed_tasks'):
            state['error'] = "No tasks completed"
            return state
        
        # Check success rate
        success_rate = len(state['completed_tasks']) / len(state['tasks']) if state['tasks'] else 0
        if success_rate < 0.5:  # Less than 50% success rate
            state['error'] = f"Low success rate: {success_rate:.2%}"
            return state
        
        return state

    async def run_workflow(
        self,
        business_id: str,
        context: Dict[str, Any],
        workflow_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a complete workflow"""
        
        # Generate workflow ID
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        
        # Merge configuration
        config = self.workflow_config.__dict__.copy()
        if workflow_config:
            config.update(workflow_config)
        
        # Create initial state
        initial_state = EnhancedOrchestratorState(
            business_id=business_id,
            workflow_id=workflow_id,
            mode=config["mode"],
            routing_strategy=config["routing_strategy"],
            tasks=[],
            completed_tasks=[],
            failed_tasks=[],
            active_tasks={},
            task_results={},
            workflow_config=config,
            real_time_metrics={},
            collaboration_sessions={},
            cost_tracking={},
            performance_metrics={},
            error=None,
            status=AgentStatus.INITIALIZING.value,
            timestamp=datetime.now().isoformat()
        )
        
        # Add context
        initial_state["context"] = context
        
        try:
            final_state = await self.app.ainvoke(initial_state)
            return {
                "success": final_state["status"] == AgentStatus.COMPLETED.value,
                "workflow_id": workflow_id,
                "status": final_state["status"],
                "results": final_state.get("aggregated_results", {}),
                "insights": final_state.get("workflow_insights", {}),
                "error": final_state.get("error"),
                "performance": final_state.get("performance_metrics", {})
            }
        except Exception as e:
            logger.exception(f"Workflow {workflow_id} crashed: {str(e)}")
            return {
                "success": False,
                "workflow_id": workflow_id,
                "status": AgentStatus.FAILED.value,
                "error": str(e),
                "results": {}
            }


# Create enhanced singleton instance
enhanced_orchestrator = EnhancedOrchestratorAgent()

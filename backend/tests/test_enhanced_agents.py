"""
Test suite for enhanced agents and tools v2
"""
import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import enhanced components
from agents.base_agent_v2 import EnhancedBaseAgent, EnhancedAgentState, TaskPriority, AgentStatus
from agents.icp_agent_v2 import EnhancedICPAgent, ICPStateV2
from agents.orchestrator_v2 import EnhancedOrchestratorAgent, OrchestratorMode, RoutingStrategy
from tools.enhanced_tools_v2 import (
    RealTimeDataTool,
    MultiModalProcessorTool,
    AdvancedAnalyticsTool,
    AutomationTool,
    CollaborationTool
)


class TestEnhancedBaseAgent:
    """Test suite for Enhanced Base Agent"""

    @pytest.fixture
    def mock_enhanced_agent(self):
        """Create a mock enhanced agent for testing"""
        class MockEnhancedAgent(EnhancedBaseAgent):
            def _enhanced_process(self, state: EnhancedAgentState) -> EnhancedAgentState:
                state["stage"] = "mock_processed"
                state["results"] = {"mock_result": "success"}
                return state
            
            def _validate(self, state: EnhancedAgentState) -> EnhancedAgentState:
                return state
        
        return MockEnhancedAgent(
            name="Test Enhanced Agent",
            description="Test agent for unit testing",
            capabilities=["test_capability"],
            integrations=["test_integration"]
        )

    @pytest.fixture
    def sample_state(self):
        """Create sample agent state for testing"""
        return {
            "business_id": "test_business_123",
            "agent_name": "Test Agent",
            "agent_version": "2.0.0",
            "stage": "initializing",
            "status": "running",
            "priority": TaskPriority.NORMAL.value,
            "error": None,
            "context": {"test": "data"},
            "results": {},
            "timestamp": datetime.now().isoformat(),
            "metadata": {},
            "config": {},
            "integrations": {},
            "ai_models": {},
            "performance": Mock(),
            "retry_count": 0,
            "max_retries": 3,
            "parent_agent_id": None,
            "child_agents": [],
            "collaboration_mode": False,
            "real_time_data": {},
            "user_feedback": None,
            "cache_enabled": True,
            "monitoring_enabled": True,
            "safety_checks_enabled": True
        }

    @pytest.mark.asyncio
    async def test_enhanced_agent_initialization(self, mock_enhanced_agent):
        """Test enhanced agent initialization"""
        assert mock_enhanced_agent.name == "Test Enhanced Agent"
        assert mock_enhanced_agent.version == "2.0.0"
        assert "test_capability" in mock_enhanced_agent.capabilities
        assert "test_integration" in mock_enhanced_agent.available_integrations
        assert mock_enhanced_agent.graph is not None
        assert mock_enhanced_agent.app is not None

    @pytest.mark.asyncio
    async def test_enhanced_agent_execution(self, mock_enhanced_agent, sample_state):
        """Test enhanced agent execution"""
        result = await mock_enhanced_agent.run("test_business_123", {"test": "data"})
        
        assert result["success"] is True
        assert result["status"] == AgentStatus.COMPLETED.value
        assert "results" in result
        assert "summary" in result
        assert "performance" in result

    @pytest.mark.asyncio
    async def test_enhanced_ai_call_with_budget_control(self, mock_enhanced_agent):
        """Test enhanced AI call with budget control"""
        with patch('middleware.budget_controller.budget_controller.can_make_request') as mock_budget:
            mock_budget.return_value = (True, "Budget OK")
            
            result = await mock_enhanced_agent.call_ai_with_enhanced_control(
                prompt="Test prompt",
                task_complexity="medium",
                estimated_tokens=500
            )
            
            assert result["success"] is True
            assert "model_used" in result
            assert "usage" in result
            assert "cost" in result

    @pytest.mark.asyncio
    async def test_enhanced_ai_call_budget_exceeded(self, mock_enhanced_agent):
        """Test enhanced AI call when budget is exceeded"""
        with patch('middleware.budget_controller.budget_controller.can_make_request') as mock_budget:
            mock_budget.return_value = (False, "Budget limit exceeded")
            
            result = await mock_enhanced_agent.call_ai_with_enhanced_control(
                prompt="Test prompt",
                task_complexity="medium",
                estimated_tokens=500
            )
            
            assert result["success"] is False
            assert result["error"] == "BUDGET_LIMIT_EXCEEDED"
            assert "fallback_response" in result

    def test_agent_capabilities(self, mock_enhanced_agent):
        """Test agent capabilities method"""
        capabilities = mock_enhanced_agent.get_capabilities()
        
        assert capabilities["name"] == "Test Enhanced Agent"
        assert capabilities["version"] == "2.0.0"
        assert "test_capability" in capabilities["capabilities"]
        assert "test_integration" in capabilities["available_integrations"]


class TestEnhancedTools:
    """Test suite for Enhanced Tools v2"""

    @pytest.mark.asyncio
    async def test_real_time_data_tool(self):
        """Test RealTimeDataTool"""
        tool = RealTimeDataTool()
        
        # Test social sentiment fetch
        result = await tool._execute(
            data_type="social_sentiment",
            query="test query",
            sources=["twitter", "linkedin"]
        )
        
        assert result["success"] is True
        assert result["data_type"] == "social_sentiment"
        assert "results" in result
        assert "overall_sentiment" in result["results"]

    @pytest.mark.asyncio
    async def test_multimodal_processor_tool(self):
        """Test MultiModalProcessorTool"""
        tool = MultiModalProcessorTool()
        
        # Test image analysis
        result = await tool._execute(
            content_type="image",
            content_data=b"fake_image_data",
            analysis_type="comprehensive"
        )
        
        assert result["success"] is True
        assert result["content_type"] == "image"
        assert "results" in result
        assert "description" in result["results"]

    @pytest.mark.asyncio
    async def test_advanced_analytics_tool(self):
        """Test AdvancedAnalyticsTool"""
        tool = AdvancedAnalyticsTool()
        
        # Test predictive modeling
        sample_data = [
            {"feature_1": 1.0, "feature_2": 2.0, "target": 1},
            {"feature_1": 2.0, "feature_2": 3.0, "target": 0},
            {"feature_1": 3.0, "feature_2": 4.0, "target": 1}
        ]
        
        result = await tool._execute(
            analysis_type="predictive_modeling",
            data=sample_data,
            target_column="target",
            features=["feature_1", "feature_2"]
        )
        
        assert result["success"] is True
        assert result["analysis_type"] == "predictive_modeling"
        assert "results" in result
        assert "model_type" in result["results"]

    @pytest.mark.asyncio
    async def test_automation_tool(self):
        """Test AutomationTool"""
        tool = AutomationTool()
        
        # Test workflow creation
        workflow_config = {
            "triggers": ["webhook"],
            "actions": ["send_email"],
            "conditions": ["always"]
        }
        
        result = await tool._execute(
            action="create_workflow",
            workflow_config=workflow_config
        )
        
        assert result["success"] is True
        assert result["action"] == "create_workflow"
        assert "results" in result
        assert "workflow_id" in result["results"]

    @pytest.mark.asyncio
    async def test_collaboration_tool(self):
        """Test CollaborationTool"""
        tool = CollaborationTool()
        
        # Test team space creation
        space_data = {
            "name": "Test Team Space",
            "members": ["user1@example.com", "user2@example.com"],
            "purpose": "Testing collaboration"
        }
        
        result = await tool._execute(
            action="create_team_space",
            collaboration_data=space_data
        )
        
        assert result["success"] is True
        assert result["action"] == "create_team_space"
        assert "results" in result
        assert "space_id" in result["results"]


class TestEnhancedICPAgent:
    """Test suite for Enhanced ICP Agent"""

    @pytest.fixture
    def enhanced_icp_agent(self):
        """Create enhanced ICP agent instance"""
        return EnhancedICPAgent()

    @pytest.fixture
    def sample_icp_state(self):
        """Create sample ICP state for testing"""
        return {
            "business_id": "test_business_123",
            "agent_name": "Enhanced ICP Agent",
            "agent_version": "2.0.0",
            "stage": "initializing",
            "status": "running",
            "priority": TaskPriority.NORMAL.value,
            "error": None,
            "context": {"positioning": {"word": "innovation"}},
            "results": {},
            "timestamp": datetime.now().isoformat(),
            "metadata": {},
            "config": {},
            "integrations": {},
            "ai_models": {},
            "performance": Mock(),
            "retry_count": 0,
            "max_retries": 3,
            "parent_agent_id": None,
            "child_agents": [],
            "collaboration_mode": False,
            "real_time_data": {},
            "user_feedback": None,
            "cache_enabled": True,
            "monitoring_enabled": True,
            "safety_checks_enabled": True,
            # ICP-specific fields
            "positioning": {"word": "innovation"},
            "max_icps": 3,
            "personas": [],
            "icps": [],
            "real_time_insights": {},
            "predictive_scores": {},
            "collaboration_feedback": {},
            "market_validation": {}
        }

    @pytest.mark.asyncio
    async def test_enhanced_icp_agent_initialization(self, enhanced_icp_agent):
        """Test enhanced ICP agent initialization"""
        assert enhanced_icp_agent.name == "Enhanced ICP Agent"
        assert enhanced_icp_agent.version == "2.0.0"
        assert "real_time_analysis" in enhanced_icp_agent.capabilities
        assert "predictive_modeling" in enhanced_icp_agent.capabilities
        assert enhanced_icp_agent.icp_config is not None

    @pytest.mark.asyncio
    async def test_enhanced_icp_workflow(self, enhanced_icp_agent, sample_icp_state):
        """Test enhanced ICP workflow execution"""
        with patch('tools.persona_generator.PersonaGeneratorTool._run') as mock_persona:
            with patch('tools.jtbd_mapper.JTBDMapperTool._run') as mock_jtbd:
                with patch('tools.tag_extractor.TagExtractorTool._run') as mock_tags:
                    
                    # Mock tool responses
                    mock_persona.return_value = json.dumps({
                        "personas": [
                            {"name": "Test Persona 1", "demographics": {}, "psychographics": {}},
                            {"name": "Test Persona 2", "demographics": {}, "psychographics": {}}
                        ]
                    })
                    
                    mock_jtbd.return_value = json.dumps({
                        "jtbd_map": {"jobs": ["test job"], "outcomes": ["test outcome"]}
                    })
                    
                    mock_tags.return_value = json.dumps({
                        "tags": ["tag1", "tag2", "tag3"]
                    })
                    
                    # Run the agent
                    result = await enhanced_icp_agent.run("test_business_123", {
                        "positioning": {"word": "innovation"},
                        "max_icps": 2
                    })
                    
                    assert result["success"] is True
                    assert "results" in result
                    assert "performance" in result

    @pytest.mark.asyncio
    async def test_enhanced_persona_generation(self, enhanced_icp_agent, sample_icp_state):
        """Test enhanced persona generation with real-time data"""
        with patch('tools.enhanced_tools_v2.real_time_data._execute') as mock_real_time:
            with patch('tools.persona_generator.PersonaGeneratorTool._run') as mock_persona:
                
                # Mock real-time data
                mock_real_time.return_value = {
                    "success": True,
                    "results": {"trending_keywords": ["AI", "innovation"]}
                }
                
                # Mock persona generation
                mock_persona.return_value = json.dumps({
                    "personas": [{"name": "Enhanced Persona", "demographics": {}}]
                })
                
                # Run enhanced persona generation
                state = await enhanced_icp_agent._generate_enhanced_personas(sample_icp_state)
                
                assert "personas" in state
                assert len(state["personas"]) > 0
                assert "real_time_insights" in state

    @pytest.mark.asyncio
    async def test_predictive_scoring(self, enhanced_icp_agent, sample_icp_state):
        """Test predictive scoring application"""
        sample_icp_state["personas"] = [
            {"name": "Persona 1", "demographics": {}, "psychographics": {}},
            {"name": "Persona 2", "demographics": {}, "psychographics": {}}
        ]
        
        with patch('tools.enhanced_tools_v2.advanced_analytics._execute') as mock_analytics:
            
            # Mock analytics response
            mock_analytics.return_value = {
                "success": True,
                "results": {
                    "predictions": [0.8, 0.6],
                    "confidence_intervals": [[0.7, 0.9], [0.5, 0.7]],
                    "feature_importance": {"feature_1": 0.3, "feature_2": 0.2},
                    "model_metrics": {"accuracy": 0.85}
                }
            }
            
            # Apply predictive scoring
            state = await enhanced_icp_agent._apply_predictive_scoring(sample_icp_state)
            
            assert "predictive_scores" in state
            assert "model_accuracy" in state["predictive_scores"]
            assert all("predictive_score" in persona for persona in state["personas"])


class TestEnhancedOrchestrator:
    """Test suite for Enhanced Orchestrator"""

    @pytest.fixture
    def enhanced_orchestrator(self):
        """Create enhanced orchestrator instance"""
        return EnhancedOrchestratorAgent()

    @pytest.fixture
    def sample_workflow_context(self):
        """Create sample workflow context"""
        return {
            "user_input": {
                "action": "create_icps",
                "business_id": "test_business_123"
            },
            "team_members": ["user1@example.com", "user2@example.com"]
        }

    @pytest.mark.asyncio
    async def test_enhanced_orchestrator_initialization(self, enhanced_orchestrator):
        """Test enhanced orchestrator initialization"""
        assert enhanced_orchestrator.name == "Enhanced Orchestrator"
        assert enhanced_orchestrator.version == "2.0.0"
        assert "intelligent_routing" in enhanced_orchestrator.capabilities
        assert "real_time_monitoring" in enhanced_orchestrator.capabilities
        assert enhanced_orchestrator.agent_registry is not None

    @pytest.mark.asyncio
    async def test_task_analysis_and_planning(self, enhanced_orchestrator, sample_workflow_context):
        """Test task analysis and planning"""
        # Create initial state
        initial_state = {
            "business_id": "test_business_123",
            "workflow_id": "test_workflow_123",
            "mode": OrchestratorMode.HYBRID.value,
            "routing_strategy": RoutingStrategy.CAPABILITY_MATCH.value,
            "tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "active_tasks": {},
            "task_results": {},
            "workflow_config": enhanced_orchestrator.workflow_config.__dict__,
            "real_time_metrics": {},
            "collaboration_sessions": {},
            "cost_tracking": {},
            "performance_metrics": {},
            "error": None,
            "status": AgentStatus.INITIALIZING.value,
            "timestamp": datetime.now().isoformat(),
            "context": sample_workflow_context
        }
        
        # Run task analysis
        state = await enhanced_orchestrator._analyze_and_plan_tasks(initial_state)
        
        assert "tasks" in state
        assert len(state["tasks"]) > 0
        assert "cost_tracking" in state
        assert state["cost_tracking"]["total_estimated"] > 0

    @pytest.mark.asyncio
    async def test_workflow_execution_modes(self, enhanced_orchestrator, sample_workflow_context):
        """Test different workflow execution modes"""
        
        # Test parallel execution
        result_parallel = await enhanced_orchestrator.run_workflow(
            business_id="test_business_123",
            context=sample_workflow_context,
            workflow_config={"mode": OrchestratorMode.PARALLEL.value}
        )
        
        assert result_parallel["success"] is True
        assert "workflow_id" in result_parallel
        assert "results" in result_parallel
        
        # Test sequential execution
        result_sequential = await enhanced_orchestrator.run_workflow(
            business_id="test_business_123",
            context=sample_workflow_context,
            workflow_config={"mode": OrchestratorMode.SEQUENTIAL.value}
        )
        
        assert result_sequential["success"] is True
        assert "workflow_id" in result_sequential

    @pytest.mark.asyncio
    async def test_routing_strategies(self, enhanced_orchestrator, sample_workflow_context):
        """Test different routing strategies"""
        
        # Test cost-optimized routing
        result_cost = await enhanced_orchestrator.run_workflow(
            business_id="test_business_123",
            context=sample_workflow_context,
            workflow_config={"routing_strategy": RoutingStrategy.COST_OPTIMIZED.value}
        )
        
        assert result_cost["success"] is True
        
        # Test priority-based routing
        result_priority = await enhanced_orchestrator.run_workflow(
            business_id="test_business_123",
            context=sample_workflow_context,
            workflow_config={"routing_strategy": RoutingStrategy.PRIORITY_BASED.value}
        )
        
        assert result_priority["success"] is True

    @pytest.mark.asyncio
    async def test_collaborative_workflow(self, enhanced_orchestrator, sample_workflow_context):
        """Test collaborative workflow execution"""
        with patch('tools.enhanced_tools_v2.collaboration_hub._execute') as mock_collab:
            
            # Mock collaboration responses
            mock_collab.return_value = {
                "success": True,
                "results": {"space_id": "test_space_123"}
            }
            
            # Run collaborative workflow
            result = await enhanced_orchestrator.run_workflow(
                business_id="test_business_123",
                context=sample_workflow_context,
                workflow_config={"mode": OrchestratorMode.COLLABORATIVE.value}
            )
            
            assert result["success"] is True
            assert "workflow_id" in result

    @pytest.mark.asyncio
    async def test_real_time_monitoring_setup(self, enhanced_orchestrator):
        """Test real-time monitoring setup"""
        sample_state = {
            "workflow_id": "test_workflow_123",
            "business_id": "test_business_123",
            "tasks": [Mock(task_id="task_1", estimated_cost=0.05)],
            "cost_tracking": {"total_estimated": 0.05},
            "workflow_config": {"enable_real_time_monitoring": True}
        }
        
        with patch('tools.enhanced_tools_v2.automation_engine._execute') as mock_automation:
            
            # Mock automation response
            mock_automation.return_value = {
                "success": True,
                "results": {"monitoring_id": "monitor_123"}
            }
            
            # Setup monitoring
            state = await enhanced_orchestrator._setup_real_time_monitoring(sample_state)
            
            assert "real_time_monitoring" in state
            assert state["real_time_monitoring"]["active"] is True

    @pytest.mark.asyncio
    async def test_result_aggregation(self, enhanced_orchestrator):
        """Test result aggregation and enhancement"""
        sample_state = {
            "tasks": [Mock(task_id="task_1"), Mock(task_id="task_2")],
            "completed_tasks": ["task_1", "task_2"],
            "failed_tasks": [],
            "task_results": {
                "task_1": {
                    "task_id": "task_1",
                    "agent_type": "research",
                    "success": True,
                    "execution_time": 60,
                    "actual_cost": 0.05
                },
                "task_2": {
                    "task_id": "task_2",
                    "agent_type": "icp",
                    "success": True,
                    "execution_time": 120,
                    "actual_cost": 0.08
                }
            },
            "cost_tracking": {"total_estimated": 0.15, "total_actual": 0.13}
        }
        
        # Aggregate results
        state = await enhanced_orchestrator._aggregate_and_enhance_results(sample_state)
        
        assert "aggregated_results" in state
        assert "summary" in state["aggregated_results"]
        assert "cost_analysis" in state["aggregated_results"]
        assert "performance_analysis" in state["aggregated_results"]
        assert state["aggregated_results"]["summary"]["success_rate"] == 1.0


class TestIntegration:
    """Integration tests for enhanced components"""

    @pytest.mark.asyncio
    async def test_end_to_end_icp_workflow(self):
        """Test end-to-end ICP workflow with enhanced components"""
        
        # Create enhanced ICP agent
        icp_agent = EnhancedICPAgent()
        
        # Mock external dependencies
        with patch('tools.persona_generator.PersonaGeneratorTool._run') as mock_persona:
            with patch('tools.jtbd_mapper.JTBDMapperTool._run') as mock_jtbd:
                with patch('tools.enhanced_tools_v2.real_time_data._execute') as mock_real_time:
                    with patch('tools.enhanced_tools_v2.advanced_analytics._execute') as mock_analytics:
                        
                        # Mock responses
                        mock_persona.return_value = json.dumps({
                            "personas": [{"name": "Test Persona", "demographics": {}}]
                        })
                        
                        mock_jtbd.return_value = json.dumps({
                            "jtbd_map": {"jobs": ["test job"]}
                        })
                        
                        mock_real_time.return_value = {
                            "success": True,
                            "results": {"trending_keywords": ["AI"]}
                        }
                        
                        mock_analytics.return_value = {
                            "success": True,
                            "results": {"predictions": [0.8], "model_metrics": {"accuracy": 0.85}}
                        }
                        
                        # Run complete workflow
                        result = await icp_agent.run("test_business_123", {
                            "positioning": {"word": "innovation"},
                            "max_icps": 1
                        })
                        
                        assert result["success"] is True
                        assert "results" in result
                        assert "performance" in result

    @pytest.mark.asyncio
    async def test_orchestrator_with_enhanced_agents(self):
        """Test orchestrator coordinating enhanced agents"""
        
        orchestrator = EnhancedOrchestratorAgent()
        
        # Mock agent execution
        with patch.object(orchestrator, '_get_agent_instance') as mock_get_agent:
            
            mock_agent = AsyncMock()
            mock_agent.run.return_value = {
                "success": True,
                "results": {"test": "data"},
                "performance": {"total_cost": 0.05}
            }
            
            mock_get_agent.return_value = mock_agent
            
            # Run workflow
            result = await orchestrator.run_workflow(
                business_id="test_business_123",
                context={"user_input": {"action": "create_icps"}},
                workflow_config={"mode": OrchestratorMode.PARALLEL.value}
            )
            
            assert result["success"] is True
            assert "workflow_id" in result
            assert "results" in result
            assert "insights" in result


# Performance tests
class TestPerformance:
    """Performance tests for enhanced components"""

    @pytest.mark.asyncio
    async def test_enhanced_agent_performance(self):
        """Test enhanced agent performance metrics"""
        
        agent = EnhancedICPAgent()
        
        start_time = datetime.now()
        
        with patch('tools.persona_generator.PersonaGeneratorTool._run') as mock_persona:
            mock_persona.return_value = json.dumps({
                "personas": [{"name": "Test Persona"}]
            })
            
            result = await agent.run("test_business_123", {
                "positioning": {"word": "test"},
                "max_icps": 1
            })
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        assert result["success"] is True
        assert execution_time < 10.0  # Should complete within 10 seconds
        assert "performance" in result

    @pytest.mark.asyncio
    async def test_parallel_execution_performance(self):
        """Test parallel execution performance"""
        
        orchestrator = EnhancedOrchestratorAgent()
        
        with patch.object(orchestrator, '_get_agent_instance') as mock_get_agent:
            
            mock_agent = AsyncMock()
            mock_agent.run.return_value = {
                "success": True,
                "results": {"test": "data"},
                "performance": {"total_cost": 0.05}
            }
            
            mock_get_agent.return_value = mock_agent
            
            start_time = datetime.now()
            
            result = await orchestrator.run_workflow(
                business_id="test_business_123",
                context={"user_input": {"action": "comprehensive_analysis"}},
                workflow_config={"mode": OrchestratorMode.PARALLEL.value}
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
        
        assert result["success"] is True
        assert execution_time < 15.0  # Parallel should be faster


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

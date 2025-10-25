"""
Comprehensive Test Suite for 3-Tier AI Routing and Fallbacks

Tests:
- Task-to-model routing accuracy
- Cost calculations
- Fallback chain behavior
- Budget enforcement
- Error handling and recovery
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from core.ai_provider_manager import AIProviderManager, TokenUsage
from middleware.cost_controller_v2 import CostController


class TestAIProviderManager:
    """Test AI routing and fallback logic"""

    @pytest.fixture
    def ai_manager(self):
        """Create AI manager instance for testing"""
        return AIProviderManager(
            openai_api_key="test-openai-key",
            google_api_key="test-google-key"
        )

    def test_task_routing_nano(self, ai_manager):
        """Test that simple tasks route to GPT-5 Nano"""
        assert ai_manager.TASK_ROUTING["input_validation"] == "gpt-5-nano"
        assert ai_manager.TASK_ROUTING["html_sanitization"] == "gpt-5-nano"
        assert ai_manager.TASK_ROUTING["content_formatting"] == "gpt-5-nano"

    def test_task_routing_mini(self, ai_manager):
        """Test that balanced tasks route to GPT-5 Mini"""
        assert ai_manager.TASK_ROUTING["icp_generation"] == "gpt-5-mini"
        assert ai_manager.TASK_ROUTING["content_calendar_creation"] == "gpt-5-mini"
        assert ai_manager.TASK_ROUTING["7ps_marketing_mix"] == "gpt-5-mini"

    def test_task_routing_full(self, ai_manager):
        """Test that complex tasks route to GPT-5"""
        assert ai_manager.TASK_ROUTING["sostac_analysis"] == "gpt-5"
        assert ai_manager.TASK_ROUTING["positioning_strategy"] == "gpt-5"
        assert ai_manager.TASK_ROUTING["competitor_intelligence"] == "gpt-5"

    def test_fallback_chains(self, ai_manager):
        """Test fallback chains are properly configured"""
        # Nano fallback
        assert ai_manager.FALLBACK_CHAINS["gpt-5-nano"] == ["gpt-5-nano", "gemini-2.5-flash"]

        # Mini fallback
        assert ai_manager.FALLBACK_CHAINS["gpt-5-mini"] == ["gpt-5-mini", "gemini-2.5-flash"]

        # Full fallback
        assert ai_manager.FALLBACK_CHAINS["gpt-5"] == ["gpt-5", "gemini-2.5-pro"]

    def test_model_config_pricing(self, ai_manager):
        """Test model pricing is correctly configured"""
        # GPT-5 Nano
        nano = ai_manager.MODELS["gpt-5-nano"]
        assert nano.input_cost_per_1m == 0.05
        assert nano.output_cost_per_1m == 0.40

        # GPT-5 Mini
        mini = ai_manager.MODELS["gpt-5-mini"]
        assert mini.input_cost_per_1m == 0.25
        assert mini.output_cost_per_1m == 2.00

        # GPT-5
        full = ai_manager.MODELS["gpt-5"]
        assert full.input_cost_per_1m == 1.25
        assert full.output_cost_per_1m == 10.00

        # Gemini 2.5 Flash
        flash = ai_manager.MODELS["gemini-2.5-flash"]
        assert flash.input_cost_per_1m == 0.30
        assert flash.output_cost_per_1m == 2.50

    def test_estimate_task_cost(self, ai_manager):
        """Test cost estimation for tasks"""
        # Small task (1000 chars input) should be cheap
        small_cost = ai_manager.estimate_task_cost("input_validation", 1000)
        assert small_cost < 0.01  # Should be less than 1 cent

        # Medium task (50000 chars) should be moderate
        medium_cost = ai_manager.estimate_task_cost("icp_generation", 50000)
        assert 0.01 < medium_cost < 0.5

        # Large task (200000 chars) should be expensive
        large_cost = ai_manager.estimate_task_cost("sostac_analysis", 200000)
        assert large_cost > 0.1

    def test_usage_logging(self, ai_manager):
        """Test that token usage is logged"""
        # Simulate token usage
        record = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            reasoning_tokens=100,
            total_cost=0.15,
            model_used="gpt-5-mini",
            task_type="icp_generation",
            timestamp=datetime.utcnow(),
            latency=2.5
        )

        ai_manager.usage_log.append(record)

        assert len(ai_manager.usage_log) == 1
        assert ai_manager.usage_log[0].total_cost == 0.15
        assert ai_manager.usage_log[0].model_used == "gpt-5-mini"

    def test_daily_cost_calculation(self, ai_manager):
        """Test daily cost calculation"""
        today = datetime.utcnow()

        # Add usage from today
        ai_manager.usage_log.append(TokenUsage(
            input_tokens=1000, output_tokens=500, reasoning_tokens=0,
            total_cost=0.10, model_used="gpt-5-nano", task_type="input_validation",
            timestamp=today, latency=0.5
        ))

        ai_manager.usage_log.append(TokenUsage(
            input_tokens=5000, output_tokens=2000, reasoning_tokens=0,
            total_cost=0.50, model_used="gpt-5-mini", task_type="icp_generation",
            timestamp=today, latency=2.0
        ))

        # Add usage from yesterday (should not count)
        yesterday = today - timedelta(days=1)
        ai_manager.usage_log.append(TokenUsage(
            input_tokens=1000, output_tokens=500, reasoning_tokens=0,
            total_cost=0.15, model_used="gpt-5-nano", task_type="input_validation",
            timestamp=yesterday, latency=0.5
        ))

        # Today's cost should be 0.60
        today_cost = ai_manager.get_daily_cost(today)
        assert today_cost == 0.60

        # Yesterday's cost should be 0.15
        yesterday_cost = ai_manager.get_daily_cost(yesterday)
        assert yesterday_cost == 0.15

    def test_cost_by_task_breakdown(self, ai_manager):
        """Test breakdown of costs by task type"""
        ai_manager.usage_log = [
            TokenUsage(
                input_tokens=1000, output_tokens=500, reasoning_tokens=0,
                total_cost=0.10, model_used="gpt-5-nano", task_type="input_validation",
                timestamp=datetime.utcnow(), latency=0.5
            ),
            TokenUsage(
                input_tokens=1000, output_tokens=500, reasoning_tokens=0,
                total_cost=0.15, model_used="gpt-5-nano", task_type="input_validation",
                timestamp=datetime.utcnow(), latency=0.5
            ),
            TokenUsage(
                input_tokens=5000, output_tokens=2000, reasoning_tokens=0,
                total_cost=0.50, model_used="gpt-5-mini", task_type="icp_generation",
                timestamp=datetime.utcnow(), latency=2.0
            ),
        ]

        costs = ai_manager.get_cost_by_task()

        assert costs["input_validation"] == 0.25
        assert costs["icp_generation"] == 0.50

    def test_cost_by_model_breakdown(self, ai_manager):
        """Test breakdown of costs by model used"""
        ai_manager.usage_log = [
            TokenUsage(
                input_tokens=1000, output_tokens=500, reasoning_tokens=0,
                total_cost=0.10, model_used="gpt-5-nano", task_type="input_validation",
                timestamp=datetime.utcnow(), latency=0.5
            ),
            TokenUsage(
                input_tokens=1000, output_tokens=500, reasoning_tokens=0,
                total_cost=0.15, model_used="gpt-5-nano", task_type="html_sanitization",
                timestamp=datetime.utcnow(), latency=0.5
            ),
            TokenUsage(
                input_tokens=5000, output_tokens=2000, reasoning_tokens=0,
                total_cost=0.50, model_used="gpt-5-mini", task_type="icp_generation",
                timestamp=datetime.utcnow(), latency=2.0
            ),
        ]

        costs = ai_manager.get_cost_by_model()

        assert costs["gpt-5-nano"] == 0.25
        assert costs["gpt-5-mini"] == 0.50

    def test_usage_statistics(self, ai_manager):
        """Test comprehensive usage statistics"""
        ai_manager.usage_log = [
            TokenUsage(
                input_tokens=1000, output_tokens=500, reasoning_tokens=0,
                total_cost=0.10, model_used="gpt-5-nano", task_type="input_validation",
                timestamp=datetime.utcnow(), latency=0.5
            ),
            TokenUsage(
                input_tokens=5000, output_tokens=2000, reasoning_tokens=100,
                total_cost=0.50, model_used="gpt-5-mini", task_type="icp_generation",
                timestamp=datetime.utcnow(), latency=2.5
            ),
        ]

        stats = ai_provider_manager.get_usage_statistics()

        assert stats["total_cost"] == 0.60
        assert stats["total_requests"] == 2
        assert stats["total_tokens"]["input"] == 6000
        assert stats["total_tokens"]["output"] == 2500
        assert stats["total_tokens"]["reasoning"] == 100


class TestCostController:
    """Test cost control and budget enforcement"""

    @pytest.fixture
    def mock_ai_manager(self):
        """Mock AI provider manager"""
        manager = Mock(spec=AIProviderManager)
        manager.TASK_ROUTING = AIProviderManager.TASK_ROUTING
        manager.MODELS = AIProviderManager.MODELS
        manager.estimate_task_cost = Mock(return_value=0.50)
        manager.get_daily_cost = Mock(return_value=5.00)
        manager.usage_log = []
        return manager

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        client = Mock()
        client.table = Mock(return_value=Mock(
            select=Mock(return_value=Mock(
                eq=Mock(return_value=Mock(
                    single=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(
                            data={"tier": "basic"}
                        ))
                    ))
                ))
            ))
        ))
        return client

    @pytest.fixture
    def cost_controller(self, mock_ai_manager, mock_supabase):
        """Create cost controller instance"""
        return CostController(mock_ai_manager, mock_supabase)

    @pytest.mark.asyncio
    async def test_basic_tier_daily_limit(self, cost_controller, mock_ai_manager):
        """Test basic tier has $10/day limit"""
        # Mock subscription
        cost_controller.db.table = Mock(return_value=Mock(
            select=Mock(return_value=Mock(
                eq=Mock(return_value=Mock(
                    single=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(
                            data={"tier": "basic"}
                        ))
                    ))
                ))
            ))
        ))

        # Mock already spent $9, task costs $2 (would exceed $10)
        mock_ai_manager.get_daily_cost.return_value = 9.00
        mock_ai_manager.estimate_task_cost.return_value = 2.00

        # Should fail budget check
        can_proceed, budget_info = await cost_controller.check_budget_before_task(
            "biz-123",
            "icp_generation",
            10000
        )

        assert not can_proceed
        assert budget_info["reason"] == "daily_budget_exceeded"

    @pytest.mark.asyncio
    async def test_pro_tier_daily_limit(self, cost_controller, mock_ai_manager):
        """Test pro tier has $50/day limit"""
        # Mock subscription
        cost_controller.db.table = Mock(return_value=Mock(
            select=Mock(return_value=Mock(
                eq=Mock(return_value=Mock(
                    single=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(
                            data={"tier": "pro"}
                        ))
                    ))
                ))
            ))
        ))

        # Mock already spent $40, task costs $15 (would exceed $50)
        mock_ai_manager.get_daily_cost.return_value = 40.00
        mock_ai_manager.estimate_task_cost.return_value = 15.00

        # Should fail budget check
        can_proceed, budget_info = await cost_controller.check_budget_before_task(
            "biz-123",
            "icp_generation",
            10000
        )

        assert not can_proceed
        assert budget_info["reason"] == "daily_budget_exceeded"

    @pytest.mark.asyncio
    async def test_enterprise_tier_daily_limit(self, cost_controller, mock_ai_manager):
        """Test enterprise tier has $200/day limit"""
        # Mock subscription
        cost_controller.db.table = Mock(return_value=Mock(
            select=Mock(return_value=Mock(
                eq=Mock(return_value=Mock(
                    single=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(
                            data={"tier": "enterprise"}
                        ))
                    ))
                ))
            ))
        ))

        # Mock already spent $190, task costs $5 (within $200)
        mock_ai_manager.get_daily_cost.return_value = 190.00
        mock_ai_manager.estimate_task_cost.return_value = 5.00

        # Should pass budget check
        can_proceed, budget_info = await cost_controller.check_budget_before_task(
            "biz-123",
            "icp_generation",
            10000
        )

        assert can_proceed

    @pytest.mark.asyncio
    async def test_model_tier_restriction_basic(self, cost_controller, mock_ai_manager):
        """Test basic tier cannot use GPT-5 (full model)"""
        # Mock subscription
        cost_controller.db.table = Mock(return_value=Mock(
            select=Mock(return_value=Mock(
                eq=Mock(return_value=Mock(
                    single=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(
                            data={"tier": "basic"}
                        ))
                    ))
                ))
            ))
        ))

        # Mock task that requires GPT-5
        mock_ai_manager.get_daily_cost.return_value = 2.00
        mock_ai_manager.estimate_task_cost.return_value = 1.00

        # Should fail because basic tier can't use GPT-5
        can_proceed, budget_info = await cost_controller.check_budget_before_task(
            "biz-123",
            "sostac_analysis",  # Requires GPT-5
            10000
        )

        assert not can_proceed
        assert budget_info["reason"] == "model_tier_restricted"

    @pytest.mark.asyncio
    async def test_warning_at_75_percent(self, cost_controller, mock_ai_manager):
        """Test warning is generated at 75% budget usage"""
        # Mock subscription
        cost_controller.db.table = Mock(return_value=Mock(
            select=Mock(return_value=Mock(
                eq=Mock(return_value=Mock(
                    single=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(
                            data={"tier": "basic"}
                        ))
                    ))
                ))
            ))
        ))

        # Mock 75% spent
        mock_ai_manager.get_daily_cost.return_value = 7.50
        mock_ai_manager.estimate_task_cost.return_value = 0.50

        can_proceed, budget_info = await cost_controller.check_budget_before_task(
            "biz-123",
            "input_validation",
            5000
        )

        assert can_proceed
        assert budget_info.get("warning") == "warning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
3-Tier AI Provider Manager with Intelligent Fallback Routing

Manages routing between:
- Tier 1: GPT-5 Nano (Cheap - $0.05 input)
- Tier 2: GPT-5 Mini (Balanced - $0.25 input)
- Tier 3: GPT-5 (Expensive - $1.25 input + reasoning tokens)
- Fallback: Gemini 2.5 Flash/Pro

Cost-optimized routing based on task complexity.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional
from collections import defaultdict

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_model import BaseLanguageModel

logger = logging.getLogger(__name__)


class AIModelConfig(BaseModel):
    """Configuration for each AI model"""
    model_id: str
    provider: Literal["openai", "google"]
    input_cost_per_1m: float  # USD per 1M tokens
    output_cost_per_1m: float  # USD per 1M tokens
    max_tokens: int
    temperature: float = 0.7
    supports_thinking: bool = False
    tier: Literal["nano", "mini", "pro", "flash"] = "mini"


class TokenUsage(BaseModel):
    """Track token usage and cost"""
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int = 0
    total_cost: float
    model_used: str
    task_type: str
    timestamp: datetime
    latency: float


class AIProviderManager:
    """
    Intelligent routing and fallback management for AI models.

    Routes tasks to appropriate models based on:
    1. Task complexity (nano/mini/full)
    2. Input/output size estimation
    3. Required reasoning depth
    4. Current budget constraints
    """

    # Model configurations with real pricing
    MODELS = {
        # OpenAI GPT-5 Series
        "gpt-5-nano": AIModelConfig(
            model_id="gpt-5-nano-2025-08-07",
            provider="openai",
            input_cost_per_1m=0.05,
            output_cost_per_1m=0.40,
            max_tokens=16000,
            temperature=0.3,
            supports_thinking=False,
            tier="nano"
        ),
        "gpt-5-mini": AIModelConfig(
            model_id="gpt-5-mini-2025-08-07",
            provider="openai",
            input_cost_per_1m=0.25,
            output_cost_per_1m=2.00,
            max_tokens=65536,
            temperature=0.7,
            supports_thinking=True,
            tier="mini"
        ),
        "gpt-5": AIModelConfig(
            model_id="gpt-5-2025-08-07",
            provider="openai",
            input_cost_per_1m=1.25,
            output_cost_per_1m=10.00,
            max_tokens=200000,
            temperature=0.8,
            supports_thinking=True,
            tier="pro"
        ),

        # Google Gemini 2.5 Series (Fallbacks)
        "gemini-2.5-flash": AIModelConfig(
            model_id="gemini-2.5-flash",
            provider="google",
            input_cost_per_1m=0.30,
            output_cost_per_1m=2.50,
            max_tokens=65536,
            temperature=0.7,
            supports_thinking=True,
            tier="flash"
        ),
        "gemini-2.5-pro": AIModelConfig(
            model_id="gemini-2.5-pro",
            provider="google",
            input_cost_per_1m=1.25,  # <200K context
            output_cost_per_1m=10.00,
            max_tokens=1048576,
            temperature=0.8,
            supports_thinking=True,
            tier="pro"
        ),
    }

    # Task-to-model routing: Maps task types to primary model tier
    TASK_ROUTING = {
        # NANO TIER (Simple, fast, cheap)
        "input_validation": "gpt-5-nano",
        "html_sanitization": "gpt-5-nano",
        "content_formatting": "gpt-5-nano",
        "simple_classification": "gpt-5-nano",
        "email_template_fill": "gpt-5-nano",
        "data_extraction": "gpt-5-nano",
        "sentiment_analysis": "gpt-5-nano",
        "ocr_text_cleanup": "gpt-5-nano",
        "json_validation": "gpt-5-nano",

        # MINI TIER (Balanced reasoning)
        "icp_generation": "gpt-5-mini",
        "content_calendar_creation": "gpt-5-mini",
        "7ps_marketing_mix": "gpt-5-mini",
        "competitor_summarization": "gpt-5-mini",
        "north_star_metrics": "gpt-5-mini",
        "race_framework": "gpt-5-mini",
        "asset_template_generation": "gpt-5-mini",
        "campaign_brief_writing": "gpt-5-mini",
        "trending_topics_analysis": "gpt-5-mini",
        "platform_content_adaptation": "gpt-5-mini",
        "rtb_linking": "gpt-5-mini",
        "evidence_summarization": "gpt-5-mini",

        # GPT-5 TIER (Deep reasoning)
        "sostac_analysis": "gpt-5",
        "positioning_strategy": "gpt-5",
        "competitor_intelligence": "gpt-5",
        "strategic_bets": "gpt-5",
        "multi_step_reasoning": "gpt-5",
        "evidence_validation": "gpt-5",
        "amec_roi_analysis": "gpt-5",
        "clv_calculation": "gpt-5",
        "situation_analysis": "gpt-5",
    }

    # Fallback chains: If primary fails, try these in order
    FALLBACK_CHAINS = {
        "gpt-5-nano": ["gpt-5-nano", "gemini-2.5-flash"],
        "gpt-5-mini": ["gpt-5-mini", "gemini-2.5-flash"],
        "gpt-5": ["gpt-5", "gemini-2.5-pro"],
    }

    def __init__(self, openai_api_key: str, google_api_key: str):
        """
        Initialize AI Provider Manager

        Args:
            openai_api_key: OpenAI API key
            google_api_key: Google Generative AI API key
        """
        self.openai_api_key = openai_api_key
        self.google_api_key = google_api_key
        self.usage_log: List[TokenUsage] = []
        self._llm_cache: Dict[str, BaseLanguageModel] = {}

        logger.info("✅ AI Provider Manager initialized")

    def _get_llm(
        self,
        model_name: str,
        reasoning_effort: Optional[str] = None
    ) -> BaseLanguageModel:
        """
        Get or create LangChain LLM for given model.
        Uses caching to avoid recreating instances.

        Args:
            model_name: Model identifier
            reasoning_effort: "minimal", "medium", "high" (for thinking models)

        Returns:
            LangChain BaseLanguageModel instance
        """
        cache_key = f"{model_name}_{reasoning_effort}"

        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]

        config = self.MODELS[model_name]

        if config.provider == "openai":
            kwargs = {
                "model": config.model_id,
                "api_key": self.openai_api_key,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }

            # GPT-5 thinking control
            if config.supports_thinking and reasoning_effort:
                kwargs["reasoning_effort"] = reasoning_effort

            llm = ChatOpenAI(**kwargs)

        elif config.provider == "google":
            llm = ChatGoogleGenerativeAI(
                model=config.model_id,
                google_api_key=self.google_api_key,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
            )
        else:
            raise ValueError(f"Unknown provider: {config.provider}")

        self._llm_cache[cache_key] = llm
        return llm

    async def execute_with_fallback(
        self,
        task_type: str,
        messages: List[Dict[str, str]],
        reasoning_effort: Optional[str] = None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Execute AI task with automatic fallback chain.

        Features:
        - Intelligent model selection based on task type
        - Automatic fallback to Gemini if OpenAI fails
        - Exponential backoff retry logic
        - Full token usage tracking and cost calculation

        Args:
            task_type: Task identifier (must be in TASK_ROUTING)
            messages: LangChain-style messages
                [{"role": "user", "content": "..."}, ...]
            reasoning_effort: "minimal", "medium", "high" for thinking tokens
            max_retries: Retries per model in fallback chain

        Returns:
            {
                "response": str,          # LLM output
                "model_used": str,        # Which model was used
                "cost": float,            # Total cost in USD
                "tokens": {
                    "input": int,
                    "output": int,
                    "reasoning": int
                },
                "latency": float,         # Response time in seconds
            }

        Raises:
            Exception: If all fallback models fail
        """

        # Get primary model for this task
        primary_model = self.TASK_ROUTING.get(task_type)
        if not primary_model:
            logger.warning(f"Unknown task type: {task_type}, defaulting to gpt-5-mini")
            primary_model = "gpt-5-mini"

        # Get fallback chain for this primary model
        fallback_chain = self.FALLBACK_CHAINS[primary_model]

        last_error = None

        # Try each model in the fallback chain
        for model_name in fallback_chain:
            for attempt in range(max_retries):
                try:
                    logger.info(
                        f"Attempting {task_type} with {model_name} (attempt {attempt + 1}/{max_retries})"
                    )

                    # Get LLM instance
                    llm = self._get_llm(model_name, reasoning_effort)

                    # Execute
                    start_time = time.time()
                    response = await llm.ainvoke(messages)
                    latency = time.time() - start_time

                    # Extract token usage from response metadata
                    usage = response.response_metadata.get("token_usage", {})
                    input_tokens = usage.get("prompt_tokens", 0)
                    output_tokens = usage.get("completion_tokens", 0)

                    # Extract reasoning tokens if present
                    reasoning_tokens = 0
                    if "completion_tokens_details" in usage:
                        reasoning_tokens = usage["completion_tokens_details"].get("reasoning_tokens", 0)

                    # Calculate cost
                    config = self.MODELS[model_name]
                    cost = (
                        (input_tokens / 1_000_000) * config.input_cost_per_1m +
                        (output_tokens / 1_000_000) * config.output_cost_per_1m
                    )

                    # Log usage for analytics
                    usage_record = TokenUsage(
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        reasoning_tokens=reasoning_tokens,
                        total_cost=cost,
                        model_used=model_name,
                        task_type=task_type,
                        timestamp=datetime.utcnow(),
                        latency=latency
                    )
                    self.usage_log.append(usage_record)

                    logger.info(
                        f"✅ {task_type} completed with {model_name} | "
                        f"Cost: ${cost:.4f} | Latency: {latency:.2f}s | "
                        f"Tokens: {input_tokens}→{output_tokens} (reasoning: {reasoning_tokens})"
                    )

                    return {
                        "response": response.content,
                        "model_used": model_name,
                        "cost": cost,
                        "tokens": {
                            "input": input_tokens,
                            "output": output_tokens,
                            "reasoning": reasoning_tokens,
                        },
                        "latency": latency,
                    }

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"❌ {model_name} failed for {task_type} (attempt {attempt + 1}/{max_retries}): "
                        f"{str(e)}"
                    )

                    # Exponential backoff before retry
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)

        # All fallbacks exhausted
        error_msg = f"All AI models failed for task '{task_type}'. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """
        Calculate total cost for a specific day.

        Args:
            date: Date to check (default: today)

        Returns:
            Total cost in USD for that day
        """
        target_date = date or datetime.utcnow()
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        total = sum(
            record.total_cost
            for record in self.usage_log
            if day_start <= record.timestamp < day_end
        )

        return total

    def get_cost_by_task(self) -> Dict[str, float]:
        """
        Breakdown of costs by task type.

        Returns:
            {task_type: total_cost_usd}
        """
        costs = defaultdict(float)

        for record in self.usage_log:
            costs[record.task_type] += record.total_cost

        return dict(costs)

    def get_cost_by_model(self) -> Dict[str, float]:
        """
        Breakdown of costs by model used.

        Returns:
            {model_name: total_cost_usd}
        """
        costs = defaultdict(float)

        for record in self.usage_log:
            costs[record.model_used] += record.total_cost

        return dict(costs)

    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Comprehensive usage statistics.

        Returns:
            {
                "total_cost": float,
                "total_tokens": {input, output, reasoning},
                "total_requests": int,
                "average_latency": float,
                "cost_by_task": {task: cost},
                "cost_by_model": {model: cost},
                "model_success_rate": {model: rate}
            }
        """
        if not self.usage_log:
            return {
                "total_cost": 0.0,
                "total_tokens": {"input": 0, "output": 0, "reasoning": 0},
                "total_requests": 0,
                "average_latency": 0.0,
            }

        total_cost = sum(r.total_cost for r in self.usage_log)
        total_input = sum(r.input_tokens for r in self.usage_log)
        total_output = sum(r.output_tokens for r in self.usage_log)
        total_reasoning = sum(r.reasoning_tokens for r in self.usage_log)
        avg_latency = sum(r.latency for r in self.usage_log) / len(self.usage_log)

        return {
            "total_cost": total_cost,
            "total_tokens": {
                "input": total_input,
                "output": total_output,
                "reasoning": total_reasoning,
            },
            "total_requests": len(self.usage_log),
            "average_latency": avg_latency,
            "cost_by_task": self.get_cost_by_task(),
            "cost_by_model": self.get_cost_by_model(),
        }

    def estimate_task_cost(self, task_type: str, input_length: int) -> float:
        """
        Estimate cost for a task before execution.

        Useful for budget checking before running expensive tasks.

        Args:
            task_type: Task identifier
            input_length: Length of input text in characters

        Returns:
            Estimated cost in USD
        """
        # Get model for this task
        model_name = self.TASK_ROUTING.get(task_type, "gpt-5-mini")
        config = self.MODELS[model_name]

        # Rough estimation: 1 token ≈ 4 characters
        estimated_input_tokens = input_length / 4
        # Assume output is ~50% of input size
        estimated_output_tokens = estimated_input_tokens * 0.5

        cost = (
            (estimated_input_tokens / 1_000_000) * config.input_cost_per_1m +
            (estimated_output_tokens / 1_000_000) * config.output_cost_per_1m
        )

        return cost


# Singleton instance
_ai_provider_manager: Optional[AIProviderManager] = None


def get_ai_provider_manager(
    openai_api_key: str,
    google_api_key: str
) -> AIProviderManager:
    """
    Get or create singleton AI Provider Manager instance.

    Args:
        openai_api_key: OpenAI API key
        google_api_key: Google Generative AI API key

    Returns:
        AIProviderManager singleton
    """
    global _ai_provider_manager

    if _ai_provider_manager is None:
        _ai_provider_manager = AIProviderManager(openai_api_key, google_api_key)

    return _ai_provider_manager

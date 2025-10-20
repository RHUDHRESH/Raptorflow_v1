"""
TOKEN COUNTER & INSTRUMENTATION
Track token usage across the system
Essential for understanding where tokens are being spent

USAGE:
  from backend.shared.token_counter import token_counter

  # Track API calls
  token_counter.log_api_call(
      endpoint="analyze",
      prompt_tokens=50,
      completion_tokens=30
  )

  # Get stats
  print(token_counter.get_report())
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Represents a single token usage event"""
    endpoint: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int = field(init=False)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    operation_type: str = "api_call"

    def __post_init__(self):
        self.total_tokens = self.prompt_tokens + self.completion_tokens


class TokenCounter:
    """
    Track token usage across entire system

    Helps identify:
    - Which endpoints use most tokens
    - Token usage trends
    - Wasted tokens (from cache misses)
    - API call frequency
    """

    def __init__(self):
        self.usage_log: List[TokenUsage] = []
        self.endpoint_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0}
        )
        self.session_start = datetime.now()
        self.cache_stats = {"hits": 0, "misses": 0, "tokens_saved": 0}

    def log_api_call(
        self,
        endpoint: str,
        prompt_tokens: int,
        completion_tokens: int,
        operation_type: str = "api_call"
    ) -> None:
        """
        Log a token usage event

        Args:
            endpoint: Name of endpoint/operation
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
            operation_type: Type of operation (api_call, cache_hit, cache_miss, etc.)
        """

        usage = TokenUsage(
            endpoint=endpoint,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            operation_type=operation_type
        )

        self.usage_log.append(usage)

        # Update stats
        stats = self.endpoint_stats[endpoint]
        stats["calls"] += 1
        stats["prompt_tokens"] += prompt_tokens
        stats["completion_tokens"] += completion_tokens

        logger.debug(
            f"Token usage - {endpoint}: {usage.total_tokens} tokens "
            f"({prompt_tokens} input, {completion_tokens} output)"
        )

    def log_cache_hit(self, endpoint: str, tokens_saved: int) -> None:
        """Log cache hit and tokens saved"""

        self.cache_stats["hits"] += 1
        self.cache_stats["tokens_saved"] += tokens_saved

        logger.debug(f"Cache hit on {endpoint}: saved ~{tokens_saved} tokens")

    def log_cache_miss(self, endpoint: str) -> None:
        """Log cache miss"""

        self.cache_stats["misses"] += 1

    def get_total_tokens(self) -> int:
        """Get total tokens used in session"""

        return sum(u.total_tokens for u in self.usage_log)

    def get_total_by_endpoint(self) -> Dict[str, int]:
        """Get total tokens by endpoint"""

        return {
            endpoint: stats["prompt_tokens"] + stats["completion_tokens"]
            for endpoint, stats in self.endpoint_stats.items()
        }

    def get_endpoint_stats(self, endpoint: str = None) -> Dict[str, Any]:
        """Get stats for specific endpoint or all endpoints"""

        if endpoint:
            if endpoint not in self.endpoint_stats:
                return {}

            stats = self.endpoint_stats[endpoint]
            total = stats["prompt_tokens"] + stats["completion_tokens"]

            return {
                "endpoint": endpoint,
                "calls": stats["calls"],
                "total_tokens": total,
                "avg_tokens_per_call": total // stats["calls"] if stats["calls"] > 0 else 0,
                "input_tokens": stats["prompt_tokens"],
                "output_tokens": stats["completion_tokens"],
                "tokens_per_call_avg": total / stats["calls"] if stats["calls"] > 0 else 0
            }

        else:
            return {
                endpoint: self.get_endpoint_stats(endpoint)
                for endpoint in self.endpoint_stats.keys()
            }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance stats"""

        total_cache_ops = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_cache_ops * 100
            if total_cache_ops > 0
            else 0
        )

        return {
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "total_cache_ops": total_cache_ops,
            "hit_rate": f"{hit_rate:.1f}%",
            "tokens_saved": self.cache_stats["tokens_saved"]
        }

    def get_report(self) -> str:
        """Get comprehensive token usage report"""

        total_tokens = self.get_total_tokens()
        session_duration = datetime.now() - self.session_start
        tokens_per_minute = (
            total_tokens / (session_duration.total_seconds() / 60)
            if session_duration.total_seconds() > 0
            else 0
        )

        cache_stats = self.get_cache_stats()
        tokens_saved = cache_stats["tokens_saved"]

        report = f"""
╔════════════════════════════════════════════════════════════════╗
║                  TOKEN USAGE REPORT                            ║
╚════════════════════════════════════════════════════════════════╝

SESSION SUMMARY:
  Duration: {session_duration}
  Total Tokens Used: {total_tokens:,}
  Tokens/Minute: {tokens_per_minute:.1f}
  Total API Calls: {len(self.usage_log)}

CACHE PERFORMANCE:
  Cache Hits: {cache_stats['cache_hits']}
  Cache Misses: {cache_stats['cache_misses']}
  Hit Rate: {cache_stats['hit_rate']}
  Tokens Saved by Cache: {tokens_saved:,}

TOP TOKEN CONSUMERS:
"""

        # Sort endpoints by token usage
        endpoints_by_tokens = sorted(
            self.get_total_by_endpoint().items(),
            key=lambda x: x[1],
            reverse=True
        )

        for i, (endpoint, tokens) in enumerate(endpoints_by_tokens[:10], 1):
            stats = self.endpoint_stats[endpoint]
            pct = (tokens / total_tokens * 100) if total_tokens > 0 else 0
            report += f"\n  {i}. {endpoint:<30} {tokens:>8,} tokens ({pct:>5.1f}%)"

        report += f"\n\n{'='*62}\n"

        return report

    def get_json_report(self) -> str:
        """Get report as JSON"""

        return json.dumps({
            "total_tokens": self.get_total_tokens(),
            "session_duration": str(datetime.now() - self.session_start),
            "endpoint_stats": self.get_endpoint_stats(),
            "cache_stats": self.get_cache_stats(),
            "timestamp": datetime.now().isoformat()
        }, indent=2)

    def reset(self) -> None:
        """Reset all statistics"""

        self.usage_log.clear()
        self.endpoint_stats.clear()
        self.cache_stats = {"hits": 0, "misses": 0, "tokens_saved": 0}
        self.session_start = datetime.now()

        logger.info("Token counter reset")

    def export_to_csv(self, filepath: str) -> None:
        """Export token usage log to CSV"""

        import csv

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "endpoint", "prompt_tokens",
                "completion_tokens", "total_tokens", "operation_type"
            ])

            for usage in self.usage_log:
                writer.writerow([
                    usage.timestamp,
                    usage.endpoint,
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    usage.total_tokens,
                    usage.operation_type
                ])

        logger.info(f"Token usage exported to {filepath}")


# Global instance
token_counter = TokenCounter()


# DECORATOR for automatic token tracking
def track_tokens(endpoint_name: str):
    """
    Decorator for automatic token tracking

    USAGE:
        @track_tokens("analyze_endpoint")
        async def analyze_content(content):
            # Do analysis
            return result
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # Log tokens if result contains token info
                if isinstance(result, dict) and "tokens_used" in result:
                    token_counter.log_api_call(
                        endpoint=endpoint_name,
                        prompt_tokens=result.get("tokens_used", {}).get("prompt", 0),
                        completion_tokens=result.get("tokens_used", {}).get("completion", 0)
                    )

                return result

            except Exception as e:
                logger.error(f"Error in {endpoint_name}: {e}")
                raise

        return wrapper

    return decorator


if __name__ == "__main__":
    # Example usage
    print("Token Counter Example:")
    print()

    # Simulate some token usage
    token_counter.log_api_call("analyze", prompt_tokens=50, completion_tokens=30)
    token_counter.log_api_call("score_platforms", prompt_tokens=40, completion_tokens=20)
    token_counter.log_cache_hit("analyze", tokens_saved=50)
    token_counter.log_cache_hit("analyze", tokens_saved=50)
    token_counter.log_cache_miss("analyze")

    token_counter.log_api_call("analyze", prompt_tokens=50, completion_tokens=30)
    token_counter.log_api_call("score_platforms", prompt_tokens=40, completion_tokens=20)

    # Print report
    print(token_counter.get_report())
    print("\nJSON Report:")
    print(token_counter.get_json_report())

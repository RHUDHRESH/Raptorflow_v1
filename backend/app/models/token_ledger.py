"""Token Usage Ledger Models for tracking API usage and costs"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class TokenLedger(Base):
    """Token usage ledger entry for tracking API calls and costs"""

    __tablename__ = "token_ledger"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    workspace_id = Column(String, nullable=True, index=True)
    strategy_id = Column(String, nullable=True, index=True)

    # Token tracking
    tokens_used = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)

    # Agent info
    agent_name = Column(String, nullable=True)
    request_type = Column(String, nullable=True)  # analysis_submission, agent_call, etc

    # Cache info
    cached = Column(Boolean, nullable=False, default=False)

    # Metadata
    metadata = Column(JSONB, nullable=False, default={})

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TokenLedger {self.user_id} - {self.tokens_used} tokens - ${self.cost_usd}>"


class BudgetAlert(Base):
    """Budget alert/notification for users"""

    __tablename__ = "budget_alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)

    # Alert details
    alert_type = Column(String, nullable=False)  # warning, exceeded, threshold
    threshold_percentage = Column(Integer, nullable=False)  # 50, 75, 90, 100

    # Status
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)

    # Message
    message = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, nullable=False, default={})

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BudgetAlert {self.user_id} - {self.alert_type} at {self.threshold_percentage}%>"


class PricingTierSelection(Base):
    """Track pricing tier selections for dev/testing"""

    __tablename__ = "pricing_tier_selections"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, unique=True, index=True)

    # Tier selection
    current_tier = Column(String, nullable=False, default="basic")  # basic, pro, enterprise
    tier_limits = Column(JSONB, nullable=False, default={})

    # Timestamps
    selected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PricingTierSelection {self.user_id} - {self.current_tier}>"


class ApiUsageStats(Base):
    """Aggregated API usage statistics for analytics"""

    __tablename__ = "api_usage_stats"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)

    # Time period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String, nullable=False)  # daily, weekly, monthly

    # Aggregated metrics
    total_tokens = Column(Integer, nullable=False, default=0)
    total_cost_usd = Column(Float, nullable=False, default=0.0)
    total_requests = Column(Integer, nullable=False, default=0)
    cache_hits = Column(Integer, nullable=False, default=0)

    # Agent breakdown
    agent_breakdown = Column(JSONB, nullable=False, default={})  # {agent_name: {tokens, cost}}

    # Status
    is_complete = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ApiUsageStats {self.user_id} - {self.period_type} - {self.total_tokens} tokens>"

"""Import all models for Alembic migrations."""

from app.db.session import Base

# Import all models here so Alembic can detect them
from app.models.user import User, Organization, Membership, Workspace
from app.models.billing import Plan, Subscription, Payment, LedgerEntry, Invoice
from app.models.threat_intel import (
    Project,
    Indicator,
    ThreatActor,
    Campaign,
    Vulnerability,
    ThreatReport,
)

# TODO: Import when these models are created
# from app.models.api_key import APIKey
# from app.models.audit import AuditLog, APIUsageLog

__all__ = [
    "Base",
    "User",
    "Organization",
    "Membership",
    "Workspace",
    "Plan",
    "Subscription",
    "Payment",
    "LedgerEntry",
    "Invoice",
    "Project",
    "Indicator",
    "ThreatActor",
    "Campaign",
    "Vulnerability",
    "ThreatReport",
    # "APIKey",
    # "AuditLog",
    # "APIUsageLog",
]

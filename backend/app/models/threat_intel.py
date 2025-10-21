"""Threat intelligence domain models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Project(Base):
    """
    Threat intelligence project.

    A project is a container for organizing threat intelligence work.
    It groups related indicators, threat actors, campaigns, and vulnerabilities.
    """

    __tablename__ = "projects"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=list, server_default="{}")
    settings = Column(JSONB, default=dict, server_default="{}")
    archived = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    indicators = relationship("Indicator", back_populates="project", cascade="all, delete-orphan")
    threat_actors = relationship("ThreatActor", back_populates="project", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="project", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="project", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        {"comment": "Threat intelligence projects for organizing research"},
    )


class Indicator(Base):
    """
    Indicator of Compromise (IOC).

    Represents observables that may indicate malicious activity.
    Supports various types: IP, domain, URL, hash, email, etc.
    """

    __tablename__ = "indicators"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Indicator details
    type = Column(String(50), nullable=False)  # ip, domain, url, hash, email, etc.
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    # Classification
    classification = Column(String(50), nullable=True)  # malicious, suspicious, benign, unknown
    confidence = Column(Integer, nullable=True)  # 0-100
    severity = Column(String(20), nullable=True)  # critical, high, medium, low, info

    # Attribution
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(200), nullable=True)

    # Metadata
    tags = Column(ARRAY(String), default=list, server_default="{}")
    mitre_tactics = Column(ARRAY(String), default=list, server_default="{}")
    mitre_techniques = Column(ARRAY(String), default=list, server_default="{}")

    # Enrichment data (from external APIs)
    enrichment = Column(JSONB, default=dict, server_default="{}")

    # Relationships
    related_campaigns = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")
    related_threat_actors = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")

    # Status
    active = Column(Boolean, default=True, nullable=False)
    false_positive = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="indicators")

    __table_args__ = (
        {"comment": "Indicators of Compromise (IOCs)"},
    )


class ThreatActor(Base):
    """
    Threat actor (individual or group).

    Represents known adversaries tracked in threat intelligence.
    Can be APT groups, cybercrime organizations, nation-states, etc.
    """

    __tablename__ = "threat_actors"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Identity
    name = Column(String(200), nullable=False)
    aliases = Column(ARRAY(String), default=list, server_default="{}")
    description = Column(Text, nullable=True)

    # Classification
    type = Column(String(50), nullable=True)  # apt, cybercrime, nation-state, hacktivist, insider
    sophistication = Column(String(50), nullable=True)  # advanced, intermediate, beginner

    # Attribution
    origin_country = Column(String(2), nullable=True)  # ISO country code
    motivation = Column(ARRAY(String), default=list, server_default="{}")  # financial, espionage, sabotage, etc.

    # Activity
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # TTPs (Tactics, Techniques, Procedures)
    mitre_tactics = Column(ARRAY(String), default=list, server_default="{}")
    mitre_techniques = Column(ARRAY(String), default=list, server_default="{}")
    tools = Column(ARRAY(String), default=list, server_default="{}")

    # Targeting
    target_sectors = Column(ARRAY(String), default=list, server_default="{}")
    target_countries = Column(ARRAY(String), default=list, server_default="{}")

    # Metadata
    tags = Column(ARRAY(String), default=list, server_default="{}")
    references = Column(ARRAY(String), default=list, server_default="{}")  # URLs to reports

    # Status
    active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="threat_actors")
    campaigns = relationship("Campaign", back_populates="threat_actor")

    __table_args__ = (
        {"comment": "Threat actors (APTs, cybercrime groups, etc.)"},
    )


class Campaign(Base):
    """
    Threat campaign.

    Represents a coordinated series of attacks or operations by a threat actor.
    Links together related indicators, targets, and tactics.
    """

    __tablename__ = "campaigns"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    threat_actor_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("threat_actors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Identity
    name = Column(String(200), nullable=False)
    aliases = Column(ARRAY(String), default=list, server_default="{}")
    description = Column(Text, nullable=True)

    # Timeline
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # Objectives
    objectives = Column(ARRAY(String), default=list, server_default="{}")  # espionage, disruption, theft, etc.

    # TTPs
    mitre_tactics = Column(ARRAY(String), default=list, server_default="{}")
    mitre_techniques = Column(ARRAY(String), default=list, server_default="{}")

    # Targeting
    target_sectors = Column(ARRAY(String), default=list, server_default="{}")
    target_countries = Column(ARRAY(String), default=list, server_default="{}")

    # Associated indicators
    indicator_ids = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")

    # Metadata
    tags = Column(ARRAY(String), default=list, server_default="{}")
    references = Column(ARRAY(String), default=list, server_default="{}")

    # Status
    active = Column(Boolean, default=True, nullable=False)
    severity = Column(String(20), nullable=True)  # critical, high, medium, low

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="campaigns")
    threat_actor = relationship("ThreatActor", back_populates="campaigns")

    __table_args__ = (
        {"comment": "Threat campaigns (coordinated attack series)"},
    )


class Vulnerability(Base):
    """
    Vulnerability (CVE, 0-day, etc.).

    Tracks vulnerabilities relevant to threat intelligence work.
    Can be linked to campaigns, threat actors, and exploited systems.
    """

    __tablename__ = "vulnerabilities"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Identity
    cve_id = Column(String(50), nullable=True, unique=True)  # CVE-2024-12345
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Classification
    cvss_score = Column(Integer, nullable=True)  # 0-10 (stored as 0-100 for precision)
    severity = Column(String(20), nullable=True)  # critical, high, medium, low

    # Affected systems
    affected_products = Column(ARRAY(String), default=list, server_default="{}")
    affected_versions = Column(ARRAY(String), default=list, server_default="{}")

    # Exploit information
    exploit_available = Column(Boolean, default=False, nullable=False)
    exploited_in_wild = Column(Boolean, default=False, nullable=False)
    exploit_references = Column(ARRAY(String), default=list, server_default="{}")

    # Remediation
    patch_available = Column(Boolean, default=False, nullable=False)
    patch_references = Column(ARRAY(String), default=list, server_default="{}")
    workarounds = Column(Text, nullable=True)

    # Timeline
    published_date = Column(DateTime(timezone=True), nullable=True)
    discovered_date = Column(DateTime(timezone=True), nullable=True)

    # Attribution
    related_campaigns = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")
    related_threat_actors = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")

    # Metadata
    tags = Column(ARRAY(String), default=list, server_default="{}")
    references = Column(ARRAY(String), default=list, server_default="{}")

    # Enrichment data (NVD, vendor advisories, etc.)
    enrichment = Column(JSONB, default=dict, server_default="{}")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="vulnerabilities")

    __table_args__ = (
        {"comment": "Vulnerabilities (CVEs, 0-days)"},
    )


class ThreatReport(Base):
    """
    Threat intelligence report.

    Structured report combining indicators, threat actors, campaigns, and analysis.
    Can be exported in various formats (PDF, STIX, JSON).
    """

    __tablename__ = "threat_reports"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Identity
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # Markdown format

    # Classification
    classification = Column(String(50), default="internal", nullable=False)  # public, tlp_white, tlp_green, tlp_amber, tlp_red, internal
    severity = Column(String(20), nullable=True)  # critical, high, medium, low, info

    # Associated entities
    indicator_ids = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")
    threat_actor_ids = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")
    campaign_ids = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")
    vulnerability_ids = Column(ARRAY(PGUUID(as_uuid=True)), default=list, server_default="{}")

    # Metadata
    tags = Column(ARRAY(String), default=list, server_default="{}")
    references = Column(ARRAY(String), default=list, server_default="{}")

    # Publishing
    published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        {"comment": "Threat intelligence reports"},
    )

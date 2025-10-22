"""Strategy Workspace data models for RaptorFlow 2.0"""
from sqlalchemy import Column, String, Text, Integer, Float, JSON, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

Base = declarative_base()


class ContextItemType(str, enum.Enum):
    """Types of context items"""
    TEXT = "text"
    FILE_IMAGE = "file_image"
    FILE_PDF = "file_pdf"
    FILE_VIDEO = "file_video"
    FILE_AUDIO = "file_audio"
    URL = "url"


class ContextSource(str, enum.Enum):
    """Sources for context items"""
    USER_INPUT = "user_input"
    UPLOADED_FILE = "uploaded_file"
    WEB_LINK = "web_link"
    TRANSCRIPTION = "transcription"


class MoodType(str, enum.Enum):
    """Mood indicators for ICPs"""
    THRIVING = "thriving"
    NEUTRAL = "neutral"
    AT_RISK = "at_risk"


class ContextItem(Base):
    """Context item in the strategy workspace"""
    __tablename__ = "strategy_context_items"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("strategy_workspaces.id"), nullable=False)
    item_type = Column(SQLEnum(ContextItemType), nullable=False)
    source = Column(SQLEnum(ContextSource), nullable=False)
    raw_content = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=True)
    transcribed_text = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    url = Column(String, nullable=True)

    # NLP Analysis
    topics = Column(JSON, nullable=True)  # List[str]
    entities = Column(JSON, nullable=True)  # List[str]
    keywords = Column(JSON, nullable=True)  # List[str]
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    emotions = Column(JSON, nullable=True)  # List[str]

    # Metadata
    metadata = Column(JSON, nullable=True)  # Custom metadata
    tagged_jtbd_ids = Column(JSON, nullable=True)  # List of JTBD IDs linked to this context

    # Embeddings
    embedding = Column(JSON, nullable=True)  # Vector embedding for similarity search

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class JTBD(Base):
    """Jobs-to-be-done extracted from context"""
    __tablename__ = "strategy_jtbds"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("strategy_workspaces.id"), nullable=False)

    # Core JTBD Definition
    why = Column(Text, nullable=False)  # The job statement
    circumstances = Column(Text, nullable=False)  # When/where the job occurs
    forces = Column(Text, nullable=False)  # Drivers and pushes toward the job
    anxieties = Column(Text, nullable=False)  # Worries and pulls against the job

    # Evidence tracking
    evidence_citations = Column(JSON, nullable=True)  # List of context item IDs that support this JTBD

    # Metadata
    confidence_score = Column(Float, default=0.8)  # 0-1 confidence in extraction
    status = Column(String, default="extracted")  # extracted, reviewed, locked
    user_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ICP(Base):
    """Ideal Customer Profile extracted from context and jobs"""
    __tablename__ = "strategy_icps"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("strategy_workspaces.id"), nullable=False)

    # Identity
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    avatar_color = Column(String, nullable=True)  # Hex color
    avatar_type = Column(String, nullable=True)  # icon, icon_letter, frame

    # Characteristics
    traits = Column(JSON, nullable=True)  # Dict of trait: value pairs
    pain_points = Column(JSON, nullable=True)  # List[str]
    behaviors = Column(JSON, nullable=True)  # List[str]

    # Health metrics
    health_score = Column(Float, default=0.5)  # 0-1 based on receipt outcomes
    mood = Column(SQLEnum(MoodType), default=MoodType.NEUTRAL)  # Health indicator

    # Confidence
    confidence_score = Column(Float, default=0.8)  # 0-1 confidence in ICP creation
    evidence_citations = Column(JSON, nullable=True)  # List of context item IDs that support this ICP

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Channel(Base):
    """Marketing channel recommendation in AISAS matrix"""
    __tablename__ = "strategy_channels"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("strategy_workspaces.id"), nullable=False)
    icp_id = Column(String, ForeignKey("strategy_icps.id"), nullable=False)
    jtbd_id = Column(String, ForeignKey("strategy_jtbds.id"), nullable=False)

    # Channel info
    channel_name = Column(String, nullable=False)  # YouTube, LinkedIn, Instagram, etc.
    content_type = Column(String, nullable=True)  # Hero, Hub, Help

    # AISAS stage positioning (0-100 scale)
    aisas_stage = Column(Float, nullable=False)  # 0=Attention, 100=Share
    # Breakdown of AISAS
    aisas_attention = Column(Float, default=0)  # 0-100
    aisas_interest = Column(Float, default=0)   # 0-100
    aisas_search = Column(Float, default=0)     # 0-100
    aisas_action = Column(Float, default=0)     # 0-100
    aisas_share = Column(Float, default=0)      # 0-100

    # Platform specifications
    cadence = Column(String, nullable=True)  # posting frequency
    posting_times = Column(JSON, nullable=True)  # List[str] of optimal times
    content_length = Column(String, nullable=True)  # typical post length
    tone = Column(String, nullable=True)  # tone of voice

    # Recommendation info
    confidence_score = Column(Float, default=0.8)
    reasoning = Column(Text, nullable=True)  # Why this channel was recommended

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Citation(Base):
    """Evidence citation linking explanations to context"""
    __tablename__ = "strategy_citations"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("strategy_workspaces.id"), nullable=False)
    context_item_id = Column(String, ForeignKey("strategy_context_items.id"), nullable=False)

    # What this citation is for
    entity_type = Column(String, nullable=False)  # jtbd, icp, channel
    entity_id = Column(String, nullable=False)

    # Citation details
    quote = Column(Text, nullable=True)  # The specific text being cited
    start_offset = Column(Integer, nullable=True)  # Character offset in source
    end_offset = Column(Integer, nullable=True)
    relevance_score = Column(Float, default=0.8)  # How relevant is this citation

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Explanation(Base):
    """Explanation with evidence for strategic decisions"""
    __tablename__ = "strategy_explanations"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("strategy_workspaces.id"), nullable=False)

    # What this explains
    entity_type = Column(String, nullable=False)  # jtbd, icp, channel, aisas
    entity_id = Column(String, nullable=False)

    # Explanation content
    title = Column(String, nullable=False)
    rationale = Column(Text, nullable=False)  # The explanation
    explanation_type = Column(String, nullable=True)  # wisdom_rule, platform_spec, context_ref, confidence

    # Evidence
    citation_ids = Column(JSON, nullable=True)  # List of Citation IDs
    evidence_summary = Column(Text, nullable=True)

    # Metadata
    confidence_score = Column(Float, default=0.8)
    is_pinned = Column(Boolean, default=False)
    user_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Strategy(Base):
    """Strategy workspace container"""
    __tablename__ = "strategy_workspaces"

    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)

    # Metadata
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Status tracking
    status = Column(String, default="context_intake")  # context_intake, analyzing, ready_for_moves

    # Settings
    settings = Column(JSON, nullable=True)  # Custom workspace settings

    # Analysis state
    context_processed = Column(Boolean, default=False)
    jtbds_extracted = Column(Boolean, default=False)
    icps_built = Column(Boolean, default=False)
    channels_mapped = Column(Boolean, default=False)
    explanations_generated = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Pydantic models for API requests/responses

class ContextItemRequest(BaseModel):
    """Request to add context item"""
    item_type: ContextItemType
    content: str  # Raw content (text, URL, or file path)
    metadata: Optional[Dict[str, Any]] = None


class ContextItemResponse(BaseModel):
    """Response with processed context item"""
    id: str
    item_type: ContextItemType
    source: ContextSource
    extracted_text: Optional[str]
    topics: Optional[List[str]]
    entities: Optional[List[str]]
    keywords: Optional[List[str]]
    sentiment: Optional[str]
    created_at: datetime


class JTBDRequest(BaseModel):
    """Request to create/update JTBD"""
    why: str
    circumstances: str
    forces: str
    anxieties: str


class JTBDResponse(BaseModel):
    """Response with JTBD"""
    id: str
    why: str
    circumstances: str
    forces: str
    anxieties: str
    confidence_score: float
    evidence_citations: Optional[List[str]]
    status: str


class ICPRequest(BaseModel):
    """Request to create/update ICP"""
    name: str
    traits: Optional[Dict[str, str]] = None
    pain_points: Optional[List[str]] = None
    behaviors: Optional[List[str]] = None


class ICPResponse(BaseModel):
    """Response with ICP"""
    id: str
    name: str
    avatar_url: Optional[str]
    avatar_color: Optional[str]
    traits: Optional[Dict[str, str]]
    pain_points: Optional[List[str]]
    behaviors: Optional[List[str]]
    health_score: float
    mood: MoodType
    confidence_score: float


class ChannelRequest(BaseModel):
    """Request to create/update channel"""
    icp_id: str
    jtbd_id: str
    channel_name: str
    aisas_stage: float
    content_type: Optional[str] = None


class ChannelResponse(BaseModel):
    """Response with channel recommendation"""
    id: str
    channel_name: str
    aisas_stage: float
    content_type: Optional[str]
    cadence: Optional[str]
    tone: Optional[str]
    confidence_score: float
    reasoning: Optional[str]


class ExplanationResponse(BaseModel):
    """Response with explanation"""
    id: str
    entity_type: str
    entity_id: str
    title: str
    rationale: str
    explanation_type: Optional[str]
    confidence_score: float
    citation_ids: Optional[List[str]]


class StrategyResponse(BaseModel):
    """Response with complete strategy workspace"""
    id: str
    business_id: str
    name: Optional[str]
    status: str
    context_items: Optional[List[ContextItemResponse]]
    jtbds: Optional[List[JTBDResponse]]
    icps: Optional[List[ICPResponse]]
    channels: Optional[List[ChannelResponse]]
    explanations: Optional[List[ExplanationResponse]]
    created_at: datetime
    updated_at: datetime

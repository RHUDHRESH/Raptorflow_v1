"""User, Organization, and Membership models."""

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class Role(enum.IntEnum):
    """User role hierarchy."""

    VIEWER = 1
    EDITOR = 2
    ADMIN = 3
    OWNER = 4


class User(Base):
    """Local user profile linked to external auth (Supabase)."""

    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    auth_sub = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    display_name = Column(String)
    avatar_url = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    created_projects = relationship("Project", back_populates="creator")
    api_keys = relationship("APIKey", back_populates="creator")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Organization(Base):
    """Top-level tenant and billing entity."""

    __tablename__ = "organizations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    billing_email = Column(String)
    website = Column(String)
    industry = Column(String)
    size = Column(String)  # startup, small, medium, enterprise
    logo_url = Column(String)
    settings = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    memberships = relationship("Membership", back_populates="organization", cascade="all, delete-orphan")
    workspaces = relationship("Workspace", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="organization", uselist=False)
    payments = relationship("Payment", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"


class Membership(Base):
    """User-to-organization relationship with role."""

    __tablename__ = "memberships"

    org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(Enum(Role), nullable=False)
    invited_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    invited_at = Column(DateTime)
    accepted_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    organization = relationship("Organization", back_populates="memberships")
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self) -> str:
        return f"<Membership {self.user_id} -> {self.org_id} ({self.role.name})>"


class Workspace(Base):
    """Optional sub-grouping within organizations."""

    __tablename__ = "workspaces"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="workspaces")
    projects = relationship("Project", back_populates="workspace")

    def __repr__(self) -> str:
        return f"<Workspace {self.name}>"

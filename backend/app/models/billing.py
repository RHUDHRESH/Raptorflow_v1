"""Billing models: Plans, Subscriptions, Payments, Ledger."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class Plan(Base):
    """Subscription plan/tier."""

    __tablename__ = "plans"

    id = Column(String, primary_key=True)  # free, pro, enterprise
    name = Column(String, nullable=False)
    description = Column(Text)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="INR")
    billing_period = Column(String, nullable=False)  # monthly, yearly

    # Rate limits
    api_requests_per_month = Column(Integer, nullable=False)
    ai_tokens_per_month = Column(Integer, nullable=False)

    # Features
    features = Column(JSONB, nullable=False, default={})

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self) -> str:
        return f"<Plan {self.id} - {self.name}>"


class Subscription(Base):
    """Organization subscription to a plan."""

    __tablename__ = "subscriptions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    plan_id = Column(String, ForeignKey("plans.id"), nullable=False)
    status = Column(String, nullable=False)  # trialing, active, past_due, canceled

    # Trial
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)

    # Billing period
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)

    # Usage tracking
    api_requests_used = Column(Integer, nullable=False, default=0)
    ai_tokens_used = Column(Integer, nullable=False, default=0)

    # Cancellation
    cancel_at_period_end = Column(Boolean, nullable=False, default=False)
    canceled_at = Column(DateTime)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")

    def __repr__(self) -> str:
        return f"<Subscription {self.id} - {self.plan_id} ({self.status})>"


class Payment(Base):
    """Payment transaction from Razorpay."""

    __tablename__ = "payments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(PGUUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"))

    # Razorpay details
    provider = Column(String, nullable=False, default="razorpay")
    provider_payment_id = Column(String, unique=True, index=True)
    provider_order_id = Column(String, nullable=False)

    # Amount
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="INR")

    # Status
    status = Column(String, nullable=False)  # pending, captured, refunded, failed

    # Payment method
    method = Column(String)  # card, upi, netbanking, wallet

    # Metadata
    description = Column(Text)
    meta = Column(JSONB, nullable=False, default={})

    # Timestamps
    captured_at = Column(DateTime)
    refunded_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment {self.id} - {self.amount_cents/100} {self.currency} ({self.status})>"


class LedgerEntry(Base):
    """Double-entry accounting ledger."""

    __tablename__ = "ledger_entries"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    # Transaction
    entry_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    account = Column(String, nullable=False, index=True)  # cash, ar, revenue, refunds
    direction = Column(String, nullable=False)  # DR or CR

    # Amount
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="INR")

    # Reference
    ref_type = Column(String)  # payment, refund, credit
    ref_id = Column(String)
    description = Column(Text)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<LedgerEntry {self.account} {self.direction} {self.amount_cents/100}>"


class Invoice(Base):
    """Generated invoice for payment."""

    __tablename__ = "invoices"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(PGUUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"))

    # Invoice details
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    issued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_at = Column(DateTime)

    # Amounts
    subtotal_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, nullable=False, default=0)  # GST 18%
    total_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="INR")

    # Status
    status = Column(String, nullable=False)  # draft, issued, paid, void
    paid_at = Column(DateTime)

    # PDF
    pdf_url = Column(String)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number} - {self.total_cents/100} {self.currency}>"

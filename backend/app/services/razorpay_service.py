"""Razorpay payment service."""

import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import razorpay
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.billing import Payment, Subscription, LedgerEntry
from app.crud.organization import get_organization


class RazorpayService:
    """Service for Razorpay payment operations."""

    def __init__(self):
        """Initialize Razorpay client."""
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    def create_order(
        self,
        amount_cents: int,
        currency: str,
        receipt: str,
        notes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create Razorpay order.

        Args:
            amount_cents: Amount in smallest currency unit (paise for INR)
            currency: Currency code (INR, USD, etc.)
            receipt: Unique receipt ID
            notes: Optional metadata

        Returns:
            Razorpay order object
        """
        return self.client.order.create(
            {
                "amount": amount_cents,
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {},
            }
        )

    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> bool:
        """
        Verify Razorpay payment signature.

        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Signature from Razorpay

        Returns:
            True if valid, False otherwise
        """
        try:
            self.client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                }
            )
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str) -> bool:
        """
        Verify Razorpay webhook signature.

        Args:
            body: Raw request body (bytes)
            signature: X-Razorpay-Signature header

        Returns:
            True if valid, False otherwise
        """
        expected = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def create_payment_record(
        self,
        db: AsyncSession,
        org_id: UUID,
        order_id: str,
        amount_cents: int,
        currency: str,
        subscription_id: UUID | None = None,
    ) -> Payment:
        """
        Create payment record in database.

        Args:
            db: Database session
            org_id: Organization ID
            order_id: Razorpay order ID
            amount_cents: Amount in smallest currency unit
            currency: Currency code
            subscription_id: Optional subscription ID

        Returns:
            Created payment record
        """
        payment = Payment(
            org_id=org_id,
            subscription_id=subscription_id,
            provider_order_id=order_id,
            amount_cents=amount_cents,
            currency=currency,
            status="pending",
        )
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment

    async def capture_payment(
        self,
        db: AsyncSession,
        payment: Payment,
        provider_payment_id: str,
        method: str | None = None,
    ) -> Payment:
        """
        Mark payment as captured and create ledger entries.

        Args:
            db: Database session
            payment: Payment record
            provider_payment_id: Razorpay payment ID
            method: Payment method used

        Returns:
            Updated payment record
        """
        # Update payment
        payment.provider_payment_id = provider_payment_id
        payment.status = "captured"
        payment.captured_at = datetime.utcnow()
        payment.method = method

        # Create ledger entries (double-entry)
        await self.create_ledger_entries(
            db,
            org_id=payment.org_id,
            amount_cents=payment.amount_cents,
            currency=payment.currency,
            ref_type="payment",
            ref_id=str(payment.id),
            description=f"Payment captured: {provider_payment_id}",
        )

        # Update subscription if linked
        if payment.subscription_id:
            subscription = await db.get(Subscription, payment.subscription_id)
            if subscription:
                subscription.status = "active"
                subscription.current_period_start = datetime.utcnow()
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)

        await db.commit()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def create_ledger_entries(
        db: AsyncSession,
        org_id: UUID,
        amount_cents: int,
        currency: str,
        ref_type: str,
        ref_id: str,
        description: str | None = None,
        created_by: UUID | None = None,
    ) -> list[LedgerEntry]:
        """
        Create double-entry ledger entries.

        For payment capture:
        - DR cash (increase)
        - CR revenue (increase)

        Args:
            db: Database session
            org_id: Organization ID
            amount_cents: Amount in smallest currency unit
            currency: Currency code
            ref_type: Reference type (payment, refund, etc.)
            ref_id: Reference ID
            description: Optional description
            created_by: Optional user who created entry

        Returns:
            List of created ledger entries
        """
        entries = [
            # Debit cash account
            LedgerEntry(
                org_id=org_id,
                account="cash",
                direction="DR",
                amount_cents=amount_cents,
                currency=currency,
                ref_type=ref_type,
                ref_id=ref_id,
                description=description,
                created_by=created_by,
            ),
            # Credit revenue account
            LedgerEntry(
                org_id=org_id,
                account="revenue",
                direction="CR",
                amount_cents=amount_cents,
                currency=currency,
                ref_type=ref_type,
                ref_id=ref_id,
                description=description,
                created_by=created_by,
            ),
        ]

        for entry in entries:
            db.add(entry)

        await db.commit()
        return entries

    async def refund_payment(
        self,
        db: AsyncSession,
        payment: Payment,
        amount_cents: int | None = None,
    ) -> Payment:
        """
        Process payment refund.

        Args:
            db: Database session
            payment: Payment to refund
            amount_cents: Amount to refund (None = full refund)

        Returns:
            Updated payment record
        """
        refund_amount = amount_cents or payment.amount_cents

        # Call Razorpay API to refund
        self.client.payment.refund(payment.provider_payment_id, {"amount": refund_amount})

        # Update payment status
        payment.status = "refunded"
        payment.refunded_at = datetime.utcnow()

        # Create ledger entries for refund
        await self.create_ledger_entries(
            db,
            org_id=payment.org_id,
            amount_cents=refund_amount,
            currency=payment.currency,
            ref_type="refund",
            ref_id=str(payment.id),
            description=f"Refund for payment: {payment.provider_payment_id}",
        )

        await db.commit()
        await db.refresh(payment)
        return payment


# Global service instance
razorpay_service = RazorpayService()

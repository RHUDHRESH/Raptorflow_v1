"""Payment endpoints for Razorpay integration."""

import json
import time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_with_org, require_role
from app.db.session import get_db
from app.models.billing import Payment, Plan, Subscription
from app.schemas.auth import Principal
from app.services.razorpay_service import razorpay_service

router = APIRouter(prefix="/payments", tags=["payments"])


class CreateOrderRequest(BaseModel):
    """Request to create payment order."""

    plan_id: str


class CreateOrderResponse(BaseModel):
    """Response with Razorpay order details."""

    order_id: str
    amount: int
    currency: str
    key: str


class VerifyPaymentRequest(BaseModel):
    """Request to verify payment after user completes it."""

    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_payment_order(
    request: CreateOrderRequest,
    principal: Principal = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Razorpay order for subscription payment.

    Only organization owners can initiate payments.
    """
    # Get plan
    plan = await db.get(Plan, request.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Check if org already has active subscription
    result = await db.execute(
        select(Subscription).filter(
            Subscription.org_id == principal.org_id,
            Subscription.status.in_(["active", "trialing"]),
        )
    )
    existing_subscription = result.scalar_one_or_none()
    if existing_subscription:
        raise HTTPException(
            status_code=400,
            detail="Organization already has an active subscription",
        )

    # Create Razorpay order
    receipt = f"sub_{principal.org_id}_{int(time.time())}"
    razorpay_order = razorpay_service.create_order(
        amount_cents=plan.price_cents,
        currency=plan.currency,
        receipt=receipt,
        notes={
            "org_id": str(principal.org_id),
            "plan_id": plan.id,
            "user_id": str(principal.user_id),
        },
    )

    # Create payment record
    payment = await razorpay_service.create_payment_record(
        db,
        org_id=principal.org_id,
        order_id=razorpay_order["id"],
        amount_cents=plan.price_cents,
        currency=plan.currency,
    )

    # Return order details for frontend
    from app.core.config import settings

    return CreateOrderResponse(
        order_id=razorpay_order["id"],
        amount=plan.price_cents,
        currency=plan.currency,
        key=settings.RAZORPAY_KEY_ID,
    )


@router.post("/verify")
async def verify_payment(
    request: VerifyPaymentRequest,
    principal: Principal = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify payment signature after user completes payment.

    This is called from frontend after Razorpay checkout completes.
    """
    # Verify signature
    is_valid = razorpay_service.verify_payment_signature(
        order_id=request.razorpay_order_id,
        payment_id=request.razorpay_payment_id,
        signature=request.razorpay_signature,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature",
        )

    # Get payment record
    result = await db.execute(
        select(Payment).filter(Payment.provider_order_id == request.razorpay_order_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Verify org ownership
    if payment.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Mark as captured (webhook will also do this, but frontend verification is faster)
    if payment.status == "pending":
        await razorpay_service.capture_payment(
            db,
            payment,
            provider_payment_id=request.razorpay_payment_id,
        )

    return {"status": "success", "payment_id": str(payment.id)}


@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(..., alias="X-Razorpay-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Razorpay webhook events.

    This is called by Razorpay when payment events occur.
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify webhook signature
    is_valid = razorpay_service.verify_webhook_signature(body, x_razorpay_signature)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    # Parse event
    event = json.loads(body)
    event_type = event.get("event")
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    payment_id = payment_entity.get("id")

    if not payment_id:
        return {"status": "ok"}  # Ignore non-payment events

    # Check idempotency (prevent duplicate processing)
    from app.core.redis import redis_client

    idempotency_key = f"webhook:razorpay:{payment_id}"
    if await redis_client.exists(idempotency_key):
        return {"status": "ok"}  # Already processed
    await redis_client.setex(idempotency_key, 3600, "1")  # Lock for 1 hour

    # Get payment record
    result = await db.execute(
        select(Payment).filter(Payment.provider_payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        # Payment not in our system yet (shouldn't happen)
        return {"status": "ok"}

    # Handle event
    if event_type == "payment.captured":
        if payment.status == "pending":
            await razorpay_service.capture_payment(
                db,
                payment,
                provider_payment_id=payment_id,
                method=payment_entity.get("method"),
            )

    elif event_type == "payment.failed":
        payment.status = "failed"
        await db.commit()

    # TODO: Enqueue background jobs:
    # - Generate invoice
    # - Send payment confirmation email
    # - Update analytics

    return {"status": "ok"}


@router.get("/history")
async def get_payment_history(
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """Get payment history for organization."""
    result = await db.execute(
        select(Payment)
        .filter(Payment.org_id == principal.org_id)
        .order_by(Payment.created_at.desc())
        .limit(50)
    )
    payments = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "amount": p.amount_cents / 100,
            "currency": p.currency,
            "status": p.status,
            "method": p.method,
            "created_at": p.created_at.isoformat(),
            "captured_at": p.captured_at.isoformat() if p.captured_at else None,
        }
        for p in payments
    ]

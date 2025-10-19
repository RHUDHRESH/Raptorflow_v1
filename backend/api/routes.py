"""
API Routes - Clean FastAPI endpoints for frontend consumption
"""
import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import json

from api.client import api_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["raptorflow"])

# ==================== REQUEST MODELS ====================


class IntakeRequest(BaseModel):
    """Business intake form data"""
    name: str
    industry: str
    location: str
    description: str
    goals: str


class PositioningSelectionRequest(BaseModel):
    """Positioning option selection"""
    option_index: int


class ICPGenerationRequest(BaseModel):
    """ICP generation request"""
    max_icps: Optional[int] = 3


class PaymentRequest(BaseModel):
    """Payment/subscription request"""
    tier: str  # basic, pro, enterprise
    business_id: str


class PerformanceMetricsRequest(BaseModel):
    """Performance metrics submission"""
    move_id: str
    metrics: dict


# ==================== INTAKE ENDPOINTS ====================


@router.post("/intake")
async def intake_business(request: IntakeRequest):
    """Create new business"""
    try:
        result = await api_client.intake_business(
            name=request.name,
            industry=request.industry,
            location=request.location,
            description=request.description,
            goals=request.goals
        )

        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))

    except Exception as e:
        logger.exception(f"Intake failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business/{business_id}")
async def get_business(business_id: str):
    """Get business details"""
    try:
        result = await api_client.get_business(business_id)
        if result.get("success"):
            return result["data"]
        else:
            raise HTTPException(status_code=404, detail="Business not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription/{business_id}")
async def get_subscription(business_id: str):
    """Get subscription tier"""
    try:
        result = await api_client.get_subscription(business_id)
        if result.get("success"):
            return result["data"]
        else:
            raise HTTPException(status_code=404, detail="Subscription not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RESEARCH ENDPOINTS ====================


@router.websocket("/research/{business_id}")
async def research_websocket(websocket: WebSocket, business_id: str):
    """Research analysis with WebSocket streaming"""
    await websocket.accept()

    try:
        async for update in api_client.run_research(business_id):
            await websocket.send_json(update)
    except Exception as e:
        logger.exception(f"Research WebSocket error: {str(e)}")
        await websocket.send_json({
            "stage": "error",
            "status": "failed",
            "error": str(e)
        })
    finally:
        await websocket.close()


@router.get("/research/{business_id}")
async def get_research(business_id: str):
    """Get research results"""
    try:
        result = await api_client.get_research_data(business_id)
        if result.get("success"):
            return result["data"]
        else:
            raise HTTPException(status_code=404, detail="Research not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== POSITIONING ENDPOINTS ====================


@router.websocket("/positioning/{business_id}")
async def positioning_websocket(websocket: WebSocket, business_id: str):
    """Positioning analysis with WebSocket streaming"""
    await websocket.accept()

    try:
        async for update in api_client.generate_positioning(business_id):
            await websocket.send_json(update)
    except Exception as e:
        logger.exception(f"Positioning WebSocket error: {str(e)}")
        await websocket.send_json({
            "stage": "error",
            "status": "failed",
            "error": str(e)
        })
    finally:
        await websocket.close()


@router.get("/positioning/{business_id}")
async def get_positioning(business_id: str):
    """Get positioning analysis"""
    try:
        result = await api_client.get_positioning(business_id)
        if result.get("success"):
            return result["data"]
        else:
            raise HTTPException(status_code=404, detail="Positioning not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/positioning/{business_id}/select")
async def select_positioning(business_id: str, request: PositioningSelectionRequest):
    """Select a positioning option"""
    try:
        result = await api_client.select_positioning(business_id, request.option_index)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ICP ENDPOINTS ====================


@router.websocket("/icps/{business_id}")
async def icps_websocket(websocket: WebSocket, business_id: str):
    """ICP generation with WebSocket streaming"""
    await websocket.accept()

    try:
        async for update in api_client.generate_icps(business_id):
            await websocket.send_json(update)
    except Exception as e:
        logger.exception(f"ICP WebSocket error: {str(e)}")
        await websocket.send_json({
            "stage": "error",
            "status": "failed",
            "error": str(e)
        })
    finally:
        await websocket.close()


@router.get("/icps/{business_id}")
async def get_icps(business_id: str):
    """Get all ICPs"""
    try:
        result = await api_client.get_icps(business_id)
        if result.get("success"):
            return {"icps": result["data"]}
        else:
            raise HTTPException(status_code=404, detail="ICPs not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PAYMENT ENDPOINTS ====================


@router.post("/payment/checkout")
async def create_checkout(request: PaymentRequest):
    """Create Razorpay checkout"""
    try:
        from utils.razorpay_client import get_razorpay_client
        import os

        razorpay = get_razorpay_client()

        pricing = {
            'basic': 2000,
            'pro': 3500,
            'enterprise': 5000
        }

        amount = pricing.get(request.tier, 2000) * 100

        order = razorpay.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'business_id': request.business_id,
                'tier': request.tier
            }
        })

        return {
            "success": True,
            "order_id": order['id'],
            "amount": amount,
            "currency": "INR",
            "key_id": os.getenv('RAZORPAY_KEY_ID')
        }

    except Exception as e:
        logger.exception(f"Checkout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment/webhook")
async def payment_webhook(payload: dict):
    """Handle Razorpay webhook"""
    try:
        from utils.supabase_client import get_supabase_client

        event = payload.get('event')

        if event == 'payment.captured':
            payment = payload['payload']['payment']['entity']
            notes = payment['notes']

            tier = notes['tier']
            max_icps = {'basic': 3, 'pro': 6, 'enterprise': 9}[tier]

            supabase = get_supabase_client()
            supabase.table('subscriptions').update({
                'tier': tier,
                'max_icps': max_icps,
                'status': 'active',
                'razorpay_subscription_id': payment['id']
            }).eq('business_id', notes['business_id']).execute()

            return {"success": True}

        return {"success": True}

    except Exception as e:
        logger.exception(f"Webhook failed: {str(e)}")
        return {"success": False, "error": str(e)}


# ==================== HEALTH CHECK ====================


@router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": str(__import__('datetime').datetime.now())
    }

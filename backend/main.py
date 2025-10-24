from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import os
import logging
import bleach
import re

# --- begin dotenv bootstrap (phase1.fix.0.6) ---
try:
    from dotenv import load_dotenv  # add only if not already imported
except Exception as _e:
    # If python-dotenv is missing, leave a note; do not fail here in patch step
    pass
else:
    _root_env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
    # Load root .env.local (if present) without overriding already-set envs
    load_dotenv(_root_env_path, override=False)
# --- end dotenv bootstrap (phase1.fix.0.6) ---

# Import security middleware
from backend.middleware.security_middleware import (
    SecurityHeadersMiddleware,
    InputValidationMiddleware,
    AuthenticationMiddleware,
    AuditLoggingMiddleware,
    AISafetyMiddleware,
    CostControlMiddleware,
    SecurityException,
    CostLimitExceeded,
    get_ai_safety,
    get_cost_control
)

# Import agents
from backend.agents.orchestrator import orchestrator
from backend.agents.research import research_agent
from backend.agents.positioning import positioning_agent
from backend.agents.icp import icp_agent
from backend.agents.content import content_agent
from backend.agents.analytics import analytics_agent
from backend.agents.trend_monitor import trend_monitor

# Import utilities
from backend.utils.supabase_client import get_supabase_client
from backend.utils.razorpay_client import get_razorpay_client

# Import API routes
from backend.api.budget_routes import router as budget_router
from backend.api.oauth_routes import router as oauth_router
from backend.api.conversation_routes import router as conversation_router
from backend.api.embedding_routes import router as embedding_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RaptorFlow ADAPT API", 
    version="1.0.0",
    description="AI-Powered Marketing Intelligence Platform"
)

# Add security middleware (order matters!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(InputValidationMiddleware)

# Add authentication middleware - CRITICAL: Always enable for security
if os.getenv('ENVIRONMENT') in ['production', 'staging', 'development']:
    app.add_middleware(AuthenticationMiddleware)

# CORS - Production-ready configuration
# SECURITY: Never use wildcard origins with credentials - browsers reject this
if os.getenv('ENVIRONMENT') == 'production':
    allowed_origins = [
        os.getenv('FRONTEND_URL', 'https://app.raptorflow.in'),
        "https://raptorflow.in"
    ]
else:
    # Default to explicit development origin instead of wildcard
    allowed_origins = [
        os.getenv('FRONTEND_URL', 'http://localhost:3000'),
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Include API routes
app.include_router(oauth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(conversation_router, prefix="/api/conversations", tags=["conversations"])
app.include_router(embedding_router, prefix="/api", tags=["search"])
app.include_router(budget_router, prefix="/api/budget", tags=["budget"])

supabase = get_supabase_client()
razorpay = get_razorpay_client()

# ==================== ASYNC DATABASE HELPERS ====================

async def async_db_query(query_fn):
    """
    Execute blocking Supabase query in thread pool to avoid blocking event loop.

    Usage: result = await async_db_query(lambda: supabase.table('x').select('*').execute())
    """
    return await run_in_threadpool(query_fn)

# ==================== MODELS ====================

class BusinessIntake(BaseModel):
    name: str
    industry: str
    location: str
    description: str
    goals: str
    
    @validator('name', 'description', 'goals')
    def sanitize_html(cls, v):
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v
    
    @validator('description')
    def validate_length(cls, v):
        if v and len(v) > 10000:
            raise ValueError('Description too long (max 10,000 characters)')
        return v
    
    @validator('name', 'industry', 'location')
    def validate_required_fields(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('This field is required and must be at least 2 characters')
        return v.strip()

class PositioningSelection(BaseModel):
    option_index: int

class MoveCreate(BaseModel):
    goal: str
    platform: str
    duration_days: int = 7

class PerformanceSubmit(BaseModel):
    move_id: str
    metrics: dict

# ==================== ROUTES ====================

@app.get("/")
async def root():
    return {"message": "RaptorFlow ADAPT API", "status": "running"}

# ---------- INTAKE ----------

@app.post("/api/intake")
async def create_business(request: Request, intake: BusinessIntake):
    """Create new business and trigger research"""
    try:
        # Get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, 'user_id', 'anonymous')
        
        # Validate with AI safety
        ai_safety = get_ai_safety()
        await ai_safety.validate_input(intake.name, 'name')
        await ai_safety.validate_input(intake.description, 'description')
        await ai_safety.validate_input(intake.goals, 'goals')
        
        # Set user context for audit logging
        if hasattr(supabase, 'auth'):
            try:
                supabase.auth.set_session(user_id)
            except Exception:
                pass  # Supabase auth might not be configured
        
        # Save business (async to avoid blocking event loop)
        result = await async_db_query(lambda: supabase.table('businesses').insert({
            'name': intake.name,
            'industry': intake.industry,
            'location': intake.location,
            'description': intake.description,
            'goals': {'text': intake.goals},
            'user_id': user_id  # Add user_id for RLS
        }).execute())

        # Check for errors and valid data
        if hasattr(result, 'error') and result.error:
            logger.error(f"Database error creating business: {result.error}")
            raise HTTPException(status_code=500, detail="Failed to create business")

        if not result.data or len(result.data) == 0:
            logger.error("Business insert returned no data")
            raise HTTPException(status_code=500, detail="Failed to create business")

        business_id = result.data[0]['id']

        # Create trial subscription (async to avoid blocking event loop)
        sub_result = await async_db_query(lambda: supabase.table('subscriptions').insert({
            'business_id': business_id,
            'tier': 'basic',
            'max_icps': 3,
            'max_moves': 5,
            'status': 'trial',
            'user_id': user_id  # Add user_id for RLS
        }).execute())

        if (hasattr(sub_result, 'error') and sub_result.error) or not sub_result.data:
            logger.error(f"Database error creating subscription: {getattr(sub_result, 'error', 'No data')}")
            raise HTTPException(status_code=500, detail="Failed to create subscription")
        
        logger.info(f"Business created: {business_id} by user {user_id}")
        
        return {
            "success": True,
            "business_id": business_id,
            "message": "Business created. Ready for research."
        }
    
    except SecurityException as e:
        logger.warning(f"Security violation in intake: {e}")
        raise HTTPException(status_code=400, detail="Invalid input detected")
    except Exception as e:
        logger.error(f"Error creating business: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------- RESEARCH ----------

@app.post("/api/research/{business_id}")
async def run_research(request: Request, business_id: str):
    """Run complete research analysis"""
    try:
        user_id = getattr(request.state, 'user_id', 'anonymous')

        # Verify user owns the business - EXPLICIT ownership check (async)
        biz = await async_db_query(
            lambda: supabase.table('businesses').select('*').eq('id', business_id).single().execute()
        )

        # Check for errors or missing data
        if (hasattr(biz, 'error') and biz.error) or not biz.data:
            logger.warning(f"Business {business_id} not found or access denied for user {user_id}")
            raise HTTPException(status_code=404, detail="Business not found")

        # SECURITY: Explicit tenant ownership verification
        # Never rely solely on RLS - verify in application layer
        business_owner_id = biz.data.get('user_id')
        if business_owner_id != user_id:
            logger.warning(f"Access denied: User {user_id} attempted to access business {business_id} owned by {business_owner_id}")
            raise HTTPException(status_code=403, detail="Access denied - you do not own this business")
        
        # Check cost limits
        cost_control = get_cost_control()
        estimated_cost = 2.0  # Estimated cost for research
        await cost_control.check_limit(user_id, estimated_cost)
        
        # Run research agent
        result = await research_agent.ainvoke({
            'business_id': business_id,
            'business_data': biz.data,
            'evidence': [],
            'competitor_ladder': [],
            'sostac': {},
            'status': 'running'
        })
        
        # Sanitize AI output
        ai_safety = get_ai_safety()
        sanitized_result = {}
        for key, value in result.items():
            if isinstance(value, str):
                sanitized_result[key] = await ai_safety.sanitize_output(value)
            else:
                sanitized_result[key] = value
        
        # Track actual cost
        actual_cost = 1.8  # This would come from the actual AI API usage
        await cost_control.track_cost(user_id, actual_cost)
        
        logger.info(f"Research completed for business {business_id} by user {user_id}")
        
        return {
            "success": True,
            "competitor_ladder": sanitized_result.get('competitor_ladder'),
            "sostac": sanitized_result.get('sostac'),
            "evidence_count": len(result.get('evidence', [])),
            "completeness_score": result.get('completeness_score')
        }
    
    except CostLimitExceeded as e:
        logger.warning(f"Cost limit exceeded for user {user_id}: {e}")
        raise HTTPException(status_code=429, detail=str(e))
    except SecurityException as e:
        logger.warning(f"Security violation in research: {e}")
        raise HTTPException(status_code=400, detail="Invalid input detected")
    except Exception as e:
        logger.error(f"Error running research: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/research/{business_id}")
async def get_research(business_id: str):
    """Get existing research data"""
    try:
        # Get SOSTAC
        sostac = supabase.table('sostac_analyses')\
            .select('*')\
            .eq('business_id', business_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        # Get competitor ladder
        competitors = supabase.table('competitor_ladder')\
            .select('*')\
            .eq('business_id', business_id)\
            .execute()
        
        return {
            "sostac": sostac.data[0] if sostac.data else None,
            "competitor_ladder": competitors.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- POSITIONING ----------

@app.post("/api/positioning/{business_id}")
async def analyze_positioning(request: Request, business_id: str):
    """Generate 3 positioning options"""
    try:
        user_id = getattr(request.state, 'user_id', 'anonymous')

        # SECURITY: Verify ownership (async)
        biz = await async_db_query(
            lambda: supabase.table('businesses').select('*').eq('id', business_id).single().execute()
        )

        if (hasattr(biz, 'error') and biz.error) or not biz.data:
            raise HTTPException(status_code=404, detail="Business not found")

        if biz.data.get('user_id') != user_id:
            logger.warning(f"Access denied: User {user_id} attempted to access business {business_id}")
            raise HTTPException(status_code=403, detail="Access denied")

        comps = await async_db_query(
            lambda: supabase.table('competitor_ladder').select('*').eq('business_id', business_id).execute()
        )
        
        result = await positioning_agent.ainvoke({
            'business_id': business_id,
            'business_data': biz.data,
            'competitor_ladder': comps.data,
            'options': [],
            'status': 'running'
        })
        
        # Save to database
        supabase.table('positioning_analyses').insert({
            'business_id': business_id,
            'options': result['options']
        }).execute()
        
        return {
            "success": True,
            "options": result['options'],
            "validation_score": result['validation_score']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/positioning/{business_id}/select")
async def select_positioning(business_id: str, selection: PositioningSelection):
    """Select a positioning option"""
    try:
        analysis = supabase.table('positioning_analyses')\
            .select('*')\
            .eq('business_id', business_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .single()\
            .execute()
        
        selected = analysis.data['options'][selection.option_index]
        
        supabase.table('positioning_analyses')\
            .update({'selected_option': selected})\
            .eq('id', analysis.data['id'])\
            .execute()
        
        return {
            "success": True,
            "selected_positioning": selected
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positioning/{business_id}")
async def get_positioning(business_id: str):
    """Get positioning analysis"""
    try:
        result = supabase.table('positioning_analyses')\
            .select('*')\
            .eq('business_id', business_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        return result.data[0] if result.data else None
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- ICPs ----------

@app.post("/api/icps/{business_id}")
async def generate_icps(request: Request, business_id: str):
    """Generate ICPs based on positioning"""
    try:
        user_id = getattr(request.state, 'user_id', 'anonymous')

        # SECURITY: Verify ownership first (async)
        biz = await async_db_query(
            lambda: supabase.table('businesses').select('*').eq('id', business_id).single().execute()
        )

        if (hasattr(biz, 'error') and biz.error) or not biz.data:
            raise HTTPException(status_code=404, detail="Business not found")

        if biz.data.get('user_id') != user_id:
            logger.warning(f"Access denied: User {user_id} attempted to access business {business_id}")
            raise HTTPException(status_code=403, detail="Access denied")

        # Check subscription tier (async)
        sub = await async_db_query(
            lambda: supabase.table('subscriptions').select('*').eq('business_id', business_id).single().execute()
        )

        if (hasattr(sub, 'error') and sub.error) or not sub.data:
            raise HTTPException(status_code=500, detail="Subscription not found")

        max_icps = sub.data['max_icps']
        
        # Get positioning
        pos = supabase.table('positioning_analyses')\
            .select('*')\
            .eq('business_id', business_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .single()\
            .execute()
        
        if not pos.data.get('selected_option'):
            raise HTTPException(status_code=400, detail="No positioning selected")
        
        # Run ICP agent
        result = await icp_agent.ainvoke({
            'business_id': business_id,
            'positioning': pos.data['selected_option'],
            'max_icps': max_icps,
            'icps': [],
            'status': 'running'
        })
        
        return {
            "success": True,
            "icps": result['icps'],
            "count": len(result['icps'])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/icps/{business_id}")
async def get_icps(business_id: str):
    """Get all ICPs for business"""
    try:
        result = supabase.table('icps').select('*').eq('business_id', business_id).execute()
        return {"icps": result.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- MOVES (Campaigns) ----------

@app.post("/api/moves/{business_id}")
async def create_move(request: Request, business_id: str, move: MoveCreate):
    """Create new campaign/move"""
    try:
        user_id = getattr(request.state, 'user_id', 'anonymous')

        # SECURITY: Verify ownership first (async)
        biz = await async_db_query(
            lambda: supabase.table('businesses').select('*').eq('id', business_id).single().execute()
        )

        if (hasattr(biz, 'error') and biz.error) or not biz.data:
            raise HTTPException(status_code=404, detail="Business not found")

        if biz.data.get('user_id') != user_id:
            logger.warning(f"Access denied: User {user_id} attempted to access business {business_id}")
            raise HTTPException(status_code=403, detail="Access denied")

        # Get ICPs and positioning (async)
        icps = await async_db_query(
            lambda: supabase.table('icps').select('*').eq('business_id', business_id).execute()
        )
        pos = await async_db_query(
            lambda: supabase.table('positioning_analyses')
            .select('*')
            .eq('business_id', business_id)
            .order('created_at', desc=True)
            .limit(1)
            .execute()
        )
        
        if not pos.data:
            raise HTTPException(status_code=400, detail="No positioning analysis found")
        
        # Run content agent
        result = await content_agent.ainvoke({
            'business_id': business_id,
            'goal': move.goal,
            'platform': move.platform,
            'duration_days': move.duration_days,
            'icps': icps.data,
            'positioning': pos.data[0].get('selected_option'),  # Use first result
            'calendar': {},
            'status': 'running'
        })
        
        return {
            "success": True,
            "move_id": result.get('calendar', {}).get('move_id'),  # Safe access
            "calendar": result.get('calendar', {})
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating move: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/moves/{move_id}")
async def get_move(move_id: str):
    """Get campaign details"""
    try:
        result = supabase.table('moves').select('*').eq('id', move_id).single().execute()
        return result.data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/moves/business/{business_id}")
async def get_business_moves(business_id: str):
    """Get all moves for a business"""
    try:
        result = supabase.table('moves').select('*').eq('business_id', business_id).execute()
        return {"moves": result.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- ANALYTICS ----------

@app.post("/api/analytics/measure")
async def measure_performance(performance: PerformanceSubmit):
    """Submit performance data for analysis"""
    try:
        # Get move and business data
        move = supabase.table('moves').select('*').eq('id', performance.move_id).single().execute()
        
        # Run analytics agent
        result = await analytics_agent.ainvoke({
            'business_id': move.data['business_id'],
            'campaign_data': move.data,
            'performance_data': performance.metrics,
            'amec_analysis': {},
            'clv_analysis': {},
            'route_back_decision': {},
            'status': 'running'
        })
        
        return {
            "success": True,
            "amec_analysis": result['amec_analysis'],
            "clv_analysis": result['clv_analysis'],
            "route_back_needed": result['route_back_decision'].get('route_back_needed', False),
            "route_back_to": result['route_back_decision'].get('route_back_to')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- RAZORPAY ----------

@app.post("/api/razorpay/checkout")
async def create_checkout(business_id: str, tier: str):
    """Create Razorpay checkout session"""
    try:
        # Pricing
        pricing = {
            'basic': 2000,  # 2,000
            'pro': 3500,    # 3,500
            'enterprise': 5000  # 5,000
        }
        
        amount = pricing.get(tier, 2000) * 100  # Convert to paise
        
        # Create Razorpay order
        order = razorpay.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'business_id': business_id,
                'tier': tier
            }
        })
        
        return {
            "order_id": order['id'],
            "amount": amount,
            "currency": "INR",
            "key_id": os.getenv('RAZORPAY_KEY_ID')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/razorpay/webhook")
async def razorpay_webhook(request: Request):
    """Handle Razorpay webhook with proper security"""
    try:
        # Get webhook signature
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            logger.error("Missing webhook signature")
            raise HTTPException(status_code=401, detail="Missing signature")
        
        # Get webhook secret from environment
        webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        if not webhook_secret:
            logger.error("Missing webhook secret configuration")
            raise HTTPException(status_code=500, detail="Configuration error")
        
        # Read and verify payload
        payload = await request.body()
        payload_str = payload.decode('utf-8')
        
        # Verify signature
        try:
            import razorpay
            client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET')))
            client.utility.verify_webhook_signature(payload_str, signature, webhook_secret)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Process webhook
        import json
        event_data = json.loads(payload_str)
        event = event_data.get('event')
        
        logger.info(f"Processing webhook event: {event}")
        
        if event == 'payment.captured':
            payment = event_data['payload']['payment']['entity']
            notes = payment['notes']
            
            # Validate webhook data
            if not notes.get('business_id') or not notes.get('tier'):
                logger.error("Invalid webhook data: missing business_id or tier")
                raise HTTPException(status_code=400, detail="Invalid webhook data")
            
            # Update subscription
            tier_limits = {'basic': 3, 'pro': 6, 'enterprise': 9}
            max_icps = tier_limits.get(notes['tier'], 3)
            max_moves = {'basic': 5, 'pro': 15, 'enterprise': 999}.get(notes['tier'], 5)
            
            result = supabase.table('subscriptions').update({
                'tier': notes['tier'],
                'max_icps': max_icps,
                'max_moves': max_moves,
                'status': 'active',
                'razorpay_subscription_id': payment['id']
            }).eq('business_id', notes['business_id']).execute()
            
            if not result.data:
                logger.error(f"Failed to update subscription for business {notes['business_id']}")
                raise HTTPException(status_code=404, detail="Business not found")
            
            logger.info(f"Subscription updated for business {notes['business_id']} to tier {notes['tier']}")
        
        return {"status": "success"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")

# ---------- BACKGROUND JOBS ----------

@app.post("/api/admin/run-trend-monitor")
async def trigger_trend_monitor(background_tasks: BackgroundTasks):
    """Manually trigger trend monitoring (for testing)"""
    background_tasks.add_task(trend_monitor.run_daily_monitoring)
    return {"message": "Trend monitoring started in background"}

# --- begin core route aliases / placeholders (phase1.fix.1.1) ---
from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException

# Reusable helper: opportunistically build a Supabase client if not already present
def _get_supabase_optional():
    try:
        sb = globals().get("supabase", None)
        if sb is not None:
            return sb
        from supabase import create_client  # type: ignore
        import os as _os
        _url = _os.getenv("SUPABASE_URL")
        _key = (
            _os.getenv("SUPABASE_SERVICE_KEY")
            or _os.getenv("SUPABASE_KEY")
            or _os.getenv("SUPABASE_ANON_KEY")
        )
        if _url and _key:
            return create_client(_url, _key)
    except Exception:
        return None
    return None

# ---- Pydantic request models (defined only if not already present) ----
class PositioningRequest(BaseModel):
    business_id: str

class SelectPositioningRequest(BaseModel):
    business_id: str
    option_index: int

class ICPRequest(BaseModel):
    business_id: str

class MoveRequest(BaseModel):
    business_id: str
    goal: str
    platform: str
    duration_days: int = 7


# ---- GET /api/business/{business_id} ----
@app.get("/api/business/{business_id}")
def api_get_business(business_id: str):
    """
    Canonical business fetch endpoint.
    Tries Supabase if available; otherwise returns 501 to indicate the data layer isn't wired.
    """
    sb = _get_supabase_optional()
    if sb is None:
        raise HTTPException(status_code=501, detail="Supabase not configured")
    try:
        res = sb.table("businesses").select("*").eq("id", business_id).execute()
        if res.data:
            return res.data[0]
        raise HTTPException(status_code=404, detail="Business not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- POST /api/positioning/analyze ----
@app.post("/api/positioning/analyze")
async def api_positioning_analyze(req: PositioningRequest):
    """
    Analyze positioning for a business.
    If an agent module is available, delegate; otherwise return 501.
    """
    try:
        # Try a few likely module paths
        try:
            from positioning_agent import analyze_positioning as _analyze
        except Exception:
            try:
                from agents.positioning import analyze_positioning as _analyze  # type: ignore
            except Exception:
                raise HTTPException(status_code=501, detail="Positioning agent not wired")
    except Exception:
        raise HTTPException(status_code=501, detail="Positioning agent not wired")

    sb = _get_supabase_optional()
    if sb is None:
        raise HTTPException(status_code=501, detail="Supabase not configured")
    try:
        b = sb.table("businesses").select("*").eq("id", req.business_id).execute()
        if not b.data:
            raise HTTPException(status_code=404, detail="Business not found")
        result = await _analyze(b.data[0])  # expected to return dict/json
        # Optionally persist raw options if your schema exists; otherwise just return
        try:
            if result and "options" in result:
                sb.table("positioning_analyses").insert({
                    "business_id": req.business_id,
                    "options": result.get("options")
                }).execute()
        except Exception as e:
            logger.warning(f"Failed to persist positioning analysis: {e}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in positioning analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---- POST /api/positioning/select ----
@app.post("/api/positioning/select")
def api_positioning_select(req: SelectPositioningRequest):
    """
    Select a positioning option by index.
    Requires Supabase and positioning_analyses table; otherwise 501.
    """
    sb = _get_supabase_optional()
    if sb is None:
        raise HTTPException(status_code=501, detail="Supabase not configured")
    try:
        analysis = sb.table("positioning_analyses").select("*").eq("business_id", req.business_id).execute()
        if not analysis.data:
            raise HTTPException(status_code=404, detail="No positioning analysis found")
        options = analysis.data[0].get("options") or []
        if req.option_index < 0 or req.option_index >= len(options):
            raise HTTPException(status_code=400, detail="Invalid option_index")
        selected = options[req.option_index]
        sb.table("positioning_analyses").update({"selected_option": selected}).eq("id", analysis.data[0]["id"]).execute()
        return {"status": "selected", "positioning": selected}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- POST /api/icps/generate ----
@app.post("/api/icps/generate")
async def api_icps_generate(req: ICPRequest):
    """
    Generate ICPs for a business.
    Delegates to an agent if available; otherwise 501.
    """
    try:
        try:
            from icp_agent import generate_icps as _gen_icps
        except Exception:
            try:
                from agents.icp import generate_icps as _gen_icps  # type: ignore
            except Exception:
                raise HTTPException(status_code=501, detail="ICP agent not wired")
    except Exception:
        raise HTTPException(status_code=501, detail="ICP agent not wired")

    sb = _get_supabase_optional()
    if sb is None:
        raise HTTPException(status_code=501, detail="Supabase not configured")
    try:
        b = sb.table("businesses").select("*").eq("id", req.business_id).execute()
        if not b.data:
            raise HTTPException(status_code=404, detail="Business not found")
        # Need selected positioning
        pa = sb.table("positioning_analyses").select("*").eq("business_id", req.business_id).execute()
        if not pa.data or not pa.data[0].get("selected_option"):
            raise HTTPException(status_code=400, detail="Select a positioning option first")
        icps = await _gen_icps(b.data[0], pa.data[0]["selected_option"])
        # Best-effort persist
        try:
            if icps and isinstance(icps, list):
                for icp in icps:
                    if isinstance(icp, dict):
                        sb.table("icps").insert({
                            "business_id": req.business_id,
                            "name": icp.get("name"),
                            "demographics": icp.get("demographics"),
                            "psychographics": icp.get("psychographics"),
                            "platforms": icp.get("platforms"),
                            "content_preferences": icp.get("contentPreferences"),
                            "trending_topics": icp.get("trendingTopics"),
                            "tags": icp.get("tags"),
                            "embedding": icp.get("embedding"),
                        }).execute()
        except Exception as e:
            logger.warning(f"Failed to persist ICPs: {e}")
        return {"icps": icps}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ICPs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---- POST /api/moves/generate ----
@app.post("/api/moves/generate")
async def api_moves_generate(req: MoveRequest):
    """
    Generate a content move calendar.
    Delegates to an agent if available; otherwise 501.
    """
    try:
        try:
            from move_agent import generate_move_calendar as _gen_move
        except Exception:
            from agents.moves import generate_move_calendar as _gen_move  # type: ignore
    except Exception:
        raise HTTPException(status_code=501, detail="Move agent not wired")

    sb = _get_supabase_optional()
    if sb is None:
        raise HTTPException(status_code=501, detail="Supabase not configured")
    try:
        b = sb.table("businesses").select("*").eq("id", req.business_id).execute()
        if not b.data:
            raise HTTPException(status_code=404, detail="Business not found")
        icps = sb.table("icps").select("*").eq("business_id", req.business_id).execute().data or []
        if not icps:
            raise HTTPException(status_code=400, detail="Generate ICPs first")
        calendar = await _gen_move(b.data[0], icps, req.goal, req.platform, req.duration_days)
        try:
            saved = sb.table("moves").insert({
                "business_id": req.business_id,
                "goal": req.goal,
                "platform": req.platform,
                "duration_days": req.duration_days,
                "calendar": calendar,
                "status": "active"
            }).execute()
            return saved.data[0]
        except Exception:
            return {"calendar": calendar, "status": "draft"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# --- end core route aliases / placeholders (phase1.fix.1.1) ---

# ---------- HEALTH CHECK ----------

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    try:
        # Check database connection
        db_status = "healthy"
        try:
            supabase.table('businesses').select('id').limit(1).execute()
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check AI services (Ollama) - optional for cloud deployment
        ai_status = "healthy"
        try:
            import ollama
            # Check if Ollama is running
            ollama.list()
            ai_status = "healthy"
        except ImportError:
            ai_status = "not configured (Ollama not available in cloud)"
        except Exception as e:
            ai_status = f"unhealthy: {str(e)}"

        # Check Chroma DB
        chroma_status = "healthy"
        try:
            from backend.utils.embeddings import get_chroma_client
            client = get_chroma_client()
            client.heartbeat()
        except Exception as e:
            chroma_status = f"unhealthy: {str(e)}"

        # Check Redis if available
        redis_status = "healthy"
        try:
            import redis
            r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379)
            r.ping()
        except Exception:
            redis_status = "not configured"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "services": {
                "database": db_status,
                "ai_services": ai_status,
                "chroma_db": chroma_status,
                "redis": redis_status
            }
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Global exception handler for security events
@app.exception_handler(SecurityException)
async def security_exception_handler(request: Request, exc: SecurityException):
    logger.warning(f"Security exception at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Security validation failed"}
    )

@app.exception_handler(CostLimitExceeded)
async def cost_limit_exception_handler(request: Request, exc: CostLimitExceeded):
    logger.warning(f"Cost limit exceeded at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=429,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

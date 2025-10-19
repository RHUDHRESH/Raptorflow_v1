from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

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

# Import agents
from agents.orchestrator import orchestrator
from agents.research import research_agent
from agents.positioning import positioning_agent
from agents.icp import icp_agent
from agents.content import content_agent
from agents.analytics import analytics_agent
from agents.trend_monitor import trend_monitor

# Import utilities
from utils.supabase_client import get_supabase_client
from utils.razorpay_client import get_razorpay_client

app = FastAPI(title="RaptorFlow ADAPT API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = get_supabase_client()
razorpay = get_razorpay_client()

# ==================== MODELS ====================

class BusinessIntake(BaseModel):
    name: str
    industry: str
    location: str
    description: str
    goals: str

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
async def create_business(intake: BusinessIntake):
    """Create new business and trigger research"""
    try:
        # Save business
        result = supabase.table('businesses').insert({
            'name': intake.name,
            'industry': intake.industry,
            'location': intake.location,
            'description': intake.description,
            'goals': {'text': intake.goals}
        }).execute()
        
        business_id = result.data[0]['id']
        
        # Create trial subscription
        supabase.table('subscriptions').insert({
            'business_id': business_id,
            'tier': 'basic',
            'max_icps': 3,
            'status': 'trial'
        }).execute()
        
        return {
            "success": True,
            "business_id": business_id,
            "message": "Business created. Ready for research."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- RESEARCH ----------

@app.post("/api/research/{business_id}")
async def run_research(business_id: str):
    """Run complete research analysis"""
    try:
        # Get business
        biz = supabase.table('businesses').select('*').eq('id', business_id).single().execute()
        
        # Run research agent
        result = await research_agent.ainvoke({
            'business_id': business_id,
            'business_data': biz.data,
            'evidence': [],
            'competitor_ladder': [],
            'sostac': {},
            'status': 'running'
        })
        
        return {
            "success": True,
            "competitor_ladder": result['competitor_ladder'],
            "sostac": result['sostac'],
            "evidence_count": len(result['evidence']),
            "completeness_score": result['completeness_score']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def analyze_positioning(business_id: str):
    """Generate 3 positioning options"""
    try:
        biz = supabase.table('businesses').select('*').eq('id', business_id).single().execute()
        comps = supabase.table('competitor_ladder').select('*').eq('business_id', business_id).execute()
        
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
async def generate_icps(business_id: str):
    """Generate ICPs based on positioning"""
    try:
        # Check subscription tier
        sub = supabase.table('subscriptions').select('*').eq('business_id', business_id).single().execute()
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

@app.post("/api/moves")
async def create_move(business_id: str, move: MoveCreate):
    """Create new campaign/move"""
    try:
        # Get ICPs and positioning
        icps = supabase.table('icps').select('*').eq('business_id', business_id).execute()
        pos = supabase.table('positioning_analyses')\
            .select('*')\
            .eq('business_id', business_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .single()\
            .execute()
        
        # Run content agent
        result = await content_agent.ainvoke({
            'business_id': business_id,
            'goal': move.goal,
            'platform': move.platform,
            'duration_days': move.duration_days,
            'icps': icps.data,
            'positioning': pos.data.get('selected_option'),
            'calendar': {},
            'status': 'running'
        })
        
        return {
            "success": True,
            "move_id": result['calendar']['move_id'],
            "calendar": result['calendar']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def razorpay_webhook(payload: dict):
    """Handle Razorpay webhook"""
    try:
        # Verify signature (important for security)
        # signature = request.headers.get('X-Razorpay-Signature')
        # razorpay.utility.verify_webhook_signature(payload, signature, os.getenv('RAZORPAY_WEBHOOK_SECRET'))
        
        event = payload.get('event')
        
        if event == 'payment.captured':
            payment = payload['payload']['payment']['entity']
            notes = payment['notes']
            
            # Update subscription
            tier = notes['tier']
            max_icps = {'basic': 3, 'pro': 6, 'enterprise': 9}[tier]
            
            supabase.table('subscriptions').update({
                'tier': tier,
                'max_icps': max_icps,
                'status': 'active',
                'razorpay_subscription_id': payment['id']
            }).eq('business_id', notes['business_id']).execute()
        
        return {"status": "success"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
try:
    PositioningRequest
except NameError:
    class PositioningRequest(BaseModel):
        business_id: str

try:
    SelectPositioningRequest
except NameError:
    class SelectPositioningRequest(BaseModel):
        business_id: str
        option_index: int

try:
    ICPRequest
except NameError:
    class ICPRequest(BaseModel):
        business_id: str

try:
    MoveRequest
except NameError:
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
            from agents.positioning import analyze_positioning as _analyze  # type: ignore
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
            sb.table("positioning_analyses").insert({
                "business_id": req.business_id,
                "options": result.get("options")
            }).execute()
        except Exception:
            pass
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            from agents.icp import generate_icps as _gen_icps  # type: ignore
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
            for icp in icps:
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
        except Exception:
            pass
        return {"icps": icps}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

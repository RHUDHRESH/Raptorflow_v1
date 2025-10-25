"""
RaptorFlow v1 Main Application - Updated with 3-Tier AI Integration

Integrates:
- AI Provider Manager with intelligent routing
- Cost Controller with budget enforcement
- Vertex AI Vector Database
- WebSocket streaming for real-time updates
- GCP Secrets Manager
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import core components
from core.ai_provider_manager import get_ai_provider_manager
from middleware.cost_controller_v2 import CostController
from utils.gcp_secrets import get_secret_manager, SecretKeys
from utils.vertex_ai_vector_db import get_vertex_ai_db
from agents.orchestration_v2 import RaptorFlowOrchestrator

# Import existing middleware
from middleware.security_middleware import (
    SecurityHeadersMiddleware,
    InputValidationMiddleware,
    AuthenticationMiddleware,
)

# Import API routes
from api.research_routes import router as research_router
from api.conversation_routes import router as conversation_router
from api.embedding_routes import router as embedding_router
from api.budget_routes import router as budget_router
from api.ocr_routes import router as ocr_router
from api.websocket_routes import router as websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Global Instances
# ============================================================================

ai_provider_manager = None
cost_controller = None
orchestrator = None
secret_manager = None
vertex_ai_db = None

# ============================================================================
# Startup/Shutdown Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup/shutdown.

    Handles:
    - Initializing AI providers
    - Setting up cost controller
    - Preparing vector database
    - Logging session info
    """
    global ai_provider_manager, cost_controller, orchestrator, secret_manager, vertex_ai_db

    # ========== STARTUP ==========
    logger.info("🚀 RaptorFlow v1 Starting up...")

    try:
        # Initialize Secret Manager
        secret_manager = get_secret_manager()
        logger.info("✅ Secret Manager initialized")

        # Get API keys
        openai_key = secret_manager.get_secret(SecretKeys.OPENAI_API_KEY)
        gemini_key = secret_manager.get_secret(SecretKeys.GEMINI_API_KEY)

        # Initialize AI Provider Manager
        ai_provider_manager = get_ai_provider_manager(openai_key, gemini_key)
        logger.info("✅ AI Provider Manager initialized with GPT-5 series + Gemini fallbacks")

        # Initialize cost controller (needs Supabase client)
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        cost_controller = CostController(ai_provider_manager, supabase)
        logger.info("✅ Cost Controller initialized with tier-based budgets")

        # Initialize Vertex AI Vector DB
        project_id = os.getenv("GCP_PROJECT_ID")
        if project_id:
            vertex_ai_db = get_vertex_ai_db(project_id)
            logger.info("✅ Vertex AI Vector DB initialized")
        else:
            logger.warning("⚠️  GCP_PROJECT_ID not set, Vertex AI features disabled")

        # Initialize Orchestrator
        orchestrator = RaptorFlowOrchestrator(
            ai_provider_manager,
            cost_controller,
            connection_manager=None  # Will be initialized in websocket routes
        )
        logger.info("✅ LangGraph Orchestrator initialized")

        logger.info("🎉 RaptorFlow v1 Ready!")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Region: {os.getenv('GCP_REGION', 'us-central1')}")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # ========== SHUTDOWN ==========
    logger.info("🛑 RaptorFlow v1 Shutting down...")

    # Log final statistics
    if ai_provider_manager:
        stats = ai_provider_manager.get_usage_statistics()
        logger.info(
            f"📊 Session Statistics: "
            f"Cost: ${stats.get('total_cost', 0):.2f}, "
            f"Requests: {stats.get('total_requests', 0)}, "
            f"Avg Latency: {stats.get('average_latency', 0):.2f}s"
        )

    logger.info("✅ Shutdown complete")


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="RaptorFlow ADAPT API v2",
    version="2.0.0",
    description="AI-Powered Marketing Intelligence Platform with 3-Tier AI Routing",
    lifespan=lifespan,
)

# Add security middleware (order matters!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputValidationMiddleware)

# Add authentication middleware for protected routes
if os.getenv('ENVIRONMENT') in ['production', 'staging', 'development']:
    app.add_middleware(AuthenticationMiddleware)

# CORS Configuration
environment = os.getenv('ENVIRONMENT', 'development')
if environment == 'production':
    allowed_origins = [
        os.getenv('FRONTEND_URL', 'https://app.raptorflow.in'),
        "https://raptorflow.in"
    ]
else:
    allowed_origins = [
        os.getenv('FRONTEND_URL', 'http://localhost:3000'),
        "http://localhost:5173",
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

# ============================================================================
# Include API Routes
# ============================================================================

app.include_router(websocket_router, tags=["websocket"])
app.include_router(research_router, prefix="/api/research", tags=["research"])
app.include_router(conversation_router, prefix="/api/conversations", tags=["conversations"])
app.include_router(embedding_router, prefix="/api", tags=["search"])
app.include_router(budget_router, prefix="/api/budget", tags=["budget"])
app.include_router(ocr_router, prefix="/api/ocr", tags=["ocr"])

# ============================================================================
# Core Routes
# ============================================================================

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "service": "RaptorFlow ADAPT API v2",
        "status": "running",
        "version": "2.0.0",
        "ai_model": "GPT-5 series with Gemini fallbacks",
    }


@app.get("/health")
async def health_check():
    """
    Enhanced health check with system status.

    Returns:
        {
            "status": "healthy" | "unhealthy",
            "services": {
                "ai_provider": str,
                "cost_controller": str,
                "vector_db": str,
                "database": str
            },
            "models_available": [str],
            "version": str
        }
    """
    from datetime import datetime

    services_status = {}

    # Check AI Provider
    if ai_provider_manager:
        services_status["ai_provider"] = "✅ healthy"
        try:
            # Verify we can create LLM instances
            _ = ai_provider_manager._get_llm("gpt-5-nano")
            services_status["ai_models"] = "✅ OpenAI + Gemini fallback configured"
        except Exception as e:
            services_status["ai_models"] = f"⚠️  {str(e)}"
    else:
        services_status["ai_provider"] = "❌ not initialized"

    # Check Cost Controller
    if cost_controller:
        services_status["cost_controller"] = "✅ healthy"
    else:
        services_status["cost_controller"] = "⚠️  not initialized"

    # Check Vector DB
    if vertex_ai_db:
        services_status["vector_db"] = "✅ Vertex AI Matching Engine ready"
    else:
        services_status["vector_db"] = "⚠️  not configured"

    # Check Database
    try:
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        supabase.table('businesses').select('count').limit(1).execute()
        services_status["database"] = "✅ Supabase connected"
    except Exception as e:
        services_status["database"] = f"❌ {str(e)}"

    return {
        "status": "healthy" if "❌" not in str(services_status) else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": environment,
        "services": services_status,
        "models_available": list(ai_provider_manager.MODELS.keys()) if ai_provider_manager else [],
    }


@app.post("/api/analyze/{business_id}")
async def analyze_business(
    business_id: str,
    request: Request
):
    """
    Trigger complete RaptorFlow analysis with 3-tier AI routing.

    Uses the LangGraph orchestrator with:
    - Intelligent model selection (nano/mini/full)
    - Real-time progress streaming
    - Budget enforcement
    - Comprehensive error handling

    Args:
        business_id: ID of business to analyze

    Returns:
        {
            "success": bool,
            "total_cost": float,
            "duration": float,
            "results": {...},
            "models_used": [str]
        }
    """
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not initialized. Service may still be starting."
        )

    try:
        user_id = getattr(request.state, 'user_id', 'anonymous')

        # Get business data
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        business = supabase.table("businesses") \
            .select("*") \
            .eq("id", business_id) \
            .single() \
            .execute()

        if not business.data:
            raise HTTPException(status_code=404, detail="Business not found")

        # Verify ownership
        if business.data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Check budget before starting expensive workflow
        can_proceed, budget_info = await cost_controller.check_budget_before_task(
            business_id,
            "situation_analysis",  # Estimate for first expensive task
            len(business.data.get("description", ""))
        )

        if not can_proceed:
            raise HTTPException(
                status_code=429,
                detail=f"Budget limit exceeded: {budget_info.get('reason')}"
            )

        # Initialize state for orchestration
        initial_state = {
            "business_id": business_id,
            "business_data": business.data,
            "industry": business.data.get("industry", ""),
            "description": business.data.get("description", ""),
            "goals": business.data.get("goals", []),
            "situation_analysis": None,
            "competitor_ladder": None,
            "evidence": None,
            "sostac": None,
            "positioning_options": None,
            "selected_positioning": None,
            "icps": None,
            "marketing_7ps": None,
            "north_star_metrics": None,
            "content_calendar": None,
            "asset_templates": None,
            "amec_analysis": None,
            "clv_analysis": None,
            "total_cost": 0.0,
            "total_duration": 0.0,
            "models_used": [],
            "errors": [],
            "workflow_stage": "init",
        }

        # Run orchestration
        logger.info(f"Starting orchestration for {business_id}")
        final_state = await orchestrator.run_workflow(initial_state)

        # Check for errors
        if final_state.get("errors"):
            logger.warning(f"Orchestration completed with errors: {final_state['errors']}")
            return {
                "success": False,
                "errors": final_state["errors"],
                "partial_results": {
                    "positioning": final_state.get("selected_positioning"),
                    "icps": final_state.get("icps"),
                },
                "total_cost": final_state["total_cost"],
            }

        # Success
        return {
            "success": True,
            "total_cost": round(final_state["total_cost"], 4),
            "total_duration": round(final_state["total_duration"], 2),
            "models_used": list(set(final_state["models_used"])),
            "results": {
                "situation_analysis": final_state.get("situation_analysis"),
                "competitors": final_state.get("competitor_ladder"),
                "sostac": final_state.get("sostac"),
                "positioning": final_state.get("selected_positioning"),
                "icps": final_state.get("icps"),
                "marketing_mix_7ps": final_state.get("marketing_7ps"),
                "north_star": final_state.get("north_star_metrics"),
                "content_calendar": final_state.get("content_calendar"),
                "analytics": final_state.get("amec_analysis"),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.get("/api/cost-summary/{business_id}")
async def get_cost_summary(business_id: str):
    """
    Get cost and budget summary for a business.

    Returns comprehensive cost and usage information.
    """
    if not cost_controller:
        raise HTTPException(status_code=503, detail="Cost controller not initialized")

    try:
        budget_status = await cost_controller.get_budget_status(business_id)
        usage_history = await cost_controller.get_usage_history(business_id, days=7)
        feature_limits = await cost_controller.get_feature_limits(business_id)

        return {
            "budget": budget_status,
            "usage_history": usage_history,
            "feature_limits": feature_limits,
            "ai_model_stats": ai_provider_manager.get_usage_statistics() if ai_provider_manager else {}
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cost summary")


@app.get("/api/ai-models")
async def list_ai_models():
    """
    Get list of available AI models and their configuration.

    Returns info about all 3 tiers and fallbacks.
    """
    if not ai_provider_manager:
        raise HTTPException(status_code=503, detail="AI provider not initialized")

    models = {}
    for model_name, config in ai_provider_manager.MODELS.items():
        models[model_name] = {
            "provider": config.provider,
            "tier": config.tier,
            "input_cost_per_1m_tokens": config.input_cost_per_1m,
            "output_cost_per_1m_tokens": config.output_cost_per_1m,
            "max_tokens": config.max_tokens,
            "supports_thinking": config.supports_thinking,
        }

    return {
        "models": models,
        "task_routing": ai_provider_manager.TASK_ROUTING,
        "fallback_chains": ai_provider_manager.FALLBACK_CHAINS,
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

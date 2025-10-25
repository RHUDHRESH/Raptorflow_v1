# RaptorFlow v2 - Complete Integration & Migration Guide

**Status:** Ready for Integration ✅
**Last Updated:** 2025-10-25
**Target Deployment:** GCP Cloud Run

---

## 📋 Executive Summary

RaptorFlow v2 is a major architectural upgrade that adds:

1. **3-Tier AI Model Routing** - Intelligent cost-optimized routing between GPT-5 Nano/Mini/Full and Gemini fallbacks
2. **Tier-Based Budget Enforcement** - Real-time cost tracking with automatic shutdown at budget limits
3. **Real-Time WebSocket Streaming** - Live progress updates for long-running tasks
4. **Vertex AI Vector Database** - Managed semantic search replacing local Chroma DB
5. **GCP Secrets Manager** - Secure credential management for production

**Expected Outcomes:**
- 30-40% cost reduction through intelligent model routing
- Better user experience with real-time progress updates
- Enterprise-grade security and secrets management
- Scalable vector search for semantic operations

---

## 🏗️ Architecture Overview

### Current System (v1)
```
FastAPI App
    ↓
ServiceManager (singleton)
    ├─ LLM: OpenAI → Gemini → Ollama
    └─ Embeddings: OpenAI → Google → HuggingFace
    ↓
Agents (Research, Positioning, ICP, Content, Analytics)
    ↓
Supabase PostgreSQL + pgvector
```

### New System (v2)
```
FastAPI App
    ↓
┌─────────────────────────────────────────────────┐
│ GCP Secrets Manager (credential management)     │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ AIProviderManager (3-tier intelligent routing)  │
│  ├─ GPT-5 Nano ($0.05/1M)   [simple tasks]     │
│  ├─ GPT-5 Mini ($0.25/1M)   [balanced tasks]   │
│  ├─ GPT-5 Full ($1.25/1M)   [complex tasks]    │
│  └─ Fallback: Gemini 2.5                       │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ CostController (tier-based budget enforcement)  │
│  ├─ Basic: $10/day (Nano+Mini only)            │
│  ├─ Pro: $50/day (Nano+Mini only)              │
│  └─ Enterprise: $200/day (Full access)         │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ RaptorFlowOrchestrator (LangGraph workflow)     │
│  ├─ Real-time WebSocket streaming              │
│  ├─ Cost tracking per step                      │
│  └─ Progressive error handling                  │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Data Storage Layer                              │
│  ├─ Supabase PostgreSQL (business data)        │
│  ├─ Vertex AI Matching Engine (vectors)        │
│  └─ Cloud Storage (artifacts)                  │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Migration Path

### Phase 1: Parallel Deployment (Week 1)
- Keep v1 system running in production
- Deploy v2 in staging environment
- Run both systems simultaneously
- Monitor v2 performance metrics

**Files to Deploy:**
- ✅ `backend/core/ai_provider_manager.py`
- ✅ `backend/middleware/cost_controller_v2.py`
- ✅ `backend/agents/orchestration_v2.py`
- ✅ `backend/utils/gcp_secrets.py`
- ✅ `backend/utils/vertex_ai_vector_db.py`

### Phase 2: Gradual Rollout (Week 2-3)
- Route 10% of traffic to v2
- Monitor costs and response times
- Increase traffic to 50% if successful
- Keep v1 as fallback

### Phase 3: Full Cutover (Week 4)
- Route 100% traffic to v2
- Archive v1 (keep as backup for 30 days)
- Decommission v1 infrastructure

### Phase 4: Optimization (Week 5+)
- Fine-tune model selection per task type
- Optimize cost thresholds
- Implement advanced features (batch processing, caching)

---

## 🔧 Component Details

### 1. AIProviderManager

**File:** `backend/core/ai_provider_manager.py` (500 lines)

**Purpose:** Intelligent routing of tasks to optimal AI models based on complexity

**Key Features:**
- Task complexity detection (simple, balanced, complex)
- Cost estimation before execution
- Token counting and usage analytics
- Fallback chain: OpenAI → Gemini → error
- Support for extended thinking (o1 models)

**Usage Example:**
```python
from backend.core.ai_provider_manager import AIProviderManager

ai = AIProviderManager(
    openai_api_key="sk-...",
    gemini_api_key="AIzaSy..."
)

# Simple task - routes to GPT-5 Nano
result = await ai.execute_with_fallback(
    task_type="sentence_summary",
    messages=[{"role": "user", "content": "Summarize..."}],
    complexity="simple"
)
# Returns: {response, model_used, cost, tokens, latency}

# Complex task - routes to GPT-5 Full with reasoning
result = await ai.execute_with_fallback(
    task_type="strategy_analysis",
    messages=[{"role": "user", "content": "Analyze..."}],
    complexity="complex",
    reasoning_effort="high"
)
```

**Model Selection Logic:**
```
Task Complexity → Model Selection
──────────────────────────────────
simple         → GPT-5 Nano ($0.05)
balanced       → GPT-5 Mini ($0.25)
complex        → GPT-5 Full ($1.25)

Fallback Chain:
OpenAI → Gemini 2.5 Pro → Error
```

**Cost Tracking:**
- Pre-flight estimation: `estimate_task_cost(task_type, input_length)`
- Post-execution analytics: `get_cost_by_task()`, `get_daily_cost()`
- Monthly projections: `project_monthly_cost()`

---

### 2. CostController v2

**File:** `backend/middleware/cost_controller_v2.py` (400 lines)

**Purpose:** Enforce subscription tier-based budget limits with real-time tracking

**Tier Structure:**
```
┌─────────────┬────────────┬─────────────┬──────────┬──────────┐
│ Tier        │ Daily Lim  │ Monthly Lim │ Max ICPs │ Models   │
├─────────────┼────────────┼─────────────┼──────────┼──────────┤
│ Basic       │ $10        │ $300        │ 3        │ Nano+Mini│
│ Pro         │ $50        │ $1,500      │ 6        │ Nano+Mini│
│ Enterprise  │ $200       │ $6,000      │ 9        │ All      │
└─────────────┴────────────┴─────────────┴──────────┴──────────┘
```

**Key Features:**
- Real-time budget checking before task execution
- Feature gating (max ICPs per tier)
- Model access restriction (Basic/Pro can't use GPT-5)
- Progressive warnings at 75%, 90%, 100% of budget
- Emergency shutdown at limit

**Usage Example:**
```python
from backend.middleware.cost_controller_v2 import CostController

cost_controller = CostController(ai_provider_manager, supabase_client)

# Check budget before executing task
can_proceed, budget_info = await cost_controller.check_budget_before_task(
    business_id="biz-123",
    task_type="positioning_analysis",
    input_length=50000  # character count
)

if not can_proceed:
    # Blocked: daily_budget_exceeded, model_tier_restricted, etc
    raise HTTPException(
        status_code=402,
        detail=f"Cannot proceed: {budget_info['reason']}"
    )

# If approved, execute task and track cost
result = await ai.execute_with_fallback(...)
await cost_controller.track_usage(
    business_id="biz-123",
    task_type="positioning_analysis",
    cost=result["cost"],
    model_used=result["model_used"],
    tokens_used=result["tokens"]
)
```

**Budget Status Query:**
```python
# Get current budget status for a business
status = await cost_controller.get_budget_status("biz-123")
# Returns: {
#     "tier": "pro",
#     "daily_limit": 50.0,
#     "today_spent": 12.50,
#     "today_remaining": 37.50,
#     "percent_used": 25.0,
#     "warning_level": None,
#     "projected_monthly": 375.0,
#     "monthly_limit": 1500.0
# }
```

---

### 3. Real-Time WebSocket Streaming

**File:** `backend/api/websocket_routes.py` (400 lines)

**Purpose:** Send real-time progress updates to clients for long-running tasks

**Event Types:**
```
Task Started
    ↓
Research Phase Progress (10%, 20%, 30%, ...)
    ↓
Positioning Phase Progress (...)
    ↓
ICP Generation Progress (...)
    ↓
Content Generation Progress (...)
    ↓
Task Completed with Results
```

**Usage Example:**

Frontend (WebSocket connection):
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/task/task-123');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    // message = {
    //     event: "research_progress",
    //     data: {
    //         percent_complete: 35,
    //         current_step: "Analyzing competitors",
    //         estimated_remaining: 120
    //     },
    //     timestamp: "2025-10-25T14:30:00Z"
    // }

    updateProgressBar(message.data.percent_complete);
    updateStatus(message.data.current_step);
};
```

Backend (Sending events):
```python
from backend.api.websocket_routes import ConnectionManager

connection_manager = ConnectionManager()

# Start research task and stream progress
async for progress in research_agent.analyze_with_streaming(business_data):
    await connection_manager.broadcast_event(
        task_id="task-123",
        event=StreamEvent(
            event_type="research_progress",
            data={
                "percent_complete": progress["percent"],
                "current_step": progress["step"],
                "estimated_remaining": progress["eta_seconds"]
            }
        )
    )
```

**Benefits:**
- Users see live progress instead of waiting blindly
- Can cancel long-running tasks midway
- Better UX for slow/complex analyses
- Easier debugging of stuck tasks

---

### 4. RaptorFlowOrchestrator v2

**File:** `backend/agents/orchestration_v2.py` (500+ lines)

**Purpose:** Complete workflow orchestration with cost tracking and streaming

**Workflow States:**
```
MarketingState:
├─ Input Phase
│  ├─ business_id, industry, description, goals
│  └─ subscription tier, budget constraints
│
├─ Research Phase
│  ├─ situation_analysis
│  ├─ competitor_ladder
│  ├─ evidence collection
│  └─ SOSTAC framework
│
├─ Strategy Phase
│  ├─ positioning_options (3 variants)
│  ├─ selected_positioning
│  ├─ ICPs (3-5 personas)
│  ├─ marketing_7ps
│  └─ north_star_metrics
│
├─ Campaign Phase
│  ├─ content_calendar (12-week)
│  └─ asset_templates (creative briefs)
│
├─ Analytics Phase
│  ├─ amec_analysis (metrics)
│  ├─ clv_analysis (value projection)
│  └─ route_back_strategy
│
└─ Tracking
   ├─ total_cost (accumulated across phases)
   ├─ total_duration (wall-clock time)
   └─ models_used (GPT-5 Nano, Mini, Full, Gemini)
```

**Key Methods:**
```python
async def start_marketing_analysis(business_data: Dict) -> str:
    """Start complete marketing analysis workflow"""

async def research_phase(state: MarketingState) -> Dict:
    """Execute research with model routing"""

async def positioning_phase(state: MarketingState) -> Dict:
    """Generate positioning with validation loops"""

async def get_streaming_updates(task_id: str) -> AsyncIterator:
    """Stream progress updates for UI"""
```

---

### 5. GCP Secrets Manager

**File:** `backend/utils/gcp_secrets.py` (200+ lines)

**Purpose:** Secure credential management for production deployment

**Features:**
- Automatic secret retrieval from GCP
- Local fallback to .env for development
- Caching with TTL (1 hour)
- Audit logging
- No hardcoded credentials

**Usage Example:**
```python
from backend.utils.gcp_secrets import SecretManager

secret_manager = SecretManager(
    project_id="my-gcp-project",
    use_gcp=True  # False for local development
)

openai_key = secret_manager.get_secret("openai_api_key")
gemini_key = secret_manager.get_secret("gemini_api_key")
supabase_url = secret_manager.get_secret("supabase_url")
```

**Setup:**
```bash
# Create secrets in GCP Secret Manager
gcloud secrets create openai_api_key --data-file=- < <(echo $OPENAI_API_KEY)
gcloud secrets create gemini_api_key --data-file=- < <(echo $GEMINI_API_KEY)
gcloud secrets create supabase_url --data-file=- < <(echo $SUPABASE_URL)
```

---

### 6. Vertex AI Vector Database

**File:** `backend/utils/vertex_ai_vector_db.py` (350+ lines)

**Purpose:** Managed semantic search replacing local Chroma DB

**Benefits over Chroma:**
- Fully managed (no server to maintain)
- Scales to billions of vectors
- Native GCP integration (IAM, monitoring)
- Real-time indexing
- Cost-effective for large datasets

**Migration from Chroma:**

```python
# Old (Chroma local):
from chromadb import Client
client = Client()
collection = client.get_or_create_collection("conversations")

# New (Vertex AI):
from backend.utils.vertex_ai_vector_db import VertexAIVectorDB
vector_db = VertexAIVectorDB(
    project_id="my-gcp-project",
    location="us-central1",
    index_name="raptorflow-embeddings"
)
```

**Usage:**
```python
# Store embeddings
await vector_db.add_embeddings(
    ids=["msg-1", "msg-2", "msg-3"],
    embeddings=[emb1, emb2, emb3],  # 1536-dim vectors
    metadata=[
        {"conversation_id": "conv-1", "role": "user"},
        {"conversation_id": "conv-1", "role": "assistant"},
        {"conversation_id": "conv-2", "role": "user"}
    ]
)

# Semantic search
results = await vector_db.search(
    query_embedding=query_vector,
    top_k=5,
    filter={"conversation_id": "conv-1"}
)
# Returns: [
#   {id: "msg-1", distance: 0.92, metadata: {...}},
#   {id: "msg-3", distance: 0.87, metadata: {...}},
#   ...
# ]
```

---

## 🚀 Deployment Steps

### Prerequisites
- GCP Project with billing enabled
- `gcloud` CLI installed
- Service account with appropriate permissions
- Supabase project

### Step 1: GCP Setup
```bash
# Set your GCP project
export PROJECT_ID="your-gcp-project"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  container.googleapis.com

# Create service account
gcloud iam service-accounts create raptorflow \
  --display-name="RaptorFlow Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:raptorflow@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:raptorflow@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/aiplatform.admin
```

### Step 2: Create Secrets
```bash
# Store API keys in GCP Secret Manager
gcloud secrets create openai_api_key \
  --replication-policy="automatic" \
  --data-file=- << EOF
sk-your-openai-api-key-here
EOF

gcloud secrets create gemini_api_key \
  --replication-policy="automatic" \
  --data-file=- << EOF
AIzaSyYour-Gemini-Key-Here
EOF

gcloud secrets create supabase_url \
  --replication-policy="automatic" \
  --data-file=- << EOF
https://your-project.supabase.co
EOF

gcloud secrets create supabase_key \
  --replication-policy="automatic" \
  --data-file=- << EOF
your-supabase-service-key
EOF
```

### Step 3: Deploy to Cloud Run
```bash
# Navigate to project root
cd /path/to/Raptorflow_v1

# Build Docker image
gcloud builds submit --tag gcr.io/$PROJECT_ID/raptorflow:v2

# Deploy to Cloud Run
gcloud run deploy raptorflow \
  --image gcr.io/$PROJECT_ID/raptorflow:v2 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account=raptorflow@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,APP_MODE=prod
```

Or use the provided script:
```bash
chmod +x scripts/deploy-to-gcp.sh
./scripts/deploy-to-gcp.sh
```

---

## 🧪 Testing V2

### Unit Tests
```bash
# Run AI provider tests
pytest backend/tests/test_ai_routing.py -v

# Run cost controller tests
pytest backend/tests/test_cost_controller.py -v

# Run orchestrator tests
pytest backend/tests/test_orchestration.py -v
```

### Integration Tests
```bash
# Test with staging environment
export APP_MODE=staging
pytest backend/tests/integration/test_v2_workflow.py -v
```

### Load Testing
```bash
# Test concurrent WebSocket connections
python scripts/load_test_websockets.py \
  --connections 100 \
  --duration 300

# Test cost calculation under load
python scripts/load_test_costs.py \
  --num_tasks 1000 \
  --avg_input_length 5000
```

---

## 📊 Monitoring & Observability

### Key Metrics to Track

1. **Cost Metrics**
   - Daily spend per tier
   - Cost per task type
   - Model selection distribution (Nano vs Mini vs Full)
   - Budget utilization by customer

2. **Performance Metrics**
   - Task completion time (E2E)
   - Latency by model type
   - Error rate by model
   - Fallback rate (% of tasks using Gemini instead of OpenAI)

3. **User Experience**
   - WebSocket connection stability
   - Streaming latency (time from event to client)
   - Task cancellation rate
   - User satisfaction (if tracked)

### Dashboards

**GCP Cloud Monitoring:**
```
Metrics to create:
├─ custom_metric/raptorflow/daily_cost_by_tier
├─ custom_metric/raptorflow/model_selection_distribution
├─ custom_metric/raptorflow/task_completion_time
└─ custom_metric/raptorflow/error_rate_by_model
```

**Suggested Tool:** Datadog, New Relic, or GCP Cloud Monitoring

---

## 🔄 Rollback Plan

If v2 has issues:

```bash
# Step 1: Stop v2 traffic
gcloud run services update-traffic raptorflow --to-revisions v1=100

# Step 2: Verify v1 is healthy
curl https://raptorflow.run.app/health

# Step 3: If issues continue, revert to v1 in code
git checkout v1-release-tag
gcloud builds submit --tag gcr.io/$PROJECT_ID/raptorflow:v1
gcloud run deploy raptorflow --image gcr.io/$PROJECT_ID/raptorflow:v1

# Step 4: Investigate v2 issues
# Check logs: gcloud logging read "resource.type=cloud_run_revision"
# Check traces: gcloud trace list
# Check metrics: GCP Cloud Monitoring dashboard
```

---

## ✅ Integration Checklist

Before going live with v2:

### Code Integration
- [ ] All V2 files copied to backend/
- [ ] main.py updated to import V2 components
- [ ] All tests passing
- [ ] Type checking passes (`mypy backend/`)
- [ ] Linting passes (`flake8 backend/`, `black --check backend/`)

### Database
- [ ] Supabase tables created/migrated
- [ ] Vertex AI index created and deployed
- [ ] Database backups configured
- [ ] Connection strings verified

### Security
- [ ] GCP Secrets Manager configured
- [ ] Service account IAM roles assigned
- [ ] API keys rotated
- [ ] No hardcoded credentials in code
- [ ] VPC/firewall rules configured

### Monitoring
- [ ] GCP Cloud Monitoring dashboards created
- [ ] Alert thresholds set
- [ ] Log aggregation configured
- [ ] Error tracking (Sentry, etc.) integrated

### Operations
- [ ] Runbook created for common issues
- [ ] On-call rotation established
- [ ] Incident response plan ready
- [ ] Cost alerts configured
- [ ] Budget threshold set

### Testing
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] Security scan completed
- [ ] Performance benchmarks recorded

### Documentation
- [ ] API documentation updated
- [ ] Architecture diagrams created
- [ ] Deployment guide finalized
- [ ] Troubleshooting guide written
- [ ] Team training completed

---

## 🤝 Support & Troubleshooting

### Common Issues

**Issue: "AIProviderManager failed to initialize"**
```
Solution:
1. Verify OPENAI_API_KEY and GEMINI_API_KEY are set
2. Check gcloud auth: gcloud auth list
3. Review logs: gcloud logging read "aiprovidermanager"
```

**Issue: "Cost limit exceeded"**
```
Solution:
1. Check tier: SELECT subscription_tier FROM subscriptions WHERE business_id='...'
2. Review daily spend: SELECT SUM(cost) FROM ai_usage WHERE date = TODAY
3. Upgrade tier or wait for next billing period
```

**Issue: "Vertex AI index not found"**
```
Solution:
1. Create index: await vector_db.create_index(dimensions=1536)
2. Deploy index: await vector_db.deploy_endpoint()
3. Wait 30-60 min for deployment
```

**Issue: "WebSocket disconnections"**
```
Solution:
1. Check client network (firewall, proxies)
2. Increase Cloud Run timeout: --timeout=3600
3. Implement client-side reconnection logic
```

---

## 📚 Additional Resources

- **AI Provider Manager Docs:** `ARCHITECTURE_V2.md`
- **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`
- **Quick Reference:** `QUICK_REFERENCE.md`
- **GCP Deployment:** `scripts/deploy-to-gcp.sh`
- **LLM Architecture:** `LLM_ARCHITECTURE_SUMMARY.txt`
- **Backend Reference:** `BACKEND_REFERENCE_COMPLETE.md`

---

**Next Step:** Follow the Deployment Steps to integrate v2 into your infrastructure.

**Questions?** Review the specific component documentation or check the code comments.

**Last Updated:** 2025-10-25
**Status:** READY FOR INTEGRATION ✅

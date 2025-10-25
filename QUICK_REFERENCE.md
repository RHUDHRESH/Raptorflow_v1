# RaptorFlow v2 - Quick Reference Guide

## 🎯 30-Second Overview

**What:** AI-powered marketing strategy generator with 3-tier cost-optimized model routing
**Where:** 100% GCP Cloud Run (no local dependencies)
**Cost:** $1,200-1,500/month for 1000 analyses (71% savings vs fixed models)
**Deploy:** One script (`./scripts/deploy-to-gcp.sh`)

---

## 📋 Core Components

### **1. AI Provider Manager**
Routes tasks intelligently to optimal model

```python
from core.ai_provider_manager import get_ai_provider_manager

ai = get_ai_provider_manager(openai_key, gemini_key)

result = await ai.execute_with_fallback(
    task_type="icp_generation",        # Routes to GPT-5 Mini
    messages=[{"role": "user", "content": "..."}],
    reasoning_effort="medium"
)
# Returns: {response, model_used, cost, tokens, latency}
```

### **2. Cost Controller**
Enforces tier-based budgets ($10/$50/$200/day)

```python
from middleware.cost_controller_v2 import CostController

can_proceed, budget_info = await cost_controller.check_budget_before_task(
    business_id="biz-123",
    task_type="sostac_analysis",
    input_length=50000
)

if not can_proceed:
    # Blocked: daily_budget_exceeded, model_tier_restricted, etc
    print(budget_info["reason"])
```

### **3. WebSocket Streaming**
Real-time progress updates

```python
# Client
const ws = new WebSocket('wss://api.raptorflow.in/ws/research/biz-123');
ws.onmessage = (e) => {
  const {event, data} = JSON.parse(e.data);
  if(event === 'progress') updateBar(data.progress);
};

# Server
await emit_progress("biz-123", "research", "competitor_analysis", 33, {...});
```

### **4. Vertex AI Vector DB**
Semantic search for conversations & research

```python
from utils.vertex_ai_vector_db import get_vertex_ai_db

db = get_vertex_ai_db(project_id="raptorflow-prod")
results = await db.semantic_search(
    query_embedding=[...],
    top_k=10,
    filters={"business_id": ["biz-123"]}
)
```

### **5. Secrets Manager**
Secure credential access (GCP fallback to env vars)

```python
from utils.gcp_secrets import get_secret_manager

mgr = get_secret_manager(project_id="raptorflow-prod")
openai_key = mgr.get_secret("openai_api_key")  # Auto GCP→Env fallback
```

### **6. Orchestrator**
8-stage workflow with budget checks

```python
from agents.orchestration_v2 import RaptorFlowOrchestrator

orchestrator = RaptorFlowOrchestrator(ai_manager, cost_controller)
final_state = await orchestrator.run_workflow(initial_state)
# Returns: {results, total_cost, models_used, errors}
```

---

## 🔀 Task Routing Matrix

| Task | Model | Cost | Speed |
|------|-------|------|-------|
| input_validation | Nano | $0.001 | ⚡⚡⚡ |
| html_sanitization | Nano | $0.001 | ⚡⚡⚡ |
| sentiment_analysis | Nano | $0.002 | ⚡⚡⚡ |
| icp_generation | Mini | $0.06 | ⚡⚡ |
| content_calendar | Mini | $0.08 | ⚡⚡ |
| 7ps_marketing | Mini | $0.05 | ⚡⚡ |
| sostac_analysis | GPT-5 | $0.60 | ⚡ |
| positioning | GPT-5 | $0.50 | ⚡ |
| competitor_intel | GPT-5 | $1.20 | ⚡ |
| amec_roi | GPT-5 | $0.40 | ⚡ |

**Fallback Chain:** Each tier auto-falls back to Gemini on failure (exponential backoff)

---

## 💰 Budget Tiers

| Tier | Daily | Monthly | Max Models | Max ICPs | Max Moves |
|------|-------|---------|-----------|---------|-----------|
| Basic | $10 | $300 | Nano+Mini | 3 | 5 |
| Pro | $50 | $1,500 | Nano+Mini | 6 | 15 |
| Enterprise | $200 | $6,000 | All (Nano+Mini+Full) | 9 | 999 |

**Auto-Enforcement:**
- ✋ Blocks at limit
- ⚠️ Warns at 75%, 90%
- 🔴 Emergency shutdown at 100%

---

## 📊 API Endpoints Quick Reference

### **Analysis & Workflow**
```
POST   /api/analyze/{business_id}              # Full workflow
GET    /api/cost-summary/{business_id}         # Budget info
GET    /api/ai-models                          # Model config
```

### **Real-Time Updates**
```
WS     /ws/research/{business_id}              # Research progress
WS     /ws/positioning/{business_id}           # Positioning progress
WS     /ws/icps/{business_id}                  # ICP progress
WS     /ws/content/{business_id}               # Content progress
```

### **Existing Routes (Still Available)**
```
POST   /api/research/{business_id}             # Research analysis
POST   /api/icps/{business_id}                 # Generate ICPs
POST   /api/positioning/{business_id}          # Generate positioning
GET    /api/budget/status                      # Budget status
GET    /health                                 # System health
```

---

## 🔧 Deployment Checklist

### **Before Deploy**
- [ ] GCP project created
- [ ] Billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] `GCP_PROJECT_ID` environment variable set
- [ ] Secrets ready (OpenAI, Gemini, Supabase, etc.)

### **Deploy**
```bash
# One command deployment
./scripts/deploy-to-gcp.sh production us-central1

# What it does:
# 1. Enables APIs (Cloud Run, Container Registry, Secret Manager, etc)
# 2. Creates/verifies secrets in GCP Secret Manager
# 3. Builds Docker image
# 4. Pushes to GCP Container Registry
# 5. Deploys to Cloud Run (auto-scaling, managed)
# 6. Runs health check
# 7. Outputs service URL
```

### **After Deploy**
```bash
# View logs
gcloud run logs read raptorflow-backend --region=us-central1

# Scale settings (if needed)
gcloud run services update raptorflow-backend \
  --min-instances=3 --max-instances=50 --region=us-central1

# View metrics
gcloud monitoring read --resource=cloud_run_revision
```

---

## 💾 File Structure Reference

```
backend/
├── core/ai_provider_manager.py          # 3-tier routing
├── middleware/
│   ├── cost_controller_v2.py            # Budget enforcement
│   └── security_middleware.py           # Existing security
├── agents/orchestration_v2.py           # 8-stage workflow
├── api/websocket_routes.py              # Real-time streaming
├── utils/
│   ├── gcp_secrets.py                   # Secrets management
│   └── vertex_ai_vector_db.py           # Vector search
├── main_v2.py                           # Updated FastAPI app
└── requirements.txt                     # Dependencies
```

---

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/test_ai_routing.py -v

# Test specific component
pytest backend/tests/test_ai_routing.py::TestAIProviderManager -v
pytest backend/tests/test_ai_routing.py::TestCostController -v

# With coverage report
pytest backend/tests/ --cov=backend --cov-report=html
```

---

## 🐛 Common Issues & Solutions

### **"All AI models failed"**
```bash
# Check API keys in Secret Manager
gcloud secrets versions access latest --secret="openai_api_key"
gcloud secrets versions access latest --secret="gemini_api_key"

# Update if needed
echo "new-key" | gcloud secrets versions add openai_api_key --data-file=-
```

### **"Daily budget exceeded"**
```bash
# Check usage
curl https://YOUR_SERVICE_URL/api/cost-summary/business-id | jq

# View budget limits
curl https://YOUR_SERVICE_URL/api/budget/status | jq
```

### **"Vector DB not ready"**
```bash
# Check if deployed
python backend/utils/vertex_ai_vector_db.py get_index_stats

# If not deployed
python backend/utils/vertex_ai_vector_db.py deploy_endpoint
```

### **"Port 8080 already in use"**
```bash
# Use different port locally
PORT=8081 python backend/main_v2.py
```

---

## 📈 Monitoring Commands

```bash
# Real-time logs (follow mode)
gcloud run logs read raptorflow-backend --region=us-central1 --follow

# Recent logs
gcloud run logs read raptorflow-backend --region=us-central1 --limit=50

# Filter by error level
gcloud run logs read raptorflow-backend --region=us-central1 \
  --filter="severity>=ERROR"

# View service metrics
gcloud run services describe raptorflow-backend --region=us-central1

# Current usage/requests
gcloud monitoring read \
  --resource=cloud_run_revision \
  --start-time=-1h
```

---

## 🔐 Security Commands

```bash
# List all secrets
gcloud secrets list --filter='labels.app:raptorflow'

# Create new secret
echo "value" | gcloud secrets create new_secret_name \
  --data-file=- --replication-policy="automatic"

# Rotate secret (create new version)
echo "new_value" | gcloud secrets versions add secret_name --data-file=-

# Delete secret (irreversible after 30 days)
gcloud secrets delete old_secret_name
```

---

## 📊 Cost Tracking

```bash
# Get cost summary for business
curl https://YOUR_SERVICE_URL/api/cost-summary/business-123 | jq

# Expected output:
{
  "budget": {
    "tier": "pro",
    "daily_limit": 50.0,
    "spent_today": 12.50,
    "remaining_today": 37.50,
    "usage_percent": 25
  },
  "usage_history": {
    "dates": ["2025-01-18", ...],
    "daily_costs": [5.20, 8.50, ...],
    "average_cost_per_request": 0.35
  }
}
```

---

## 🚀 Advanced Usage

### **Enable Thinking Tokens (GPT-5 reasoning)**
```python
result = await ai.execute_with_fallback(
    task_type="sostac_analysis",
    messages=[...],
    reasoning_effort="high"  # "minimal", "medium", "high"
)
# Uses thinking tokens for deeper reasoning
```

### **Stream Progress from Agent**
```python
from api.websocket_routes import emit_progress, emit_error, emit_complete

try:
    await emit_progress("biz-123", "research", "stage_1", 25, {"details": "..."})
    # ... do work ...
    await emit_progress("biz-123", "research", "stage_2", 50)
    # ... more work ...
    await emit_complete("biz-123", "research", {result})
except Exception as e:
    await emit_error("biz-123", "research", str(e))
```

### **Migrate Chroma to Vertex AI**
```python
from utils.vertex_ai_vector_db import migrate_chroma_to_vertex_ai

stats = await migrate_chroma_to_vertex_ai(
    chroma_client=chroma_client,
    vertex_ai_db=vertex_ai_db,
    embedding_service=embeddings,
    business_id="biz-123"
)
print(f"Migrated: {stats['total_migrated']}, Failed: {stats['failed']}")
```

### **Custom Model Override**
```python
# Force a specific model (bypass routing)
config = ai.MODELS["gpt-5"]  # Direct access to config
llm = ai._get_llm("gpt-5", reasoning_effort="high")
```

---

## 📞 Key Files for Reference

- **Architecture Details**: `ARCHITECTURE_V2.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **This Reference**: `QUICK_REFERENCE.md`
- **Deployment Script**: `scripts/deploy-to-gcp.sh`
- **Main Application**: `backend/main_v2.py`
- **AI Routing**: `backend/core/ai_provider_manager.py`
- **Cost Control**: `backend/middleware/cost_controller_v2.py`
- **Tests**: `backend/tests/test_ai_routing.py`

---

## 🎓 Architecture at a Glance

```
User Request
    ↓
Cost Check ← Budget Controller
    ↓
Task Routing ← AI Provider Manager
    ├─ Simple (Nano)
    ├─ Balanced (Mini)
    └─ Complex (GPT-5)
    ↓
Execute with Fallback → Gemini if needed
    ↓
Stream Progress ← WebSocket to Client
    ↓
Save Results → Supabase + Vertex AI
    ↓
Return to Client
```

---

**Everything you need is in this quick reference!** 🚀

For details, see the full architecture documentation. For questions, check the main files.

**Status:** Ready for Production ✅

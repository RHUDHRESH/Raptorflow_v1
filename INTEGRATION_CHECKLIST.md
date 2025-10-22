# Integration Checklist - Dev/Cloud Mode System

## Phase 1: Foundation Setup ✅ COMPLETE

- [x] Master configuration system (`config.py`)
- [x] Service factory pattern (`service_factories.py`)
- [x] Database layer refactoring (`db/session.py`)
- [x] Main app initialization (`main.py`)
- [x] Environment templates (`.env.dev`, `.env.cloud`)
- [x] Comprehensive documentation

---

## Phase 2: Agent Integration 🔄 IN PROGRESS

### Research Agent
- [ ] Remove hardcoded OpenAI imports
- [ ] Update to use `services.llm`
- [ ] Update embeddings to use `services.embeddings`
- [ ] Add mode checks for Perplexity fallback
- [ ] Test in dev mode
- [ ] Test in cloud mode
- [ ] Update documentation

**File**: `backend/agents/research.py` & `backend/agents/research_v2.py` & `backend/agents/research_v3_enhanced.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 1 & 4

**Estimated time**: 30 minutes

### Positioning Agent
- [ ] Remove hardcoded OpenAI imports
- [ ] Update to use `services.llm`
- [ ] Update embeddings to use `services.embeddings`
- [ ] Test in both modes
- [ ] Update documentation

**File**: `backend/agents/positioning.py` & `backend/agents/positioning_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 2

**Estimated time**: 20 minutes

### ICP Agent
- [ ] Remove hardcoded Supabase imports
- [ ] Update to use `services.vector_db`
- [ ] Update embeddings to use `services.embeddings`
- [ ] Test vector storage in both modes
- [ ] Update documentation

**File**: `backend/agents/icp.py` & `backend/agents/icp_agent_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 3

**Estimated time**: 25 minutes

### Strategy Agent
- [ ] Remove hardcoded OpenAI imports
- [ ] Update to use `services.llm`
- [ ] Test in both modes
- [ ] Update documentation

**File**: `backend/agents/strategy.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 1

**Estimated time**: 20 minutes

### Content Agent
- [ ] Remove hardcoded OpenAI imports
- [ ] Update to use `services.llm`
- [ ] Update cache calls to use `services.cache`
- [ ] Test in both modes
- [ ] Update documentation

**File**: `backend/agents/content.py` & `backend/agents/moves_content_agent_enhanced.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 5

**Estimated time**: 25 minutes

### Analytics Agent
- [ ] Remove hardcoded OpenAI imports
- [ ] Update to use `services.llm`
- [ ] Update cache calls to use `services.cache`
- [ ] Test in both modes
- [ ] Update documentation

**File**: `backend/agents/analytics.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 5

**Estimated time**: 20 minutes

### Base Agent Classes
- [ ] Update `BaseAgent` to use `services`
- [ ] Update `BaseAgentV2` to use `services`
- [ ] Update budget checking for cloud-only
- [ ] Test inheritance in derived agents

**File**: `backend/agents/base_agent.py` & `backend/agents/base_agent_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 7

**Estimated time**: 30 minutes

### Orchestrator Classes
- [ ] Update `OrchestratorV1` to work with new agents
- [ ] Update `OrchestratorV2` to be mode-aware
- [ ] Add cost checking for cloud mode only
- [ ] Test agent routing in both modes

**File**: `backend/agents/orchestrator.py` & `backend/agents/orchestrator_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 6

**Estimated time**: 40 minutes

### Reasoning & Neural Engines
- [ ] Update `ai_reasoning_engine.py` to use services
- [ ] Update `neural_network_engine.py` to use services
- [ ] Update `quantum_optimization_engine.py` to use services
- [ ] Test in both modes

**File**: `backend/agents/ai_reasoning_engine.py` etc.

**Estimated time**: 30 minutes each

---

## Phase 3: Tool Integration 🔄 NEXT

### Research Tools
- [ ] Update `perplexity_search_v2.py` to be mode-aware
- [ ] Add local search fallback for dev mode
- [ ] Update embeddings to use `services.embeddings`
- [ ] Test in both modes

**File**: `backend/tools/perplexity_search_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 4

**Estimated time**: 25 minutes

### Content Tools
- [ ] Remove hardcoded providers
- [ ] Update to use `services.llm` and `services.cache`
- [ ] Test in both modes

**File**: `backend/tools/content_tools_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 1

**Estimated time**: 20 minutes

### Analytics Tools
- [ ] Update to use `services.cache` for caching
- [ ] Update embeddings to use `services.embeddings`
- [ ] Test in both modes

**File**: `backend/tools/analytics_tools_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 5

**Estimated time**: 20 minutes

### Competitor Analysis Tools
- [ ] Update `competitor_analysis_v2.py` to use services
- [ ] Add mode-aware search logic
- [ ] Test in both modes

**File**: `backend/tools/competitor_analysis_v2.py`

**Estimated time**: 25 minutes

### Evidence Graph Tools
- [ ] Update `evidence_graph_v2.py` to use `services.vector_db`
- [ ] Test vector storage in both modes

**File**: `backend/tools/evidence_graph_v2.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 3

**Estimated time**: 20 minutes

### Platform Tools
- [ ] Update `platform_recommendation_tools.py` to use services
- [ ] Test in both modes

**File**: `backend/tools/platform_recommendation_tools.py`

**Estimated time**: 15 minutes

### Audience Matching
- [ ] Update `audience_matching_tool.py` to use services
- [ ] Update `multi_platform_orchestrator.py` to use services
- [ ] Test in both modes

**File**: `backend/tools/audience_matching_tool.py` & `backend/tools/multi_platform_orchestrator.py`

**Estimated time**: 25 minutes

### Enhanced Tools
- [ ] Update `enhanced_tools_v2.py` (all 31KB) to use services
- [ ] Test in both modes

**File**: `backend/tools/enhanced_tools_v2.py`

**Estimated time**: 40 minutes

### Base Tool Class
- [ ] Update `BaseTool` to support mode-aware operations
- [ ] Ensure all tool subclasses inherit properly

**File**: `backend/tools/base_tool.py`

**Estimated time**: 15 minutes

### Other Tools
- [ ] Update `trend_monitor.py`
- [ ] Update all other specialized tools
- [ ] Test in both modes

**Estimated time**: 30 minutes total

---

## Phase 4: Middleware Integration 🔄 NEXT

### Budget Controller
- [ ] Add mode check (cloud-only budget enforcement)
- [ ] Update cost calculation for OpenAI only
- [ ] Keep dev mode unrestricted
- [ ] Test in both modes

**File**: `backend/middleware/budget_controller.py`

**Pattern**: See `AGENT_TOOL_REFACTORING_GUIDE.md` → Pattern 7

**Estimated time**: 20 minutes

### Rate Limiter
- [ ] Update to work in both modes
- [ ] Adjust limits per mode if needed
- [ ] Test in both modes

**File**: `backend/middleware/rate_limiter.py`

**Estimated time**: 15 minutes

### Subscription Rate Limiter
- [ ] Add mode check (cloud-only)
- [ ] Dev mode: unlimited usage
- [ ] Cloud mode: monthly limits
- [ ] Test in both modes

**File**: `backend/middleware/SubscriptionRateLimitMiddleware` (in `app/main.py`)

**Estimated time**: 20 minutes

### Other Middleware
- [ ] Update `cost_control.py`
- [ ] Update `ai_safety.py`
- [ ] Update `security_middleware.py`
- [ ] Update `data_quality.py`
- [ ] Update `monitoring.py`
- [ ] Update `validation.py`

**Estimated time**: 60 minutes total

---

## Phase 5: API Integration 🔄 NEXT

### Users Endpoint
- [ ] Verify works in both modes
- [ ] Test database operations
- [ ] Update documentation

**File**: `backend/app/api/v1/endpoints/users.py`

**Estimated time**: 10 minutes

### Organizations Endpoint
- [ ] Verify works in both modes
- [ ] Test database operations
- [ ] Update documentation

**File**: `backend/app/api/v1/endpoints/organizations.py`

**Estimated time**: 10 minutes

### Projects Endpoint
- [ ] Verify works in both modes
- [ ] Test database operations
- [ ] Update documentation

**File**: `backend/app/api/v1/endpoints/projects.py`

**Estimated time**: 10 minutes

### Indicators Endpoint
- [ ] Verify works in both modes
- [ ] Test vector storage
- [ ] Update documentation

**File**: `backend/app/api/v1/endpoints/indicators.py`

**Estimated time**: 10 minutes

### Payments Endpoint
- [ ] Update to disable in dev mode
- [ ] Verify works in cloud mode only
- [ ] Test documentation

**File**: `backend/app/api/v1/endpoints/payments.py`

**Estimated time**: 15 minutes

### Additional Endpoints
- [ ] Create threat_actors endpoint if needed
- [ ] Create campaigns endpoint if needed
- [ ] Create vulnerabilities endpoint if needed

**Estimated time**: 30 minutes total

---

## Phase 6: Testing 🔄 NEXT

### Unit Tests
- [ ] Test config loading
- [ ] Test service factory creation
- [ ] Test each service class
- [ ] Test mode checking

**Estimated time**: 2 hours

### Integration Tests
- [ ] Test agent in dev mode
- [ ] Test agent in cloud mode
- [ ] Test tool in dev mode
- [ ] Test tool in cloud mode
- [ ] Test mode switching

**Estimated time**: 3 hours

### End-to-End Tests
- [ ] Test full workflow in dev mode
- [ ] Test full workflow in cloud mode
- [ ] Test data migration between modes
- [ ] Performance testing

**Estimated time**: 4 hours

### Performance Tests
- [ ] LLM latency (dev vs cloud)
- [ ] Embeddings latency (dev vs cloud)
- [ ] Vector search latency (dev vs cloud)
- [ ] Cache hit rate

**Estimated time**: 2 hours

---

## Phase 7: Documentation Updates 🔄 NEXT

### Docstrings
- [ ] Add mode information to all modified functions
- [ ] Document service factory usage
- [ ] Document mode-specific behavior

**Estimated time**: 2 hours

### README Updates
- [ ] Update backend README with mode info
- [ ] Add examples for both modes
- [ ] Add troubleshooting section

**Estimated time**: 1 hour

### API Documentation
- [ ] Update `/docs` with mode information
- [ ] Document mode-specific endpoints
- [ ] Add mode examples to schemas

**Estimated time**: 1 hour

### Deployment Guides
- [ ] Update dev deployment guide
- [ ] Update cloud deployment guide
- [ ] Add mode switching section

**Estimated time**: 1 hour

---

## Phase 8: Deployment & Verification 🔄 FINAL

### Pre-Deployment
- [ ] All tests passing in dev mode
- [ ] All tests passing in cloud mode
- [ ] No hardcoded API keys remaining
- [ ] All documentation updated
- [ ] Performance acceptable

**Estimated time**: 1 hour

### Deploy to Dev Environment
- [ ] Deploy with `EXECUTION_MODE=dev`
- [ ] Verify all services running
- [ ] Test full workflow
- [ ] Monitor logs

**Estimated time**: 30 minutes

### Deploy to Cloud Environment
- [ ] Deploy with `EXECUTION_MODE=cloud`
- [ ] Verify all services running
- [ ] Test full workflow
- [ ] Monitor costs
- [ ] Monitor logs

**Estimated time**: 30 minutes

### Post-Deployment
- [ ] Monitor performance
- [ ] Check error logs
- [ ] Verify budget tracking
- [ ] Get team feedback
- [ ] Document lessons learned

**Estimated time**: 1 hour

---

## Summary

### Total Effort Estimation

| Phase | Tasks | Estimated Time |
|-------|-------|-----------------|
| 1. Foundation | 6 items | ✅ Complete |
| 2. Agents | 9 agents + base/orchestrator | 8-10 hours |
| 3. Tools | 10+ tools | 4-5 hours |
| 4. Middleware | 6 middleware | 2 hours |
| 5. API | 5 endpoints | 1 hour |
| 6. Testing | Unit, integration, E2E, performance | 11 hours |
| 7. Documentation | Code, README, API, deployment | 5 hours |
| 8. Deployment | Setup and verification | 2 hours |
| **TOTAL** | **~38 hours** | **1-2 weeks** |

### Recommended Schedule

**Week 1:**
- Phase 2: Agent Integration (Days 1-2)
- Phase 3: Tool Integration (Days 2-3)
- Phase 4: Middleware Integration (Day 3)

**Week 2:**
- Phase 5: API Integration (Day 1)
- Phase 6: Testing (Days 1-2)
- Phase 7: Documentation (Days 3)
- Phase 8: Deployment & Verification (Days 3-4)

---

## Quick Reference

### Files to Check for Agent Integration

**Agent files:**
- `backend/agents/research.py`
- `backend/agents/positioning.py`
- `backend/agents/icp.py`
- `backend/agents/strategy.py`
- `backend/agents/content.py`
- `backend/agents/analytics.py`
- `backend/agents/base_agent.py`
- `backend/agents/orchestrator.py`

**Replace patterns:**
```python
# ❌ OLD
from openai import AsyncOpenAI
llm = AsyncOpenAI()

# ✅ NEW
from app.core.service_factories import services
response = await services.llm.generate(prompt)
```

### Files to Check for Tool Integration

**Tool files:**
- `backend/tools/perplexity_search_v2.py`
- `backend/tools/content_tools_v2.py`
- `backend/tools/analytics_tools_v2.py`
- `backend/tools/competitor_analysis_v2.py`
- `backend/tools/evidence_graph_v2.py`
- `backend/tools/base_tool.py`

**Replace patterns:**
```python
# ❌ OLD
from supabase import create_client
db = create_client(url, key)

# ✅ NEW
from app.core.service_factories import services
results = await services.vector_db.search(embedding)
```

### Files to Check for Middleware Integration

**Middleware files:**
- `backend/middleware/budget_controller.py`
- `backend/middleware/rate_limiter.py`

**Replace patterns:**
```python
# ❌ OLD
# Always check budget

# ✅ NEW
from app.core.config import settings
if settings.is_cloud_mode:
    await self.check_budget()
```

---

## Progress Tracking

Print or bookmark this page and check off each item as you complete it.

**Current Status**: Phase 1 Complete ✅ | Phase 2-8 Pending 🔄

---

## Getting Help

- **Refactoring patterns**: See `AGENT_TOOL_REFACTORING_GUIDE.md`
- **Configuration issues**: See `MODE_SWITCHING_GUIDE.md` → Troubleshooting
- **Architecture questions**: See `IMPLEMENTATION_SUMMARY.md`
- **Service API reference**: See code comments in `service_factories.py`

---

**Good luck with the integration! 🚀**

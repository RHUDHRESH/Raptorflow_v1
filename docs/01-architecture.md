# Architecture

**System design, service boundaries, data flow, and technology decisions**

## Overview

RaptorFlow ADAPT is a multi-service application designed for cyber threat intelligence automation and defense. The architecture follows a service-oriented approach with clear boundaries, enabling independent scaling and deployment.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             │ HTTPS                          │ HTTPS
             ▼                                ▼
    ┌────────────────┐                ┌──────────────┐
    │   Cloud CDN    │                │  Razorpay    │
    │   (Static)     │                │  (Webhooks)  │
    └────────┬───────┘                └──────┬───────┘
             │                               │
             │                               │
    ┌────────▼────────────────────────────────▼──────────┐
    │             Cloud Load Balancer                    │
    │         (SSL termination, DDoS protection)         │
    └────────┬──────────────────────────┬─────────────────┘
             │                          │
             │                          │
    ┌────────▼────────┐        ┌────────▼────────┐
    │   apps/web      │        │    apps/api     │
    │   (Next.js)     │───────▶│   (FastAPI)     │
    │   Cloud Run     │  HTTP  │   Cloud Run     │
    └─────────────────┘        └────┬────┬───────┘
                                    │    │
                ┌───────────────────┘    │
                │                        │
       ┌────────▼────────┐      ┌────────▼────────┐
       │   apps/worker   │      │   Cloud SQL     │
       │   (Celery/RQ)   │      │  (PostgreSQL)   │
       │   Cloud Run     │      └─────────────────┘
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │     Redis       │
       │ (Memorystore)   │
       └─────────────────┘
                │
       ┌────────▼────────┐
       │  Cloud Storage  │
       │   (Assets)      │
       └─────────────────┘
```

## Service Boundaries

### apps/web (Frontend)

**Technology**: Next.js 14 with App Router

**Responsibilities**:
- Server-side rendering (SSR) and incremental static regeneration (ISR)
- User interface and interactions
- Client-side state management
- API client for backend communication
- Authentication UI flows

**Key Principles**:
- ❌ NO direct database access
- ❌ NO business logic beyond presentation
- ✅ All data through API calls
- ✅ Thin client, thick server

**External Dependencies**:
- `apps/api` for all data operations
- Razorpay SDK for payment UI
- Supabase Auth for authentication

**Deployment**:
- Docker container on Cloud Run
- Static assets served via Cloud CDN
- Auto-scaling based on traffic

### apps/api (Backend Gateway)

**Technology**: FastAPI with uvicorn

**Responsibilities**:
- Authentication & authorization (JWT validation)
- Business logic orchestration
- Database operations (CRUD)
- Multi-tenancy enforcement (org scoping)
- Rate limiting & request validation
- Payment processing & webhooks
- AI agent orchestration
- API documentation (OpenAPI)

**Key Principles**:
- Single entry point for all business operations
- Enforces all security policies
- Validates all inputs with Pydantic
- Returns structured error responses
- Emits structured logs and metrics

**External Dependencies**:
- Cloud SQL (PostgreSQL) for primary data
- Redis for caching and rate limiting
- Cloud Storage for file uploads
- Supabase Auth JWKS for JWT verification
- Razorpay API for payment operations
- OpenAI/Gemini/Perplexity for AI operations

**Deployment**:
- Docker container on Cloud Run
- Multiple instances with auto-scaling
- Health checks on `/health` and `/ready`
- Graceful shutdown handling

### apps/worker (Background Jobs)

**Technology**: Celery or RQ with Redis

**Responsibilities**:
- Long-running AI agent tasks
- Scheduled jobs (trend monitoring, reports)
- Async webhook processing
- Bulk operations (exports, imports)
- Email notifications
- Report generation

**Key Principles**:
- Idempotent job execution
- Retry logic with exponential backoff
- Dead letter queue for failed jobs
- Cost tracking for LLM tokens
- Progress reporting for long tasks

**Queue Structure**:
- `priority`: High-priority user requests (< 5s)
- `default`: Standard async tasks (< 60s)
- `long-running`: AI agents, reports (< 30min)
- `scheduled`: Cron-triggered jobs

**Deployment**:
- Docker container on Cloud Run
- Separate containers per queue (optional)
- Min instances = 1 (for scheduled jobs)
- Max instances = 10 (cost control)

## Data Architecture

### Database (Cloud SQL - PostgreSQL 15)

**Primary data store for all application state**

**Key Tables**:

```sql
-- Identity & Access
users, organizations, memberships, api_keys

-- Billing
plans, subscriptions, payments, ledger_entries, invoices

-- Core Domain
projects, agents, threat_actors, tactics, indicators

-- Observability
audit_logs, api_usage_logs

-- System
alembic_version, schema_migrations
```

**Tenancy Model**:
- Every row has `org_id` (UUID)
- Optional `workspace_id` for sub-scopes
- Row-level security via application logic
- Database-level policies (optional, future)

**Indexes**:
- `idx_org_id` on all tenant tables
- `idx_created_at` for time-series queries
- `idx_status` for state-based filtering
- Composite indexes for common filters

**Backup Strategy**:
- Automated daily snapshots (30-day retention)
- Point-in-time recovery (7 days)
- Quarterly restore testing
- Geo-redundant storage

### Cache & Queue (Redis - Cloud Memorystore)

**Use Cases**:
- Session storage (JWT refresh tokens)
- Rate limiting buckets (token bucket algorithm)
- Job queue (Celery/RQ backend)
- Temporary data (OTP codes, preview data)
- Cache warm data (user profiles, org settings)

**Eviction Policy**: `volatile-lru` (evict LRU keys with TTL)

**High Availability**: Multi-zone replica for production

### Object Storage (Cloud Storage)

**Use Cases**:
- User uploads (threat intel PDFs, YARA rules)
- Generated reports (PDF, CSV, JSON exports)
- Agent execution artifacts (logs, traces)
- Static assets (if not using CDN)

**Bucket Structure**:
- `raptorflow-{env}-uploads/`: User-uploaded files
- `raptorflow-{env}-exports/`: Generated exports
- `raptorflow-{env}-artifacts/`: Agent outputs

**Security**:
- Signed URLs with 1-hour expiry
- CORS policy for web uploads
- Lifecycle policy (delete after 90 days)
- Encryption at rest (Google-managed keys)

### Secrets (Secret Manager)

**All sensitive configuration**:
- Database credentials
- API keys (OpenAI, Razorpay, Supabase)
- JWT signing keys
- Webhook secrets
- OAuth client secrets

**Access Control**:
- Service-specific service accounts
- Least-privilege IAM policies
- Audit logging enabled

## Data Flow

### 1. User Request Flow

```
User Browser
    │
    ├─→ Static Asset? ──→ Cloud CDN ──→ Response
    │
    └─→ Dynamic Page ──→ apps/web (SSR)
            │
            └─→ API call ──→ apps/api
                    │
                    ├─→ Validate JWT (Supabase JWKS)
                    ├─→ Load user membership & org
                    ├─→ Check rate limits (Redis)
                    ├─→ Execute business logic
                    │       │
                    │       ├─→ Database query (with org_id filter)
                    │       ├─→ External API call (OpenAI, etc.)
                    │       └─→ Enqueue job (Redis → apps/worker)
                    │
                    ├─→ Log request (structlog)
                    ├─→ Emit metrics (OTEL)
                    └─→ Return JSON response
```

### 2. Background Job Flow

```
apps/api enqueues job
    │
    └─→ Redis (job queue)
            │
            └─→ apps/worker picks up job
                    │
                    ├─→ Fetch job data from DB
                    ├─→ Execute long-running task
                    │       │
                    │       ├─→ Call LLM API
                    │       ├─→ Update progress in DB
                    │       └─→ Store result in GCS
                    │
                    ├─→ Update job status (DB)
                    ├─→ Emit metrics (token cost, duration)
                    └─→ Send notification (optional)
```

### 3. Payment Flow

```
User initiates payment
    │
    └─→ apps/web calls API
            │
            └─→ apps/api creates order
                    │
                    ├─→ Razorpay.create_order()
                    ├─→ Store order in DB (pending)
                    └─→ Return order_id + key
                            │
                            └─→ apps/web shows Razorpay UI
                                    │
                                    └─→ User completes payment
                                            │
                                            └─→ Razorpay webhook
                                                    │
                                                    └─→ apps/api /webhooks/razorpay
                                                            │
                                                            ├─→ Verify signature (HMAC)
                                                            ├─→ Check idempotency (Redis)
                                                            ├─→ Update payment (captured)
                                                            ├─→ Create ledger entries
                                                            ├─→ Update subscription status
                                                            └─→ Emit event (for worker)
```

## Authentication & Authorization

### Authentication Flow

```
1. User signs in via Supabase Auth (OAuth / Email)
2. Supabase returns access_token (JWT) + refresh_token
3. apps/web stores tokens in httpOnly cookies
4. On API request:
   - apps/web sends: Authorization: Bearer {access_token}
   - apps/api validates JWT against Supabase JWKS
   - apps/api extracts claims (sub, email, exp)
   - apps/api loads user from DB (by auth_sub)
   - apps/api loads org memberships
   - apps/api enforces RBAC on route
```

### Authorization Model

**Roles** (per organization membership):
- `owner`: Full control (billing, members, delete org)
- `admin`: Manage projects, members (no billing)
- `editor`: Create/edit projects and agents
- `viewer`: Read-only access

**Permission Matrix**:

| Action | Owner | Admin | Editor | Viewer |
|--------|-------|-------|--------|--------|
| View projects | ✅ | ✅ | ✅ | ✅ |
| Create project | ✅ | ✅ | ✅ | ❌ |
| Edit project | ✅ | ✅ | ✅ | ❌ |
| Delete project | ✅ | ✅ | ❌ | ❌ |
| Manage members | ✅ | ✅ | ❌ | ❌ |
| View billing | ✅ | ❌ | ❌ | ❌ |
| Manage billing | ✅ | ❌ | ❌ | ❌ |

**Implementation** (FastAPI):

```python
from fastapi import Depends, HTTPException
from typing import Annotated

async def require_role(min_role: Role = Role.VIEWER):
    async def check(principal: Annotated[Principal, Depends(get_principal)]):
        if principal.role < min_role:
            raise HTTPException(403, "Insufficient permissions")
        return principal
    return check

@router.post("/projects", dependencies=[Depends(require_role(Role.EDITOR))])
async def create_project(data: ProjectCreate, principal: Principal):
    # principal.org_id is automatically available
    pass
```

## API Design Principles

### Versioning
- Prefix: `/v1/` (never break, deprecate with headers)
- Future: `/v2/` when breaking changes needed

### Error Responses

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {"field": "email", "message": "Invalid email format"}
    ],
    "trace_id": "7f3d9e2a-4b1c-4f5e-9d8a-1c2b3d4e5f6g"
  }
}
```

### Pagination

```
GET /v1/projects?page[size]=20&page[cursor]=eyJ...
```

Response:
```json
{
  "data": [...],
  "meta": {
    "next_cursor": "eyJ...",
    "has_more": true
  }
}
```

### Rate Limiting Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642521600
```

## Scaling Strategy

### Horizontal Scaling
- **apps/web**: Auto-scale 1-10 instances based on CPU (target: 70%)
- **apps/api**: Auto-scale 2-20 instances based on request count
- **apps/worker**: Fixed 1-5 instances per queue

### Vertical Scaling
- **Database**: Start with 2 vCPU, 8GB RAM; scale to 8 vCPU, 32GB RAM
- **Redis**: Standard tier (1.5GB) → High Availability (5GB)

### Caching Strategy
1. **CDN**: Static assets (frontend build, images)
2. **Application**: Frequently accessed data (user profiles, org settings)
3. **Database**: Connection pooling (SQLAlchemy pool_size=20)

### Database Optimization
- Read replicas for analytics queries (future)
- Partitioning for large tables (audit_logs, api_usage_logs)
- Materialized views for complex aggregations

## Technology Decisions

### Why FastAPI?
- ✅ Async/await native (high concurrency)
- ✅ Pydantic v2 (fast validation)
- ✅ Auto-generated OpenAPI docs
- ✅ Type hints + IDE support
- ✅ Large ecosystem

### Why Next.js?
- ✅ React + SSR/ISR out of the box
- ✅ App Router (modern patterns)
- ✅ Edge-ready
- ✅ Excellent DX
- ✅ Strong community

### Why PostgreSQL?
- ✅ ACID compliance (financial data)
- ✅ JSONB for flexible schemas
- ✅ Full-text search
- ✅ pgvector for embeddings (future)
- ✅ Battle-tested at scale

### Why Cloud Run?
- ✅ Serverless (no cluster management)
- ✅ Scale to zero (cost savings)
- ✅ Fast cold starts (<1s)
- ✅ Easy gradual rollouts
- ❌ Migrate to GKE if needed (same containers)

## Future Enhancements

### Phase 2 (Q2 2025)
- WebSocket support for real-time updates
- GraphQL API for complex queries
- Multi-region deployment (Asia + US)
- Database read replicas

### Phase 3 (Q3 2025)
- Kubernetes migration for advanced orchestration
- Event sourcing for audit trail
- CQRS for read-heavy operations
- Vector search for threat intelligence

---

**See Also**:
- [02-setup-local.md](./02-setup-local.md) - Local development setup
- [04-security.md](./04-security.md) - Security architecture
- [08-deployments.md](./08-deployments.md) - Deployment procedures

# Accounts, Organizations & Billing

**Multi-tenancy model, RBAC, subscription billing, and payment processing**

## Overview

RaptorFlow uses a **hierarchical multi-tenancy model** with:
- **Users**: Individual accounts (authenticated via Supabase)
- **Organizations**: Billing entities (one or more users)
- **Workspaces**: Optional sub-grouping within organizations
- **Projects**: Threat intelligence projects within org/workspace
- **Memberships**: User-to-org relationships with roles

## Entity Relationship

```
User ──┐
       ├──▶ Membership ──▶ Organization ──▶ Subscription ──▶ Plan
User ──┘                        │
                                ├──▶ Projects
                                ├──▶ API Keys
                                ├──▶ Payments
                                └──▶ Audit Logs
```

## Data Model

### Users

**Purpose**: Local profile linked to external auth provider (Supabase)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_sub TEXT UNIQUE NOT NULL,              -- Supabase UID (external)
    email TEXT NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_auth_sub ON users(auth_sub);
CREATE INDEX idx_users_email ON users(email);
```

**Fields**:
- `auth_sub`: External auth provider subject ID (Supabase UID)
- `email`: User's email (synced from auth provider)
- `display_name`: User's chosen display name
- `avatar_url`: Profile picture URL

**Notes**:
- Users are **created automatically** on first sign-in
- Email is **not used for authentication** (handled by Supabase)
- Local profile stores app-specific data only

### Organizations

**Purpose**: Top-level tenant and billing entity

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,                  -- URL-friendly identifier
    billing_email TEXT,
    website TEXT,
    industry TEXT,
    size TEXT,                                   -- startup, small, medium, enterprise
    logo_url TEXT,
    settings JSONB NOT NULL DEFAULT '{}',       -- Org-specific config
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_organizations_slug ON organizations(slug);
```

**Fields**:
- `name`: Organization display name
- `slug`: URL-friendly identifier (e.g., "acme-corp")
- `billing_email`: Email for invoices (may differ from owner email)
- `settings`: JSON object for org preferences

**Settings Example**:
```json
{
  "timezone": "Asia/Kolkata",
  "language": "en",
  "notification_preferences": {
    "email_alerts": true,
    "slack_webhook": "https://hooks.slack.com/..."
  },
  "security": {
    "require_2fa": false,
    "allowed_ip_ranges": ["1.2.3.0/24"]
  }
}
```

### Memberships

**Purpose**: User-to-org relationship with role

```sql
CREATE TYPE role AS ENUM ('owner', 'admin', 'editor', 'viewer');

CREATE TABLE memberships (
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role role NOT NULL,
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (org_id, user_id)
);

CREATE INDEX idx_memberships_user_id ON memberships(user_id);
CREATE INDEX idx_memberships_org_id ON memberships(org_id);
```

**Roles** (hierarchical):

| Role | Level | Description |
|------|-------|-------------|
| **Owner** | 4 | Full control (billing, delete org, manage all) |
| **Admin** | 3 | Manage projects, members (no billing) |
| **Editor** | 2 | Create/edit projects and agents |
| **Viewer** | 1 | Read-only access |

**Constraints**:
- Every org must have **at least one owner**
- Owners cannot be removed unless another owner exists
- Users can be members of multiple orgs

### Workspaces (Optional)

**Purpose**: Sub-grouping within organizations (e.g., teams, departments)

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, name)
);

CREATE INDEX idx_workspaces_org_id ON workspaces(org_id);
```

**Use Cases**:
- Large orgs with multiple teams
- Isolating projects by department
- Different security policies per workspace

**Note**: Workspaces are **optional**. Most orgs use just org-level scoping.

### Projects

**Purpose**: Container for threat intelligence work

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_org_id ON projects(org_id);
CREATE INDEX idx_projects_workspace_id ON projects(workspace_id);
```

**Scoping**:
- All queries **must** filter by `org_id`
- Optional filter by `workspace_id` if using workspaces

## Role-Based Access Control (RBAC)

### Permission Matrix

| Action | Owner | Admin | Editor | Viewer |
|--------|-------|-------|--------|--------|
| **Organizations** |
| View org details | ✅ | ✅ | ✅ | ✅ |
| Update org settings | ✅ | ❌ | ❌ | ❌ |
| Delete org | ✅ | ❌ | ❌ | ❌ |
| **Members** |
| View members | ✅ | ✅ | ✅ | ✅ |
| Invite members | ✅ | ✅ | ❌ | ❌ |
| Remove members | ✅ | ✅ | ❌ | ❌ |
| Change roles | ✅ | ✅ (not owners) | ❌ | ❌ |
| **Projects** |
| View projects | ✅ | ✅ | ✅ | ✅ |
| Create projects | ✅ | ✅ | ✅ | ❌ |
| Edit projects | ✅ | ✅ | ✅ | ❌ |
| Delete projects | ✅ | ✅ | ❌ | ❌ |
| **Agents** |
| Run agents | ✅ | ✅ | ✅ | ❌ |
| Configure agents | ✅ | ✅ | ✅ | ❌ |
| View results | ✅ | ✅ | ✅ | ✅ |
| **Billing** |
| View billing | ✅ | ❌ | ❌ | ❌ |
| Manage subscription | ✅ | ❌ | ❌ | ❌ |
| View invoices | ✅ | ❌ | ❌ | ❌ |
| Update payment method | ✅ | ❌ | ❌ | ❌ |
| **API Keys** |
| View API keys | ✅ | ✅ | ❌ | ❌ |
| Create API keys | ✅ | ✅ | ❌ | ❌ |
| Revoke API keys | ✅ | ✅ | ❌ | ❌ |

### Implementation (FastAPI)

```python
from enum import IntEnum
from fastapi import Depends, HTTPException

class Role(IntEnum):
    VIEWER = 1
    EDITOR = 2
    ADMIN = 3
    OWNER = 4

class Principal:
    def __init__(self, user: User, org_id: UUID, role: Role):
        self.user = user
        self.org_id = org_id
        self.role = role

    def can(self, action: str, resource: str = None) -> bool:
        """Check if principal can perform action on resource."""
        permissions = {
            "view_org": Role.VIEWER,
            "edit_org": Role.OWNER,
            "invite_member": Role.ADMIN,
            "create_project": Role.EDITOR,
            "delete_project": Role.ADMIN,
            "manage_billing": Role.OWNER,
        }
        required_role = permissions.get(action, Role.OWNER)
        return self.role >= required_role

async def require_role(min_role: Role):
    """Dependency to enforce minimum role."""
    async def check(principal: Principal = Depends(get_principal)):
        if principal.role < min_role:
            raise HTTPException(403, f"Requires {min_role.name} role")
        return principal
    return check

# Usage in routes
@router.post("/projects", dependencies=[Depends(require_role(Role.EDITOR))])
async def create_project(data: ProjectCreate, principal: Principal):
    # principal.org_id is automatically available
    project = Project(org_id=principal.org_id, **data.dict())
    await db.save(project)
    return project
```

## Subscription Billing

### Plans

**Purpose**: Define product tiers and limits

```sql
CREATE TABLE plans (
    id TEXT PRIMARY KEY,                        -- free, pro, enterprise
    name TEXT NOT NULL,
    description TEXT,
    price_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    billing_period TEXT NOT NULL,               -- monthly, yearly

    -- Rate limits
    api_requests_per_month INT NOT NULL,
    ai_tokens_per_month INT NOT NULL,

    -- Feature flags
    features JSONB NOT NULL DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Plan Tiers**:

| Plan | Price | API Requests | AI Tokens | Features |
|------|-------|--------------|-----------|----------|
| **Free** | ₹0 | 10,000/mo | 10,000/mo | Basic threat intel |
| **Pro** | ₹3,500/mo | 100,000/mo | 500,000/mo | AI agents, exports, trend monitoring |
| **Enterprise** | Custom | Unlimited | Custom | Dedicated support, SLA, custom integrations |

**Features JSON** (example for Pro plan):
```json
{
  "ai_agents": true,
  "trend_monitoring": true,
  "exports": true,
  "api_access": true,
  "priority_support": false,
  "sla": false,
  "custom_integrations": false,
  "dedicated_account_manager": false
}
```

### Subscriptions

**Purpose**: Link org to plan with billing status

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    plan_id TEXT NOT NULL REFERENCES plans(id),
    status TEXT NOT NULL,                       -- trialing, active, past_due, canceled

    -- Trial
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,

    -- Billing period
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,

    -- Usage tracking
    api_requests_used INT NOT NULL DEFAULT 0,
    ai_tokens_used INT NOT NULL DEFAULT 0,

    -- Cancellation
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    canceled_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(org_id)  -- One subscription per org
);

CREATE INDEX idx_subscriptions_org_id ON subscriptions(org_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

**Status Flow**:
```
trialing → active → past_due → canceled
    ↓         ↓
    └─────────┴──────▶ active (after payment)
```

**Status Definitions**:
- `trialing`: In trial period (no payment required)
- `active`: Paid and current
- `past_due`: Payment failed, grace period (7 days)
- `canceled`: Subscription ended

### Payments

**Purpose**: Record payment transactions from Razorpay

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,

    -- Razorpay details
    provider TEXT NOT NULL DEFAULT 'razorpay',
    provider_payment_id TEXT UNIQUE NOT NULL,   -- Razorpay payment ID
    provider_order_id TEXT NOT NULL,            -- Razorpay order ID

    -- Amount
    amount_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',

    -- Status
    status TEXT NOT NULL,                       -- pending, captured, refunded, failed

    -- Payment method
    method TEXT,                                 -- card, upi, netbanking, wallet

    -- Metadata
    description TEXT,
    meta JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    captured_at TIMESTAMPTZ,
    refunded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_org_id ON payments(org_id);
CREATE INDEX idx_payments_provider_payment_id ON payments(provider_payment_id);
CREATE INDEX idx_payments_status ON payments(status);
```

### Ledger (Double-Entry Accounting)

**Purpose**: Maintain accurate financial records

```sql
CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id),

    -- Transaction
    entry_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account TEXT NOT NULL,                      -- cash, ar, revenue, refunds
    direction TEXT NOT NULL,                    -- DR or CR

    -- Amount
    amount_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',

    -- Reference
    ref_type TEXT,                              -- payment, refund, credit
    ref_id TEXT,                                -- ID of referenced entity
    description TEXT,

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_direction CHECK (direction IN ('DR', 'CR'))
);

CREATE INDEX idx_ledger_org_id ON ledger_entries(org_id);
CREATE INDEX idx_ledger_entry_at ON ledger_entries(entry_at);
CREATE INDEX idx_ledger_account ON ledger_entries(account);
```

**Account Types**:
- `cash`: Bank account balance
- `ar` (Accounts Receivable): Money owed to us
- `revenue`: Income from subscriptions
- `refunds`: Money refunded to customers
- `discounts`: Promotional discounts

**Example: Payment Capture**:
```python
# Payment of ₹3,500 captured
await create_ledger_entries([
    LedgerEntry(org_id=org_id, account="cash", direction="DR", amount_cents=350000),
    LedgerEntry(org_id=org_id, account="revenue", direction="CR", amount_cents=350000),
])
```

**Example: Refund**:
```python
# Refund of ₹3,500
await create_ledger_entries([
    LedgerEntry(org_id=org_id, account="refunds", direction="DR", amount_cents=350000),
    LedgerEntry(org_id=org_id, account="cash", direction="CR", amount_cents=350000),
])
```

### Invoices

**Purpose**: Generate PDF invoices for payments

```sql
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,

    -- Invoice details
    invoice_number TEXT UNIQUE NOT NULL,        -- INV-2025-001
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due_at TIMESTAMPTZ,

    -- Amounts
    subtotal_cents INT NOT NULL,
    tax_cents INT NOT NULL DEFAULT 0,           -- GST 18%
    total_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',

    -- Status
    status TEXT NOT NULL,                       -- draft, issued, paid, void
    paid_at TIMESTAMPTZ,

    -- PDF
    pdf_url TEXT,                               -- GCS URL to PDF

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invoices_org_id ON invoices(org_id);
CREATE INDEX idx_invoices_invoice_number ON invoices(invoice_number);
```

## Payment Flow (Razorpay)

### 1. Order Creation

```python
@router.post("/billing/create-order")
async def create_payment_order(
    plan_id: str,
    principal: Principal = Depends(get_principal_owner),
):
    """Create Razorpay order for subscription payment."""

    # Get plan
    plan = await get_plan(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")

    # Create Razorpay order
    razorpay_order = razorpay_client.order.create({
        "amount": plan.price_cents,  # In paise
        "currency": plan.currency,
        "receipt": f"sub_{principal.org_id}_{int(time.time())}",
        "notes": {
            "org_id": str(principal.org_id),
            "plan_id": plan_id,
        }
    })

    # Store pending payment
    payment = Payment(
        org_id=principal.org_id,
        provider_order_id=razorpay_order["id"],
        amount_cents=plan.price_cents,
        currency=plan.currency,
        status="pending",
    )
    await db.save(payment)

    # Return order details for frontend
    return {
        "order_id": razorpay_order["id"],
        "amount": plan.price_cents,
        "currency": plan.currency,
        "key": RAZORPAY_KEY_ID,  # Public key for frontend
    }
```

### 2. Frontend Payment

```typescript
// Frontend (Next.js)
const handlePayment = async () => {
  const { order_id, amount, currency, key } = await createOrder(planId);

  const options = {
    key: key,
    order_id: order_id,
    amount: amount,
    currency: currency,
    name: "RaptorFlow",
    description: "Pro Plan Subscription",
    handler: async (response) => {
      // Payment successful
      await verifyPayment(response);
    },
    prefill: {
      email: user.email,
      name: user.displayName,
    },
  };

  const rzp = new Razorpay(options);
  rzp.open();
};
```

### 3. Webhook Capture

```python
@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(...),
):
    """Handle Razorpay payment webhook."""

    # Verify signature
    body = await request.body()
    verify_razorpay_signature(body, x_razorpay_signature)

    # Parse event
    event = json.loads(body)
    payment_entity = event["payload"]["payment"]["entity"]
    payment_id = payment_entity["id"]

    # Idempotency check (prevent duplicate processing)
    redis_key = f"webhook:razorpay:{payment_id}"
    if await redis.exists(redis_key):
        return {"status": "ok"}  # Already processed
    await redis.setex(redis_key, 3600, "1")  # Lock for 1 hour

    # Update payment
    payment = await get_payment_by_provider_id(payment_id)
    if not payment:
        raise HTTPException(404, "Payment not found")

    payment.status = "captured"
    payment.provider_payment_id = payment_id
    payment.captured_at = datetime.utcnow()
    payment.method = payment_entity.get("method")
    await db.save(payment)

    # Create ledger entries
    await create_ledger_entries([
        LedgerEntry(
            org_id=payment.org_id,
            account="cash",
            direction="DR",
            amount_cents=payment.amount_cents,
            ref_type="payment",
            ref_id=str(payment.id),
        ),
        LedgerEntry(
            org_id=payment.org_id,
            account="revenue",
            direction="CR",
            amount_cents=payment.amount_cents,
            ref_type="payment",
            ref_id=str(payment.id),
        ),
    ])

    # Update subscription
    subscription = await get_subscription(payment.org_id)
    subscription.status = "active"
    subscription.current_period_start = datetime.utcnow()
    subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
    await db.save(subscription)

    # Generate invoice (async)
    await enqueue_job("generate_invoice", payment_id=str(payment.id))

    # Send confirmation email (async)
    await enqueue_job("send_payment_confirmation", org_id=str(payment.org_id))

    return {"status": "ok"}
```

## API Keys

**Purpose**: Programmatic access to API

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Key (hashed)
    key_prefix TEXT NOT NULL,                   -- First 8 chars (for display)
    key_hash TEXT UNIQUE NOT NULL,              -- SHA-256 hash

    -- Metadata
    name TEXT NOT NULL,                         -- User-friendly name
    scopes TEXT[] NOT NULL DEFAULT '{}',        -- Permissions

    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    last_used_ip INET,

    -- Lifecycle
    expires_at TIMESTAMPTZ,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(id),

    -- Audit
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_api_keys_org_id ON api_keys(org_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

**Scopes**:
- `read:projects`: Read project data
- `write:projects`: Create/update projects
- `run:agents`: Execute AI agents
- `read:billing`: View billing info

**Generation**:
```python
import secrets
import hashlib

def create_api_key(org_id: UUID, name: str, scopes: list[str], created_by: UUID):
    # Generate random key
    raw_key = f"rk_{secrets.token_urlsafe(32)}"

    # Hash for storage
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12]  # "rk_xxxxxxxx"

    # Store in DB
    api_key = APIKey(
        org_id=org_id,
        key_prefix=key_prefix,
        key_hash=key_hash,
        name=name,
        scopes=scopes,
        created_by=created_by,
    )
    db.add(api_key)

    # Return raw key ONCE (never show again!)
    return raw_key, api_key
```

## Usage Tracking

**Purpose**: Enforce plan limits

```python
async def track_api_request(org_id: UUID):
    """Increment API request counter for org."""
    subscription = await get_subscription(org_id)
    subscription.api_requests_used += 1

    # Check limit
    if subscription.api_requests_used > subscription.plan.api_requests_per_month:
        raise HTTPException(429, "API request limit exceeded. Please upgrade.")

    await db.save(subscription)

async def track_ai_tokens(org_id: UUID, tokens: int):
    """Track AI token usage."""
    subscription = await get_subscription(org_id)
    subscription.ai_tokens_used += tokens

    # Check limit
    if subscription.ai_tokens_used > subscription.plan.ai_tokens_per_month:
        raise HTTPException(402, "AI token limit exceeded. Please upgrade.")

    await db.save(subscription)
```

**Reset Monthly**:
```python
# Cron job (runs on 1st of each month)
async def reset_usage_counters():
    """Reset monthly usage counters for all subscriptions."""
    subscriptions = await db.query(Subscription).filter(
        Subscription.status == "active"
    ).all()

    for sub in subscriptions:
        sub.api_requests_used = 0
        sub.ai_tokens_used = 0
        sub.current_period_start = datetime.utcnow()
        sub.current_period_end = datetime.utcnow() + timedelta(days=30)

    await db.commit()
```

---

**See Also**:
- [04-security.md](./04-security.md) - Security implementation
- [01-architecture.md](./01-architecture.md) - System architecture
- [06-observability.md](./06-observability.md) - Usage metrics

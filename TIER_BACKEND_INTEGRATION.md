# Tier System Backend Integration Roadmap

**Status:** Config Updated ✅ | Implementation TODO
**Last Updated:** 2025-10-25

---

## What's Done

### 1. Canonical Tier Configuration ✅
**File:** `backend/utils/subscription_tiers.py`

- All three tiers (Breeze, Glide, Soar) fully defined
- Prices, capacities, features, collaboration limits all specified
- Helper functions: `get_tier_config()`, `validate_tier_access()`, `get_capacity_limit()`

### 2. Documentation ✅
- `TIER_DEFINITIONS.md` - Full specs (300+ lines)
- `TIER_QUICK_REFERENCE.md` - Quick lookup card
- `TIER_LOCK_SUMMARY.md` - What's locked + next steps
- This file - Backend integration roadmap

---

## What Needs to Be Built

### Phase 1: Tier Enforcement Middleware (HIGH PRIORITY)

#### 1.1 Quota Validation Middleware
**File:** `backend/middleware/tier_quota_validator.py` (NEW)

```python
class TierQuotaValidator:
    """Enforce capacity limits per tier"""

    async def validate_project_creation(user_id, business_id):
        """Check if user can create another project"""
        tier = get_user_tier(business_id)
        project_count = get_project_count(business_id)
        max_projects = get_capacity_limit(tier, 'projects')

        if max_projects != inf and project_count >= max_projects:
            raise TierLimitExceeded(
                f"You've reached {max_projects} projects on {tier}. "
                f"Upgrade to Glide for unlimited projects."
            )

    async def validate_persona_creation(business_id):
        """Check if user can add another persona"""
        tier = get_user_tier(business_id)
        persona_count = get_persona_count(business_id)
        max_personas = get_capacity_limit(tier, 'personas_active')

        if persona_count >= max_personas:
            raise TierLimitExceeded(
                f"Breeze limited to 3 personas. Upgrade to Soar for 5."
            )

    async def validate_asset_generation(business_id):
        """Check monthly asset quota"""
        tier = get_user_tier(business_id)
        assets_this_month = get_monthly_asset_count(business_id)
        limit = get_capacity_limit(tier, 'assets_per_month')

        if assets_this_month >= limit:
            raise TierLimitExceeded(
                f"Monthly limit: {limit}. Next refill: {next_reset_date}."
            )

    async def validate_research_run(business_id):
        """Check research run quota"""
        # Similar to asset validation
        pass
```

**Integration Points:**
- Add to middleware stack in `main.py`
- Call in `/api/projects`, `/api/personas`, `/api/assets/generate`, `/api/research`

#### 1.2 Feature Gating
**File:** `backend/middleware/tier_feature_gate.py` (NEW)

```python
class TierFeatureGate:
    """Gate features by tier"""

    async def check_feature_access(tier, feature_key):
        """Block access to tier-locked features"""
        is_available = validate_tier_access(tier, feature_key)

        if not is_available:
            raise FeatureNotAvailable(
                feature=feature_key,
                tier=tier,
                upgrade_tier=get_minimum_tier_for_feature(feature_key)
            )

    # Specific checkers for common features
    async def require_batch_recipes(tier):
        """Batch Recipes are Soar-only"""
        if not validate_tier_access(tier, 'batch_recipes'):
            raise FeatureNotAvailable(
                "Batch Recipes are available on Soar tier only. "
                "Upgrade to automate multi-step workflows."
            )

    async def require_rotators(tier):
        """Rotators are Soar-only"""
        # Similar to above
        pass

    async def require_qr_generation(tier):
        """QR codes require Glide or Soar"""
        if not validate_tier_access(tier, 'qr_generation'):
            raise FeatureNotAvailable("Upgrade to Glide for QR code generation.")
```

**Integration Points:**
- Decorator-style: `@require_feature('qr_generation')`
- Or inline: `await feature_gate.require_batch_recipes(user_tier)`

---

### Phase 2: Tier-Aware API Endpoints (MEDIUM PRIORITY)

#### 2.1 Subscription Endpoint Update
**File:** `backend/api/budget_routes.py` or new `backend/api/subscription_routes.py`

```python
@router.get("/api/subscription/{business_id}")
async def get_subscription(business_id: str, request: Request):
    """Return subscription info including tier config"""
    user_id = get_user_id(request)

    # Verify ownership
    verify_business_ownership(business_id, user_id)

    # Get subscription
    sub = supabase.table('subscriptions').select('*').eq('business_id', business_id).single().execute()

    # Get tier config
    tier = sub.data['tier']  # 'breeze', 'glide', 'soar'
    tier_config = get_tier_config(tier)

    # Get usage
    usage = {
        'projects': get_project_count(business_id),
        'assets_this_month': get_monthly_asset_count(business_id),
        'research_runs_this_month': get_monthly_research_count(business_id),
        'personas': get_persona_count(business_id),
        'team_members': get_team_member_count(business_id),
    }

    return {
        'tier': tier,
        'tier_config': tier_config,
        'usage': usage,
        'limits': {
            'projects': tier_config['capacity']['projects'],
            'assets_per_month': tier_config['capacity']['assets_per_month'],
            'research_runs_per_month': tier_config['capacity']['research_runs_per_month'],
            'personas': tier_config['capacity']['personas_active'],
            'channels': tier_config['dispatch']['channels'],
            'active_editor_slots': tier_config['collaboration']['active_editor_slots'],
        },
        'upgrade_available': tier != 'soar',
        'next_tier': get_next_tier(tier),
    }
```

#### 2.2 Feature Availability Endpoint
**New endpoint:** `GET /api/tier/features/{business_id}`

```python
@router.get("/api/tier/features/{business_id}")
async def get_available_features(business_id: str):
    """Return all features + availability for this tier"""
    tier = get_user_tier(business_id)
    tier_config = get_tier_config(tier)

    return {
        'tier': tier,
        'features': tier_config['features'],
        'strategy_features': tier_config['strategy_features'],
        'creation': tier_config['creation'],
        'dispatch': tier_config['dispatch'],
        'measurement': tier_config['measurement'],
        'governance': tier_config['governance'],
    }
```

#### 2.3 Upgrade Path Endpoint
**New endpoint:** `POST /api/tier/upgrade/{business_id}`

```python
@router.post("/api/tier/upgrade/{business_id}")
async def initiate_upgrade(business_id: str, req: UpgradeRequest):
    """Initiate upgrade to next tier"""
    user_id = get_user_id(request)
    verify_business_ownership(business_id, user_id)

    current_tier = get_user_tier(business_id)
    target_tier = req.target_tier  # 'glide' or 'soar'

    # Validate upgrade path
    if target_tier not in get_valid_upgrade_tiers(current_tier):
        raise HTTPException(status_code=400, detail="Invalid upgrade path")

    # Create Razorpay order for upgrade
    tier_price = TIER_PRICES[target_tier]
    current_price = TIER_PRICES[current_tier]

    # Proration: if monthly, charge difference
    days_remaining = get_days_until_renewal(business_id)
    prorated_price = int((tier_price - current_price) * days_remaining / 30)

    order = razorpay.order.create({
        'amount': prorated_price * 100,  # Convert to paise
        'currency': 'INR',
        'payment_capture': 1,
        'notes': {
            'business_id': business_id,
            'tier': target_tier,
            'upgrade_from': current_tier,
        }
    })

    return {
        'order_id': order['id'],
        'amount': prorated_price,
        'current_tier': current_tier,
        'target_tier': target_tier,
    }
```

---

### Phase 3: Database Schema Updates (MEDIUM PRIORITY)

#### 3.1 Update subscriptions Table
**Migration:** `database/migrations/002_update_subscription_tiers.sql`

```sql
-- Update existing subscriptions to use new tier names
-- Map: basic → breeze, pro → glide, enterprise → soar

ALTER TABLE subscriptions
ALTER COLUMN tier TYPE VARCHAR(50);

UPDATE subscriptions SET tier = 'breeze' WHERE tier = 'basic';
UPDATE subscriptions SET tier = 'glide' WHERE tier = 'pro';
UPDATE subscriptions SET tier = 'soar' WHERE tier = 'enterprise';

-- Add tier metadata columns
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS
    tier_metadata JSONB DEFAULT NULL;

-- tier_metadata will store capacity snapshots for audit
-- Example: {"projects": 5, "assets_per_month": 40, "locked_at": "2025-10-25"}
```

#### 3.2 Add Usage Tracking Table
**Migration:** `database/migrations/003_add_usage_tracking.sql`

```sql
CREATE TABLE IF NOT EXISTS subscription_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id),
    tier VARCHAR(50) NOT NULL,
    month DATE NOT NULL,  -- First day of month

    -- Monthly counts
    projects_created INT DEFAULT 0,
    assets_generated INT DEFAULT 0,
    research_runs INT DEFAULT 0,
    personas_created INT DEFAULT 0,

    -- Checkpoint for quota tracking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(business_id, month),
    FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE INDEX IF NOT EXISTS idx_usage_business_month
    ON subscription_usage(business_id, month);
```

---

### Phase 4: Razorpay Webhook Updates (HIGH PRIORITY)

**File:** `backend/main.py` - Update `/api/razorpay/webhook`

Current code (lines 699-726 in main.py):
```python
if event == 'payment.captured':
    payment = event_data['payload']['payment']['entity']
    notes = payment['notes']

    # OLD: Sets 'basic', 'pro', 'enterprise'
    tier_limits = {'basic': 3, 'pro': 6, 'enterprise': 9}
    max_icps = tier_limits.get(notes['tier'], 3)
```

**Update to:**
```python
if event == 'payment.captured':
    payment = event_data['payload']['payment']['entity']
    notes = payment['notes']
    target_tier = notes.get('tier')  # Now 'breeze', 'glide', 'soar'

    # Validate tier
    if target_tier not in ['breeze', 'glide', 'soar']:
        logger.error(f"Invalid tier in webhook: {target_tier}")
        raise HTTPException(status_code=400, detail="Invalid tier")

    # Get tier config
    tier_config = get_tier_config(target_tier)

    # Update subscription
    result = supabase.table('subscriptions').update({
        'tier': target_tier,
        'max_icps': tier_config['capacity']['personas_active'],
        'max_moves': 999,  # Now unlimited for Glide/Soar
        'max_research_runs': tier_config['capacity']['research_runs_per_month'],
        'max_assets': tier_config['capacity']['assets_per_month'],
        'status': 'active',
        'razorpay_subscription_id': payment['id'],
        'tier_metadata': {
            'locked_at': datetime.now().isoformat(),
            'tier_config': tier_config,
        }
    }).eq('business_id', notes['business_id']).execute()
```

---

### Phase 5: Editor Concurrency Control (COMPLEX - LOWER PRIORITY)

This is complex. For Glide and Soar, you need to track who is currently editing.

**File:** `backend/middleware/editor_concurrency.py` (NEW)

```python
import redis

class EditorConcurrencyController:
    """Track concurrent editors per business"""

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

    async def check_available_slot(self, business_id: str, user_id: str):
        """Check if user can start editing"""
        tier = get_user_tier(business_id)
        tier_config = get_tier_config(tier)
        max_slots = tier_config['collaboration']['active_editor_slots']

        # Get current editors
        editors_key = f"editors:{business_id}"
        current_editors = self.redis.hgetall(editors_key)

        # Remove stale editors (older than 30 minutes)
        now = time.time()
        for editor_id, timestamp in current_editors.items():
            if now - float(timestamp) > 1800:  # 30 min
                self.redis.hdel(editors_key, editor_id)

        current_count = len(self.redis.hgetall(editors_key))

        if current_count >= max_slots:
            # Check if this user is already editing
            if not self.redis.hexists(editors_key, user_id):
                raise ConcurrencyLimitExceeded(
                    f"Maximum {max_slots} editors active. "
                    f"Current: {current_count}. Please wait or upgrade tier."
                )

        # Register this user as editor
        self.redis.hset(editors_key, user_id, now)
        self.redis.expire(editors_key, 3600)  # Auto-cleanup after 1 hour

    async def release_slot(self, business_id: str, user_id: str):
        """User stops editing"""
        editors_key = f"editors:{business_id}"
        self.redis.hdel(editors_key, user_id)

# Use in endpoints:
# @router.post("/api/assets/generate")
# async def generate_asset(request: Request, body: GenerateAssetRequest):
#     business_id = get_business_id(request)
#     user_id = get_user_id(request)
#
#     concurrency = EditorConcurrencyController()
#     await concurrency.check_available_slot(business_id, user_id)
#
#     try:
#         result = await generate_asset_logic(...)
#     finally:
#         await concurrency.release_slot(business_id, user_id)
#
#     return result
```

**Note:** This requires Redis. Add to docker-compose and requirements if not present.

---

## Implementation Priority

### MUST DO (v1 Launch)
1. ✅ Tier configuration (DONE)
2. 📋 Quota validation middleware (Phase 1.1)
3. 📋 Feature gating (Phase 1.2)
4. 📋 Update Razorpay webhook (Phase 4)
5. 📋 Subscription endpoint + tier config return (Phase 2.1)
6. 📋 Database migration for new tier names (Phase 3.1)

### SHOULD DO (v1 or shortly after)
7. 📋 Feature availability endpoint (Phase 2.2)
8. 📋 Upgrade path endpoint (Phase 2.3)
9. 📋 Usage tracking table (Phase 3.2)

### CAN DO LATER (v1.1+)
10. 📋 Editor concurrency control (Phase 5)
11. 📋 Advanced audit trails (part of Soar)

---

## Code Checklist

Before each piece goes to production:

- [ ] Tests written (unit + integration)
- [ ] Tier limits enforced correctly
- [ ] Error messages are user-friendly
- [ ] Upgrade paths are clear
- [ ] Rollback plan documented
- [ ] Database migrations are reversible
- [ ] No hardcoded tier names (use `subscription_tiers.py`)
- [ ] Logging for quota/feature/limit events
- [ ] Support has runbook for tier-related issues

---

## Testing Strategy

### Unit Tests
Test each helper function in `subscription_tiers.py`:
```python
def test_get_tier_config():
    assert get_tier_config('breeze')['capacity']['projects'] == 5
    assert get_tier_config('soar')['capacity']['research_runs_per_month'] == 180

def test_validate_tier_access():
    assert validate_tier_access('soar', 'batch_recipes') == True
    assert validate_tier_access('breeze', 'batch_recipes') == False

def test_get_capacity_limit():
    assert get_capacity_limit('glide', 'assets_per_month') == 120
```

### Integration Tests
Test quota enforcement in real endpoints:
```python
@pytest.mark.asyncio
async def test_project_limit_breeze():
    """Breeze user can't create 6th project"""
    user, business = setup_breeze_subscription()

    # Create 5 projects (at limit)
    for i in range(5):
        create_project(business, f"Project {i}")

    # 6th should fail
    with pytest.raises(TierLimitExceeded):
        create_project(business, "Project 6")

@pytest.mark.asyncio
async def test_feature_gate_batch_recipes():
    """Breeze user can't access Batch Recipes"""
    user, business = setup_breeze_subscription()

    with pytest.raises(FeatureNotAvailable):
        trigger_batch_recipe(business, "research → assets")
```

### Load Tests
Verify quota system scales:
- 1000 concurrent asset generation requests
- 100 businesses checking subscription status simultaneously

---

## Monitoring & Alerts

Add to observability:

```python
# Log every quota check + result
logger.info(
    "quota_check",
    extra={
        'business_id': business_id,
        'tier': tier,
        'check_type': 'projects',
        'current': 4,
        'limit': 5,
        'status': 'OK',
    }
)

# Alert on quota rejections
if not within_limit:
    logger.warning(
        "tier_limit_exceeded",
        extra={
            'business_id': business_id,
            'tier': tier,
            'feature': 'project_creation',
            'upgrade_prompt': f"Upgrade to {next_tier} for more projects",
        }
    )
```

---

## Questions?

Refer to:
- `TIER_DEFINITIONS.md` - All specs
- `TIER_QUICK_REFERENCE.md` - Quick lookup
- `backend/utils/subscription_tiers.py` - Code reference

Last updated: 2025-10-25

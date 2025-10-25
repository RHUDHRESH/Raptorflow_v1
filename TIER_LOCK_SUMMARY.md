# RaptorFlow Tier Structure - LOCKED & DOCUMENTED

**Date:** 2025-10-25
**Status:** ✅ CANONICAL - PRODUCTION BINDING
**Last Modified:** 2025-10-25

---

## What Just Got Locked In

The **Breeze → Glide → Soar** tier structure is now the official, canonical, production-binding tier model for RaptorFlow. This replaces the old "Basic/Pro/Enterprise" naming and specs.

### Documents Created

1. **`/TIER_DEFINITIONS.md`** ← THE SOURCE OF TRUTH
   - 300+ lines of canonical tier specs
   - Every feature, capacity limit, and differentiator defined
   - Single point of reference for all teams

2. **`/TIER_QUICK_REFERENCE.md`** ← QUICK LOOKUP CARD
   - Printable quick reference
   - All tables and upgrade paths at a glance
   - For salespeople, support, and developers

3. **`/backend/utils/subscription_tiers.py`** ← BACKEND ENFORCEMENT
   - Python config enforcing all tier specs
   - Helper functions: `get_tier_config()`, `validate_tier_access()`, `get_capacity_limit()`
   - Replaces old "basic/pro/enterprise" code

---

## The Three Tiers (Locked)

### Breeze
- **Price:** ₹1,499/mo + GST
- **Target:** Solo founder, very lean team, single brand
- **Tagline:** "Give me clarity, fast."
- **Capacity:** 5 projects, 30 research runs/mo, 40 assets/mo, 3 personas
- **Key Differentiator:** Solo operator + 2 guest approvers (lightweight)
- **Channels:** 1
- **Unique:** Lift Lite measurement, no advanced strategy depth

### Glide
- **Price:** ₹2,499/mo + GST
- **Target:** Small teams, boutique agencies, growing brands
- **Tagline:** "My team is in this with me now."
- **Capacity:** Unlimited projects, 120 research runs/mo, 120 assets/mo, 3 personas
- **Key Differentiator:** 3 pooled editor slots (team concurrency), unlimited invites
- **Channels:** 2
- **Strategy Upgrades:** Adjacency Mapping Pro, Offer Stress-Test, POV Heatmap
- **Unique:** Brand Guard, QR codes, Creative Leaderboard

### Soar
- **Price:** ₹4,999/mo + GST
- **Target:** Agencies with multiple clients, performance teams
- **Tagline:** "I am running this like an operation."
- **Capacity:** Unlimited projects, 180 research runs/mo, 200 assets/mo, 5 personas
- **Key Differentiator:** 5 named seats, 5 pooled editor slots, audit trails
- **Channels:** 3
- **Strategy Upgrades:** Everything from Glide + Competitor Watch, Market Pulse, Offer Ladder Simulator
- **Unique:** Batch Recipes, Rotators, Approval History export, Role-based permissions

---

## What All Tiers Get (Non-Negotiable)

✓ **Strategy Workspace** (full access, no gatekeeping)
  - ICP & Persona Studio
  - Positioning / Point of View
  - Offer & Pricing Builder
  - PMF Pulse & Cadence Planner
  - Category Mapper
  - Anti-Persona Guard
  - Wedge Finder
  - Objection Map

✓ **Evidence Locker** (storage varies: 10k → 50k → 100k chunks)
✓ **Message Matrix & Copy Studio** (Light + Pro assets, auto-upgrade)
✓ **Dispatch & Tracking** (schedule, UTMs, log)
✓ **Lift Measurement** (before vs. after KPIs)

**Rationale:** Never cripple the thinking brain. Tier differences are scale, collaboration, and depth — not strategy access.

---

## How the Tiers Drive Upgrades (SaaS Pricing Strategy)

### Breeze → Glide Trigger
- Hired first team member
- Need more than 40 assets/month
- Want QR codes (offline campaigns)
- Need stress-testing tools for positioning confidence

### Glide → Soar Trigger
- Multiple clients or high-CAC projects
- Need 5+ personas active
- Need batch automation (Batch Recipes)
- Need compliance audit trails
- Running A/B tests (need rotators)
- Need competitive intelligence

**Design Principle:** Each tier has obvious "headroom" for the next tier. No arbitrary feature gating. Clear value progression.

---

## Backend Integration

### File: `backend/utils/subscription_tiers.py`

All tier specs are now in ONE place (not scattered across 5 files).

#### Usage in Code

```python
from backend.utils.subscription_tiers import (
    get_tier_config,
    validate_tier_access,
    get_capacity_limit,
    SUBSCRIPTION_TIERS
)

# Check if user's tier has access to a feature
if validate_tier_access('glide', 'qr_generation'):
    # Feature is available
    pass

# Get a capacity limit
assets_limit = get_capacity_limit('soar', 'assets_per_month')  # Returns 200

# Get full tier config
tier = get_tier_config('breeze')
print(tier['capacity']['research_runs_per_month'])  # Returns 30
```

#### Key Helpers Added
- `get_tier_config(tier_key)` - Get full config dict
- `validate_tier_access(tier_key, feature)` - Boolean feature check
- `get_capacity_limit(tier_key, capacity_type)` - Get numeric limit
- `TIER_NAMES` - Lookup dict (Breeze → breeze)
- `TIER_PRICES` - Lookup dict (breeze → 1499)

---

## What Changed from Old Tiers

| Aspect | Old | New |
|--------|-----|-----|
| Names | Basic, Pro, Enterprise | Breeze, Glide, Soar |
| Pricing | Not specified | ₹1,499 / ₹2,499 / ₹4,999 |
| Max ICPs | 3 / 6 / 9 | 3 / 3 / 5 |
| Max Projects | Not specified | 5 / ∞ / ∞ |
| Personas | Implicit | Explicit capacity |
| Editor Slots | Not defined | 1 / 3 pooled / 5 pooled |
| Strategy Depth | Shallow | Full core + upgrades by tier |
| Channels | Not specified | 1 / 2 / 3 |
| Audit Trail | No | No / No / Yes |
| Feature Set | Vague | Comprehensive, locked |

---

## Next Steps for Each Team

### Backend Team
✅ Already done:
- `subscription_tiers.py` updated with canonical specs
- Helper functions added

TODO:
- [ ] Update `/api/subscription/{business_id}` to return tier config
- [ ] Add tier validation middleware to enforce quotas
- [ ] Update `/api/razorpay/webhook` to set tier to "breeze", "glide", or "soar" (not "basic/pro/enterprise")
- [ ] Add tests for tier enforcement (e.g., can't create >3 personas on Breeze)

### Frontend Team
TODO:
- [ ] Update UI to show Breeze/Glide/Soar names
- [ ] Update pricing page with new prices (₹1,499 / ₹2,499 / ₹4,999)
- [ ] Update "current tier" display in dashboard
- [ ] Add "Upgrade" buttons with clear value props
- [ ] Update feature availability checks to reference new tier structure
- [ ] Show upgrade paths (Breeze → Glide, Glide → Soar) with "why upgrade" messaging

### Sales/Support Team
TODO:
- [ ] Print and distribute `TIER_QUICK_REFERENCE.md`
- [ ] Update sales deck with new tier names and pricing
- [ ] Create customer communication plan for tier name migration
- [ ] Train on upgrade triggers (who upgrades when, and why)
- [ ] Update support docs with tier-specific feature lists

### Product/Finance Team
TODO:
- [ ] Plan migration for existing customers (Basic → Breeze, Pro → Glide, Enterprise → Soar)
- [ ] Decide: grandfather at old price for X months? Or migrate with notice?
- [ ] Update Razorpay subscription creation to use new tier names
- [ ] Track upgrade rates from Breeze → Glide and Glide → Soar
- [ ] Evaluate if pricing is aligned with market (₹1,499 / ₹2,499 / ₹4,999)

---

## Enforcement Rules (Backend Must Implement)

### Capacity Enforcement
If a user on **Breeze** tries to:
- Create 6th project → Error: "Upgrade to Glide for unlimited projects"
- Create 4th persona → Error: "Breeze limited to 3 personas. Upgrade to Soar for 5."
- Generate 41st asset → Error: "Monthly limit reached (40). Purchase add-on or upgrade."

### Feature Gating
If a user on **Breeze** tries to:
- Access Batch Recipes → 404 (Soar only)
- Add 3rd editor → Warn: "Add 3 pooled editors with Glide (₹2,499/mo)"
- Connect 2nd channel → Error: "Breeze limited to 1 channel. Upgrade to Glide."

### Approval Flow
- **Breeze:** 2 guest approvers (view/comment, no generation, no concurrency)
- **Glide:** 2 formal approvers (role-based, shared quota)
- **Soar:** Role-based (Owner, Editor, Approver, Viewer) with audit trail

---

## Version Control & Updates

**This document is the canonical source.** If specs change:

1. Update `/TIER_DEFINITIONS.md` first
2. Update `/backend/utils/subscription_tiers.py`
3. Notify all teams
4. Update `/TIER_QUICK_REFERENCE.md`
5. Commit with message: "lock: update tier specs for [reason]"

**Do not** create ad-hoc tier variations in code. Always update the central config.

---

## Questions / Clarifications

**Q: Why no free tier?**
A: Entry point is Breeze at ₹1,499. No freemium complexity. Clear monetization from day 1.

**Q: Why pooled editor slots instead of per-seat pricing?**
A: Avoids per-user pricing model which can quickly become unprofitable and adds friction. Pooled slots = clear upgrade path + fair pricing (you pay for team size, not seat count).

**Q: Why 3 personas on Breeze/Glide but 5 on Soar?**
A: Breeze is for solo founders or very small teams (maybe 1 buyer persona is enough). Glide is for agencies managing one client well (3 personas = TOFU/MOFU/BOFU coverage). Soar is for multi-client agencies (5 personas = multiple ICP profiles across multiple businesses).

**Q: Can we offer add-ons (extra assets, extra projects)?**
A: Not in v1. Keep it simple: Breeze → Glide → Soar or stay on current tier. Add overage metering in v2 if needed.

**Q: What about existing customers on old tiers?**
A: Grandfathering decision is product/finance team's call. Recommend: offer 1-month trial of new tier names, then let customers choose on renewal (no forced migration).

---

## Sign-Off

✅ **Tier structure is LOCKED.**
✅ **Backend config is updated.**
✅ **Documentation is canonical.**

Teams can now build features with confidence that tier specs won't change mid-sprint.

**Last updated:** 2025-10-25
**Locked by:** Product / Leadership
**Next review:** Quarterly (or if pricing strategy changes)

# RaptorFlow Tier System - Rollout Checklist

**Status:** Documentation Complete ✅ | Implementation In Progress
**Last Updated:** 2025-10-25

---

## What's Complete ✅

- [x] Tier names locked: **Breeze / Glide / Soar**
- [x] Pricing locked: **₹1,499 / ₹2,499 / ₹4,999**
- [x] Capacity limits defined
- [x] Feature list comprehensive
- [x] Backend config updated: `subscription_tiers.py`
- [x] Documentation complete (5 canonical docs created)
- [x] Git commits made with full change history

---

## Pre-Launch Checklist (DO BEFORE GOING LIVE)

### Backend Development [ ]

**Tier Enforcement Middleware**
- [ ] Build `backend/middleware/tier_quota_validator.py`
  - [ ] Project creation quota check
  - [ ] Persona creation quota check
  - [ ] Asset generation quota check
  - [ ] Research run quota check
  - [ ] Editor concurrency limits (Glide: 3, Soar: 5)

- [ ] Build `backend/middleware/tier_feature_gate.py`
  - [ ] QR generation (Glide+)
  - [ ] Batch Recipes (Soar only)
  - [ ] Rotators (Soar only)
  - [ ] Competitor Watch (Soar only)
  - [ ] Market Pulse (Soar only)
  - [ ] Offer Ladder Simulator (Soar only)
  - [ ] Approval history export (Soar only)

**API Endpoints**
- [ ] Update `/api/subscription/{business_id}` to return full tier config
- [ ] Add `GET /api/tier/features/{business_id}` endpoint
- [ ] Add `POST /api/tier/upgrade/{business_id}` endpoint
- [ ] Update `/api/razorpay/webhook` to handle new tier names (breeze/glide/soar)
- [ ] Add `/api/tier/capacity/{business_id}` endpoint (usage + limits)

**Database**
- [ ] Create migration: `002_update_subscription_tiers.sql`
  - [ ] Rename column values: basic → breeze, pro → glide, enterprise → soar
  - [ ] Add `tier_metadata` JSONB column
  - [ ] Backfill existing subscriptions

- [ ] Create migration: `003_add_usage_tracking.sql`
  - [ ] Create `subscription_usage` table
  - [ ] Add monthly usage tracking columns
  - [ ] Create indexes on `(business_id, month)`

**Testing**
- [ ] Unit tests for `subscription_tiers.py` helper functions
- [ ] Integration tests for quota enforcement
- [ ] Integration tests for feature gating
- [ ] Test Razorpay webhook with new tier names
- [ ] Load test: 1000 concurrent quota checks
- [ ] Test database migrations (backup + restore)

**Logging & Monitoring**
- [ ] Add logging for every quota check (success/fail)
- [ ] Add logging for feature gate rejections
- [ ] Add alerts for quota-exceeded events
- [ ] Add dashboard showing upgrade rates (Breeze→Glide, Glide→Soar)

---

### Frontend Development [ ]

**UI Updates**
- [ ] Replace "Basic/Pro/Enterprise" with "Breeze/Glide/Soar"
  - [ ] Pricing page
  - [ ] Dashboard tier display
  - [ ] Billing page
  - [ ] Onboarding flow
  - [ ] Account settings page

- [ ] Show current tier and limits
  - [ ] Display: Projects used / limit
  - [ ] Display: Assets used this month / limit
  - [ ] Display: Personas used / limit
  - [ ] Display: Active editors / limit

- [ ] Add upgrade CTA buttons
  - [ ] "Upgrade to Glide" button on Breeze dashboard
  - [ ] "Upgrade to Soar" button on Glide dashboard
  - [ ] Show pricing & upgrade path

- [ ] Update feature availability UI
  - [ ] Gray out unavailable features
  - [ ] Show "Available on Glide" / "Available on Soar" badges
  - [ ] Link to pricing when user tries locked feature

**Onboarding**
- [ ] Update tier selection on signup
  - [ ] Show tier cards: Breeze | Glide | Soar
  - [ ] Display pricing clearly
  - [ ] Show target user for each tier
  - [ ] Recommend Breeze for new users

- [ ] Create upgrade flow
  - [ ] Modal: "Ready to upgrade?"
  - [ ] Show what's unlocked with upgrade
  - [ ] Prorated pricing calculation
  - [ ] Link to Razorpay checkout

**Testing**
- [ ] Test on mobile (pricing cards, upgrade buttons)
- [ ] Test upgrade flow end-to-end
- [ ] Test feature gating (locked features show upgrade prompt)
- [ ] A/B test: Does clearer pricing drive upgrades?

---

### Database Migrations [ ]

**Before Running**
- [ ] Backup production database
- [ ] Test migration on staging environment
- [ ] Document rollback procedure
- [ ] Schedule migration during low-traffic window

**Migration Steps**
1. [ ] Run migration 002 (rename tier values)
2. [ ] Run migration 003 (add usage tracking)
3. [ ] Verify all subscriptions have correct tier name (breeze/glide/soar)
4. [ ] Test API returns correct tier config
5. [ ] Monitor for any errors in logs

**Post-Migration**
- [ ] Verify all users can still access their tier features
- [ ] Run quota validation tests
- [ ] Check Razorpay webhook still works
- [ ] Monitor API response times (should be unchanged)

---

### Sales & Customer Communication [ ]

**Sales Team**
- [ ] Print TIER_VISUAL_COMPARISON.txt and distribute
- [ ] Update sales deck with new tier names
- [ ] Create "upgrade guide" for salespeople
  - [ ] When does Breeze user upgrade to Glide?
  - [ ] When does Glide user upgrade to Soar?
  - [ ] What's the typical upgrade path?

- [ ] Train on new pricing
  - [ ] ₹1,499 (Breeze)
  - [ ] ₹2,499 (Glide)
  - [ ] ₹4,999 (Soar)
  - [ ] Prorated pricing for mid-month upgrades

- [ ] Create case studies
  - [ ] Example: Breeze founder → found PMF → upgrades to Glide
  - [ ] Example: Glide agency → scales to 5 clients → upgrades to Soar

**Support Team**
- [ ] Update support docs with tier-specific feature lists
- [ ] Create FAQ: "What's the difference between tiers?"
- [ ] Create runbook: "Customer wants to upgrade"
  - [ ] Check their usage vs. limits
  - [ ] Calculate prorated pricing
  - [ ] Send upgrade link
  - [ ] Confirm Razorpay success

- [ ] Train on quota explanation
  - [ ] "You've hit your 40 assets/month limit on Breeze"
  - [ ] "Upgrade to Glide for 120 assets/month"

- [ ] Prepare migration communication
  - [ ] Email template: "We're renaming Basic → Breeze"
  - [ ] FAQ: "Will my price change?"
  - [ ] FAQ: "Do I have to migrate?"

**Product & Finance**
- [ ] Decide: Grandfathering strategy
  - [ ] Option A: All customers migrate to new tier on next renewal
  - [ ] Option B: Offer 1-month trial of new tier name, then choose
  - [ ] Option C: Keep old customers on old pricing, new customers on new pricing

- [ ] Plan customer communication
  - [ ] Email 1 (Week 1): "New tier names, same great features"
  - [ ] Email 2 (Week 2): "Learn about your new tier"
  - [ ] Email 3 (Week 3): "Upgrade paths and pricing"
  - [ ] In-app banner: "Welcome to Breeze/Glide/Soar"

- [ ] Set up Razorpay plan mapping
  - [ ] Plan ID for Breeze
  - [ ] Plan ID for Glide
  - [ ] Plan ID for Soar

- [ ] Create tracking for upgrade metrics
  - [ ] Dashboard: Upgrades per month (Breeze→Glide, Glide→Soar)
  - [ ] Dashboard: Average tenure before first upgrade
  - [ ] Dashboard: Revenue by tier
  - [ ] Dashboard: Churn by tier

---

### Launch Timeline [ ]

**Week 1: Internal Testing**
- [ ] All code complete and tested (backend, frontend, DB)
- [ ] Staging environment fully configured
- [ ] Run end-to-end smoke tests
- [ ] Sales/Support trained on new tiers

**Week 2: Staging Launch**
- [ ] Deploy to staging
- [ ] Run full integration tests
- [ ] Invite beta customers (if applicable)
- [ ] Get feedback on UX

**Week 3: Production Preparation**
- [ ] Database backup scheduled
- [ ] Rollback plan documented
- [ ] Support team ready
- [ ] Sales team ready
- [ ] Customer communication scheduled

**Week 4: Production Launch**
- [ ] Run database migration during low-traffic window
- [ ] Deploy API changes
- [ ] Deploy frontend changes
- [ ] Monitor logs for errors
- [ ] Send customer communication

**Post-Launch: Monitoring**
- [ ] Monitor API response times (quota checks shouldn't add latency)
- [ ] Monitor for quota-exceeded errors (track by tier)
- [ ] Monitor for feature gate rejections
- [ ] Monitor Razorpay webhook success rate
- [ ] Track upgrade conversions (dashboard metrics)

---

## Success Criteria

After launch, verify:

- [ ] 100% of existing customers are on Breeze/Glide/Soar (no old tier names)
- [ ] New customers can select Breeze/Glide/Soar on signup
- [ ] Quota limits are enforced (can't exceed project/asset/persona limits)
- [ ] Features are gated correctly (can't access Soar-only features on Breeze)
- [ ] Razorpay webhook correctly sets tier to breeze/glide/soar
- [ ] Upgrade flow works end-to-end (Breeze → Glide, Glide → Soar)
- [ ] No increase in API latency due to quota checks
- [ ] Support team can handle tier-related customer issues
- [ ] No customer complaints about tier naming or features

---

## Post-Launch Monitoring (30 Days)

Track these metrics:
- [ ] Upgrade rate: % of Breeze users upgrading to Glide per month (Target: 5-10%)
- [ ] Upgrade rate: % of Glide users upgrading to Soar per month (Target: 3-5%)
- [ ] Churn by tier (Track if Breeze has higher churn than Glide/Soar)
- [ ] ARPU by tier (Average Revenue Per User)
- [ ] Feature adoption: Which Glide/Soar features are most used?
- [ ] Support tickets by tier (Track if Breeze has high quota-related tickets)

---

## Long-Term Maintenance

After launch, keep these things in sync:

- [ ] If tier specs change, update TIER_DEFINITIONS.md FIRST
- [ ] Then update subscription_tiers.py
- [ ] Then update TIER_QUICK_REFERENCE.md
- [ ] Then notify all teams
- [ ] Never hardcode tier specs anywhere else

---

## Questions Before Launch?

Refer to:
- `TIER_DEFINITIONS.md` - Full specs
- `TIER_QUICK_REFERENCE.md` - Quick lookup
- `TIER_BACKEND_INTEGRATION.md` - Implementation details
- `TIER_STRUCTURE_SUMMARY.txt` - Plain English summary
- `TIER_VISUAL_COMPARISON.txt` - Side-by-side feature comparison

**If you have questions that aren't answered in these docs, update the docs before proceeding.**

---

## Sign-Off

Launch can proceed once all items in the "Pre-Launch Checklist" are complete.

- [ ] Backend Lead: Sign off on code quality
- [ ] Frontend Lead: Sign off on UX
- [ ] Product: Sign off on feature list
- [ ] Finance: Sign off on pricing & billing
- [ ] Support: Sign off on documentation & training

**Date Signed Off:** _________________
**Launched:** _________________

---

Good luck! This is a big move. The docs are locked in, the code is updated, and the team is ready. 🚀

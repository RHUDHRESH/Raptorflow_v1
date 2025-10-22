# RaptorFlow Integration - Quick Start Guide

## Overview

This guide walks you through integrating the complete frontend-backend system for RaptorFlow 2.0. All code is production-ready and fully tested.

## What's Included

- ✅ Frontend API client (Axios with auth)
- ✅ React hooks (Auth, Agent, Token, Tier)
- ✅ React components (AgentMonitor, TokenCounter, PricingTierSelector)
- ✅ Backend REST API routes (Analysis, Billing)
- ✅ Token tracking and ledger system
- ✅ Pricing tier selector (dev mode only)

## 5-Minute Setup

### 1. Copy Frontend Files

```bash
# Copy API client
cp frontend/lib/api-client.ts YOUR_PROJECT/lib/

# Copy hooks
cp frontend/lib/hooks/*.ts YOUR_PROJECT/lib/hooks/

# Copy components
cp frontend/components/*.tsx YOUR_PROJECT/components/
```

### 2. Copy Backend Files

```bash
# Copy routes
cp backend/app/routes/analysis.py YOUR_PROJECT/app/routes/
cp backend/app/routes/billing.py YOUR_PROJECT/app/routes/

# Copy models
cp backend/app/models/token_ledger.py YOUR_PROJECT/app/models/
```

### 3. Register Routes

In your backend `main.py`:

```python
from app.routes import analysis, billing

# Include routers
app.include_router(analysis.router)
app.include_router(billing.router)
```

### 4. Use in Your App

```tsx
import { AgentMonitor } from '@/components/AgentMonitor'
import { TokenCounter } from '@/components/TokenCounter'
import { PricingTierSelector } from '@/components/PricingTierSelector'

export function StrategyPage({ strategyId }: { strategyId: string }) {
  return (
    <div className="space-y-6">
      {/* Real-time agent monitoring */}
      <AgentMonitor strategyId={strategyId} />

      {/* Token & cost tracking */}
      <TokenCounter strategyId={strategyId} />

      {/* Pricing tier selector (dev mode only) */}
      <PricingTierSelector />
    </div>
  )
}
```

## Key Features

### 1. Real-time Agent Monitoring

```tsx
import { useAgent } from '@/lib/hooks/useAgent'

const { startAnalysis, isRunning, progress, events, error } = useAgent()

// Start analysis
await startAnalysis(strategyId)

// Monitor progress
console.log(`Progress: ${progress}%`)
console.log(`Running: ${isRunning}`)
console.log(`Events: ${events.length}`)
```

### 2. Token Usage Tracking

```tsx
import { useTokenUsage } from '@/lib/hooks/useTokenUsage'

const { usage, getDailyPercentage, getMonthlyPercentage } = useTokenUsage()

// Check usage
if (usage) {
  console.log(`Total tokens: ${usage.total_tokens}`)
  console.log(`Cost: ${usage.estimated_cost}`)
  console.log(`Daily: ${getDailyPercentage()}%`)
  console.log(`Monthly: ${getMonthlyPercentage()}%`)
}
```

### 3. Pricing Tier Selection (Dev Mode)

```tsx
import { usePricingTier } from '@/lib/hooks/usePricingTier'

const { currentTier, setTier, isDevelopmentMode } = usePricingTier()

// Only available in dev mode
if (isDevelopmentMode) {
  await setTier('pro')  // Switch to pro tier
  console.log(`Current tier: ${currentTier}`)
}
```

## API Endpoints

### Strategies
```
POST   /api/v1/strategies              - Create strategy
GET    /api/v1/strategies              - List strategies
GET    /api/v1/strategies/{id}         - Get strategy
PATCH  /api/v1/strategies/{id}         - Update strategy
DELETE /api/v1/strategies/{id}         - Delete strategy
```

### Context Items
```
POST   /api/v1/strategies/{id}/context-items        - Add context
GET    /api/v1/strategies/{id}/context-items        - List context
DELETE /api/v1/strategies/{id}/context-items/{id}   - Remove context
```

### Analysis
```
POST   /api/v1/strategies/{id}/analysis             - Submit analysis
GET    /api/v1/strategies/{id}/analysis/stream      - Stream events (SSE)
GET    /api/v1/analysis/{id}/status                 - Check status
GET    /api/v1/strategies/{id}/analysis-results     - Get results
```

### Token Usage
```
GET    /api/v1/token-usage                          - Get total usage
GET    /api/v1/token-usage/{strategy_id}            - Get strategy usage
GET    /api/v1/budget-status                        - Get budget info
```

### Subscription
```
GET    /api/v1/subscription/tier                    - Get current tier
GET    /api/v1/features                             - Get features
```

### Dev Mode
```
POST   /api/v1/dev/set-tier                         - Set tier (dev only)
GET    /api/v1/dev/current-tier                     - Get tier
GET    /api/v1/dev/available-tiers                  - List tiers
```

## Pricing Tiers (Dev Mode)

### Basic ($20/mo, ₹2000)
- 3 ICPs (Ideal Customer Profiles)
- 5 Moves per analysis
- 50,000 tokens/day
- Basic analytics
- Email support

### Professional ($35/mo, ₹3500)
- 6 ICPs
- 15 Moves per analysis
- 150,000 tokens/day
- Advanced analytics
- Priority email support
- API access

### Enterprise ($50/mo, ₹5000)
- 9 ICPs
- Unlimited Moves
- 500,000 tokens/day
- Advanced analytics
- 24/7 dedicated support
- Custom integrations

## Testing

### Test Token Tracking

```bash
# In your app:
1. Create a strategy
2. Add context items
3. Start analysis
4. Check /api/v1/token-usage endpoint
5. Verify tokens were incremented
```

### Test Pricing Tiers

```bash
# In dev mode only:
1. Open PricingTierSelector component
2. Select different tiers
3. Verify tier limits change
4. Check /api/v1/dev/current-tier endpoint
```

### Test Agent Streaming

```bash
# In your app:
1. Start analysis with AgentMonitor
2. Watch progress bar update
3. View event log in real-time
4. Check completion status
```

## Common Issues

### Issue: API client not injecting auth token

**Solution:**
```tsx
import { useAuth } from '@/lib/hooks/useAuth'

// Make sure useAuth is called before making API calls
const { session } = useAuth()

// API client session is auto-synced via useEffect
```

### Issue: PricingTierSelector not showing

**Solution:**
```tsx
// Check if in dev mode
import { isDevelopmentMode } from '@/lib/hooks/usePricingTier'

if (!isDevelopmentMode()) {
  console.log('Pricing tier selector only available in dev mode')
}
```

### Issue: Token usage not updating

**Solution:**
```tsx
import { useTokenUsage } from '@/lib/hooks/useTokenUsage'

// Make sure to pass strategyId
const { usage, refetch } = useTokenUsage(strategyId)

// Manual refresh if needed
await refetch()
```

## Performance Tips

1. **Use Compact Components**
   ```tsx
   // For sidebars/widgets
   <AgentMonitor compact={true} />
   <TokenCounter compact={true} />
   ```

2. **Disable Auto-Refresh**
   ```tsx
   // If tokens don't change frequently
   const { usage } = useTokenUsage(strategyId, false)
   ```

3. **Memoize Results**
   ```tsx
   import { useMemo } from 'react'

   const percentage = useMemo(() => getDailyPercentage(), [usage])
   ```

## Security Notes

- ✅ JWT auth tokens automatically injected
- ✅ 401 errors trigger auto-logout
- ✅ Session synced on every useAuth call
- ✅ No tokens stored in localStorage
- ✅ API errors handled gracefully

## Troubleshooting

### Enable Debug Logging

```typescript
// In api-client.ts
const DEBUG = process.env.NODE_ENV === 'development'

// In hooks
if (DEBUG) console.log('useAuth:', { session, isLoading })
```

### Check API Response

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/token-usage
```

### Monitor Event Stream

```bash
curl -N http://localhost:8000/api/v1/strategies/STRATEGY_ID/analysis/stream
```

## Next Steps

1. ✅ Copy files to your project
2. ✅ Register routes in backend
3. ✅ Test API endpoints
4. ✅ Integrate components in pages
5. ✅ Run integration tests
6. ✅ Deploy to staging
7. ✅ Deploy to production

## Support

For issues or questions:
1. Check the detailed integration guide
2. Review API endpoint specifications
3. Check console for error messages
4. Enable debug logging
5. Test endpoints with curl/Postman

---

**Status:** Production Ready ✅
**Last Updated:** October 22, 2025
**Version:** 1.0.0

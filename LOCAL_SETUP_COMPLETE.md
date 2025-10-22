# RaptorFlow 2.0 - Complete Local Development Setup

## 🎯 What You Now Have

You have a **complete, production-ready frontend-backend system** ready for local testing with:

- ✅ Real-time agent monitoring
- ✅ Live token tracking
- ✅ Network speed monitoring
- ✅ Dev hover button with full metrics
- ✅ Complete API integration
- ✅ Budget tracking
- ✅ Pricing tier selector (dev mode)

---

## ⚡ Quick Start (5 Minutes)

### Terminal 1: Frontend
```bash
cd frontend
npm install
npm run dev
# Opens http://localhost:3000
```

### Terminal 2: Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

### Terminal 3: Database (if needed)
```bash
createdb raptorflow_dev
cd backend
alembic upgrade head
```

---

## 🖥️ Using the Dev Monitor

### Hover Button Features

The **dev monitor button** (⚙️) appears in the bottom-right corner when development mode is active.

**Click to expand and see:**

1. **🌐 Network Metrics**
   - Average response time
   - Last response time
   - Total requests made
   - Error count
   - Network latency
   - Bandwidth estimation

2. **💰 Token Metrics**
   - Session tokens used
   - Total tokens used
   - Estimated cost
   - Cost per agent
   - API calls made
   - Cache hit ratio
   - Budget status

3. **⚡ Performance Metrics**
   - React render count
   - Average render time
   - Total API calls
   - Cache hit percentage

4. **🏥 Health Status**
   - API Server status
   - Database connection
   - Authentication status
   - Uptime counter

5. **ℹ️ Environment Info**
   - Development mode indicator
   - Node.js version
   - Timestamp
   - All live updates

---

## 🌐 Network Speed Tracking

### How It Works

The `networkMonitor` utility automatically tracks every network request:

```typescript
import { networkMonitor } from '@/lib/utils/networkMonitor'

// Get statistics anytime
const stats = networkMonitor.getStats()
console.log(`Average response time: ${stats.averageResponseTime}ms`)
console.log(`Network speed: ${stats.networkSpeed}`)

// Log everything to console
networkMonitor.logStats()

// Get slow requests (> 500ms)
const slowReqs = networkMonitor.getSlowRequests(500)

// Export data
const json = networkMonitor.exportMetrics()
```

### Network Metrics Tracked

```
✓ Request URL & method
✓ Response time (milliseconds)
✓ HTTP status code
✓ Response size
✓ Timestamp
✓ Error information
```

### View in Dev Monitor

In the DevMonitor panel under **🌐 Network**:
```
Avg Response:   145ms
Last Response:  234ms
Requests:       12
Errors:         0
Latency:        12ms
Bandwidth:      2.3 MB/s
```

---

## 💰 Token Usage Tracking

### How It Works

The `tokenTracker` utility tracks every token consumption:

```typescript
import { tokenTracker } from '@/lib/utils/tokenTracker'

// Record tokens used
tokenTracker.recordTokens(500, 0.0005, 'AgentName', 'https://...')

// Get statistics
const stats = tokenTracker.getStats()
console.log(`Session tokens: ${stats.sessionTokens}`)
console.log(`Session cost: $${stats.sessionCost.toFixed(4)}`)

// Get tokens by agent
const byAgent = tokenTracker.getTokensByAgent()

// Check budget
const budget = tokenTracker.getBudgetStatus(15) // $15/month
console.log(`Budget: ${budget.percentage}% used`)

// Log everything
tokenTracker.logStats()
```

### Token Metrics Tracked

```
✓ Tokens used per request
✓ Cost per request
✓ Agent name
✓ Endpoint URL
✓ HTTP status code
✓ Timestamp
```

### View in Dev Monitor

In the DevMonitor panel under **💰 Tokens**:
```
Session Tokens:    3,450
Total Tokens:      15,234
Estimated Cost:    $0.015
API Calls:         12
Cache Hits:        4
Budget Status:     ✓ OK (45% used)
```

---

## 🔧 Environment Setup

### Frontend `.env.local`

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000

# Supabase (for auth)
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...

# Debug & Monitoring
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_ENABLE_DEV_TOOLS=true
NEXT_PUBLIC_NETWORK_MONITOR=true
NEXT_PUBLIC_TOKEN_MONITOR=true
NEXT_PUBLIC_ENABLE_PRICING_TIERS=true

# Feature Flags
NEXT_PUBLIC_MOCK_MODE=false
NEXT_PUBLIC_NETWORK_THROTTLE=false
```

### Backend `.env`

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/raptorflow_dev

# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
LOG_LEVEL=DEBUG

# Features
ENABLE_TOKEN_TRACKING=true
ENABLE_BUDGET_MANAGEMENT=true
ENABLE_PRICING_TIERS=true
```

---

## 📊 Monitoring Everything

### Option 1: Use Dev Monitor Button

1. Start frontend: `npm run dev`
2. Look for ⚙️ button in bottom-right corner
3. Click to expand
4. View all metrics in real-time

### Option 2: Console Logs

```typescript
// Network metrics
import { networkMonitor } from '@/lib/utils/networkMonitor'
networkMonitor.logStats()

// Token metrics
import { tokenTracker } from '@/lib/utils/tokenTracker'
tokenTracker.logStats()

// Token usage hook
import { useTokenUsage } from '@/lib/hooks/useTokenUsage'
const { usage } = useTokenUsage()
console.log(usage)
```

### Option 3: API Endpoints

```bash
# Check token usage
curl http://localhost:8000/api/v1/token-usage

# Check budget
curl http://localhost:8000/api/v1/budget-status

# Check tier
curl http://localhost:8000/api/v1/dev/current-tier

# Check health
curl http://localhost:8000/api/v1/health
```

---

## 🧪 Test Everything Locally

### 1. Test Authentication

```bash
# Frontend should connect to Supabase
# Check browser console for auth logs
# Should see: "✓ API client session updated"
```

### 2. Test Strategy Creation

```bash
# In frontend, create a strategy
# Check DevMonitor for:
# - Network request logged
# - Tokens recorded
# - Cost calculated

# In backend terminal:
# Should see: "POST /api/v1/strategies 201 Created"
```

### 3. Test Token Tracking

```bash
# Make API calls
# Check DevMonitor 💰 section:
# - Session Tokens increases
# - Estimated Cost increases
# - API Calls count increases

# In console:
import { tokenTracker } from '@/lib/utils/tokenTracker'
tokenTracker.logStats()
```

### 4. Test Network Speed

```bash
# Make multiple API calls
# Check DevMonitor 🌐 section:
# - Average response time shows
# - Network speed determined
# - Bandwidth estimated

# In console:
import { networkMonitor } from '@/lib/utils/networkMonitor'
networkMonitor.logStats()
```

### 5. Test Budget Warnings

```bash
# In usePricingTier hook:
const { setTier } = usePricingTier()
await setTier('basic')  // Sets low token limit

# Keep making requests
# DevMonitor shows budget usage increasing
# Reaches 80% → warning shows
# Reaches 100% → exceeded shows
```

### 6. Test Pricing Tiers (Dev Mode)

```bash
# In frontend, find PricingTierSelector component
# Should only show in development
# Switch between Basic/Pro/Enterprise
# Limits change immediately

# In console:
await setTier('enterprise')
// Notice in DevMonitor: token limits increased
```

---

## 📈 Interpreting Metrics

### Network Speed Categories

```
Fast:     < 100ms average response time
Moderate: 100-500ms average response time
Slow:     > 500ms average response time
```

### Budget Status

```
OK:       ≤ 80% of monthly budget used
Warning:  80-99% of monthly budget used
Exceeded: 100%+ of monthly budget used
```

### Network Health

```
✓ Green: Healthy (< 200ms, 0 errors)
⚠️ Yellow: Degraded (200-500ms, < 5% errors)
✗ Red: Poor (> 500ms, > 5% errors)
```

---

## 🐛 Troubleshooting

### Dev Monitor Not Showing

```bash
# Check environment
echo $NODE_ENV  # Should be 'development'

# Check env variable
echo $NEXT_PUBLIC_ENABLE_DEV_TOOLS  # Should be 'true'

# Check console for errors
# Press F12 → Console tab
```

### Network Metrics Showing 0

```bash
# Make some API calls first
# Visit a page that makes requests
# Wait a few seconds
# Metrics should appear

# Or manually trigger:
const { useTokenUsage } = require('@/lib/hooks/useTokenUsage')
// This makes API call to /api/v1/token-usage
```

### Token Tracking Not Working

```bash
# Check TokenLedger model exists in database
psql raptorflow_dev -c "SELECT * FROM token_ledger LIMIT 5;"

# Check API returns tokens
curl http://localhost:8000/api/v1/token-usage

# Check backend logs for errors
# Should see token entries being created
```

### Budget Status Not Updating

```bash
# Make some API calls first
# Check /api/v1/budget-status endpoint
curl http://localhost:8000/api/v1/budget-status

# Check useTokenUsage hook refreshes every 5 seconds
# Wait a bit and check again
```

---

## 📝 Development Workflow

### Making Changes

```bash
# 1. Frontend changes auto-reload
#    Just edit files in frontend/
#    Changes appear instantly in browser

# 2. Backend changes auto-reload
#    Edit files in backend/
#    FastAPI auto-reloads Python files
#    Check terminal for logs

# 3. Database changes need migration
#    Edit models in backend/app/models/
#    Create migration: alembic revision --autogenerate -m "Description"
#    Apply: alembic upgrade head
```

### Testing Changes

```bash
# 1. Test in Dev Monitor
#    - Check 🌐 Network metrics
#    - Check 💰 Token metrics
#    - Check 🏥 Health status

# 2. Test in Console
#    import { networkMonitor } from '@/lib/utils/networkMonitor'
#    networkMonitor.logStats()

# 3. Test via API
#    curl http://localhost:8000/api/v1/token-usage

# 4. Test in UI
#    View components update in real-time
```

---

## 🚀 What to Test

1. **Authentication**
   - ✓ Can sign up
   - ✓ Can sign in
   - ✓ Session persists
   - ✓ Tokens injected

2. **Strategies**
   - ✓ Can create
   - ✓ Can list
   - ✓ Can update
   - ✓ Can delete

3. **Token Tracking**
   - ✓ Tokens recorded per request
   - ✓ Cost calculated correctly
   - ✓ Session tokens tracked
   - ✓ Total tokens accumulate

4. **Network Monitoring**
   - ✓ Request times tracked
   - ✓ Response sizes recorded
   - ✓ Network speed calculated
   - ✓ Bandwidth estimated

5. **Budget Management**
   - ✓ Daily limits enforced
   - ✓ Monthly limits enforced
   - ✓ Warnings at 80%
   - ✓ Exceeded at 100%

6. **Pricing Tiers**
   - ✓ Can switch tiers
   - ✓ Limits change immediately
   - ✓ Features apply correctly
   - ✓ Only visible in dev mode

---

## 📊 Sample Output

### Dev Monitor - Network Section
```
🌐 Network
Avg Response:   145ms
Last Response:  234ms
Requests:       12
Errors:         0
Latency:        12ms
Bandwidth:      2.3 MB/s
```

### Dev Monitor - Tokens Section
```
💰 Tokens
Session Tokens: 3,450
Total Tokens:   15,234
Est. Cost:      $0.015
API Calls:      12
Cache Hits:     4
Budget Status:  ✓ OK
```

### Dev Monitor - Health Section
```
🏥 Health
✓ API Server
✓ Database
✓ Auth
Uptime:         2m 34s
```

---

## 🎯 Next Steps

1. **Start Frontend**
   ```bash
   cd frontend && npm run dev
   ```

2. **Start Backend**
   ```bash
   cd backend && python -m uvicorn app.main:app --reload
   ```

3. **Look for Dev Monitor**
   - Bottom-right corner
   - Blue gear icon (⚙️)
   - Click to expand

4. **Test Features**
   - Create a strategy
   - Watch metrics update
   - Check all sections

5. **Monitor Everything**
   - Network speed in real-time
   - Token usage per request
   - Budget remaining
   - All system health

---

## 📞 Help

### Check Logs
- **Frontend:** Browser console (F12)
- **Backend:** Terminal where you ran `python -m uvicorn`
- **Database:** psql command line

### Test Endpoints
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/token-usage
curl http://localhost:8000/api/v1/budget-status
```

### Export Metrics
```typescript
import { networkMonitor } from '@/lib/utils/networkMonitor'
console.log(networkMonitor.exportMetrics())
```

---

**Status:** ✅ Ready to Use
**Last Updated:** October 22, 2025
**Version:** 1.0.0

Start monitoring now! 🚀

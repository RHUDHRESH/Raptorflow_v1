# RaptorFlow 2.0 - Local Development Setup Guide

## 🚀 Quick Start (15 minutes)

### Prerequisites

```bash
# Check Node.js version (need 18+)
node --version

# Check Python version (need 3.10+)
python --version

# Check Git
git --version
```

### 1. Clone & Install Frontend

```bash
cd RaptorFlow_v1/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs on: **http://localhost:3000**

### 2. Setup Backend

```bash
cd RaptorFlow_v1/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on: **http://localhost:8000**

### 3. Setup Database (PostgreSQL)

```bash
# Install PostgreSQL (if not already installed)
# On Mac: brew install postgresql
# On Windows: Download from postgresql.org
# On Linux: sudo apt-get install postgresql

# Start PostgreSQL service
# On Mac/Linux: brew services start postgresql
# On Windows: Services app or pg_ctl start

# Create database
createdb raptorflow_dev

# Set connection string in .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/raptorflow_dev
```

### 4. Verify Setup

```bash
# Terminal 1: Frontend
cd frontend && npm run dev

# Terminal 2: Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 3: Check API
curl http://localhost:8000/api/v1/health
# Should return: {"status":"ok",...}
```

---

## 📊 Monitoring & Dev Tools

### Enable Debug Logging

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_MOCK_MODE=false
```

Create `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/raptorflow_dev
DEBUG=True
LOG_LEVEL=DEBUG
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Start with Full Logging

```bash
# Backend with debug output
python -m uvicorn app.main:app --reload --log-level debug

# Frontend with debug mode
npm run dev -- --verbose
```

---

## 🔧 Configuration Files

### `.env.local` (Frontend)

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Debug & Monitoring
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_ENABLE_DEV_TOOLS=true
NEXT_PUBLIC_NETWORK_MONITOR=true
NEXT_PUBLIC_TOKEN_MONITOR=true

# Feature Flags
NEXT_PUBLIC_ENABLE_PRICING_TIERS=true
NEXT_PUBLIC_PRICING_TIER_DEV_MODE=true
```

### `.env` (Backend)

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/raptorflow_dev

# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# API
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=debug

# Development
DEBUG=True
ENVIRONMENT=development

# Feature Flags
ENABLE_TOKEN_TRACKING=true
ENABLE_BUDGET_MANAGEMENT=true
ENABLE_PRICING_TIERS=true
```

---

## 🎯 Using the Dev Monitor (Hover Button)

The dev monitor button appears in bottom-right corner during development.

### What It Shows

**Network Monitoring:**
- Request/response times
- Network latency
- Bandwidth usage
- Request count
- Error rate

**Token Monitoring:**
- Tokens used this session
- Tokens used overall
- Cost estimation
- Cost breakdown by agent
- Budget status

**Performance:**
- React component render times
- API response times
- Memory usage
- CPU usage (if available)

**System Info:**
- Environment (dev/prod)
- Node version
- API status
- Database status

### Click to Expand

Click the button to see detailed metrics and logs.

---

## 📝 Complete Local Configuration

### Frontend Structure

```
frontend/
├── .env.local                 # Local environment variables
├── next.config.js
├── tsconfig.json
├── package.json
├── lib/
│   ├── api-client.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useAgent.ts
│   │   ├── useTokenUsage.ts
│   │   └── usePricingTier.ts
│   └── utils/
│       ├── devMonitor.ts      # Dev monitoring utility
│       ├── networkMonitor.ts  # Network speed tracking
│       └── tokenTracker.ts    # Token tracking utility
├── components/
│   ├── AgentMonitor.tsx
│   ├── TokenCounter.tsx
│   ├── PricingTierSelector.tsx
│   └── DevMonitor.tsx         # Hover button component
└── pages/
    └── [...].tsx
```

### Backend Structure

```
backend/
├── .env                       # Local environment variables
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── analysis.py
│   │   └── billing.py
│   ├── models/
│   │   ├── token_ledger.py
│   │   └── ...
│   └── utils/
│       ├── logging.py         # Debug logging
│       └── monitoring.py      # Request monitoring
└── tests/
    ├── test_api.py
    └── test_integration.py
```

---

## 🧪 Testing Locally

### Test API Endpoints

```bash
# Test health
curl http://localhost:8000/api/v1/health

# Test auth (create strategy)
curl -X POST http://localhost:8000/api/v1/strategies \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "test", "name": "Test Strategy"}'

# Test token usage
curl http://localhost:8000/api/v1/token-usage

# Test budget status
curl http://localhost:8000/api/v1/budget-status

# Test pricing tiers (dev mode)
curl -X POST http://localhost:8000/api/v1/dev/set-tier \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro"}'
```

### Test Frontend Components

```bash
# Start dev server with fast refresh
npm run dev

# Open http://localhost:3000
# See components reload automatically on file changes

# Open browser DevTools (F12)
# Check Console for debug logs
# Check Network tab for API calls
```

### Test Token Tracking

```bash
# 1. Open frontend
# 2. Go to strategy page
# 3. Check DevMonitor button (bottom-right)
# 4. Create a strategy
# 5. Check token count increases
# 6. Check cost display updates
```

---

## 🐛 Debugging

### Enable Console Logging

In `frontend/lib/api-client.ts`:
```typescript
const DEBUG = process.env.NEXT_PUBLIC_DEBUG === 'true'

if (DEBUG) {
  console.log('Request:', method, url, data)
  console.log('Response:', response.data)
}
```

### Check Backend Logs

```bash
# Backend will show:
# - Request logs (method, endpoint, duration)
# - Database queries
# - Token tracking
# - Errors with stack traces
```

### Use Browser DevTools

**Network Tab:**
- Check request/response times
- View request headers
- Check response payloads
- Monitor WebSocket/SSE

**Console Tab:**
- View debug logs
- Check for errors
- Monitor performance
- Test API client

**Storage Tab:**
- Check localStorage (tokens, session)
- Check sessionStorage
- View cookies

---

## 🔍 Monitoring Dashboard (Dev Monitor)

### Features

**Network Metrics:**
```
Average Response Time: 145ms
Last Response Time: 234ms
Network Latency: 12ms
Requests/min: 5
Error Rate: 0%
Bandwidth: 2.3 MB/s
```

**Token Metrics:**
```
Session Tokens: 3,450
Total Tokens: 15,234
Estimated Cost: $0.015
Cost Breakdown:
  - Agent1: $0.008
  - Agent2: $0.007
Budget Status: OK (45% used)
```

**Performance Metrics:**
```
React Renders: 23
Render Time: 145ms
API Calls: 12
Cache Hit Rate: 35%
Memory Usage: 125 MB
```

**System Info:**
```
Environment: development
Node Version: v18.16.0
API Status: ✓ Connected
Database: ✓ Connected
Auth: ✓ Authenticated
```

---

## 📊 Live Network Monitoring

The dev monitor tracks in real-time:

**Request Tracking:**
- Every API call is logged
- Response time recorded
- Error status tracked
- Payload size tracked

**Network Analysis:**
- Average response time
- P95/P99 latency
- Network speed estimation
- Bandwidth calculation

**Token Tracking:**
- Tokens per request
- Cost per request
- Running total
- Budget remaining

---

## 🎮 Dev Mode Features

### Pricing Tier Selector

```typescript
import { usePricingTier } from '@/lib/hooks/usePricingTier'

const { currentTier, setTier } = usePricingTier()

// Switch tiers dynamically
await setTier('pro')  // Changes limits immediately
```

### Mock API Mode

```env
# In .env.local
NEXT_PUBLIC_MOCK_MODE=true
```

This mocks API responses for testing without backend.

### Network Throttling

```typescript
// In devMonitor.ts
const throttle = process.env.NEXT_PUBLIC_NETWORK_THROTTLE // '3g', '4g', etc
```

Simulates slow networks for testing.

---

## 🚀 Production Checklist Before Deployment

- [ ] All .env.local variables removed
- [ ] DEBUG mode disabled
- [ ] Dev monitor hidden in production
- [ ] All console.log statements removed (or wrapped in DEBUG check)
- [ ] API endpoints verified
- [ ] Database migrations applied
- [ ] Auth tokens working
- [ ] Token tracking functional
- [ ] Budget enforcement active
- [ ] Pricing tiers working
- [ ] Error handling tested
- [ ] Performance metrics checked

---

## 📞 Troubleshooting

### Frontend Won't Start

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Backend Won't Connect

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Check logs for errors
# Check .env DATABASE_URL is correct
# Check port 8000 is available
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
# Check DATABASE_URL in .env is correct
# Check database exists:
psql -U postgres -l | grep raptorflow_dev

# Create if missing:
createdb raptorflow_dev

# Run migrations:
alembic upgrade head
```

### Token Tracking Not Working

```bash
# Check token_ledger table exists
# Check backend TokenLedger model imported
# Check /api/v1/token-usage endpoint responds
curl http://localhost:8000/api/v1/token-usage

# Check database has entries:
psql raptorflow_dev -c "SELECT * FROM token_ledger LIMIT 5;"
```

### Dev Monitor Not Showing

```bash
# Check env variable
echo $NEXT_PUBLIC_ENABLE_DEV_TOOLS

# Should be 'true' in development

# Check DevMonitor component is imported
# Check it's not hidden in CSS
```

---

## 🔄 Hot Reload & Development

### Frontend Hot Reload

```bash
npm run dev

# Edit any file in frontend/
# Changes appear instantly in browser
# No page refresh needed
```

### Backend Hot Reload

```bash
python -m uvicorn app.main:app --reload

# Edit any Python file
# Changes auto-reload
# Keep running in separate terminal
```

### Database Changes

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Downgrade if needed
alembic downgrade -1
```

---

## 📈 Performance Testing

### Load Testing API

```bash
# Install Apache Bench
# On Mac: brew install httpd
# On Linux: sudo apt-get install apache2-utils

# Test endpoint
ab -n 100 -c 10 http://localhost:8000/api/v1/health

# Results show:
# - Requests per second
# - Response times
# - Failed requests
```

### Monitor Performance

Use dev monitor to:
- Track average response times
- Identify slow endpoints
- Monitor token usage per request
- Check error rates

---

## 🎯 Next Steps

1. ✅ Set up local database (PostgreSQL)
2. ✅ Install frontend dependencies
3. ✅ Install backend dependencies
4. ✅ Configure .env files
5. ✅ Run migrations
6. ✅ Start both servers
7. ✅ Open http://localhost:3000
8. ✅ Test with dev monitor
9. ✅ Create sample data
10. ✅ Test all features

---

## 📚 Additional Resources

- Next.js Docs: https://nextjs.org/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://sqlalchemy.org
- PostgreSQL Docs: https://www.postgresql.org/docs

---

**Last Updated:** October 22, 2025
**Status:** Ready for Local Development
**Version:** 1.0.0

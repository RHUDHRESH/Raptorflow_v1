# RaptorFlow ADAPT - Complete Deployment Guide

**Status:** Production Ready Build
**Version:** 1.0.0
**Last Updated:** October 19, 2024

---

## 🚀 Quick Start (15 minutes)

### Prerequisites
- Node.js 18+
- Python 3.11+
- Git
- Supabase Account (free tier)
- Google Cloud Account (with $100 credit)
- Razorpay Account
- OpenAI/Gemini API Keys

### Step 1: Clone & Setup Backend

```bash
cd Raptorflow_v1/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Fill in your credentials:
# GOOGLE_API_KEY=your_gemini_key
# PERPLEXITY_API_KEY=your_perplexity_key
# SUPABASE_URL=your_supabase_url
# SUPABASE_SERVICE_KEY=your_service_key
# RAZORPAY_KEY_ID=your_razorpay_key
# RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### Step 2: Setup Supabase Database

```bash
# Go to https://supabase.com and create a new project
# Get your project URL and service key

# Copy the SQL from backend/sql/schema.sql
# Paste it into Supabase SQL Editor and run
```

### Step 3: Start Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# API will be at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Step 4: Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key
EOF

# Start dev server
npm run dev
# App will be at http://localhost:3000
```

---

## 📊 Architecture Overview

### Backend (FastAPI + LangGraph)
```
Frontend (Next.js)
    ↓
API Gateway (FastAPI)
    ↓
Orchestrator Agent (LangGraph)
    ├→ Research Agent (Perplexity + Evidence Graph)
    ├→ Positioning Agent (Strategic Analysis)
    ├→ ICP Agent (Customer Profiling)
    ├→ Strategy Agent (7Ps + North Star)
    ├→ Content Agent (Calendar Generation)
    ├→ Analytics Agent (Performance Measurement)
    └→ Trend Monitor (Daily Background Job)
         ↓
    Supabase (PostgreSQL + pgvector)
```

### Database Schema

**Core Tables:**
- `businesses` - Business profiles
- `subscriptions` - Payment & tier management
- `positioning_analyses` - Strategic positioning
- `icps` - Customer profiles
- `moves` - Marketing campaigns

**Knowledge Tables:**
- `evidence_nodes` - Claims, RTBs, insights (with embeddings)
- `evidence_edges` - Relationships between evidence
- `sostac_analyses` - Situation-Objectives-Strategy framework

**Monitoring:**
- `trend_checks` - Perplexity trend results
- `performance_metrics` - Campaign performance
- `route_back_logs` - Learning from results

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
# AI Models
GOOGLE_API_KEY=your_gemini_key
PERPLEXITY_API_KEY=your_perplexity_key
OPENAI_API_KEY=optional_openai_key

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# Payment
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# Monitoring
LANGSMITH_API_KEY=optional_langsmith_key

# Environment
ENVIRONMENT=development  # or production
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000  # or prod URL
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key
```

### Subscription Tiers

```python
{
    "basic": {
        "price_inr": 2000,      # ₹2,000/month
        "max_icps": 3,          # 3 customer profiles
        "max_moves": 5,         # 5 campaigns
        "features": ["positioning", "basic_icps", "content_calendar"]
    },
    "pro": {
        "price_inr": 3500,      # ₹3,500/month
        "max_icps": 6,
        "max_moves": 15,
        "features": ["...", "trend_monitoring", "route_back_logic"]
    },
    "enterprise": {
        "price_inr": 5000,      # ₹5,000/month
        "max_icps": 9,
        "max_moves": 999,
        "features": ["all features", "white_label"]
    }
}
```

---

## 🐳 Docker & Google Cloud Deployment

### Step 1: Build Docker Images

```bash
# Backend
cd backend
docker build -t gcr.io/raptorflow/backend:latest .

# Frontend
cd ../frontend
docker build -t gcr.io/raptorflow/frontend:latest .
```

### Step 2: Push to Google Container Registry

```bash
# Authenticate with GCP
gcloud auth configure-docker

# Push images
docker push gcr.io/raptorflow/backend:latest
docker push gcr.io/raptorflow/frontend:latest
```

### Step 3: Deploy to Cloud Run

```bash
# Backend
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow/backend:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars "SUPABASE_URL=...,SUPABASE_SERVICE_KEY=..." \
  --memory 2Gi \
  --timeout 900

# Frontend
gcloud run deploy raptorflow-frontend \
  --image gcr.io/raptorflow/frontend:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://raptorflow-backend-xyz.run.app" \
  --memory 512Mi
```

### Step 4: Connect Custom Domain (Hostinger)

In Hostinger DNS panel, add CNAME records:
```
api.yourdomain.com    →  raptorflow-backend-xyz.run.app
app.yourdomain.com    →  raptorflow-frontend-xyz.run.app
```

Then in Cloud Run console, add custom domains to each service.

---

## 💰 Cost Estimation

### Development (Gemini + Google Cloud Free Tier)
- **Google Cloud:** $0 (free tier covers ~2M requests/month)
- **Gemini API:** $0 (free tier 1500 requests/day)
- **Supabase:** $0 (free tier 500MB DB)
- **Perplexity:** ~$0.05 per search
- **Total:** ~$2-5/month

### Production (10 customers on Pro tier)
- **Infrastructure:** ~$15/month (after free tier)
- **OpenAI:** ~$0.50 per analysis × 100 analyses = $50
- **Perplexity:** ~$30/month (10 customers × daily searches)
- **Supabase:** $25/month (scales with usage)
- **Total Cost:** ~$120/month
- **Revenue:** 10 × ₹3,500 = ₹35,000 (~$420/month)
- **Gross Margin:** ~71%

---

## 🧪 Testing Locally

### 1. Test Backend Only

```bash
cd backend
python3 -c "
from agents.orchestrator import orchestrator
from utils.supabase_client import get_supabase_client

# Test will use in-memory Supabase
print('Backend agents loaded successfully')
"
```

### 2. Test Full Flow

```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Test via curl
curl -X POST http://localhost:8000/api/intake \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Business",
    "industry": "SaaS",
    "location": "Singapore",
    "description": "A productivity app",
    "goals": "Gain 100 customers"
  }'

# Should return business_id
```

### 3. Manual Testing Checklist

- [ ] **Intake Flow**
  - [ ] Create business
  - [ ] Verify subscription created
  - [ ] Check Supabase database

- [ ] **Positioning Flow**
  - [ ] Run research analysis
  - [ ] Generate 3 positioning options
  - [ ] Select one option
  - [ ] Verify saved to database

- [ ] **ICP Flow**
  - [ ] Generate ICPs for positioning
  - [ ] Verify embeddings created
  - [ ] Check monitoring tags extracted

- [ ] **Strategy Flow**
  - [ ] Build 7Ps strategy
  - [ ] Define North Star metric
  - [ ] Create strategic bets

- [ ] **Content Flow**
  - [ ] Create content move/campaign
  - [ ] Generate calendar
  - [ ] Verify platform validation

- [ ] **Payment Flow**
  - [ ] Create Razorpay checkout
  - [ ] Complete test payment
  - [ ] Verify subscription upgraded
  - [ ] Check tier limits enforced

- [ ] **Trend Monitoring**
  - [ ] Trigger daily trend check
  - [ ] Verify Perplexity search
  - [ ] Check calendar injection

---

## 📈 Monitoring & Logs

### Google Cloud Run Logs
```bash
# View backend logs
gcloud run logs read raptorflow-backend --limit 50

# View frontend logs
gcloud run logs read raptorflow-frontend --limit 50

# Stream live logs
gcloud run logs read raptorflow-backend --limit 0 --follow
```

### LangSmith Monitoring (Optional)

If using LangSmith for agent monitoring:

1. Get API key from https://smith.langchain.com
2. Set in `.env`:
   ```
   LANGSMITH_API_KEY=your_key
   LANGCHAIN_TRACING_V2=true
   ```
3. View traces at https://smith.langchain.com

### Key Metrics to Monitor

- **API Response Times:** Should be <5s for most endpoints, <60s for agent operations
- **Error Rates:** Should be <1%
- **Cost:** Monitor OpenAI/Perplexity spending daily
- **Database:** Monitor Supabase usage (connection count, row count)

---

## 🔒 Security Checklist

- [ ] **Secrets Management**
  - [ ] Never commit .env files
  - [ ] Use Cloud Run secret manager for production
  - [ ] Rotate API keys monthly

- [ ] **Database**
  - [ ] Enable row-level security (RLS) in Supabase
  - [ ] Backup daily
  - [ ] Use read-only replicas for analytics

- [ ] **API Security**
  - [ ] Add rate limiting (implement in FastAPI middleware)
  - [ ] Validate all inputs
  - [ ] Use HTTPS only (auto-enabled on Cloud Run)
  - [ ] Add CORS policy (currently "*", restrict in production)

- [ ] **Payment Security**
  - [ ] Verify Razorpay webhook signatures
  - [ ] Use Razorpay's test mode for development
  - [ ] Never log payment sensitive data

---

## 📚 API Endpoints

### Intake
- `POST /api/intake` - Create business
- `GET /api/business/{business_id}` - Get business

### Research
- `POST /api/research/{business_id}` - Run research
- `GET /api/research/{business_id}` - Get research results

### Positioning
- `POST /api/positioning/{business_id}` - Generate options
- `POST /api/positioning/{business_id}/select` - Select option
- `GET /api/positioning/{business_id}` - Get positioning

### ICPs
- `POST /api/icps/{business_id}` - Generate ICPs
- `GET /api/icps/{business_id}` - List ICPs

### Moves
- `POST /api/moves` - Create campaign
- `GET /api/moves/{move_id}` - Get campaign
- `GET /api/moves/business/{business_id}` - List campaigns

### Analytics
- `POST /api/analytics/measure` - Submit performance data

### Payment
- `POST /api/razorpay/checkout` - Create payment session
- `POST /api/razorpay/webhook` - Handle Razorpay webhook

---

## 🚨 Troubleshooting

### "SUPABASE credentials missing" Error
**Solution:** Make sure `.env` has `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`

### "Invalid API Key" for OpenAI/Gemini
**Solution:** Verify keys in `.env` - check for extra spaces

### Frontend can't reach backend
**Solution:**
- Check CORS in `main.py` (line 36-42)
- Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Check if backend is running on correct port

### Razorpay webhook not firing
**Solution:**
- Add webhook URL to Razorpay dashboard
- Use ngrok for local testing: `ngrok http 8000`
- Check webhook logs in Razorpay dashboard

### High API costs
**Solution:**
- Switch to `gpt-4o-mini` for development
- Implement caching for embeddings
- Use Gemini for testing (free tier)

---

## 📖 Key Files

### Backend
- `backend/main.py` - API endpoints
- `backend/config.py` - Configuration
- `backend/agents/` - Agent implementations
- `backend/tools/` - LLM tools
- `backend/sql/schema.sql` - Database schema
- `backend/requirements.txt` - Python dependencies

### Frontend
- `frontend/app/page.tsx` - Landing page
- `frontend/app/intake/page.tsx` - Intake form
- `frontend/app/dashboard/` - Main dashboard
- `frontend/package.json` - Dependencies
- `frontend/next.config.js` - Next.js config

### Infrastructure
- `backend/Dockerfile` - Backend container
- `frontend/Dockerfile` - Frontend container
- `docker-compose.yml` - Local testing (optional)

---

## 🎯 Next Steps After Launch

### Week 1: Monitoring & Feedback
- Monitor error rates and performance
- Collect user feedback
- Fix critical bugs

### Week 2: Optimizations
- Implement caching for faster responses
- Add more trend monitoring sources
- Optimize database queries

### Week 3: Additional Features
- Asset Factory (Canva integration)
- Multi-channel publishing
- Advanced analytics dashboard

### Month 2: Scale
- Add authentication system
- Implement team collaboration
- Build white-label version

---

## 📞 Support

For issues or questions:
- Check this guide's troubleshooting section
- Review code comments and docstrings
- Check backend logs: `gcloud run logs read raptorflow-backend`
- Test endpoints with FastAPI docs: http://localhost:8000/docs

---

**Deploy Status:** Ready for Production
**Version:** 1.0.0
**Last Updated:** 2024-10-19

Made with 🚀 by RaptorFlow Team

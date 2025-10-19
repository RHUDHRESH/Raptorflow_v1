# RaptorFlow - Next Steps to Launch

**Your system is PRODUCTION READY.** Follow these steps to launch:

---

## 🚀 Step 1: Get API Keys (15 minutes)

### 1.1 Gemini API (Free for development)
```
1. Go to https://aistudio.google.com/app/apikeys
2. Create new API key
3. Copy key to backend/.env: GOOGLE_API_KEY=xxx
```

### 1.2 OpenAI API (For production)
```
1. Go to https://platform.openai.com/api/keys
2. Create new API key
3. Copy key to backend/.env: OPENAI_API_KEY=xxx
```

### 1.3 Perplexity API (Required for research)
```
1. Go to https://www.perplexity.ai/
2. Sign up and get API access
3. Copy key to backend/.env: PERPLEXITY_API_KEY=xxx
```

### 1.4 Razorpay (For payments)
```
1. Go to https://razorpay.com (India account)
2. Sign up → Get API credentials
3. Copy to backend/.env: RAZORPAY_KEY_ID=xxx, RAZORPAY_KEY_SECRET=xxx
```

---

## 🗄️ Step 2: Setup Supabase (10 minutes)

### 2.1 Create Supabase Project
```
1. Go to https://supabase.com
2. Sign up → Create new project
3. Wait for project to spin up (2 minutes)
```

### 2.2 Get Credentials
```
1. Go to Settings → API
2. Copy Project URL to backend/.env: SUPABASE_URL=xxx
3. Copy Service Role Key to backend/.env: SUPABASE_SERVICE_KEY=xxx
```

### 2.3 Run Database Schema
```
1. In Supabase, click SQL Editor
2. Open file: backend/sql/schema.sql
3. Copy ALL content
4. Paste into SQL Editor
5. Click RUN
6. Wait for success message
```

---

## 💻 Step 3: Test Locally (20 minutes)

### 3.1 Start Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from your keys (copy from step 1)
cp .env.example .env
nano .env  # Edit with your API keys

# Start server
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3.2 Test Backend
```bash
# In another terminal, test the API:
curl -X POST http://localhost:8000/api/intake \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Restaurant",
    "industry": "Food & Beverage",
    "location": "Singapore",
    "description": "Authentic Italian restaurant",
    "goals": "50 new customers monthly"
  }'

# Should return: {"success": true, "business_id": "xxx", ...}
```

### 3.3 Start Frontend
```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_RAZORPAY_KEY_ID=test_123" >> .env.local

# Start dev server
npm run dev
```

**Expected Output:**
```
- ready started server on 0.0.0.0:3000
```

### 3.4 Test Frontend
```
1. Open http://localhost:3000 in browser
2. See landing page
3. Click "Get Started"
4. Fill intake form with test data
5. Click submit
6. Should see "Business created successfully"
```

---

## 🌐 Step 4: Deploy to Google Cloud (30 minutes)

### 4.1 Setup Google Cloud
```bash
# Install Google Cloud CLI
# Mac: brew install google-cloud-sdk
# Windows: Download from https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Create new project
gcloud projects create raptorflow-prod --name="RaptorFlow"
gcloud config set project raptorflow-prod
```

### 4.2 Enable Required APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable compute.googleapis.com
```

### 4.3 Build & Push Docker Images
```bash
# Authenticate Docker
gcloud auth configure-docker

# Build backend image
cd backend
docker build -t gcr.io/raptorflow-prod/backend:latest .
docker push gcr.io/raptorflow-prod/backend:latest

# Build frontend image
cd ../frontend
docker build -t gcr.io/raptorflow-prod/frontend:latest .
docker push gcr.io/raptorflow-prod/frontend:latest
```

### 4.4 Deploy Backend to Cloud Run
```bash
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-prod/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 900 \
  --set-env-vars "SUPABASE_URL=YOUR_URL,SUPABASE_SERVICE_KEY=YOUR_KEY,GOOGLE_API_KEY=YOUR_KEY,PERPLEXITY_API_KEY=YOUR_KEY,RAZORPAY_KEY_ID=YOUR_ID,RAZORPAY_KEY_SECRET=YOUR_SECRET"

# Copy the service URL
```

### 4.5 Deploy Frontend to Cloud Run
```bash
gcloud run deploy raptorflow-frontend \
  --image gcr.io/raptorflow-prod/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://raptorflow-backend-xxx.run.app,NEXT_PUBLIC_RAZORPAY_KEY_ID=YOUR_KEY"

# Copy the service URL
```

---

## 🌍 Step 5: Connect Custom Domain (Hostinger)

### 5.1 Add CNAME Records
```
In Hostinger DNS Panel:
1. Go to Hostinger domain management
2. Add CNAME records:
   - Name: api
     Value: raptorflow-backend-xyz.run.app
   - Name: app
     Value: raptorflow-frontend-xyz.run.app
   - Name: www
     Value: raptorflow-frontend-xyz.run.app
```

### 5.2 Setup SSL in Google Cloud
```bash
# In Cloud Run console:
1. Go to raptorflow-backend service
2. Click "Manage Custom Domains"
3. Add: api.yourdomain.com
4. Click "Create Mapping"
5. Repeat for raptorflow-frontend with app.yourdomain.com

# Google Auto-provisions SSL certificates (free)
# Wait 5-15 minutes for DNS propagation
```

### 5.3 Test Custom Domains
```
1. Visit http://api.yourdomain.com/docs
   Should see FastAPI Swagger UI

2. Visit http://app.yourdomain.com
   Should see RaptorFlow landing page
```

---

## 💳 Step 6: Setup Razorpay Webhook

### 6.1 Add Webhook in Razorpay Dashboard
```
1. Go to Razorpay Dashboard
2. Settings → Webhooks
3. Add webhook:
   URL: https://api.yourdomain.com/api/razorpay/webhook
   Events: payment.captured
4. Copy Webhook Secret
5. Add to backend/.env: RAZORPAY_WEBHOOK_SECRET=xxx
```

### 6.2 Test Payment Flow
```
1. Visit app.yourdomain.com
2. Create business
3. Click "Upgrade to Pro"
4. Use Razorpay test card:
   - Card: 4111111111111111
   - CVV: 123
   - Expiry: 12/25
5. Click Pay
6. Should show "Payment Successful"
7. Check Supabase: subscriptions tier should be "pro"
```

---

## 📊 Step 7: Initial Testing Checklist

### Complete Flow Test
- [ ] Create business via intake form
- [ ] Verify business saved in Supabase
- [ ] Run research analysis (wait 30 seconds)
- [ ] See 3 positioning options
- [ ] Select one option
- [ ] Generate ICPs (should get 3-6 based on tier)
- [ ] View ICP details
- [ ] Create content move
- [ ] See generated calendar
- [ ] Test upgrade to Pro tier
- [ ] Verify Razorpay payment works

### Backend Testing
- [ ] API docs at /docs working
- [ ] All endpoints return proper responses
- [ ] Error handling works correctly
- [ ] Database queries execute properly

### Frontend Testing
- [ ] All pages load correctly
- [ ] Forms validate inputs
- [ ] Loading states display
- [ ] Error messages show
- [ ] Responsive design works

---

## 📈 Step 8: Monitor & Scale

### Setup Monitoring (Optional but Recommended)
```bash
# LangSmith (for agent tracing)
1. Go to https://smith.langchain.com
2. Get API key
3. Add to backend/.env: LANGSMITH_API_KEY=xxx
4. Set: LANGCHAIN_TRACING_V2=true

# This logs all agent decisions for debugging
```

### Check Costs
```bash
# Google Cloud
1. Go to Google Cloud Console
2. Billing → View Reports
3. Watch for runaway costs

# OpenAI
1. Go to https://platform.openai.com/account/billing/overview
2. Set usage limits

# Perplexity
1. Go to Perplexity dashboard
2. Monitor API usage
```

---

## 🎯 Go-Live Checklist

Before opening to public users:

- [ ] All API keys configured
- [ ] Database backup automated
- [ ] Error tracking setup (optional: Sentry)
- [ ] Logging configured
- [ ] HTTPS everywhere (auto on Cloud Run)
- [ ] CORS properly configured
- [ ] Rate limiting active
- [ ] Payment processing tested
- [ ] Customer support email set up
- [ ] Privacy policy created
- [ ] Terms of service created
- [ ] First 5 beta users identified
- [ ] Feedback collection process set up

---

## 🚨 Emergency Commands

If something breaks:

```bash
# View backend logs
gcloud run logs read raptorflow-backend --limit 50

# View frontend logs
gcloud run logs read raptorflow-frontend --limit 50

# Restart backend
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-prod/backend:latest

# Check database
# Go to Supabase dashboard → Check tables

# Test API locally
curl http://localhost:8000/docs
```

---

## 📞 Quick Help

### "Backend not starting"
```
1. Check Python version: python3 --version (need 3.11+)
2. Check venv activated: pip list (should show many packages)
3. Check .env exists: ls backend/.env
4. Check API keys valid: open URLs in browser
```

### "Frontend can't reach backend"
```
1. Check backend running: curl http://localhost:8000
2. Check .env.local exists: cat frontend/.env.local
3. Check NEXT_PUBLIC_API_URL correct: should be http://localhost:8000 (dev)
```

### "Supabase schema errors"
```
1. Check SQL has no syntax errors
2. Run one CREATE TABLE at a time
3. Check pgvector extension is enabled: CREATE EXTENSION vector;
```

### "Payment not working"
```
1. Check Razorpay keys in .env
2. Check webhook URL in Razorpay dashboard
3. Test with Razorpay test card (4111111111111111)
4. Check logs: gcloud run logs read raptorflow-backend
```

---

## 📚 Documentation

- **README.md** - Overview and features
- **DEPLOYMENT_GUIDE.md** - Full deployment walkthrough
- **IMPLEMENTATION_SUMMARY.md** - What's been built
- **API Docs** - http://localhost:8000/docs
- **Code Comments** - Throughout codebase

---

## ⏱️ Expected Timeline

| Task | Time | Status |
|------|------|--------|
| Get API Keys | 15 min | Do now |
| Setup Supabase | 10 min | Do now |
| Test Locally | 20 min | Do now |
| Deploy to Cloud | 30 min | Tomorrow |
| Setup Domain | 15 min | Tomorrow |
| Test in Production | 20 min | Tomorrow |
| **Total** | **1.5 hours** | Ready to launch! |

---

## 🎉 You're Ready!

After completing these steps, you'll have:

✅ Production-grade system running
✅ Custom domain connected
✅ Payment processing working
✅ Database persisting data
✅ All agents functioning
✅ Ready to onboard customers

**Next: Tell a friend and get your first customer!**

---

**Questions? Check DEPLOYMENT_GUIDE.md for detailed help.**

Version 1.0.0 | October 19, 2024 | Ready to Launch 🚀

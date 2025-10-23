# RaptorFlow ADAPT - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Configure Environment
```bash
cp .env.cloud.example .env
# Edit .env and fill in your API keys (OpenAI, Gemini, Supabase, etc.)
```

### Step 2: Start Services
```bash
docker-compose up --build
```

### Step 3: Access Application
- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

---

## 📋 Development Commands

### View Logs
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# All logs
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Without Cache
```bash
docker-compose up --build --no-cache
```

### Run Command in Container
```bash
# Backend
docker-compose exec backend sh

# Frontend
docker-compose exec frontend sh
```

### Health Check
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

---

## 🌍 Production Deployment

### Option 1: Google Cloud Run (Recommended)
```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy (uses cloudbuild.yaml)
gcloud builds submit

# Or deploy manually
gcloud run deploy raptorflow \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars APP_MODE=prod
```

### Option 2: Self-Hosted Docker
```bash
# Build images
docker build -t raptorflow-api:latest .
docker build -t raptorflow-web:latest -f Dockerfile.frontend .

# Run with docker-compose
docker-compose up -d

# Or run individually
docker run -d -p 8080:8080 --env-file .env raptorflow-api:latest
docker run -d -p 3000:3000 raptorflow-web:latest
```

### Option 3: Kubernetes
```bash
# Create deployment manifests (generate from docker-compose)
docker-compose config > k8s-deployment.yaml

# Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml
```

---

## 🔧 Configuration

### Environment Variables (Required)
```bash
# AI Provider Setup
APP_MODE=prod                          # dev or prod
OPENAI_API_KEY=sk-proj-xxx            # For production
GEMINI_API_KEY=xxx                     # For development
OPENROUTER_API_KEY=sk-or-v1-xxx       # Fallback

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SUPABASE_SERVICE_KEY=xxx

# Security
JWT_SECRET_KEY=your-secret-32-chars
ENCRYPTION_KEY=your-key-32-chars

# Payments
RAZORPAY_KEY_ID=rzp_live_xxx
RAZORPAY_KEY_SECRET=xxx
RAZORPAY_WEBHOOK_SECRET=xxx

# URLs
FRONTEND_URL=http://localhost:3000         # For dev
NEXT_PUBLIC_API_URL=http://localhost:8000  # For dev
```

### For Production
```bash
# Update URLs to your domain
FRONTEND_URL=https://app.yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Use production API keys
APP_MODE=prod
```

---

## 🐳 Docker Information

### Images
- **Backend**: python:3.11-slim (~500MB)
- **Frontend**: node:20-alpine (~300MB)

### Ports
- Backend: 8000 (external) → 8080 (internal)
- Frontend: 3000 (both internal and external)

### Health Checks
- Backend: `curl -f http://localhost:8080/health`
- Frontend: `wget --spider http://localhost:3000`

### Services
- Backend and frontend start independently
- Frontend waits for backend health check before becoming accessible

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs -f

# Verify .env exists
ls -la .env

# Rebuild with verbose output
docker-compose up --build --verbose
```

### Health check failures
```bash
# Test backend health manually
docker-compose exec backend curl -f http://localhost:8080/health

# Test frontend
docker-compose exec frontend wget --quiet --tries=1 --spider http://localhost:3000
```

### Port already in use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9  # Port 8000
lsof -ti:3000 | xargs kill -9  # Port 3000

# Or use different ports in docker-compose.yml
# Change: "8000:8080" to "8001:8080"
```

### Out of disk space
```bash
# Clean up Docker
docker system prune -a

# Remove volumes
docker volume prune

# Clear build cache
docker-compose build --no-cache
```

---

## 📚 More Information

- Full documentation: See `README.md`
- Docker guide: See `DOCKER.md`
- Deployment checklist: See `DEPLOYMENT_READY.md`
- Session summary: See `SESSION_SUMMARY.md`

---

## 🎯 Architecture

### Development Mode
```
User → Frontend (localhost:3000)
         ↓
       Backend (localhost:8000)
         ↓
       Google Gemini (primary)
         ↓ (fallback)
       OpenRouter
```

### Production Mode
```
User → Frontend (https://yourdomain.com)
         ↓
       Backend (https://api.yourdomain.com)
         ↓
       OpenAI GPT-5 (primary)
         ↓ (fallback)
       OpenRouter
```

---

## ✅ Verification Steps

After starting with `docker-compose up --build`:

1. **Backend is healthy**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

2. **Frontend is accessible**
   ```bash
   curl http://localhost:3000
   # Should return HTML content
   ```

3. **Frontend can reach backend**
   ```bash
   # Check browser console at http://localhost:3000
   # No CORS errors should appear
   ```

4. **API is working**
   ```bash
   curl -X POST http://localhost:8000/api/endpoint \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

---

## 🚀 Next Steps

1. **Configure your API keys** in `.env`
2. **Test locally** with `docker-compose up --build`
3. **Deploy to Cloud Run** with `gcloud builds submit`
4. **Set up custom domain** in Cloud Run console
5. **Monitor with Cloud Logging** in GCP console

---

**Ready to deploy!** 🎉

Questions? See `DEPLOYMENT_READY.md` for comprehensive details.

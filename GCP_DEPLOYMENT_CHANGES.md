# GCP Deployment Readiness - Changes Summary

## Overview
This document summarizes all changes made to prepare RaptorFlow for deployment on Google Cloud Platform (GCP) via GitHub Actions.

## Files Modified

### 1. Backend Configuration

#### `backend/Dockerfile`
**Changes:**
- Fixed CMD to use `uvicorn main:app` instead of `gunicorn app.main:app`
- Updated to work with FastAPI application structure
- Maintained multi-stage build for optimization
- Kept Cloud Run PORT environment variable support

**Why:** The original Dockerfile referenced incorrect app path. FastAPI app is at `main.py` not `app/main.py`.

### 2. Frontend Configuration

#### `frontend/next.config.js`
**Changes:**
- Changed `output` from `'export'` to `'standalone'`
- Removed `distDir: 'out'` configuration
- Added proper environment variable handling
- Configured for Cloud Run dynamic runtime

**Why:** Cloud Run requires a running server, not static files. Next.js standalone mode creates a self-contained server.

#### `frontend/Dockerfile`
**Changes:**
- Complete rewrite for standalone output
- Three-stage build: deps → builder → runner
- Copies `.next/standalone`, `.next/static`, and `public` directories
- Uses `node server.js` as entry point
- Added health check for API endpoint

**Why:** Needed to support Next.js standalone output and proper Cloud Run deployment.

## Files Created

### 1. `.gcloudignore`
**Purpose:** Excludes unnecessary files from Cloud Build
**Contents:**
- node_modules, .git, test files
- Environment files (.env*)
- Development files (.vscode, .idea)
- Build artifacts

### 2. `setup-gcp-secrets.sh`
**Purpose:** Interactive script to set up GCP Secret Manager secrets
**Features:**
- Prompts for each secret value
- Creates or updates secrets
- Validates gcloud CLI installation
- Checks project configuration

### 3. `DEPLOY_TO_GCP.md`
**Purpose:** Quick deployment guide
**Sections:**
- Prerequisites
- Step-by-step deployment
- GitHub Actions setup
- Files modified summary

## Existing Files (Already Configured)

### `cloudbuild.yaml`
**Status:** ✅ Already properly configured
**Features:**
- Builds both backend and frontend images
- Pushes to GCR
- Deploys to Cloud Run
- Handles secrets via Secret Manager

### `.github/workflows/enhanced-cd.yml`
**Status:** ✅ Already has GCP deployment
**Features:**
- Multi-environment support (staging/production)
- Builds and pushes Docker images
- Deploys to Cloud Run
- Health checks
- Deployment summaries

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│          GitHub Repository              │
│    (Push to main or manual trigger)     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│        GitHub Actions Workflow          │
│  (.github/workflows/enhanced-cd.yml)    │
│                                         │
│  1. Build Backend Docker Image          │
│  2. Build Frontend Docker Image         │
│  3. Push to Google Container Registry   │
│  4. Deploy Backend to Cloud Run         │
│  5. Deploy Frontend to Cloud Run        │
│  6. Run Health Checks                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│        Google Cloud Platform            │
│                                         │
│  ┌─────────────────┐  ┌──────────────┐ │
│  │  Cloud Run      │  │ Secret       │ │
│  │                 │  │ Manager      │ │
│  │ • Backend       │  │              │ │
│  │ • Frontend      │  │ • API Keys   │ │
│  │                 │  │ • DB Creds   │ │
│  └─────────────────┘  └──────────────┘ │
│                                         │
│  ┌─────────────────┐                   │
│  │ Container       │                   │
│  │ Registry (GCR)  │                   │
│  │                 │                   │
│  │ • Images        │                   │
│  │ • Versions      │                   │
│  └─────────────────┘                   │
└─────────────────────────────────────────┘
```

## Environment Variables & Secrets

### Secrets (via GCP Secret Manager)
- `supabase-url`
- `supabase-key`
- `supabase-service-key`
- `openai-api-key`
- `gemini-api-key`
- `perplexity-api-key`
- `razorpay-key-id`
- `razorpay-key-secret`
- `razorpay-webhook-secret`
- `jwt-secret-key`
- `encryption-key`

### Environment Variables (Cloud Run)
Backend:
- `ENVIRONMENT=production`
- `PORT=8080`

Frontend:
- `NEXT_PUBLIC_API_URL` (set to backend URL)
- `NODE_ENV=production`
- `PORT=3000`

## GitHub Secrets Required

For GitHub Actions to work, add these secrets in your repository:

1. `GCP_PROJECT_ID` - Your GCP project ID
2. `GCP_SA_KEY` - Service account JSON key (entire contents)

Optional (for notifications):
3. `SLACK_WEBHOOK` - For deployment notifications

## Deployment Steps

### First-Time Setup

1. **Set up GCP:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable run.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com
   ```

2. **Create secrets:**
   ```bash
   ./setup-gcp-secrets.sh
   ```

3. **Create GitHub service account:**
   ```bash
   gcloud iam service-accounts create github-actions
   # Grant permissions (see DEPLOY_TO_GCP.md)
   ```

4. **Add secrets to GitHub repository**

### Subsequent Deployments

Simply push to `main` branch or manually trigger the workflow in GitHub Actions.

## Testing Locally

### Backend
```bash
cd backend
docker build -t raptorflow-backend .
docker run -p 8080:8080 --env-file ../.env.local raptorflow-backend
```

### Frontend
```bash
cd frontend
docker build -t raptorflow-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8080 raptorflow-frontend
```

## Cost Optimization Tips

1. Set `min-instances=0` for staging environments
2. Use appropriate CPU and memory limits
3. Enable request-based autoscaling
4. Set up billing alerts
5. Monitor usage with Cloud Monitoring

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all dependencies are in requirements.txt / package.json
- Test Docker build locally first

### Deployment Fails
- Check Cloud Run logs: `gcloud run services logs read SERVICE_NAME`
- Verify secrets are created
- Check IAM permissions

### App Not Starting
- Verify PORT environment variable
- Check health endpoint is accessible
- Review application logs

## Security Checklist

- ✅ Secrets stored in Secret Manager (not in code)
- ✅ .env files in .gitignore and .gcloudignore
- ✅ Non-root user in Docker containers
- ✅ Health checks configured
- ✅ CORS properly configured
- ✅ Authentication middleware in production

## Next Steps

After deployment:

1. **Configure custom domain** (optional)
2. **Set up Cloud Armor** for DDoS protection
3. **Enable Cloud CDN** for static assets
4. **Configure monitoring alerts**
5. **Set up log aggregation**
6. **Implement backup strategy**

## Support

For deployment issues:
1. Check Cloud Run logs
2. Review GitHub Actions workflow logs
3. Test Docker builds locally
4. Verify all secrets are set

---

**Status:** ✅ Ready for GCP Deployment
**Last Updated:** 2025-01-21
**Version:** 1.0.0

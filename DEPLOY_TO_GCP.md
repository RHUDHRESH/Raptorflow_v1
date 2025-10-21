# Deploy RaptorFlow to Google Cloud Platform

## Quick Start

### Prerequisites
- Google Cloud account with billing enabled
- gcloud CLI installed
- Docker installed
- GitHub account

### Step 1: GCP Setup

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
```

### Step 2: Store Secrets

```bash
# Create all required secrets in Secret Manager
gcloud secrets create supabase-url --data-file=- <<< "your-url"
gcloud secrets create supabase-key --data-file=- <<< "your-key"
gcloud secrets create openai-api-key --data-file=- <<< "your-key"
gcloud secrets create gemini-api-key --data-file=- <<< "your-key"
# ... add all other secrets
```

### Step 3: Deploy

```bash
# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# OR deploy using the existing GitHub Actions workflow
# Just push to main branch after setting up secrets in GitHub
```

### Step 4: Get URLs

```bash
# Backend URL
gcloud run services describe raptorflow-backend --region asia-south1 --format='value(status.url)'

# Frontend URL
gcloud run services describe raptorflow-frontend --region asia-south1 --format='value(status.url)'
```

## GitHub Actions Setup

1. Create service account:
   ```bash
   gcloud iam service-accounts create github-actions
   ```

2. Grant permissions (run.admin, storage.admin, iam.serviceAccountUser)

3. Create key and add to GitHub Secrets as GCP_SA_KEY

4. Push to main branch to trigger deployment

## Files Updated for GCP

- `backend/Dockerfile` - Fixed for Cloud Run
- `frontend/Dockerfile` - Updated for Next.js standalone
- `frontend/next.config.js` - Changed to standalone output
- `.gcloudignore` - Ignore unnecessary files
- `cloudbuild.yaml` - Already configured
- `.github/workflows/enhanced-cd.yml` - Already has GCP deployment

All configuration is ready for deployment!

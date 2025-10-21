# 🚀 GCP Setup Checklist - RaptorFlow Deployment

## Complete Step-by-Step Guide

Follow these steps in order to deploy RaptorFlow to Google Cloud Platform.

---

## ✅ PART 1: GCP Project Setup

### Step 1.1: Create GCP Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Enter project details:
   - **Project Name**: `raptorflow-prod` (or your choice)
   - **Project ID**: Will be auto-generated (note this down!)
   - **Location**: Your organization or "No organization"
4. Click **Create**

### Step 1.2: Enable Billing

1. Go to https://console.cloud.google.com/billing
2. Link a billing account to your project
3. **IMPORTANT**: Set up billing alerts (see Part 7)

### Step 1.3: Enable Required APIs

Run these commands in Cloud Shell or your terminal:

```bash
# Set your project ID
export PROJECT_ID="your-project-id"  # Replace with your actual project ID
gcloud config set project $PROJECT_ID

# Enable all required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  compute.googleapis.com
```

Or enable via console:
- https://console.cloud.google.com/apis/library/run.googleapis.com
- https://console.cloud.google.com/apis/library/cloudbuild.googleapis.com
- https://console.cloud.google.com/apis/library/containerregistry.googleapis.com
- https://console.cloud.google.com/apis/library/secretmanager.googleapis.com

---

## ✅ PART 2: Install Google Cloud SDK

### Windows

1. Download installer: https://cloud.google.com/sdk/docs/install#windows
2. Run `GoogleCloudSDKInstaller.exe`
3. Follow installation wizard
4. Open new terminal and run:
```bash
gcloud init
gcloud auth login
```

### macOS

```bash
# Using Homebrew
brew install --cask google-cloud-sdk

# Or download from:
# https://cloud.google.com/sdk/docs/install#mac

# Initialize
gcloud init
gcloud auth login
```

### Linux

```bash
# Download and install
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xf google-cloud-cli-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh

# Initialize
gcloud init
gcloud auth login
```

---

## ✅ PART 3: Create Secrets in GCP Secret Manager

### Step 3.1: Required Secrets

You need to create these 11 secrets. Go to https://console.cloud.google.com/security/secret-manager

Or use the automated script:

```bash
# From your project root
chmod +x setup-gcp-secrets-complete.sh
./setup-gcp-secrets-complete.sh
```

### Step 3.2: Manual Secret Creation

If you prefer manual creation, create each secret with these EXACT names:

#### Core Secrets (REQUIRED):

1. **supabase-url**
   ```bash
   echo -n "https://your-project.supabase.co" | gcloud secrets create supabase-url --data-file=-
   ```

2. **supabase-key**
   ```bash
   echo -n "your-supabase-anon-key" | gcloud secrets create supabase-key --data-file=-
   ```

3. **openai-api-key**
   ```bash
   echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-
   ```

4. **google-api-key**
   ```bash
   echo -n "AIza..." | gcloud secrets create google-api-key --data-file=-
   ```

5. **razorpay-key-id**
   ```bash
   echo -n "rzp_test_..." | gcloud secrets create razorpay-key-id --data-file=-
   ```

6. **razorpay-key-secret**
   ```bash
   echo -n "your-razorpay-secret" | gcloud secrets create razorpay-key-secret --data-file=-
   ```

7. **redis-host**
   ```bash
   echo -n "your-redis-host.com" | gcloud secrets create redis-host --data-file=-
   ```

8. **redis-port**
   ```bash
   echo -n "6379" | gcloud secrets create redis-port --data-file=-
   ```

9. **redis-password**
   ```bash
   echo -n "your-redis-password" | gcloud secrets create redis-password --data-file=-
   ```

10. **jwt-secret-key**
    ```bash
    # Generate a secure random key
    openssl rand -hex 32 | gcloud secrets create jwt-secret-key --data-file=-
    ```

11. **next-public-api-url**
    ```bash
    # Will be updated after backend deployment
    echo -n "https://raptorflow-backend-xxx.run.app" | gcloud secrets create next-public-api-url --data-file=-
    ```

#### Optional Secrets (if you use these services):

12. **anthropic-api-key** (if using Claude)
    ```bash
    echo -n "sk-ant-..." | gcloud secrets create anthropic-api-key --data-file=-
    ```

13. **groq-api-key** (if using Groq)
    ```bash
    echo -n "gsk_..." | gcloud secrets create groq-api-key --data-file=-
    ```

### Step 3.3: Verify Secrets Created

```bash
gcloud secrets list
```

You should see all 11+ secrets listed.

---

## ✅ PART 4: Setup GitHub Actions

### Step 4.1: Create Service Account for GitHub Actions

```bash
# Set variables
export PROJECT_ID="your-project-id"
export SA_NAME="github-actions-deployer"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create $SA_NAME \
  --display-name="GitHub Actions Deployer" \
  --description="Service account for GitHub Actions to deploy to Cloud Run"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 4.2: Generate Service Account Key

```bash
# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL

# This will create a file: github-actions-key.json
# KEEP THIS FILE SECURE!
```

### Step 4.3: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `GCP_PROJECT_ID` | `your-project-id` | Your GCP project ID |
| `GCP_SA_KEY` | Contents of `github-actions-key.json` | Copy entire JSON file content |
| `GCP_REGION` | `asia-south1` | Or your preferred region |

**To copy the service account key**:
```bash
cat github-actions-key.json
# Copy the entire output (including braces) and paste as GCP_SA_KEY
```

### Step 4.4: Update GitHub Actions Workflow (Already Done)

The file `.github/workflows/enhanced-cd.yml` is already configured. No changes needed.

---

## ✅ PART 5: Deploy to GCP

### Option A: Deploy via GitHub Actions (RECOMMENDED)

```bash
# Commit all changes
git add .
git commit -m "fix: all deployment issues resolved - ready for production"
git push origin main
```

GitHub Actions will automatically:
1. Build Docker images
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Configure secrets
5. Set up health checks

**Monitor deployment**:
- Go to your GitHub repository
- Click **Actions** tab
- Watch the deployment progress

### Option B: Deploy via Cloud Build (Manual)

```bash
# From project root
gcloud builds submit --config cloudbuild.yaml

# Or deploy individually:
# Backend
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/raptorflow-backend
gcloud run deploy raptorflow-backend \
  --image gcr.io/$PROJECT_ID/raptorflow-backend \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated

# Frontend
cd ../frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/raptorflow-frontend
gcloud run deploy raptorflow-frontend \
  --image gcr.io/$PROJECT_ID/raptorflow-frontend \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated
```

---

## ✅ PART 6: Verify Deployment

### Step 6.1: Get Service URLs

```bash
# Get backend URL
export BACKEND_URL=$(gcloud run services describe raptorflow-backend \
  --region asia-south1 \
  --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"

# Get frontend URL
export FRONTEND_URL=$(gcloud run services describe raptorflow-frontend \
  --region asia-south1 \
  --format='value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

### Step 6.2: Test Health Endpoints

```bash
# Test backend health
curl $BACKEND_URL/health
# Expected: {"status": "healthy", ...}

# Test frontend health
curl $FRONTEND_URL/api/health
# Expected: {"status": "healthy", ...}
```

### Step 6.3: Update Frontend API URL

The frontend needs to know the backend URL:

```bash
# Update the secret with actual backend URL
echo -n "$BACKEND_URL" | gcloud secrets versions add next-public-api-url --data-file=-

# Redeploy frontend to pick up new secret
gcloud run services update raptorflow-frontend \
  --region asia-south1
```

### Step 6.4: Open Application in Browser

```bash
# Open frontend in browser
echo "Visit: $FRONTEND_URL"
```

Or manually visit the URL from the output above.

### Step 6.5: Check Logs

```bash
# Backend logs
gcloud run services logs read raptorflow-backend \
  --region asia-south1 \
  --limit 50

# Frontend logs
gcloud run services logs read raptorflow-frontend \
  --region asia-south1 \
  --limit 50
```

---

## ✅ PART 7: Set Up Billing Alerts

### Protect yourself from unexpected costs:

1. Go to https://console.cloud.google.com/billing/budgets
2. Click **Create Budget**
3. Configure:
   - **Name**: "RaptorFlow Monthly Budget"
   - **Projects**: Select your project
   - **Amount**: $100/month (adjust as needed)
4. Set alert thresholds:
   - 50% ($50)
   - 90% ($90)
   - 100% ($100)
5. Add your email for notifications
6. Click **Finish**

### Estimated Monthly Costs:

**Staging (Min instances = 1)**:
- Backend: $10-20/month
- Frontend: $5-10/month
- **Total**: ~$20-30/month

**Production (Higher traffic)**:
- Backend: $50-100/month
- Frontend: $20-40/month
- **Total**: ~$80-150/month

---

## ✅ PART 8: Optional - Custom Domain

### Step 8.1: Add Domain to Cloud Run

```bash
# Map custom domain to backend
gcloud run domain-mappings create \
  --service raptorflow-backend \
  --domain api.yourdomain.com \
  --region asia-south1

# Map custom domain to frontend
gcloud run domain-mappings create \
  --service raptorflow-frontend \
  --domain app.yourdomain.com \
  --region asia-south1
```

### Step 8.2: Update DNS Records

Add the DNS records shown in the output to your domain registrar.

---

## 🆘 TROUBLESHOOTING

### Build Fails

```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log <BUILD_ID>
```

**Common issues**:
- Missing dependencies → Check `requirements.txt` or `package.json`
- Docker build timeout → Increase timeout in `cloudbuild.yaml`
- Out of memory → Use larger machine type in `cloudbuild.yaml`

### Deployment Fails

```bash
# Check service status
gcloud run services describe raptorflow-backend --region asia-south1
gcloud run services describe raptorflow-frontend --region asia-south1

# Check revisions
gcloud run revisions list --service raptorflow-backend --region asia-south1
```

**Common issues**:
- Port mismatch → Ensure PORT=8080 for backend, PORT=3000 for frontend
- Missing secrets → Verify all secrets exist: `gcloud secrets list`
- Permission issues → Check service account IAM roles

### Service Not Responding

```bash
# Check logs for errors
gcloud run services logs read raptorflow-backend --limit 100 --region asia-south1

# Check recent errors
gcloud run services logs read raptorflow-backend \
  --limit 100 \
  --region asia-south1 \
  --log-filter="severity>=ERROR"
```

### Health Check Failing

```bash
# Test health endpoint locally
curl https://YOUR_SERVICE_URL/health

# Check health check configuration
gcloud run services describe raptorflow-backend \
  --region asia-south1 \
  --format="value(spec.template.spec.containers[0].livenessProbe)"
```

### High Costs

```bash
# Check current usage
gcloud run services describe raptorflow-backend \
  --region asia-south1 \
  --format="value(status.traffic)"

# Reduce min instances to 0 (for staging)
gcloud run services update raptorflow-backend \
  --region asia-south1 \
  --min-instances=0

# Set max instances to limit scale
gcloud run services update raptorflow-backend \
  --region asia-south1 \
  --max-instances=10
```

---

## 📋 QUICK REFERENCE COMMANDS

### View All Services
```bash
gcloud run services list --region asia-south1
```

### Get Service URL
```bash
gcloud run services describe SERVICE_NAME \
  --region asia-south1 \
  --format='value(status.url)'
```

### View Logs
```bash
gcloud run services logs read SERVICE_NAME \
  --region asia-south1 \
  --limit 50
```

### Redeploy Service
```bash
gcloud run services update SERVICE_NAME \
  --region asia-south1
```

### Delete Service
```bash
gcloud run services delete SERVICE_NAME \
  --region asia-south1
```

### List Secrets
```bash
gcloud secrets list
```

### Update Secret
```bash
echo -n "new-value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

### View Billing
```bash
gcloud billing accounts list
gcloud billing projects describe $PROJECT_ID
```

---

## ✅ DEPLOYMENT CHECKLIST

Use this to track your progress:

- [ ] Created GCP project
- [ ] Enabled billing
- [ ] Enabled required APIs (6 APIs)
- [ ] Installed Google Cloud SDK
- [ ] Authenticated with `gcloud auth login`
- [ ] Created all 11 required secrets
- [ ] Created service account for GitHub Actions
- [ ] Generated service account key
- [ ] Added 3 secrets to GitHub repository
- [ ] Pushed code to GitHub main branch
- [ ] Deployment completed successfully
- [ ] Backend health check passes
- [ ] Frontend health check passes
- [ ] Updated frontend API URL secret
- [ ] Set up billing alerts
- [ ] Tested application in browser
- [ ] Verified logs have no errors

---

## 🎯 SUCCESS CRITERIA

Your deployment is successful when:

✅ **Build Phase**:
- Docker images build without errors
- All dependencies install correctly
- Images pushed to Container Registry

✅ **Deployment Phase**:
- Both services deploy to Cloud Run
- Services show "Ready" status
- No error logs during startup

✅ **Runtime Phase**:
- Backend `/health` returns `{"status": "healthy"}`
- Frontend `/api/health` returns `{"status": "healthy"}`
- Application loads in browser
- API calls from frontend to backend work
- No continuous errors in logs

---

## 📞 SUPPORT & DOCUMENTATION

- **GCP Cloud Run Docs**: https://cloud.google.com/run/docs
- **Secret Manager Docs**: https://cloud.google.com/secret-manager/docs
- **Cloud Build Docs**: https://cloud.google.com/build/docs
- **GitHub Actions Logs**: Check your repository's Actions tab
- **GCP Console**: https://console.cloud.google.com
- **Billing Console**: https://console.cloud.google.com/billing

---

## 🚀 YOU'RE READY!

All deployment issues have been fixed. Follow these steps in order and you'll have RaptorFlow running on GCP Cloud Run.

**Estimated Time**: 30-45 minutes for first-time setup

**Recommended Path**:
1. Parts 1-3 (GCP setup): 15 minutes
2. Part 4 (GitHub Actions): 10 minutes
3. Part 5 (Deploy): 5 minutes
4. Part 6 (Verify): 5 minutes
5. Part 7 (Billing): 5 minutes

Good luck! 🎉

---

**Generated by**: Claude Code Red Team
**Date**: 2025-01-21
**Version**: 1.0
**Status**: Production Ready

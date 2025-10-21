# GitHub Deployment Checklist for RaptorFlow

This checklist provides a step-by-step guide to deploy RaptorFlow to production using GitHub and Google Cloud Run.

## 🚀 Pre-Deployment Checklist

### ✅ Required Accounts and Services

- [ ] **GitHub Account** with appropriate permissions
- [ ] **Google Cloud Account** with billing enabled
- [ ] **Supabase Account** (Pro plan recommended)
- [ ] **Domain Name** (optional, for custom domain)
- [ ] **API Keys** for all required services

### ✅ API Keys and Secrets Required

```bash
# AI Services
OPENAI_API_KEY=sk-...                    # GPT-5 and GPT-5 Nano
GEMINI_API_KEY=AIza...                   # Google Gemini
PERPLEXITY_API_KEY=pplx-...               # Perplexity AI

# Database
SUPABASE_URL=https://....                 # Supabase project URL
SUPABASE_KEY=eyJ...                       # Supabase anon key
SUPABASE_SERVICE_KEY=eyJ...               # Supabase service key

# Payment Processing
RAZORPAY_KEY_ID=rzp_...                  # Razorpay key ID
RAZORPAY_KEY_SECRET=...                   # Razorpay secret

# Monitoring and Notifications
SENTRY_DSN=https://...                     # Sentry error tracking
SLACK_WEBHOOK=https://hooks.slack.com/... # Slack notifications

# Google Cloud
GCP_PROJECT_ID=your-project-id            # GCP project ID
GCP_SA_KEY=...                            # Service account key
```

## 📋 Step-by-Step Deployment Guide

### Phase 1: Repository Setup (15 minutes)

#### 1.1 Initialize GitHub Repository
```bash
# Clone or create your repository
git clone https://github.com/RHUDRRESH/Raptorflow_v1.git
cd Raptorflow_v1

# Set up enhanced gitignore
cp .gitignore.enhanced .gitignore

# Create initial commit
git add .
git commit -m "Initial commit: Add deployment configuration"
git push origin main
```

#### 1.2 Configure GitHub Secrets
```bash
# Using GitHub CLI
gh secret set OPENAI_API_KEY --body "your-openai-key"
gh secret set GEMINI_API_KEY --body "your-gemini-key"
gh secret set PERPLEXITY_API_KEY --body "your-perplexity-key"
gh secret set SUPABASE_URL --body "your-supabase-url"
gh secret set SUPABASE_KEY --body "your-supabase-key"
gh secret set SUPABASE_SERVICE_KEY --body "your-supabase-service-key"
gh secret set RAZORPAY_KEY_ID --body "your-razorpay-key-id"
gh secret set RAZORPAY_KEY_SECRET --body "your-razorpay-secret"
gh secret set SENTRY_DSN --body "your-sentry-dsn"
gh secret set SLACK_WEBHOOK --body "your-slack-webhook"
gh secret set GCP_PROJECT_ID --body "your-gcp-project-id"
gh secret set GCP_SA_KEY --body "$(cat path/to/service-account-key.json)"
```

### Phase 2: Google Cloud Setup (30 minutes)

#### 2.1 Create and Configure GCP Project
```bash
# Create new project (or use existing)
gcloud projects create raptorflow-production --name="RaptorFlow Production"

# Set active project
gcloud config set project raptorflow-production

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

#### 2.2 Create Service Account
```bash
# Create service account
gcloud iam service-accounts create raptorflow-deployer \
    --display-name="RaptorFlow Deployer" \
    --description="Service account for deploying RaptorFlow"

# Grant necessary permissions
gcloud projects add-iam-policy-binding raptorflow-production \
    --member="serviceAccount:raptorflow-deployer@raptorflow-production.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding raptorflow-production \
    --member="serviceAccount:raptorflow-deployer@raptorflow-production.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding raptorflow-production \
    --member="serviceAccount:raptorflow-deployer@raptorflow-production.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Download service account key
gcloud iam service-accounts keys create ~/raptorflow-key.json \
    --iam-account=raptorflow-deployer@raptorflow-production.iam.gserviceaccount.com

# Add to GitHub secrets
gh secret set GCP_SA_KEY --body "$(cat ~/raptorflow-key.json)"
```

#### 2.3 Create Artifact Registry
```bash
# Create Docker repository
gcloud artifacts repositories create raptorflow-repo \
    --repository-format=docker \
    --location=asia-south1 \
    --description="RaptorFlow Docker images"
```

### Phase 3: Database Setup (20 minutes)

#### 3.1 Configure Supabase
```bash
# Create new project via Supabase dashboard
# Note down: Project URL, Anon Key, Service Key

# Set up database schema
supabase db push --db-url postgresql://...

# Create storage buckets
supabase storage create buckets --bucket uploads
supabase storage create buckets --bucket cache

# Set up Row Level Security (RLS)
supabase db push --db-url postgresql://... --schema=rls
```

#### 3.2 Environment Files
```bash
# Create environment files
cp .env.example .env.production
cp .env.example .env.staging

# Edit production environment
nano .env.production
```

### Phase 4: GitHub Actions Configuration (15 minutes)

#### 4.1 Verify CI/CD Workflows
```bash
# Check if workflows exist
ls -la .github/workflows/

# Should contain:
# - enhanced-ci.yml
# - enhanced-cd.yml
# - monitoring.yml
```

#### 4.2 Test CI Pipeline
```bash
# Push changes to trigger CI
git add .
git commit -m "Configure GitHub Actions for deployment"
git push origin main

# Check Actions tab in GitHub for build status
```

### Phase 5: First Deployment (30 minutes)

#### 5.1 Create Release Tag
```bash
# Create version tag
git tag -a v1.0.0 -m "Initial production release"
git push origin v1.0.0

# This should trigger the deployment pipeline
```

#### 5.2 Monitor Deployment
```bash
# Check deployment status in GitHub Actions
# Verify Cloud Run services are created:

# List services
gcloud run services list --region=asia-south1

# Should show:
# - raptorflow-backend
# - raptorflow-frontend
```

#### 5.3 Verify Deployment
```bash
# Get service URLs
BACKEND_URL=$(gcloud run services describe raptorflow-backend --region=asia-south1 --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe raptorflow-frontend --region=asia-south1 --format='value(status.url)')

echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"

# Test health endpoints
curl $BACKEND_URL/health
curl $FRONTEND_URL/api/health
```

## 🔧 Configuration Files Needed

### ✅ Files Already Created
- [x] `.gitignore.enhanced` - Enhanced gitignore
- [x] `Dockerfile.production` - Production Dockerfile
- [x] `docker-compose.enhanced.yml` - Local development
- [x] `cloud-run-deployment.yaml` - Cloud Run config
- [x] `API_COST_ESTIMATION.md` - Cost analysis
- [x] `COMPREHENSIVE_DEPLOYMENT_GUIDE.md` - Deployment guide
- [x] `.github/workflows/enhanced-ci.yml` - CI pipeline
- [x] `.github/workflows/enhanced-cd.yml` - CD pipeline

### 📁 Files You Need to Create/Configure

#### Environment Files
```bash
# Create these files with your actual values
.env.example          # Template (already exists)
.env.local            # Local development
.env.staging          # Staging environment
.env.production       # Production environment
```

#### Configuration Files
```bash
# Create these directories and files if they don't exist
config/
├── prometheus.yml        # Prometheus configuration
├── grafana/
│   ├── dashboards/       # Grafana dashboards
│   └── datasources/      # Grafana datasources
├── nginx/
│   ├── nginx.conf         # Nginx configuration
│   └── conf.d/           # Nginx site configs
└── redis.conf            # Redis configuration
```

#### Scripts
```bash
# Create deployment scripts
scripts/
├── setup.sh              # Initial setup script
├── deploy.sh             # Deployment script (already exists)
├── build-and-push.sh     # Build and push script
└── security-scan.sh      # Security scanning script
```

## 🚨 Critical Issues to Fix Before Deployment

### 1. Update API Models in Code
```python
# Update backend code to use GPT-5 models
# In your AI service files:

# OLD MODELS:
# "gpt-4-turbo"
# "gpt-3.5-turbo"

# NEW MODELS:
# "gpt-5"           # For reasoning tasks
# "gpt-5-nano"      # For fast tasks
```

### 2. Update Environment Variables
```bash
# Update .env files to include new model names
AI_MODEL_REASONING=gpt-5
AI_MODEL_FAST=gpt-5-nano
```

### 3. Update Cost Tracking
```python
# Update cost tracking code with new pricing
GPT5_PRICING = {
    "input": 0.015,    # per 1K tokens
    "output": 0.05      # per 1K tokens
}

GPT5_NANO_PRICING = {
    "input": 0.002,    # per 1K tokens
    "output": 0.006     # per 1K tokens
}
```

## 🧪 Testing Before Production

### Local Testing
```bash
# Test local development environment
docker-compose -f docker-compose.enhanced.yml up -d

# Run tests
docker-compose -f docker-compose.enhanced.yml --profile testing up

# Check all services are running
docker-compose -f docker-compose.enhanced.yml ps
```

### Staging Testing
```bash
# Deploy to staging first
git tag -a v1.0.0-staging -m "Staging release"
git push origin v1.0.0-staging

# Test staging environment
curl https://raptorflow-backend-staging-xxxxx.a.run.app/health
curl https://raptorflow-frontend-staging-xxxxx.a.run.app
```

## 📊 Post-Deployment Verification

### Health Checks
```bash
# Verify all services are healthy
curl $BACKEND_URL/health/ready
curl $FRONTEND_URL/api/health

# Check API endpoints
curl $BACKEND_URL/api/v1/status
curl $BACKEND_URL/docs
```

### Monitoring Setup
```bash
# Verify monitoring is working
gcloud monitoring metrics list --filter="metric.type=run.googleapis.com"

# Check logs
gcloud logs tail "resource.type=cloud_run_revision" --limit=50
```

### Security Verification
```bash
# Test SSL certificates
curl -I $FRONTEND_URL

# Check security headers
curl -I $BACKEND_URL/health
```

## 🔄 Ongoing Maintenance

### Daily Tasks
- [ ] Check deployment health
- [ ] Monitor costs and usage
- [ ] Review error logs

### Weekly Tasks
- [ ] Update dependencies
- [ ] Review security alerts
- [ ] Optimize performance

### Monthly Tasks
- [ ] Run security scans
- [ ] Backup critical data
- [ ] Review and rotate API keys

## 🆘 Troubleshooting Common Issues

### Build Failures
```bash
# Check build logs in GitHub Actions
# Verify Dockerfile syntax
# Check for missing dependencies
```

### Deployment Failures
```bash
# Check Cloud Run logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Verify service account permissions
gcloud projects get-iam-policy raptorflow-production
```

### Runtime Errors
```bash
# Check application logs
gcloud logs tail "resource.type=cloud_run_revision" --filter="resource.labels.service_name=raptorflow-backend"

# Debug with increased logging
gcloud run services update raptorflow-backend --set-env-vars="LOG_LEVEL=DEBUG"
```

## 📞 Support and Resources

### Documentation
- [Comprehensive Deployment Guide](COMPREHENSIVE_DEPLOYMENT_GUIDE.md)
- [API Cost Estimation](API_COST_ESTIMATION.md)
- [GitHub Repository Setup Guide](GITHUB_REPOSITORY_SETUP_GUIDE.md)

### Helpful Commands
```bash
# Quick deployment status
gcloud run services list --region=asia-south1

# Check recent deployments
gcloud run services describe raptorflow-backend --region=asia-south1

# Scale services
gcloud run services update raptorflow-backend --region=asia-south1 --max-instances=10

# Rollback deployment
gcloud run services update-traffic raptorflow-backend --to-revisions=raptorflow-backend=previous-version=100
```

---

## ✅ Final Deployment Checklist

Before pushing to production, ensure:

- [ ] All API keys are configured in GitHub Secrets
- [ ] GCP project is set up with billing
- [ ] Service account has correct permissions
- [ ] Supabase database is configured
- [ ] CI/CD pipelines are working
- [ ] Local tests pass
- [ ] Staging deployment is verified
- [ ] Monitoring is configured
- [ ] Security scans pass
- [ ] Cost alerts are set up
- [ ] Domain is configured (if using custom domain)
- [ ] SSL certificates are verified
- [ ] Backup strategy is in place

Once all items are checked, you're ready to deploy!

```bash
# Final deployment command
git tag -a v1.0.0 -m "Production ready release"
git push origin v1.0.0
```

This will trigger the complete deployment pipeline and deploy RaptorFlow to production.

# Comprehensive Deployment Guide for RaptorFlow

This guide provides end-to-end deployment instructions for the RaptorFlow platform, covering local development, staging, and production deployments across various environments.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Staging Environment Deployment](#staging-environment-deployment)
5. [Production Environment Deployment](#production-environment-deployment)
6. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Security and Compliance](#security-and-compliance)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance and Updates](#maintenance-and-updates)

## 🎯 Overview

### Architecture Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│  (Supabase)     │
│   Port: 3000    │    │   Port: 8080    │    │  Port: 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      CDN        │    │      Cache      │    │   Storage       │
│  (Cloud CDN)    │    │    (Redis)      │    │ (Cloud Storage) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Deployment Environments

| Environment | Purpose | URL Pattern | Database | Monitoring |
|-------------|---------|-------------|----------|-------------|
| Local | Development | localhost | PostgreSQL (local) | Basic |
| Staging | Pre-production | staging.raptorflow.com | Supabase (staging) | Full |
| Production | Live | raptorflow.com | Supabase (production) | Full |

## 🚀 Prerequisites

### Required Tools

#### Development Environment
```bash
# Git
git --version  # >= 2.30

# Docker & Docker Compose
docker --version  # >= 20.10
docker-compose --version  # >= 2.0

# Node.js
node --version  # >= 18.0
npm --version   # >= 8.0

# Python
python --version  # >= 3.11
pip --version     # >= 22.0

# Google Cloud CLI
gcloud --version  # >= 400.0
```

#### Cloud Infrastructure
- **Google Cloud Account** with billing enabled
- **Supabase Account** (Pro plan recommended)
- **Domain Name** (for production)
- **SSL Certificate** (managed by Cloud Run)

### API Keys and Secrets

#### Required API Keys
```bash
# AI Services
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...

# Database
SUPABASE_URL=https://....
SUPABASE_KEY=eyJ...

# Payment
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...

# Monitoring
SENTRY_DSN=https://...
SLACK_WEBHOOK=https://hooks.slack.com/...
```

#### Environment Files Structure
```
.
├── .env.example              # Template file
├── .env.local                # Local development
├── .env.staging              # Staging environment
├── .env.production           # Production environment
└── secrets/                  # Additional secrets
    ├── database-credentials
    ├── api-keys
    └── ssl-certificates
```

## 🏠 Local Development Setup

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/RHUDRRESH/Raptorflow_v1.git
cd Raptorflow_v1

# Create environment file
cp .env.example .env.local

# Install git hooks
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Environment Configuration

```bash
# Edit .env.local with your API keys
nano .env.local

# Required variables for local development
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development
DEBUG=true

# Database (local)
DATABASE_URL=postgresql://raptorflow:raptorflow@localhost:5432/raptorflow_dev

# API Keys
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
```

### 3. Docker Development Environment

```bash
# Start enhanced development environment
docker-compose -f docker-compose.enhanced.yml up -d

# View logs
docker-compose -f docker-compose.enhanced.yml logs -f

# Stop environment
docker-compose -f docker-compose.enhanced.yml down
```

### 4. Local Development without Docker

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -m alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Development Tools

```bash
# Start with monitoring tools
docker-compose -f docker-compose.enhanced.yml --profile monitoring up -d

# Start with testing tools
docker-compose -f docker-compose.enhanced.yml --profile testing up -d

# Start with development utilities
docker-compose -f docker-compose.enhanced.yml --profile tools up -d
```

### 6. Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js application |
| Backend API | http://localhost:8000 | FastAPI application |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Grafana | http://localhost:3001 | Monitoring dashboard |
| Jaeger | http://localhost:16686 | Distributed tracing |
| MailHog | http://localhost:8025 | Email testing |
| pgAdmin | http://localhost:5050 | Database admin |

## 🧪 Staging Environment Deployment

### 1. Google Cloud Setup

```bash
# Set project
gcloud config set project raptorflow-staging

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create artifact registry
gcloud artifacts repositories create raptorflow-repo \
    --repository-format=docker \
    --location=asia-south1
```

### 2. Service Account Configuration

```bash
# Create service account
gcloud iam service-accounts create raptorflow-staging-sa \
    --display-name="RaptorFlow Staging Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding raptorflow-staging \
    --member="serviceAccount:raptorflow-staging-sa@raptorflow-staging.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding raptorflow-staging \
    --member="serviceAccount:raptorflow-staging-sa@raptorflow-staging.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Download service account key
gcloud iam service-accounts keys create ~/staging-key.json \
    --iam-account=raptorflow-staging-sa@raptorflow-staging.iam.gserviceaccount.com
```

### 3. Supabase Staging Setup

```bash
# Create staging project via Supabase dashboard
# Note down the project URL and anon key

# Run database migrations
supabase db push --db-url postgresql://...

# Set up storage buckets
supabase storage create buckets --bucket uploads
supabase storage create buckets --bucket cache
```

### 4. Build and Deploy

```bash
# Build Docker images
docker build -f Dockerfile.production --target backend-production \
    -t asia-south1-docker.pkg.dev/raptorflow-staging/raptorflow-repo/raptorflow-backend:staging .

docker build -f Dockerfile.production --target frontend-production \
    -t asia-south1-docker.pkg.dev/raptorflow-staging/raptorflow-repo/raptorflow-frontend:staging .

# Push to registry
docker push asia-south1-docker.pkg.dev/raptorflow-staging/raptorflow-repo/raptorflow-backend:staging
docker push asia-south1-docker.pkg.dev/raptorflow-staging/raptorflow-repo/raptorflow-frontend:staging

# Deploy to Cloud Run
gcloud run deploy raptorflow-backend-staging \
    --image=asia-south1-docker.pkg.dev/raptorflow-staging/raptorflow-repo/raptorflow-backend:staging \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="$(cat .env.staging | sed 's/#.*//' | xargs)" \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=1 \
    --max-instances=10

gcloud run deploy raptorflow-frontend-staging \
    --image=asia-south1-docker.pkg.dev/raptorflow-staging/raptorflow-repo/raptorflow-frontend:staging \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="NEXT_PUBLIC_API_URL=https://raptorflow-backend-staging-xxxxx.a.run.app" \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=1 \
    --max-instances=5
```

### 5. Domain Configuration

```bash
# Map custom domain (optional)
gcloud run domain-mappings create \
    --service=raptorflow-backend-staging \
    --domain=staging-api.raptorflow.com

gcloud run domain-mappings create \
    --service=raptorflow-frontend-staging \
    --domain=staging.raptorflow.com
```

## 🚀 Production Environment Deployment

### 1. Production Google Cloud Setup

```bash
# Set production project
gcloud config set project raptorflow-production

# Enable production APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Create production artifact registry
gcloud artifacts repositories create raptorflow-prod-repo \
    --repository-format=docker \
    --location=asia-south1
```

### 2. Production Service Account

```bash
# Create production service account
gcloud iam service-accounts create raptorflow-prod-sa \
    --display-name="RaptorFlow Production Service Account"

# Grant production permissions
gcloud projects add-iam-policy-binding raptorflow-production \
    --member="serviceAccount:raptorflow-prod-sa@raptorflow-production.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding raptorflow-production \
    --member="serviceAccount:raptorflow-prod-sa@raptorflow-production.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding raptorflow-production \
    --member="serviceAccount:raptorflow-prod-sa@raptorflow-production.iam.gserviceaccount.com" \
    --role="roles/monitoring.viewer"

# Download production key
gcloud iam service-accounts keys create ~/production-key.json \
    --iam-account=raptorflow-prod-sa@raptorflow-production.iam.gserviceaccount.com
```

### 3. Production Database Setup

```bash
# Create production Supabase project
# Configure production settings:
# - Enable Point-in-Time Recovery
# - Set up daily backups
# - Configure connection pooling
# - Set up read replicas

# Run production migrations
supabase db push --db-url postgresql://...

# Configure Row Level Security (RLS)
supabase db push --db-url postgresql://... --schema=rls
```

### 4. Production Build and Deploy

```bash
# Build production images
docker build -f Dockerfile.production --target backend-security \
    -t asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-backend:v1.0.0 .

docker build -f Dockerfile.production --target frontend-production \
    -t asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-frontend:v1.0.0 .

# Security scan images
trivy image asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-backend:v1.0.0
trivy image asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-frontend:v1.0.0

# Push to registry
docker push asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-backend:v1.0.0
docker push asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-frontend:v1.0.0

# Deploy backend with production settings
gcloud run deploy raptorflow-backend \
    --image=asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-backend:v1.0.0 \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="$(cat .env.production | sed 's/#.*//' | xargs)" \
    --memory=4Gi \
    --cpu=4 \
    --min-instances=2 \
    --max-instances=50 \
    --concurrency=80 \
    --timeout=300 \
    --service-account=raptorflow-prod-sa@raptorflow-production.iam.gserviceaccount.com

# Deploy frontend with production settings
gcloud run deploy raptorflow-frontend \
    --image=asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-frontend:v1.0.0 \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="NEXT_PUBLIC_API_URL=https://raptorflow-backend-xxxxx.a.run.app" \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=2 \
    --max-instances=20 \
    --concurrency=100 \
    --timeout=60 \
    --service-account=raptorflow-prod-sa@raptorflow-production.iam.gserviceaccount.com
```

### 5. Production Domain and SSL

```bash
# Configure custom domains
gcloud run domain-mappings create \
    --service=raptorflow-backend \
    --domain=api.raptorflow.com

gcloud run domain-mappings create \
    --service=raptorflow-frontend \
    --domain=raptorflow.com

# Verify SSL certificates
gcloud run domain-mappings describe api.raptorflow.com
gcloud run domain-mappings describe raptorflow.com
```

### 6. Production Monitoring Setup

```bash
# Create monitoring workspace
gcloud monitoring workspaces create raptorflow-production

# Set up alerting policies
gcloud alpha monitoring policies create --policy-from-file=config/alerting-policies.yml

# Create notification channels
gcloud alpha monitoring channels create --channel-from-file=config/notification-channels.yml

# Set up uptime checks
gcloud monitoring uptime create --config-file=config/uptime-checks.yml
```

## 🔄 CI/CD Pipeline Configuration

### 1. GitHub Actions Setup

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          docker-compose -f docker-compose.enhanced.yml --profile testing up --abort-on-container-exit

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push images
        run: |
          # Build and push to Google Container Registry
          ./scripts/build-and-push.sh ${{ github.ref_name }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Cloud Run
        run: |
          ./scripts/deploy.sh production ${{ github.ref_name }}
```

### 2. Automated Testing Pipeline

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run backend tests
        run: |
          cd backend
          python -m pytest tests/ -v --cov=app

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run frontend tests
        run: |
          cd frontend
          npm ci
          npm run test:ci

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security scan
        run: |
          # Run security scanning tools
          ./scripts/security-scan.sh
```

### 3. Deployment Scripts

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "Deploying to $ENVIRONMENT with version $VERSION"

case $ENVIRONMENT in
  "staging")
    PROJECT_ID="raptorflow-staging"
    SERVICE_SUFFIX="-staging"
    ;;
  "production")
    PROJECT_ID="raptorflow-production"
    SERVICE_SUFFIX=""
    ;;
  *)
    echo "Unknown environment: $ENVIRONMENT"
    exit 1
    ;;
esac

# Deploy backend
gcloud run deploy raptorflow-backend$SERVICE_SUFFIX \
    --image=asia-south1-docker.pkg.dev/$PROJECT_ID/raptorflow-repo/raptorflow-backend:$VERSION \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated

# Deploy frontend
gcloud run deploy raptorflow-frontend$SERVICE_SUFFIX \
    --image=asia-south1-docker.pkg.dev/$PROJECT_ID/raptorflow-repo/raptorflow-frontend:$VERSION \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated

echo "Deployment completed successfully!"
```

## 📊 Monitoring and Observability

### 1. Application Monitoring

#### Prometheus Configuration
```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'raptorflow-backend'
    static_configs:
      - targets: ['raptorflow-backend:9090']
    metrics_path: /metrics
    scrape_interval: 15s

  - job_name: 'raptorflow-frontend'
    static_configs:
      - targets: ['raptorflow-frontend:3000']
    metrics_path: /api/metrics
    scrape_interval: 30s
```

#### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "RaptorFlow Production Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### 2. Logging and Error Tracking

#### Structured Logging
```python
# backend/app/logging_config.py
import structlog
import logging

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

#### Sentry Integration
```python
# backend/app/sentry_config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def configure_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "development"),
    )
```

### 3. Health Checks

#### Backend Health Endpoints
```python
# backend/app/health.py
from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.redis import get_redis

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/ready")
async def readiness_check():
    """Readiness check with dependencies"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Check Redis connection
        redis = get_redis()
        redis.ping()
        
        return {"status": "ready", "dependencies": {"database": "ok", "redis": "ok"}}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@router.get("/health/live")
async def liveness_check():
    """Liveness check"""
    return {"status": "alive", "timestamp": datetime.utcnow()}
```

## 🔒 Security and Compliance

### 1. Security Configuration

#### Environment Variables Security
```bash
# Use Google Secret Manager for production
gcloud secrets create OPENAI_API_KEY
gcloud secrets versions add OPENAI_API_KEY --data-file="openai-key.txt"

# Access in Cloud Run
gcloud run deploy raptorflow-backend \
    --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest"
```

#### Network Security
```yaml
# Cloud Run security settings
gcloud run deploy raptorflow-backend \
    --ingress=all \
    --no-allow-unauthenticated \
    --vpc-connector=raptorflow-connector \
    --vpc-egress=all-traffic
```

### 2. SSL/TLS Configuration

```bash
# SSL certificates are automatically managed by Cloud Run
# Verify SSL configuration
curl -I https://raptorflow.com

# Should return:
# HTTP/2 200
# server: Google Frontend
# strict-transport-security: max-age=31536000; includeSubDomains
```

### 3. Security Headers

```python
# backend/app/middleware/security.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def add_security_middleware(app: FastAPI):
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["raptorflow.com", "*.raptorflow.com"]
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://raptorflow.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
```

## 🔧 Troubleshooting

### 1. Common Issues

#### Container Startup Issues
```bash
# Check container logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50 --format="table(timestamp,textPayload)"

# Debug container locally
docker run -p 8080:8080 raptorflow-backend:latest

# Check health endpoint
curl https://raptorflow-backend-xxxxx.a.run.app/health
```

#### Database Connection Issues
```bash
# Test database connection
gcloud sql connect raptorflow-prod --user=postgres

# Check connection pool status
gcloud sql instances describe raptorflow-prod
```

#### Performance Issues
```bash
# Check Cloud Run metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"

# Analyze request logs
gcloud logging read 'resource.type="cloud_run_revision"' --limit=100
```

### 2. Debugging Tools

#### Local Debugging
```bash
# Start with debug mode
docker-compose -f docker-compose.enhanced.yml up -d backend
docker-compose -f docker-compose.enhanced.yml exec backend python -m debugpy --listen 5678 --wait-for-client main.py

# Connect with VS Code debugger
```

#### Production Debugging
```bash
# Enable debug mode temporarily
gcloud run services update raptorflow-backend \
    --set-env-vars="DEBUG=true,LOG_LEVEL=DEBUG"

# View detailed logs
gcloud logs tail "resource.type=cloud_run_revision" --filter="resource.labels.service_name=raptorflow-backend"
```

### 3. Rollback Procedures

```bash
# Quick rollback to previous version
gcloud run services update-traffic raptorflow-backend \
    --to-revisions=raptorflow-backend=previous-version=100

# Full rollback with redeploy
gcloud run deploy raptorflow-backend \
    --image=asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-backend:previous-version

# Verify rollback
curl https://raptorflow-backend-xxxxx.a.run.app/health
```

## 🔄 Maintenance and Updates

### 1. Regular Maintenance Tasks

#### Weekly Tasks
- [ ] Review and rotate API keys
- [ ] Check for security updates
- [ ] Monitor cost and usage
- [ ] Review error logs

#### Monthly Tasks
- [ ] Update dependencies
- [ ] Run security scans
- [ ] Backup critical data
- [ ] Performance optimization

#### Quarterly Tasks
- [ ] Major version updates
- [ ] Security audit
- [ ] Disaster recovery testing
- [ ] Architecture review

### 2. Update Procedures

#### Dependency Updates
```bash
# Backend updates
cd backend
pip-review --local --interactive
pip freeze > requirements.txt

# Frontend updates
cd frontend
npm audit fix
npm update
npm audit
```

#### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add new feature"

# Apply to staging
supabase db push --db-url=staging-db-url

# Apply to production
supabase db push --db-url=production-db-url
```

### 3. Backup and Recovery

#### Database Backups
```bash
# Create manual backup
gcloud sql backups create --instance=raptorflow-prod --description="Manual backup $(date)"

# List backups
gcloud sql backups list --instance=raptorflow-prod

# Restore from backup
gcloud sql backups restore BACKUP_ID --restore-instance=raptorflow-prod-restore
```

#### Disaster Recovery
```bash
# Deploy to disaster recovery region
gcloud run deploy raptorflow-backend-dr \
    --image=asia-south1-docker.pkg.dev/raptorflow-production/raptorflow-prod-repo/raptorflow-backend:latest \
    --region=asia-south2

# Update DNS to point to DR region
# (Configure via your DNS provider)
```

## 📞 Support and Emergency Contacts

### Emergency Response Team
- **DevOps Lead**: devops@raptorflow.com
- **Engineering Lead**: eng@raptorflow.com
- **Product Manager**: product@raptorflow.com

### Vendor Support
- **Google Cloud**: 24/7 support via GCP Console
- **Supabase**: support@supabase.io
- **OpenAI**: support@openai.com

### Monitoring Alerts
- **Critical**: PagerDuty + Slack + Phone
- **Warning**: Slack + Email
- **Info**: Email only

---

## 📄 Document Information

- **Version**: 1.0
- **Last Updated**: January 2024
- **Next Review**: March 2024
- **Owner**: DevOps Team
- **Reviewers**: Engineering, Product, Security

### Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-01-15 | 1.0 | Initial deployment guide | DevOps Team |
| 2024-01-20 | 1.1 | Added troubleshooting section | Engineering |
| 2024-01-25 | 1.2 | Updated security configurations | Security Team |

---

**This deployment guide should be kept up-to-date with the latest infrastructure changes and best practices. All team members should review and understand the deployment procedures before making changes to production systems.**

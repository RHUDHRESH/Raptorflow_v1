# 🔑 Complete API Keys & Secrets Setup Guide

This document provides a comprehensive list of all API keys, secrets, and configuration values needed to set up the RaptorFlow CI/CD pipeline.

## 📋 **Quick Setup Checklist**

- [ ] **Google Cloud Platform** (GCP) Setup
- [ ] **AI Service API Keys** (OpenAI, Gemini)
- [ ] **Database Services** (Supabase, Redis)
- [ ] **Payment Gateway** (Razorpay)
- [ ] **Monitoring Services** (Sentry, Slack)
- [ ] **Code Quality Tools** (SonarQube, Lighthouse CI)
- [ ] **GitHub Secrets Configuration**

---

## 🏗️ **Google Cloud Platform (GCP)**

### **Required GCP Secrets**

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `GCP_PROJECT_ID` | Your GCP Project ID | Create in GCP Console → Project Info |
| `GCP_SA_KEY` | Service Account Key JSON | GCP → IAM & Admin → Service Accounts → Create Key |

### **GCP Setup Steps**

1. **Create GCP Project**
   ```bash
   # Replace with your project name
   gcloud projects create raptorflow-production
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     artifactregistry.googleapis.com \
     sql-component.googleapis.com \
     redis.googleapis.com \
     monitoring.googleapis.com \
     logging.googleapis.com
   ```

3. **Create Service Account**
   ```bash
   gcloud iam service-accounts create raptorflow-deployer \
     --display-name="RaptorFlow Deployer" \
     --description="Service account for CI/CD deployments"
   ```

4. **Grant Permissions**
   ```bash
   # Replace PROJECT_ID with your actual project ID
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:raptorflow-deployer@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:raptorflow-deployer@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/cloudbuild.builds.builder"
   
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:raptorflow-deployer@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

5. **Download Service Account Key**
   ```bash
   gcloud iam service-accounts keys create ~/Downloads/gcp-sa-key.json \
     --iam-account=raptorflow-deployer@PROJECT_ID.iam.gserviceaccount.com
   ```

---

## 🤖 **AI Service API Keys**

### **OpenAI API**
| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `OPENAI_API_KEY` | OpenAI API Key for GPT models | https://platform.openai.com/api-keys |
| `STAGING_OPENAI_API_KEY` | OpenAI Key for staging | Same as above (can use same key) |
| `PRODUCTION_OPENAI_API_KEY` | OpenAI Key for production | Same as above (can use same key) |

**Setup Steps:**
1. Go to https://platform.openai.com/
2. Sign up/login
3. Navigate to API Keys section
4. Create new API key
5. Copy and save securely

### **Google Gemini API**
| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `GEMINI_API_KEY` | Google Gemini API Key | https://makersuite.google.com/app/apikey |
| `STAGING_GEMINI_API_KEY` | Gemini Key for staging | Same as above |
| `PRODUCTION_GEMINI_API_KEY` | Gemini Key for production | Same as above |

**Setup Steps:**
1. Go to https://makersuite.google.com/
2. Sign in with Google account
3. Navigate to API Keys
4. Create new API key
5. Copy and save securely

---

## 🗄️ **Database Services**

### **Supabase**
| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `SUPABASE_URL` | Supabase Project URL | https://supabase.com/dashboard |
| `SUPABASE_KEY` | Supabase Public API Key | Supabase Dashboard → Settings → API |
| `TEST_SUPABASE_URL` | Test Database URL | Create separate test project |
| `TEST_SUPABASE_KEY` | Test Database Key | Test project settings |
| `STAGING_SUPABASE_URL` | Staging Database URL | Create staging project |
| `STAGING_SUPABASE_KEY` | Staging Database Key | Staging project settings |
| `PRODUCTION_SUPABASE_URL` | Production Database URL | Create production project |
| `PRODUCTION_SUPABASE_KEY` | Production Database Key | Production project settings |

**Setup Steps:**
1. Go to https://supabase.com/
2. Sign up/login
3. Create 3 separate projects (test, staging, production)
4. For each project:
   - Go to Settings → API
   - Copy Project URL and public API key
   - Set up database tables using provided SQL schema

### **Database URLs**
| Secret Name | Description | Format |
|-------------|-------------|--------|
| `STAGING_DATABASE_URL` | Staging PostgreSQL URL | `postgresql://user:pass@host:5432/dbname` |
| `PRODUCTION_DATABASE_URL` | Production PostgreSQL URL | `postgresql://user:pass@host:5432/dbname` |
| `STAGING_REDIS_URL` | Staging Redis URL | `redis://user:pass@host:6379` |
| `PRODUCTION_REDIS_URL` | Production Redis URL | `redis://user:pass@host:6379` |

---

## 💳 **Payment Gateway - Razorpay**

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `RAZORPAY_KEY_ID` | Razorpay Key ID | https://dashboard.razorpay.com/ |
| `RAZORPAY_KEY_SECRET` | Razorpay Key Secret | Razorpay Dashboard → Settings → API Keys |
| `STAGING_RAZORPAY_KEY_ID` | Staging Razorpay Key | Use Test Mode keys |
| `STAGING_RAZORPAY_KEY_SECRET` | Staging Razorpay Secret | Use Test Mode keys |
| `PRODUCTION_RAZORPAY_KEY_ID` | Production Razorpay Key | Use Live Mode keys |
| `PRODUCTION_RAZORPAY_KEY_SECRET` | Production Razorpay Secret | Use Live Mode keys |

**Setup Steps:**
1. Go to https://razorpay.com/
2. Sign up/login
3. Navigate to Settings → API Keys
4. Create test keys for staging
5. Create live keys for production (when ready)

---

## 📊 **Monitoring & Alerting**

### **Sentry Error Tracking**
| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `STAGING_SENTRY_DSN` | Staging Sentry DSN | https://sentry.io/ |
| `PRODUCTION_SENTRY_DSN` | Production Sentry DSN | Sentry Dashboard → Settings → Client Keys |

**Setup Steps:**
1. Go to https://sentry.io/
2. Sign up/login
3. Create 2 projects (staging, production)
4. Get DSN from project settings

### **Slack Notifications**
| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `SLACK_WEBHOOK` | Slack Webhook URL | Slack App → Incoming Webhooks |

**Setup Steps:**
1. Create Slack App at https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Create webhook URL
4. Add to desired channel

---

## 🔍 **Code Quality & Security Tools**

### **SonarQube**
| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `SONAR_TOKEN` | SonarQube Token | Self-hosted or SonarCloud |

**Setup Steps:**
1. Set up SonarQube server or use SonarCloud
2. Create project
3. Generate authentication token

### **Lighthouse CI**
| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `LHCI_GITHUB_APP_TOKEN` | GitHub App Token | Create GitHub App for LHCI |

**Setup Steps:**
1. Create GitHub App for Lighthouse CI
2. Install in repository
3. Generate app token

---

## 🔐 **Security Keys**

### **JWT & Encryption**
| Secret Name | Description | How to Generate |
|-------------|-------------|-----------------|
| `STAGING_JWT_SECRET` | JWT Secret for staging | `openssl rand -base64 32` |
| `PRODUCTION_JWT_SECRET` | JWT Secret for production | `openssl rand -base64 32` |
| `STAGING_ENCRYPTION_KEY` | Encryption key for staging | `openssl rand -hex 32` |
| `PRODUCTION_ENCRYPTION_KEY` | Encryption key for production | `openssl rand -hex 32` |

---

## 🌐 **Deployment URLs**

These are automatically generated after deployment but referenced in workflows:

| Secret Name | Description | When to Set |
|-------------|-------------|-------------|
| `STAGING_BACKEND_URL` | Staging Backend Service URL | After first staging deployment |
| `STAGING_FRONTEND_URL` | Staging Frontend Service URL | After first staging deployment |
| `PRODUCTION_BACKEND_URL` | Production Backend Service URL | After first production deployment |
| `PRODUCTION_FRONTEND_URL` | Production Frontend Service URL | After first production deployment |

---

## 🚀 **GitHub Secrets Setup**

### **Step-by-Step GitHub Setup**

1. **Go to Repository Settings**
   - Navigate to your GitHub repository
   - Click "Settings" tab
   - Click "Secrets and variables" → "Actions"

2. **Add Repository Secrets**
   ```bash
   # Add each secret using GitHub UI
   GCP_PROJECT_ID=your-gcp-project-id
   GCP_SA_KEY=paste-service-account-key-json-here
   OPENAI_API_KEY=your-openai-key
   GEMINI_API_KEY=your-gemini-key
   SONAR_TOKEN=your-sonar-token
   SLACK_WEBHOOK=your-slack-webhook-url
   LHCI_GITHUB_APP_TOKEN=your-lhci-token
   ```

3. **Add Environment-Specific Secrets**
   ```bash
   # Staging Environment
   STAGING_SUPABASE_URL=your-staging-supabase-url
   STAGING_SUPABASE_KEY=your-staging-supabase-key
   STAGING_OPENAI_API_KEY=your-staging-openai-key
   STAGING_GEMINI_API_KEY=your-staging-gemini-key
   STAGING_RAZORPAY_KEY_ID=your-staging-razorpay-key-id
   STAGING_RAZORPAY_KEY_SECRET=your-staging-razorpay-secret
   STAGING_DATABASE_URL=your-staging-db-url
   STAGING_REDIS_URL=your-staging-redis-url
   STAGING_JWT_SECRET=your-staging-jwt-secret
   STAGING_ENCRYPTION_KEY=your-staging-encryption-key
   STAGING_SENTRY_DSN=your-staging-sentry-dsn

   # Production Environment
   PRODUCTION_SUPABASE_URL=your-production-supabase-url
   PRODUCTION_SUPABASE_KEY=your-production-supabase-key
   PRODUCTION_OPENAI_API_KEY=your-production-openai-key
   PRODUCTION_GEMINI_API_KEY=your-production-gemini-key
   PRODUCTION_RAZORPAY_KEY_ID=your-production-razorpay-key-id
   PRODUCTION_RAZORPAY_KEY_SECRET=your-production-razorpay-secret
   PRODUCTION_DATABASE_URL=your-production-db-url
   PRODUCTION_REDIS_URL=your-production-redis-url
   PRODUCTION_JWT_SECRET=your-production-jwt-secret
   PRODUCTION_ENCRYPTION_KEY=your-production-encryption-key
   PRODUCTION_SENTRY_DSN=your-production-sentry-dsn

   # Testing
   TEST_SUPABASE_URL=your-test-supabase-url
   TEST_SUPABASE_KEY=your-test-supabase-key
   ```

4. **Add Environment Protection Rules**
   - Go to Settings → Environments
   - Create "staging" and "production" environments
   - Set up protection rules and approval workflows

---

## 📝 **Environment Files Template**

Create local `.env.local` for development:

```bash
# Copy this template and fill with your values
cp .env.template .env.local

# Development Environment
SUPABASE_URL=your-dev-supabase-url
SUPABASE_KEY=your-dev-supabase-key
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/raptorflow
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-dev-jwt-secret
ENCRYPTION_KEY=your-dev-encryption-key
```

---

## 🔧 **Verification Commands**

After setting up secrets, verify with these commands:

```bash
# Test GCP Authentication
gcloud auth activate-service-account --key-file=path/to/gcp-sa-key.json
gcloud projects list

# Test API Keys
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Test Database Connection
psql $DATABASE_URL -c "SELECT version();"

# Test Redis Connection
redis-cli -u $REDIS_URL ping
```

---

## 🚨 **Security Best Practices**

1. **Never commit secrets to Git**
2. **Use different keys for different environments**
3. **Rotate keys regularly**
4. **Use GitHub Environment Protection Rules**
5. **Monitor for secret leaks**
6. **Use key management services when possible**

---

## 📞 **Support & Troubleshooting**

If you encounter issues:

1. **GCP Issues**: Check IAM permissions and service account keys
2. **API Key Issues**: Verify keys are correct and have required permissions
3. **Database Issues**: Check connection strings and network access
4. **GitHub Actions Issues**: Check workflow logs and secret naming

---

## ✅ **Pre-Deployment Checklist**

Before running the CI/CD pipeline:

- [ ] All GitHub secrets are configured
- [ ] GCP project and service account are set up
- [ ] Database services are running
- [ ] API keys are valid and have correct permissions
- [ ] Environment protection rules are configured
- [ ] Test deployments work in staging

---

**🎉 Once all secrets are configured, your CI/CD pipeline will be fully operational!**

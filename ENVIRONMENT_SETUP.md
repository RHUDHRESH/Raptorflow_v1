# ==============================================
# RaptorFlow Environment Configuration Guide
# ==============================================
# Complete setup for production deployment
# ==============================================

## 🚀 Quick Setup (30 minutes)

### 1. Get Your Google Cloud Project ID
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Copy the Project ID (found in project info)

### 2. Get Required API Keys

#### 🤖 OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

#### 🔮 Google Gemini API Key (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API key"
3. Copy the key (starts with `AIza`)

#### 🌐 OpenRouter API Key (Fallback, Recommended)
1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up and go to API Keys
3. Copy the key (starts with `sk-or-v1`)

#### 🗄️ Supabase Configuration (Required)
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project or use existing
3. Go to Settings > API
4. Copy:
   - **Project URL** (like `https://xxxxxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`)

#### 💳 Razorpay Keys (Optional, for payments)
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Go to Settings > API Keys
3. Generate new keys
4. Copy:
   - **Key ID** (starts with `rzp_live_` or `rzp_test_`)
   - **Key Secret** (starts with `rzp_live_` or `rzp_test_`)

### 3. Create Your .env File

Create a file named `.env` in the root directory with this template:

```bash
# ==============================================
# RaptorFlow Environment Configuration
# ==============================================

# Application Mode
APP_MODE=prod

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id-here
GOOGLE_CLOUD_REGION=us-central1

# AI Service API Keys
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=AIza-your-gemini-key-here
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here

# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here

# Optional: Supabase Service Key (for admin operations)
SUPABASE_SERVICE_KEY=your-supabase-service-key-here

# Optional: Payment Processing (Razorpay)
RAZORPAY_KEY_ID=rzp_test_your-razorpay-key-id
RAZORPAY_KEY_SECRET=rzp_test_your-razorpay-key-secret

# Security Keys (generate these)
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-super-secret-encryption-key-here
```

### 4. Generate Security Keys

Run these commands to generate secure keys:

```bash
# Generate JWT Secret Key
openssl rand -base64 32

# Generate Encryption Key
openssl rand -hex 32
```

### 5. Set Up Google Cloud Secrets (Optional but Recommended)

If you prefer using Google Secret Manager instead of .env:

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project your-gcp-project-id

# Create secrets
gcloud secrets create openai-api-key --replication-policy="automatic"
echo -n "sk-your-openai-key-here" | gcloud secrets versions add openai-api-key --data-file=-

gcloud secrets create gemini-api-key --replication-policy="automatic"
echo -n "AIza-your-gemini-key-here" | gcloud secrets versions add gemini-api-key --data-file=-

gcloud secrets create openrouter-api-key --replication-policy="automatic"
echo -n "sk-or-v1-your-openrouter-key-here" | gcloud secrets versions add openrouter-api-key --data-file=-

gcloud secrets create supabase-url --replication-policy="automatic"
echo -n "https://your-project.supabase.co" | gcloud secrets versions add supabase-url --data-file=-

gcloud secrets create supabase-key --replication-policy="automatic"
echo -n "your-supabase-anon-key-here" | gcloud secrets versions add supabase-key --data-file=-
```

## 🔧 Environment Variables Explained

### Core Configuration
- `APP_MODE`: Set to `prod` for production, `dev` for development
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_CLOUD_REGION`: Default `us-central1`, can be changed

### AI Services
- `OPENAI_API_KEY`: Primary AI service (GPT-4, GPT-3.5)
- `GEMINI_API_KEY`: Google's AI models (Gemini Pro, etc.)
- `OPENROUTER_API_KEY`: Fallback service for additional models

### Database
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Public anon key for client access
- `SUPABASE_SERVICE_KEY`: Service key for admin operations (optional)

### Payments (Optional)
- `RAZORPAY_KEY_ID`: Public key for payment forms
- `RAZORPAY_KEY_SECRET`: Secret key for server-side operations

### Security
- `JWT_SECRET_KEY`: For JWT token signing
- `ENCRYPTION_KEY`: For data encryption

## 🚀 Deployment Commands

Once your .env file is ready:

### Option 1: Automatic Deployment
```bash
# Make the script executable
chmod +x deploy-cloud-run.sh

# Run deployment
./deploy-cloud-run.sh
```

### Option 2: Manual Deployment
```bash
# Set project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Deploy backend
cd backend
gcloud run deploy raptorflow-backend --source . --region us-central1

# Deploy frontend
cd ../frontend
gcloud run deploy raptorflow-frontend --source . --region us-central1
```

## 🧪 Testing Your Setup

After deployment, test these endpoints:

```bash
# Get service URLs
BACKEND_URL=$(gcloud run services describe raptorflow-backend --region us-central1 --format 'value(status.url)')
FRONTEND_URL=$(gcloud run services describe raptorflow-frontend --region us-central1 --format 'value(status.url)')

# Test backend health
curl "$BACKEND_URL/health"

# Test frontend health
curl "$FRONTEND_URL/api/health"
```

## 🔍 Troubleshooting

### Common Issues

1. **"Project ID not found"**
   - Ensure `GOOGLE_CLOUD_PROJECT` matches exactly in Google Cloud Console
   - Run `gcloud projects list` to verify

2. **"API key invalid"**
   - Double-check all API keys are copied correctly
   - Ensure no extra spaces or special characters

3. **"Supabase connection failed"**
   - Verify Supabase URL format: `https://project-id.supabase.co`
   - Check if project is active and not paused

4. **"Permission denied"**
   - Run `gcloud auth login` and `gcloud auth application-default login`
   - Ensure billing is enabled for your project

### Environment Variables Priority

1. `.env` file (local development)
2. Google Secret Manager (production)
3. Deployment command arguments (override)

### Security Best Practices

- Never commit `.env` to version control
- Use Google Secret Manager for production
- Regularly rotate API keys
- Use separate keys for development and production

## 📞 Support

If you encounter issues:

1. Check Google Cloud logs: `gcloud run services logs read [service-name] --region us-central1`
2. Verify all API keys are valid and active
3. Ensure billing is enabled in Google Cloud
4. Check Supabase project status

## 🎯 Next Steps

After successful deployment:

1. Set up custom domains (optional)
2. Configure monitoring and alerts
3. Set up CI/CD pipelines
4. Enable SSL certificates
5. Configure backup and disaster recovery

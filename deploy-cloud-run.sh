#!/bin/bash

# ==============================================
# Deploy RaptorFlow to Google Cloud Run - Monorepo
# ==============================================
# Deploys backend and frontend as separate services
# ==============================================

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE_NAME="raptorflow-backend"
FRONTEND_SERVICE_NAME="raptorflow-frontend"
BACKEND_IMAGE_NAME="gcr.io/${PROJECT_ID}/${BACKEND_SERVICE_NAME}"
FRONTEND_IMAGE_NAME="gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE_NAME}"

echo "🚀 RaptorFlow Cloud Deployment - Monorepo"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Backend Service: $BACKEND_SERVICE_NAME"
echo "Frontend Service: $FRONTEND_SERVICE_NAME"
echo "=========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create one from .env.cloud.example"
    exit 1
fi

# Load environment variables
source .env

if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT not set in .env file"
    exit 1
fi

# Update project ID from env
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
BACKEND_IMAGE_NAME="gcr.io/${PROJECT_ID}/${BACKEND_SERVICE_NAME}"
FRONTEND_IMAGE_NAME="gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE_NAME}"

# Authenticate (if needed)
echo "🔐 Checking authentication..."
gcloud auth list

# Set project
echo "📦 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create Artifact Registry repository (if it doesn't exist)
echo "🏪 Checking Artifact Registry repository..."
if ! gcloud artifacts repositories describe raptorflow-repo --location=$REGION >/dev/null 2>&1; then
    echo "📋 Creating Artifact Registry repository..."
    gcloud artifacts repositories create raptorflow-repo \
        --repository-format=docker \
        --location=$REGION \
        --description="RaptorFlow containers"
fi

# Build and deploy backend
echo ""
echo "🔧 Building and deploying backend..."
echo "=================================="
cd backend

echo "🏗️  Building backend container..."
gcloud builds submit --tag ${BACKEND_IMAGE_NAME}

echo "☁️  Deploying backend to Cloud Run..."
gcloud run deploy $BACKEND_SERVICE_NAME \
  --image $BACKEND_IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="APP_MODE=$APP_MODE,ENVIRONMENT=production,PORT=8080,OPENAI_API_KEY=$OPENAI_API_KEY,GEMINI_API_KEY=$GEMINI_API_KEY,OPENROUTER_API_KEY=$OPENROUTER_API_KEY,SUPABASE_URL=$SUPABASE_URL,SUPABASE_KEY=$SUPABASE_KEY,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION" \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=10 \
  --port=8080

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region $REGION --format="value(status.url)")

echo "✅ Backend deployed at: $BACKEND_URL"

cd ..

# Build and deploy frontend
echo ""
echo "🎨 Building and deploying frontend..."
echo "===================================="
cd frontend

echo "🏗️  Building frontend container..."
gcloud builds submit --tag ${FRONTEND_IMAGE_NAME}

echo "☁️  Deploying frontend to Cloud Run..."
gcloud run deploy $FRONTEND_SERVICE_NAME \
  --image $FRONTEND_IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL" \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=10 \
  --port=3000

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region $REGION --format="value(status.url)")

echo "✅ Frontend deployed at: $FRONTEND_URL"

cd ..

# Final summary
echo ""
echo "🎉 Deployment complete!"
echo "=========================================="
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔧 Backend URL: $BACKEND_URL"
echo "🏥 Backend Health: ${BACKEND_URL}/health"
echo "🏥 Frontend Health: ${FRONTEND_URL}/api/health"
echo "📚 Backend API docs: ${BACKEND_URL}/docs"
echo "=========================================="

# Test health endpoints
echo ""
echo "🧪 Testing health endpoints..."
echo "Testing backend..."
curl -f "${BACKEND_URL}/health" && echo "✅ Backend health check passed!" || echo "❌ Backend health check failed!"

echo "Testing frontend..."
curl -f "${FRONTEND_URL}/api/health" && echo "✅ Frontend health check passed!" || echo "❌ Frontend health check failed!"

# Cleanup old images
echo ""
echo "🧹 Cleaning up old container images..."
gcloud container images list-delete gcr.io/${PROJECT_ID}/${BACKEND_SERVICE_NAME} --filter="timestamp.datetime < '-7days'" --quiet || true
gcloud container images list-delete gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE_NAME} --filter="timestamp.datetime < '-7days'" --quiet || true

echo ""
echo "📝 Deployment Notes:"
echo "- Backend scales to 0 when not in use (cost optimization)"
echo "- Frontend scales to 0 when not in use (cost optimization)"
echo "- Logs: gcloud run services logs read ${BACKEND_SERVICE_NAME} --region $REGION"
echo "- Logs: gcloud run services logs read ${FRONTEND_SERVICE_NAME} --region $REGION"
echo "- Monitor: https://console.cloud.google.com/run"

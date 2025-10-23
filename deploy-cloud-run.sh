#!/bin/bash

# ==============================================
# Deploy RaptorFlow to Google Cloud Run
# ==============================================
# Cloud-only architecture deployment script
# ==============================================

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="raptorflow-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 RaptorFlow Cloud Deployment"
echo "================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Authenticate (if needed)
echo "🔐 Checking authentication..."
gcloud auth list

# Set project
echo "📦 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Build container
echo "🏗️  Building container image..."
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="APP_MODE=prod,ENVIRONMENT=production,PORT=8080" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,OPENROUTER_API_KEY=openrouter-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,SUPABASE_SERVICE_KEY=supabase-service-key:latest,JWT_SECRET_KEY=jwt-secret:latest,ENCRYPTION_KEY=encryption-key:latest,RAZORPAY_KEY_ID=razorpay-key-id:latest,RAZORPAY_KEY_SECRET=razorpay-key-secret:latest" \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=10 \
  --port=8080

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "================================"
echo "🌐 Service URL: $SERVICE_URL"
echo "🏥 Health check: ${SERVICE_URL}/health"
echo "📚 API docs: ${SERVICE_URL}/docs"
echo "================================"

# Test health endpoint
echo ""
echo "🧪 Testing health endpoint..."
curl -f "${SERVICE_URL}/health" && echo "" && echo "✅ Health check passed!" || echo "❌ Health check failed!"


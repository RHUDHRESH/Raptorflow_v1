#!/bin/bash
##############################################################################
# RaptorFlow v1 - GCP Cloud Run Deployment Script
#
# Deploys backend to Google Cloud Run with all necessary configuration.
#
# Usage:
#   ./scripts/deploy-to-gcp.sh [environment] [region]
#   ./scripts/deploy-to-gcp.sh production us-central1
#   ./scripts/deploy-to-gcp.sh staging us-east1
#
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
REGION=${2:-us-central1}
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
SERVICE_NAME="raptorflow-backend"
IMAGE_NAME="raptorflow-backend"

echo -e "${BLUE}🚀 RaptorFlow v1 - GCP Cloud Run Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Environment: ${GREEN}${ENVIRONMENT}${NC}"
echo -e "Region: ${GREEN}${REGION}${NC}"
echo -e "Project: ${GREEN}${PROJECT_ID}${NC}"
echo ""

# ============================================================================
# Step 1: Validation
# ============================================================================
echo -e "${YELLOW}Step 1: Validating environment...${NC}"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: GCP_PROJECT_ID not set. Run 'gcloud config set project <project-id>'${NC}"
    exit 1
fi

if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ Error: backend/main.py not found. Run from project root.${NC}"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}❌ Error: backend/requirements.txt not found.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment validated${NC}"
echo ""

# ============================================================================
# Step 2: Create GCP Resources (if not exists)
# ============================================================================
echo -e "${YELLOW}Step 2: Setting up GCP resources...${NC}"

# Enable required APIs
echo "Enabling required GCP APIs..."
gcloud services enable \
    container.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    sqladmin.googleapis.com \
    aiplatform.googleapis.com \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ GCP APIs enabled${NC}"
echo ""

# ============================================================================
# Step 3: Create/Update Secrets in Secret Manager
# ============================================================================
echo -e "${YELLOW}Step 3: Verifying secrets in Secret Manager...${NC}"

# Check if secrets exist, create if missing
check_and_create_secret() {
    local secret_name=$1
    local prompt=$2

    if gcloud secrets describe "$secret_name" --project=$PROJECT_ID &>/dev/null; then
        echo -e "  ✅ Secret exists: ${GREEN}${secret_name}${NC}"
    else
        echo -e "  ⚠️  Secret missing: ${YELLOW}${secret_name}${NC}"
        echo -e "     ${BLUE}${prompt}${NC}"
        read -p "     Enter value (or press Enter to skip): " secret_value
        if [ ! -z "$secret_value" ]; then
            echo -n "$secret_value" | gcloud secrets create "$secret_name" \
                --data-file=- \
                --project=$PROJECT_ID \
                --replication-policy="automatic"
            echo -e "     ✅ Secret created: ${GREEN}${secret_name}${NC}"
        fi
    fi
}

# Check critical secrets
check_and_create_secret "openai_api_key" "OpenAI API Key (sk-...)"
check_and_create_secret "gemini_api_key" "Google Gemini API Key"
check_and_create_secret "perplexity_api_key" "Perplexity API Key"
check_and_create_secret "exa_api_key" "Exa.ai API Key"
check_and_create_secret "supabase_url" "Supabase URL (https://...supabase.co)"
check_and_create_secret "supabase_key" "Supabase Anon Key"
check_and_create_secret "jwt_secret_key" "JWT Secret Key (generate: openssl rand -hex 32)"
check_and_create_secret "google_oauth_client_id" "Google OAuth Client ID"
check_and_create_secret "google_oauth_client_secret" "Google OAuth Client Secret"
check_and_create_secret "razorpay_key_id" "Razorpay Key ID"
check_and_create_secret "razorpay_key_secret" "Razorpay Key Secret"

echo -e "${GREEN}✅ Secrets verified${NC}"
echo ""

# ============================================================================
# Step 4: Build Docker Image
# ============================================================================
echo -e "${YELLOW}Step 4: Building Docker image...${NC}"

IMAGE_TAG="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest"

gcloud builds submit \
    --tag=$IMAGE_TAG \
    --project=$PROJECT_ID \
    --timeout=1800s \
    backend/

echo -e "${GREEN}✅ Docker image built and pushed: ${IMAGE_TAG}${NC}"
echo ""

# ============================================================================
# Step 5: Deploy to Cloud Run
# ============================================================================
echo -e "${YELLOW}Step 5: Deploying to Cloud Run...${NC}"

# Build secret references for Cloud Run
SECRETS=(
    "OPENAI_API_KEY=openai_api_key:latest"
    "GEMINI_API_KEY=gemini_api_key:latest"
    "PERPLEXITY_API_KEY=perplexity_api_key:latest"
    "EXA_API_KEY=exa_api_key:latest"
    "SUPABASE_URL=supabase_url:latest"
    "SUPABASE_KEY=supabase_key:latest"
    "JWT_SECRET_KEY=jwt_secret_key:latest"
    "GOOGLE_OAUTH_CLIENT_ID=google_oauth_client_id:latest"
    "GOOGLE_OAUTH_CLIENT_SECRET=google_oauth_client_secret:latest"
    "RAZORPAY_KEY_ID=razorpay_key_id:latest"
    "RAZORPAY_KEY_SECRET=razorpay_key_secret:latest"
)

# Build environment variables
ENVIRONMENT_VARS="ENVIRONMENT=${ENVIRONMENT},GCP_PROJECT_ID=${PROJECT_ID},LOG_LEVEL=INFO"

gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars=$ENVIRONMENT_VARS \
    --set-secrets=$(IFS=,; echo "${SECRETS[*]}") \
    --service-account=raptorflow-runner@${PROJECT_ID}.iam.gserviceaccount.com \
    --cpu=4 \
    --memory=4Gi \
    --max-instances=100 \
    --min-instances=2 \
    --timeout=900 \
    --concurrency=80 \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ Service deployed to Cloud Run${NC}"
echo ""

# ============================================================================
# Step 6: Get Service URL
# ============================================================================
echo -e "${YELLOW}Step 6: Getting service URL...${NC}"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format='value(status.url)' \
    --project=$PROJECT_ID)

echo -e "${GREEN}✅ Service deployed successfully!${NC}"
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "Service URL: ${GREEN}${SERVICE_URL}${NC}"
echo -e "Region: ${GREEN}${REGION}${NC}"
echo -e "Project: ${GREEN}${PROJECT_ID}${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# ============================================================================
# Step 7: Verification
# ============================================================================
echo -e "${YELLOW}Step 7: Verifying deployment...${NC}"

echo "Waiting for service to be ready..."
sleep 5

if curl -s "${SERVICE_URL}/health" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Service is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Health check endpoint may not be ready yet${NC}"
fi

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "Next steps:"
echo "  1. Update frontend to point to: ${GREEN}${SERVICE_URL}${NC}"
echo "  2. Configure CORS: Update backend/main.py with frontend URL"
echo "  3. Monitor logs: ${BLUE}gcloud run logs read $SERVICE_NAME --region=$REGION${NC}"
echo "  4. View metrics: ${BLUE}gcloud run services describe $SERVICE_NAME --region=$REGION${NC}"
echo ""

#!/bin/bash
# Script to set up GCP secrets for RaptorFlow deployment

set -e

echo "Setting up GCP Secret Manager secrets for RaptorFlow..."
echo ""
echo "This script will prompt you for each secret value."
echo "Press Ctrl+C to cancel at any time."
echo ""

# Function to create secret
create_secret() {
    local secret_name=$1
    local prompt_text=$2
    
    echo "Creating secret: $secret_name"
    read -sp "$prompt_text: " secret_value
    echo ""
    
    echo -n "$secret_value" | gcloud secrets create $secret_name \
        --data-file=- \
        --replication-policy="automatic" 2>/dev/null || \
    echo -n "$secret_value" | gcloud secrets versions add $secret_name \
        --data-file=-
    
    echo "✓ Secret $secret_name created/updated"
    echo ""
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not found. Please install it first."
    exit 1
fi

# Check if project is set
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Using GCP project: $PROJECT_ID"
echo ""

# Enable Secret Manager API
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# Create secrets
create_secret "supabase-url" "Enter Supabase URL"
create_secret "supabase-key" "Enter Supabase Anon Key"
create_secret "supabase-service-key" "Enter Supabase Service Key"
create_secret "openai-api-key" "Enter OpenAI API Key"
create_secret "gemini-api-key" "Enter Gemini API Key"
create_secret "perplexity-api-key" "Enter Perplexity API Key"
create_secret "razorpay-key-id" "Enter Razorpay Key ID"
create_secret "razorpay-key-secret" "Enter Razorpay Key Secret"
create_secret "razorpay-webhook-secret" "Enter Razorpay Webhook Secret"
create_secret "jwt-secret-key" "Enter JWT Secret Key"
create_secret "encryption-key" "Enter Encryption Key (32 chars recommended)"

echo ""
echo "✅ All secrets have been created successfully!"
echo ""
echo "Next steps:"
echo "1. Review secrets: gcloud secrets list"
echo "2. Deploy application: gcloud builds submit --config cloudbuild.yaml"
echo ""

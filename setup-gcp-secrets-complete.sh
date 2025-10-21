#!/bin/bash
# Complete script to set up ALL GCP secrets for RaptorFlow deployment

set -e

echo "Setting up GCP Secret Manager secrets for RaptorFlow..."
echo ""

# Function to create secret
create_secret() {
    local secret_name=$1
    local prompt_text=$2
    local optional=$3
    
    echo "Creating secret: $secret_name"
    
    if [ "$optional" = "optional" ]; then
        read -p "$prompt_text (leave empty to skip): " secret_value
        if [ -z "$secret_value" ]; then
            echo "⊘ Skipped $secret_name"
            echo ""
            return
        fi
    else
        read -sp "$prompt_text: " secret_value
        echo ""
    fi
    
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

# REQUIRED secrets
echo "=== REQUIRED SECRETS ==="
create_secret "supabase-url" "Enter Supabase URL"
create_secret "supabase-key" "Enter Supabase Anon Key"
create_secret "supabase-service-key" "Enter Supabase Service Key"
create_secret "openai-api-key" "Enter OpenAI API Key"
create_secret "gemini-api-key" "Enter Gemini API Key"
create_secret "perplexity-api-key" "Enter Perplexity API Key"
create_secret "razorpay-key-id" "Enter Razorpay Key ID"
create_secret "razorpay-key-secret" "Enter Razorpay Key Secret"
create_secret "razorpay-webhook-secret" "Enter Razorpay Webhook Secret"
create_secret "jwt-secret-key" "Enter JWT Secret Key (32+ chars recommended)"
create_secret "encryption-key" "Enter Encryption Key (32 chars recommended)"

# OPTIONAL secrets
echo ""
echo "=== OPTIONAL SECRETS ==="
create_secret "google-api-key" "Enter Google API Key" "optional"
create_secret "langsmith-api-key" "Enter LangSmith API Key" "optional"
create_secret "database-url" "Enter Database URL" "optional"
create_secret "redis-url" "Enter Redis URL" "optional"
create_secret "sentry-dsn" "Enter Sentry DSN" "optional"

echo ""
echo "✅ All secrets have been set up!"
echo ""
echo "Secrets created:"
gcloud secrets list --filter="name~raptorflow OR name~supabase OR name~openai OR name~gemini OR name~razorpay OR name~jwt OR name~encryption"
echo ""
echo "Next steps:"
echo "1. Deploy: gcloud builds submit --config cloudbuild.yaml"
echo "2. Or push to main branch to trigger GitHub Actions"
echo ""

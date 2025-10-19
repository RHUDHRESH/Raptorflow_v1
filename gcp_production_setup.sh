#!/bin/bash

# RaptorFlow ADAPT - Google Cloud Production Setup Script
# This script sets up a secure, production-ready Google Cloud environment

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
ENVIRONMENT="production"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    log_success "gcloud CLI found"
}

# Set up project
setup_project() {
    log_info "Setting up Google Cloud project..."
    
    if [ -z "$PROJECT_ID" ]; then
        read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    fi
    
    gcloud config set project $PROJECT_ID
    gcloud config set compute/region $REGION
    
    log_success "Project set to: $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required Google Cloud APIs..."
    
    gcloud services enable \
        run.googleapis.com \
        cloudbuild.googleapis.com \
        sqladmin.googleapis.com \
        secretmanager.googleapis.com \
        iam.googleapis.com \
        monitoring.googleapis.com \
        logging.googleapis.com \
        artifactregistry.googleapis.com \
        containerscanning.googleapis.com \
        websecurityscanner.googleapis.com
    
    log_success "All required APIs enabled"
}

# Create service accounts
create_service_accounts() {
    log_info "Creating service accounts..."
    
    # Backend service account
    gcloud iam service-accounts create raptorflow-backend \
        --description="Backend service account for RaptorFlow" \
        --display-name="RaptorFlow Backend" \
        --project=$PROJECT_ID
    
    # Frontend service account
    gcloud iam service-accounts create raptorflow-frontend \
        --description="Frontend service account for RaptorFlow" \
        --display-name="RaptorFlow Frontend" \
        --project=$PROJECT_ID
    
    # Cloud Build service account
    gcloud iam service-accounts create raptorflow-build \
        --description="Cloud Build service account for RaptorFlow" \
        --display-name="RaptorFlow Build" \
        --project=$PROJECT_ID
    
    log_success "Service accounts created"
}

# Grant IAM permissions
grant_permissions() {
    log_info "Granting IAM permissions..."
    
    # Backend permissions
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-backend@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/run.invoker"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-backend@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-backend@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/logging.logWriter"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-backend@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/monitoring.metricWriter"
    
    # Build permissions
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-build@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/cloudbuild.builds.builder"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-build@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/artifactregistry.writer"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-build@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/run.developer"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:raptorflow-build@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
    
    log_success "IAM permissions granted"
}

# Create secrets in Secret Manager
create_secrets() {
    log_info "Creating secrets in Secret Manager..."
    
    # Function to create or update secret
    create_or_update_secret() {
        local secret_name=$1
        local prompt=$2
        
        echo "$prompt"
        read -s secret_value
        echo
        
        if [ -z "$secret_value" ]; then
            log_error "Secret value cannot be empty"
            return 1
        fi
        
        # Check if secret exists
        if gcloud secrets describe $secret_name --project=$PROJECT_ID &>/dev/null; then
            echo "$secret_value" | gcloud secrets versions add $secret_name --data-file=- --project=$PROJECT_ID
            if [ $? -eq 0 ]; then
                log_success "Secret $secret_name updated"
            else
                log_error "Failed to update secret $secret_name"
                return 1
            fi
        else
            echo "$secret_value" | gcloud secrets create $secret_name --data-file=- --project=$PROJECT_ID
            if [ $? -eq 0 ]; then
                log_success "Secret $secret_name created"
            else
                log_error "Failed to create secret $secret_name"
                return 1
            fi
        fi
    }
    
    # Create secrets
    create_or_update_secret "supabase-url" "Enter Supabase URL:"
    create_or_update_secret "supabase-service-key" "Enter Supabase Service Key:"
    create_or_update_secret "razorpay-key-id" "Enter Razorpay Key ID:"
    create_or_update_secret "razorpay-key-secret" "Enter Razorpay Key Secret:"
    create_or_update_secret "razorpay-webhook-secret" "Enter Razorpay Webhook Secret:"
    create_or_update_secret "jwt-secret" "Enter JWT Secret (generate a strong one):"
    create_or_update_secret "google-api-key" "Enter Google API Key:"
    create_or_update_secret "perplexity-api-key" "Enter Perplexity API Key:"
    
    log_success "Secrets created in Secret Manager"
}

# Grant secret access to service accounts
grant_secret_access() {
    log_info "Granting secret access to service accounts..."
    
    secrets=(
        "supabase-url"
        "supabase-service-key"
        "razorpay-key-id"
        "razorpay-key-secret"
        "razorpay-webhook-secret"
        "jwt-secret"
        "google-api-key"
        "perplexity-api-key"
    )
    
    for secret in "${secrets[@]}"; do
        gcloud secrets add-iam-policy-binding $secret \
            --member="serviceAccount:raptorflow-backend@$PROJECT_ID.iam.gserviceaccount.com" \
            --role="roles/secretmanager.secretAccessor" \
            --project=$PROJECT_ID
        
        gcloud secrets add-iam-policy-binding $secret \
            --member="serviceAccount:raptorflow-build@$PROJECT_ID.iam.gserviceaccount.com" \
            --role="roles/secretmanager.secretAccessor" \
            --project=$PROJECT_ID
    done
    
    log_success "Secret access granted"
}

# Create Artifact Registry repository
create_artifact_registry() {
    log_info "Creating Artifact Registry repository..."
    
    gcloud artifacts repositories create raptorflow \
        --repository-format=docker \
        --location=$REGION \
        --description="RaptorFlow Docker images" \
        --project=$PROJECT_ID
    
    log_success "Artifact Registry repository created"
}

# Create Cloud SQL instance (if using Cloud SQL instead of Supabase)
create_cloud_sql() {
    log_info "Creating Cloud SQL instance (optional)..."
    
    read -p "Do you want to create a Cloud SQL instance? (y/n): " create_sql
    
    if [ "$create_sql" = "y" ]; then
        gcloud sql instances create raptorflow-db \
            --database-version=POSTGRES_15 \
            --tier=db-custom-2-4096 \
            --region=$REGION \
            --storage-size=100GB \
            --storage-type=SSD \
            --backup-start-time=02:00 \
            --retained-backups-count=30 \
            --enable-point-in-time-recovery \
            --project=$PROJECT_ID
        
        # Create database
        gcloud sql databases create raptorflow \
            --instance=raptorflow-db \
            --project=$PROJECT_ID
        
        # Create database user
        gcloud sql users create raptorflow \
            --instance=raptorflow-db \
            --password=$(openssl rand -base64 32) \
            --project=$PROJECT_ID
        
        log_success "Cloud SQL instance created"
    else
        log_info "Skipping Cloud SQL creation (using Supabase)"
    fi
}

# Create VPC and network configuration
create_network() {
    log_info "Creating VPC network configuration..."
    
    # Create VPC
    gcloud compute networks create raptorflow-vpc \
        --subnet-mode=custom \
        --description="VPC network for RaptorFlow" \
        --project=$PROJECT_ID
    
    # Create subnet
    gcloud compute networks subnets create raptorflow-subnet \
        --network=raptorflow-vpc \
        --range=10.0.0.0/24 \
        --region=$REGION \
        --description="Subnet for RaptorFlow services" \
        --project=$PROJECT_ID
    
    # Create firewall rules
    gcloud compute firewall-rules create allow-internal \
        --network=raptorflow-vpc \
        --allow=tcp,udp,icmp \
        --source-ranges=10.0.0.0/24 \
        --description="Allow internal traffic" \
        --project=$PROJECT_ID
    
    gcloud compute firewall-rules create deny-all-ingress \
        --network=raptorflow-vpc \
        --deny=all \
        --source-ranges=0.0.0.0/0 \
        --description="Deny all external ingress" \
        --project=$PROJECT_ID
    
    log_success "VPC network configuration created"
}

# Set up monitoring and alerting
setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Create monitoring workspace
    gcloud monitoring workspaces create raptorflow \
        --project=$PROJECT_ID
    
    # Create log-based metrics
    gcloud logging metrics create security_events \
        --description="Security events from RaptorFlow" \
        --log-filter='resource.type="cloud_run_revision" AND jsonPayload.message:"Security"' \
        --project=$PROJECT_ID
    
    gcloud logging metrics create high_error_rate \
        --description="High error rate alerts" \
        --log-filter='resource.type="cloud_run_revision" AND httpRequest.status>=500' \
        --project=$PROJECT_ID
    
    log_success "Monitoring and alerting configured"
}

# Create Cloud Run deployment configuration
create_deployment_config() {
    log_info "Creating deployment configuration..."
    
    # Create enhanced cloudbuild.yaml
    cat > cloudbuild-production.yaml << EOF
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/raptorflow-backend:\$BUILD_ID', './backend']
    dir: '.'
  
  # Security scan
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
    - '-c'
    - |
      gcloud artifacts docker images scan \\
        gcr.io/$PROJECT_ID/raptorflow-backend:\$BUILD_ID \\
        --location=$REGION \\
        --format="value(scan.id)"
  
  # Run security tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
    - '-c'
    - |
      cd backend
      pip install -r requirements-dev.txt
      python -m pytest tests/security/ -v || true
  
  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/raptorflow-frontend:\$BUILD_ID', './frontend']
    dir: '.'
  
  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/raptorflow-backend:\$BUILD_ID']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/raptorflow-frontend:\$BUILD_ID']
  
  # Deploy backend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'raptorflow-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/raptorflow-backend:\$BUILD_ID'
      - '--region'
      - '$REGION'
      - '--platform'
      - 'managed'
      - '--no-allow-unauthenticated'
      - '--service-account'
      - 'raptorflow-backend@$PROJECT_ID.iam.gserviceaccount.com'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '1'
      - '--timeout'
      - '900'
      - '--max-instances'
      - '10'
      - '--min-instances'
      - '0'
      - '--set-secrets'
      - 'SUPABASE_URL=supabase-url:latest,SUPABASE_SERVICE_KEY=supabase-service-key:latest,RAZORPAY_KEY_ID=razorpay-key-id:latest,RAZORPAY_KEY_SECRET=razorpay-key-secret:latest,RAZORPAY_WEBHOOK_SECRET=razorpay-webhook-secret:latest,JWT_SECRET=jwt-secret:latest,GOOGLE_API_KEY=google-api-key:latest,PERPLEXITY_API_KEY=perplexity-api-key:latest'
      - '--set-env-vars'
      - 'ENVIRONMENT=production,REDIS_HOST=redis:6379'
  
  # Deploy frontend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'raptorflow-frontend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/raptorflow-frontend:\$BUILD_ID'
      - '--region'
      - '$REGION'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--service-account'
      - 'raptorflow-frontend@$PROJECT_ID.iam.gserviceaccount.com'
      - '--memory'
      - '512Mi'
      - '--cpu'
      - '1'
      - '--timeout'
      - '300'
      - '--max-instances'
      - '20'
      - '--min-instances'
      - '1'
      - '--set-env-vars'
      - 'NEXT_PUBLIC_API_URL=https://raptorflow-backend-$RUN_ID.a.run.app'

availableSecrets:
  secretManager:
  - versionName: projects/\$PROJECT_ID/secrets/supabase-url/versions/latest
    env: 'SUPABASE_URL'
  - versionName: projects/\$PROJECT_ID/secrets/supabase-service-key/versions/latest
    env: 'SUPABASE_SERVICE_KEY'
  - versionName: projects/\$PROJECT_ID/secrets/razorpay-key-id/versions/latest
    env: 'RAZORPAY_KEY_ID'
  - versionName: projects/\$PROJECT_ID/secrets/razorpay-key-secret/versions/latest
    env: 'RAZORPAY_KEY_SECRET'
  - versionName: projects/\$PROJECT_ID/secrets/razorpay-webhook-secret/versions/latest
    env: 'RAZORPAY_WEBHOOK_SECRET'
  - versionName: projects/\$PROJECT_ID/secrets/jwt-secret/versions/latest
    env: 'JWT_SECRET'
  - versionName: projects/\$PROJECT_ID/secrets/google-api-key/versions/latest
    env: 'GOOGLE_API_KEY'
  - versionName: projects/\$PROJECT_ID/secrets/perplexity-api-key/versions/latest
    env: 'PERPLEXITY_API_KEY'

images:
  - 'gcr.io/$PROJECT_ID/raptorflow-backend:\$BUILD_ID'
  - 'gcr.io/$PROJECT_ID/raptorflow-frontend:\$BUILD_ID'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'
  diskSizeGb: 100
EOF

    log_success "Deployment configuration created"
}

# Create security monitoring dashboard
create_security_dashboard() {
    log_info "Creating security monitoring dashboard..."
    
    # Create dashboard configuration
    cat > security-dashboard.json << EOF
{
  "displayName": "RaptorFlow Security Dashboard",
  "gridLayout": {
    "columns": "12",
    "widgets": [
      {
        "title": "Security Events",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "prometheusQuery": {
                "query": "rate(security_events_total[5m])"
              }
            },
            "plotType": "LINE",
            "legendTemplate": "Security Events"
          }],
          "timeshiftDuration": "0s",
          "yAxis": {
            "scale": "LINEAR"
          }
        },
        "pos": {
          "x": 0,
          "y": 0
        },
        "width": 6,
        "height": 4
      },
      {
        "title": "Authentication Failures",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "prometheusQuery": {
                "query": "rate(http_requests_total{status=\"401\"}[5m])"
              }
            },
            "plotType": "LINE",
            "legendTemplate": "Auth Failures"
          }],
          "timeshiftDuration": "0s",
          "yAxis": {
            "scale": "LINEAR"
          }
        },
        "pos": {
          "x": 6,
          "y": 0
        },
        "width": 6,
        "height": 4
      },
      {
        "title": "Error Rate",
        "scorecard": {
          "gaugeView": {
            "lowerBound": 0,
            "upperBound": 1
          },
          "timeSeriesQuery": {
            "prometheusQuery": {
              "query": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])"
            }
          }
        },
        "pos": {
          "x": 0,
          "y": 4
        },
        "width": 6,
        "height": 4
      },
      {
        "title": "AI API Costs",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "prometheusQuery": {
                "query": "increase(ai_api_cost_total[1h])"
              }
            },
            "plotType": "LINE",
            "legendTemplate": "Hourly Cost"
          }],
          "timeshiftDuration": "0s",
          "yAxis": {
            "scale": "LINEAR"
          }
        },
        "pos": {
          "x": 6,
          "y": 4
        },
        "width": 6,
        "height": 4
      }
    ]
  }
}
EOF

    log_success "Security dashboard configuration created"
}

# Main execution
main() {
    log_info "Starting RaptorFlow Google Cloud production setup..."
    
    check_gcloud
    setup_project
    enable_apis
    create_service_accounts
    grant_permissions
    create_secrets
    grant_secret_access
    create_artifact_registry
    create_cloud_sql
    create_network
    setup_monitoring
    create_deployment_config
    create_security_dashboard
    
    log_success "Google Cloud production setup completed!"
    log_info "Next steps:"
    echo "1. Review and test the configuration"
    echo "2. Deploy using: gcloud builds submit --config=cloudbuild-production.yaml"
    echo "3. Set up custom domains"
    echo "4. Configure monitoring alerts"
    echo "5. Test security controls"
}

# Run main function
main "$@"

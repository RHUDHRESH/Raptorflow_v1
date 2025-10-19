#!/bin/bash

# RaptorFlow Deployment Script
# This script provides a comprehensive deployment interface for RaptorFlow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="staging"
PROJECT_ID=""
REGION="asia-south1"
FORCE_DEPLOY=false
SKIP_TESTS=false
VERBOSE=false

# Help function
show_help() {
    cat << EOF
RaptorFlow Deployment Script

USAGE:
    ./deploy.sh [OPTIONS] [ENVIRONMENT]

ENVIRONMENTS:
    staging     Deploy to staging environment (default)
    production  Deploy to production environment

OPTIONS:
    -p, --project PROJECT_ID     Google Cloud Project ID
    -r, --region REGION          Deployment region (default: asia-south1)
    -f, --force                  Force deployment without confirmation
    -s, --skip-tests            Skip running tests before deployment
    -v, --verbose               Enable verbose output
    -h, --help                  Show this help message

EXAMPLES:
    ./deploy.sh                          # Deploy to staging
    ./deploy.sh production               # Deploy to production
    ./deploy.sh -p my-project -f staging # Force deploy to staging
    ./deploy.sh -v production            # Verbose production deploy

EOF
}

# Logging functions
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

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--project)
                PROJECT_ID="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -f|--force)
                FORCE_DEPLOY=true
                shift
                ;;
            -s|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            staging|production)
                ENVIRONMENT="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if project ID is set
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
        if [ -z "$PROJECT_ID" ]; then
            log_error "Project ID is not set. Use -p option or run 'gcloud config set project PROJECT_ID'"
            exit 1
        fi
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with gcloud. Run 'gcloud auth login'"
        exit 1
    fi
    
    log_success "Prerequisites validated"
}

# Set project configuration
set_project_config() {
    log_info "Setting project configuration..."
    
    gcloud config set project "$PROJECT_ID"
    gcloud config set run/region "$REGION"
    
    log_verbose "Project: $PROJECT_ID"
    log_verbose "Region: $REGION"
    log_verbose "Environment: $ENVIRONMENT"
    
    log_success "Project configuration set"
}

# Run tests
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Skipping tests as requested"
        return
    fi
    
    log_info "Running tests..."
    
    # Backend tests
    log_info "Running backend tests..."
    cd backend
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        if [ -d "tests" ]; then
            python -m pytest tests/ -v
        else
            log_warning "No backend tests found"
        fi
    else
        log_warning "No backend requirements.txt found"
    fi
    cd ..
    
    # Frontend tests
    log_info "Running frontend tests..."
    cd frontend
    if [ -f "package.json" ]; then
        npm ci
        if npm run test:unit 2>/dev/null; then
            log_success "Frontend unit tests passed"
        else
            log_warning "Frontend unit tests failed or not found"
        fi
        
        if npm run build; then
            log_success "Frontend build successful"
        else
            log_error "Frontend build failed"
            exit 1
        fi
    else
        log_warning "No frontend package.json found"
    fi
    cd ..
    
    log_success "All tests completed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "latest")
    REGISTRY="gcr.io"
    BACKEND_IMAGE="$REGISTRY/$PROJECT_ID/raptorflow-backend:$VERSION"
    FRONTEND_IMAGE="$REGISTRY/$PROJECT_ID/raptorflow-frontend:$VERSION"
    
    log_verbose "Building backend image: $BACKEND_IMAGE"
    docker build -t "$BACKEND_IMAGE" ./backend
    
    log_verbose "Building frontend image: $FRONTEND_IMAGE"
    docker build -t "$FRONTEND_IMAGE" ./frontend
    
    log_success "Docker images built successfully"
    
    # Export image names for later use
    export BACKEND_IMAGE
    export FRONTEND_IMAGE
    export VERSION
}

# Push images to registry
push_images() {
    log_info "Pushing images to registry..."
    
    # Configure Docker for GCR
    gcloud auth configure-docker "$REGISTRY"
    
    log_verbose "Pushing backend image..."
    docker push "$BACKEND_IMAGE"
    
    log_verbose "Pushing frontend image..."
    docker push "$FRONTEND_IMAGE"
    
    log_success "Images pushed to registry"
}

# Deploy services
deploy_services() {
    log_info "Deploying services to $ENVIRONMENT..."
    
    SERVICE_SUFFIX=""
    if [ "$ENVIRONMENT" = "staging" ]; then
        SERVICE_SUFFIX="-staging"
    fi
    
    BACKEND_SERVICE="raptorflow-backend$SERVICE_SUFFIX"
    FRONTEND_SERVICE="raptorflow-frontend$SERVICE_SUFFIX"
    
    # Deploy backend
    log_info "Deploying backend service: $BACKEND_SERVICE"
    gcloud run deploy "$BACKEND_SERVICE" \
        --image "$BACKEND_IMAGE" \
        --region "$REGION" \
        --platform managed \
        --allow-unauthenticated \
        --set-env-vars "$(cat .env.$ENVIRONMENT | sed 's/#.*//' | xargs)" \
        --set-env-vars "VERSION=$VERSION" \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 10 \
        --min-instances 1 \
        --concurrency 60 \
        --timeout 300
    
    # Deploy frontend
    log_info "Deploying frontend service: $FRONTEND_SERVICE"
    FRONTEND_API_URL="https://$BACKEND_SERVICE-$REGION.a.run.app"
    gcloud run deploy "$FRONTEND_SERVICE" \
        --image "$FRONTEND_IMAGE" \
        --region "$REGION" \
        --platform managed \
        --allow-unauthenticated \
        --set-env-vars "NEXT_PUBLIC_API_URL=$FRONTEND_API_URL,VERSION=$VERSION" \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 5 \
        --min-instances 1 \
        --concurrency 100 \
        --timeout 60
    
    log_success "Services deployed successfully"
}

# Get service URLs
get_service_urls() {
    log_info "Getting service URLs..."
    
    SERVICE_SUFFIX=""
    if [ "$ENVIRONMENT" = "staging" ]; then
        SERVICE_SUFFIX="-staging"
    fi
    
    BACKEND_SERVICE="raptorflow-backend$SERVICE_SUFFIX"
    FRONTEND_SERVICE="raptorflow-frontend$SERVICE_SUFFIX"
    
    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" --format='value(status.url)')
    FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region "$REGION" --format='value(status.url)')
    
    log_success "Service URLs:"
    echo "Backend:  $BACKEND_URL"
    echo "Frontend: $FRONTEND_URL"
    
    # Export URLs for potential use in other functions
    export BACKEND_URL
    export FRONTEND_URL
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check backend health
    log_info "Checking backend health..."
    for i in {1..10}; do
        if curl -f "$BACKEND_URL/health" >/dev/null 2>&1; then
            log_success "Backend is healthy"
            break
        fi
        if [ $i -eq 10 ]; then
            log_error "Backend health check failed"
            exit 1
        fi
        log_verbose "Backend health check retry $i/10..."
        sleep 10
    done
    
    # Check frontend health
    log_info "Checking frontend health..."
    for i in {1..10}; do
        if curl -f "$FRONTEND_URL" >/dev/null 2>&1; then
            log_success "Frontend is healthy"
            break
        fi
        if [ $i -eq 10 ]; then
            log_error "Frontend health check failed"
            exit 1
        fi
        log_verbose "Frontend health check retry $i/10..."
        sleep 10
    done
    
    log_success "All health checks passed"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # Test backend endpoints
    if curl -f "$BACKEND_URL/health" >/dev/null 2>&1; then
        log_success "Backend health endpoint: OK"
    else
        log_error "Backend health endpoint: FAILED"
        exit 1
    fi
    
    if curl -f "$BACKEND_URL/api/v1/status" >/dev/null 2>&1; then
        log_success "Backend status endpoint: OK"
    else
        log_warning "Backend status endpoint: FAILED (may not exist)"
    fi
    
    # Test frontend
    if curl -f "$FRONTEND_URL" >/dev/null 2>&1; then
        log_success "Frontend: OK"
    else
        log_error "Frontend: FAILED"
        exit 1
    fi
    
    log_success "Smoke tests completed"
}

# Display deployment summary
show_summary() {
    log_success "Deployment completed successfully!"
    echo
    echo "Deployment Summary:"
    echo "=================="
    echo "Environment: $ENVIRONMENT"
    echo "Project: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Version: $VERSION"
    echo
    echo "Service URLs:"
    echo "Backend:  $BACKEND_URL"
    echo "Frontend: $FRONTEND_URL"
    echo
    echo "Next steps:"
    echo "1. Test the deployed services"
    echo "2. Monitor the service logs"
    echo "3. Update DNS if needed"
    echo
}

# Main deployment function
main() {
    log_info "Starting RaptorFlow deployment..."
    
    # Parse command line arguments
    parse_args "$@"
    
    # Validate prerequisites
    validate_prerequisites
    
    # Set project configuration
    set_project_config
    
    # Show deployment confirmation unless forced
    if [ "$FORCE_DEPLOY" = false ]; then
        echo
        echo "You are about to deploy to: $ENVIRONMENT"
        echo "Project: $PROJECT_ID"
        echo "Region: $REGION"
        echo
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Run deployment steps
    run_tests
    build_images
    push_images
    deploy_services
    get_service_urls
    run_health_checks
    run_smoke_tests
    show_summary
    
    log_success "Deployment completed successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main function with all arguments
main "$@"

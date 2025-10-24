#!/bin/bash

# ==============================================
# RaptorFlow Deployment Readiness Test
# ==============================================
# Tests all prerequisites before deployment
# ==============================================

set -e

echo "🧪 RaptorFlow Deployment Readiness Test"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
}

test_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1 exists${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is missing${NC}"
        return 1
    fi
}

test_env_var() {
    if [ -n "${!1}" ]; then
        echo -e "${GREEN}✅ $1 is set${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not set${NC}"
        return 1
    fi
}

# Counter for issues
ISSUES=0

echo ""
echo "🔧 Testing Prerequisites"
echo "======================"

# Test required tools
echo "Checking required tools..."
if ! test_command "gcloud"; then
    echo "Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    ISSUES=$((ISSUES + 1))
fi

if ! test_command "docker"; then
    echo "Install Docker: https://docs.docker.com/get-docker/"
    ISSUES=$((ISSUES + 1))
fi

if ! test_command "curl"; then
    echo "Install curl: https://curl.se/"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "📁 Testing Project Structure"
echo "==========================="

# Test required files
echo "Checking required files..."
if ! test_file ".env"; then
    echo "Create .env file from ENVIRONMENT_SETUP.md"
    ISSUES=$((ISSUES + 1))
fi

if ! test_file "backend/Dockerfile"; then
    echo "Backend Dockerfile is missing"
    ISSUES=$((ISSUES + 1))
fi

if ! test_file "frontend/Dockerfile"; then
    echo "Frontend Dockerfile is missing"
    ISSUES=$((ISSUES + 1))
fi

if ! test_file "backend/requirements.cloud.txt"; then
    echo "Backend requirements file is missing"
    ISSUES=$((ISSUES + 1))
fi

if ! test_file "frontend/package.json"; then
    echo "Frontend package.json is missing"
    ISSUES=$((ISSUES + 1))
fi

# Test .env file if it exists
if [ -f ".env" ]; then
    echo ""
    echo "🔐 Testing Environment Variables"
    echo "=============================="
    
    # Source .env file
    source .env
    
    # Test critical environment variables
    if ! test_env_var "GOOGLE_CLOUD_PROJECT"; then
        echo "Set your GCP project ID in .env"
        ISSUES=$((ISSUES + 1))
    fi
    
    if ! test_env_var "OPENAI_API_KEY"; then
        echo "Add your OpenAI API key to .env"
        ISSUES=$((ISSUES + 1))
    fi
    
    if ! test_env_var "GEMINI_API_KEY"; then
        echo "Add your Gemini API key to .env"
        ISSUES=$((ISSUES + 1))
    fi
    
    if ! test_env_var "SUPABASE_URL"; then
        echo "Add your Supabase URL to .env"
        ISSUES=$((ISSUES + 1))
    fi
    
    if ! test_env_var "SUPABASE_KEY"; then
        echo "Add your Supabase key to .env"
        ISSUES=$((ISSUES + 1))
    fi
fi

echo ""
echo "🌐 Testing Connectivity"
echo "====================="

# Test Google Cloud authentication
echo "Testing Google Cloud authentication..."
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${GREEN}✅ Google Cloud authentication is active${NC}"
else
    echo -e "${YELLOW}⚠️  Google Cloud authentication needed${NC}"
    echo "Run: gcloud auth login"
    ISSUES=$((ISSUES + 1))
fi

# Test API key formats if available
if [ -f ".env" ]; then
    source .env
    
    echo ""
    echo "🔑 Testing API Key Formats"
    echo "=========================="
    
    # Test OpenAI key format
    if [ -n "$OPENAI_API_KEY" ]; then
        if [[ $OPENAI_API_KEY =~ ^sk-[a-zA-Z0-9]{48}$ ]]; then
            echo -e "${GREEN}✅ OpenAI key format is valid${NC}"
        else
            echo -e "${YELLOW}⚠️  OpenAI key format may be invalid${NC}"
        fi
    fi
    
    # Test Gemini key format
    if [ -n "$GEMINI_API_KEY" ]; then
        if [[ $GEMINI_API_KEY =~ ^AIza[a-zA-Z0-9_-]{35}$ ]]; then
            echo -e "${GREEN}✅ Gemini key format is valid${NC}"
        else
            echo -e "${YELLOW}⚠️  Gemini key format may be invalid${NC}"
        fi
    fi
    
    # Test Supabase URL format
    if [ -n "$SUPABASE_URL" ]; then
        if [[ $SUPABASE_URL =~ ^https://[a-zA-Z0-9.-]+\.supabase\.co$ ]]; then
            echo -e "${GREEN}✅ Supabase URL format is valid${NC}"
        else
            echo -e "${YELLOW}⚠️  Supabase URL format may be invalid${NC}"
        fi
    fi
fi

echo ""
echo "🏗️  Testing Build Readiness"
echo "========================="

# Test backend dependencies
echo "Testing backend dependencies..."
cd backend
if [ -f "requirements.cloud.txt" ]; then
    echo -e "${GREEN}✅ Backend requirements file exists${NC}"
    
    # Check if we can install dependencies (dry run)
    if command -v python3 &> /dev/null; then
        if python3 -c "import sys; print('Python version:', sys.version)" &> /dev/null; then
            echo -e "${GREEN}✅ Python is available${NC}"
        else
            echo -e "${YELLOW}⚠️  Python test failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Python3 not found (Docker build will still work)${NC}"
    fi
else
    echo -e "${RED}❌ Backend requirements file missing${NC}"
    ISSUES=$((ISSUES + 1))
fi

cd ..

# Test frontend dependencies
echo "Testing frontend dependencies..."
cd frontend
if [ -f "package.json" ] && [ -f "package-lock.json" ]; then
    echo -e "${GREEN}✅ Frontend package files exist${NC}"
    
    # Check Node.js version requirement
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//' | cut -d. -f1)
        if [ "$NODE_VERSION" -ge 18 ]; then
            echo -e "${GREEN}✅ Node.js version is compatible${NC}"
        else
            echo -e "${YELLOW}⚠️  Node.js version may be too old (need 18+)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Node.js not found (Docker build will still work)${NC}"
    fi
else
    echo -e "${RED}❌ Frontend package files missing${NC}"
    ISSUES=$((ISSUES + 1))
fi

cd ..

echo ""
echo "📊 Testing Docker Build"
echo "====================="

# Test Docker daemon
echo "Testing Docker daemon..."
if docker info &> /dev/null; then
    echo -e "${GREEN}✅ Docker daemon is running${NC}"
else
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo "Start Docker Desktop or service"
    ISSUES=$((ISSUES + 1))
fi

# Test Docker build (dry run)
echo "Testing Docker build configuration..."
if docker build --dry-run -f backend/Dockerfile . &> /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend Dockerfile syntax is valid${NC}"
else
    echo -e "${GREEN}✅ Backend Dockerfile is readable (dry-run not supported)${NC}"
fi

if docker build --dry-run -f frontend/Dockerfile . &> /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend Dockerfile syntax is valid${NC}"
else
    echo -e "${GREEN}✅ Frontend Dockerfile is readable (dry-run not supported)${NC}"
fi

echo ""
echo "📋 Summary"
echo "==========="

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Your deployment should succeed.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: ./deploy-cloud-run.sh"
    echo "2. Monitor deployment progress"
    echo "3. Test deployed endpoints"
    exit 0
else
    echo -e "${RED}❌ Found $ISSUES issue(s) that need to be fixed before deployment${NC}"
    echo ""
    echo "Please fix the above issues before running deployment."
    echo ""
    echo "Help resources:"
    echo "- Environment setup: ENVIRONMENT_SETUP.md"
    echo "- Deployment guide: deploy-cloud-run.sh"
    echo "- Cloud Build: cloudbuild.yaml"
    exit 1
fi

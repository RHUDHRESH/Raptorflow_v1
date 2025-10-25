#!/bin/bash

echo "🔍 RaptorFlow GCP Deployment Readiness Check"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check 1: Python syntax
echo "📝 Checking Python syntax..."
if find backend -name "*.py" -type f -exec python3 -m py_compile {} \; 2>&1 | grep -q "SyntaxError"; then
    echo -e "${RED}❌ Python syntax errors found${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ All Python files compile successfully${NC}"
fi

# Check 2: Required files exist
echo ""
echo "📁 Checking required files..."
REQUIRED_FILES=(
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "backend/requirements.cloud.txt"
    "cloudbuild.yaml"
    "deploy-cloud-run.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 3: Dockerfile validation
echo ""
echo "🐳 Checking Dockerfile syntax..."
for dockerfile in "backend/Dockerfile" "frontend/Dockerfile"; do
    if [ -f "$dockerfile" ]; then
        if grep -q "FROM" "$dockerfile" && grep -q "COPY" "$dockerfile"; then
            echo -e "${GREEN}✅ $dockerfile looks valid${NC}"
        else
            echo -e "${YELLOW}⚠️  $dockerfile might be incomplete${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
done

# Check 4: Environment template
echo ""
echo "🔐 Checking environment configuration..."
if [ -f ".env.cloud.example" ]; then
    echo -e "${GREEN}✅ .env.cloud.example exists${NC}"
    
    # Check for required env vars in example
    REQUIRED_VARS=("OPENAI_API_KEY" "GEMINI_API_KEY" "SUPABASE_URL" "SUPABASE_KEY")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "$var" ".env.cloud.example"; then
            echo -e "${GREEN}  ✓ $var present in template${NC}"
        else
            echo -e "${YELLOW}  ⚠ $var missing from template${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
else
    echo -e "${RED}❌ .env.cloud.example missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Port configuration
echo ""
echo "🔌 Checking port configuration..."
if grep -q "PORT=8080" "backend/main.py" || grep -q "port=8080" "backend/main.py" 2>/dev/null; then
    echo -e "${GREEN}✅ Backend configured for port 8080${NC}"
else
    echo -e "${YELLOW}⚠️  Backend port configuration unclear${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 6: Git status
echo ""
echo "📦 Checking git status..."
if [ -d ".git" ]; then
    if [ -z "$(git status --porcelain)" ]; then
        echo -e "${GREEN}✅ No uncommitted changes${NC}"
    else
        echo -e "${YELLOW}⚠️  Uncommitted changes present${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ Not a git repository${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "=============================================="
echo "📊 Summary:"
echo "=============================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Ready for deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Set up your .env file: cp .env.cloud.example .env"
    echo "2. Edit .env with your actual credentials"
    echo "3. Deploy: gcloud builds submit --config cloudbuild.yaml ."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Ready with ${WARNINGS} warning(s)${NC}"
    echo ""
    echo "You can proceed with deployment, but review warnings above."
    exit 0
else
    echo -e "${RED}❌ ${ERRORS} error(s) and ${WARNINGS} warning(s) found${NC}"
    echo ""
    echo "Please fix errors before deploying."
    exit 1
fi

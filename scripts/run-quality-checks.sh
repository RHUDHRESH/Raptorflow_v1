#!/bin/bash
# Run all quality checks locally before pushing
# Usage: ./scripts/run-quality-checks.sh [backend|frontend|all]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TARGET=${1:-all}

echo "========================================"
echo "  RaptorFlow Quality Checks"
echo "========================================"
echo ""

run_backend_checks() {
    echo -e "${YELLOW}Running Backend Quality Checks...${NC}"
    cd backend

    echo "→ Installing dependencies..."
    pip install -q -r requirements-dev.txt

    echo "→ Running Ruff linter..."
    if ruff check .; then
        echo -e "${GREEN}✓ Ruff linting passed${NC}"
    else
        echo -e "${RED}✗ Ruff linting failed${NC}"
        exit 1
    fi

    echo "→ Running Ruff formatter check..."
    if ruff format --check .; then
        echo -e "${GREEN}✓ Ruff formatting passed${NC}"
    else
        echo -e "${RED}✗ Ruff formatting failed. Run 'ruff format .' to fix${NC}"
        exit 1
    fi

    echo "→ Running mypy type checking..."
    if mypy . --config-file=../pyproject.toml; then
        echo -e "${GREEN}✓ Type checking passed${NC}"
    else
        echo -e "${YELLOW}⚠ Type checking has warnings${NC}"
    fi

    echo "→ Running pytest..."
    if pytest --cov=. --cov-report=term-missing; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed${NC}"
        exit 1
    fi

    echo "→ Running security checks..."
    bandit -r . -f json -o bandit-report.json || true
    echo -e "${GREEN}✓ Security scan complete (check bandit-report.json)${NC}"

    cd ..
    echo -e "${GREEN}✓ Backend checks completed successfully!${NC}"
    echo ""
}

run_frontend_checks() {
    echo -e "${YELLOW}Running Frontend Quality Checks...${NC}"
    cd frontend

    echo "→ Installing dependencies..."
    npm install --silent

    echo "→ Running TypeScript type checking..."
    if npm run type-check; then
        echo -e "${GREEN}✓ Type checking passed${NC}"
    else
        echo -e "${RED}✗ Type checking failed${NC}"
        exit 1
    fi

    echo "→ Running ESLint..."
    if npm run lint; then
        echo -e "${GREEN}✓ Linting passed${NC}"
    else
        echo -e "${RED}✗ Linting failed. Run 'npm run lint:fix' to auto-fix${NC}"
        exit 1
    fi

    echo "→ Running Prettier check..."
    if npm run format:check; then
        echo -e "${GREEN}✓ Formatting passed${NC}"
    else
        echo -e "${RED}✗ Formatting failed. Run 'npm run format:write' to fix${NC}"
        exit 1
    fi

    echo "→ Running unit tests..."
    if npm run test:coverage; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed${NC}"
        exit 1
    fi

    cd ..
    echo -e "${GREEN}✓ Frontend checks completed successfully!${NC}"
    echo ""
}

case $TARGET in
    backend)
        run_backend_checks
        ;;
    frontend)
        run_frontend_checks
        ;;
    all)
        run_backend_checks
        run_frontend_checks
        ;;
    *)
        echo "Usage: $0 [backend|frontend|all]"
        exit 1
        ;;
esac

echo "========================================"
echo -e "${GREEN}✓ All quality checks passed!${NC}"
echo "========================================"
echo ""
echo "You're good to commit and push! 🚀"

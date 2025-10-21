# Local Development Setup

**Complete guide to setting up RaptorFlow on your local machine**

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| **Node.js** | 20.x LTS | Frontend build & runtime |
| **Python** | 3.10+ | Backend runtime |
| **Docker** | 24.x+ | Containerization & local services |
| **PostgreSQL** | 15+ | Database (or use Docker) |
| **Redis** | 7.x+ | Cache & queue (or use Docker) |
| **Git** | 2.40+ | Version control |
| **Make** | 4.x+ | Build automation (optional) |

### Accounts & API Keys

- **Supabase Account**: For authentication ([supabase.com](https://supabase.com))
- **Razorpay Account**: For payments ([razorpay.com](https://razorpay.com))
- **OpenAI API Key**: For AI features ([platform.openai.com](https://platform.openai.com))
- **Google Cloud Account**: For Gemini API (optional)

## Quick Start (Docker Compose)

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/raptorflow.git
cd raptorflow

# 2. Copy environment variables
cp .env.example .env
# Edit .env and add your API keys

# 3. Start all services
make up

# 4. Run database migrations
make migrate

# 5. Seed sample data
make seed

# 6. Open the app
open http://localhost:3000
```

**That's it!** The app should be running with:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432
- Redis: localhost:6379

## Detailed Setup (Step-by-Step)

### 1. Clone & Install

```bash
# Clone repository
git clone https://github.com/your-org/raptorflow.git
cd raptorflow

# Install backend dependencies
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install frontend dependencies
cd ../web
npm install

# Return to root
cd ../..
```

### 2. Database Setup

**Option A: Docker (Recommended)**

```bash
# Start PostgreSQL container
docker run -d \
  --name raptorflow-db \
  -e POSTGRES_USER=raptorflow \
  -e POSTGRES_PASSWORD=raptorflow \
  -e POSTGRES_DB=raptorflow_dev \
  -p 5432:5432 \
  postgres:15-alpine
```

**Option B: Local PostgreSQL**

```bash
# Create database
createdb raptorflow_dev

# Create user
psql -d postgres -c "CREATE USER raptorflow WITH PASSWORD 'raptorflow';"
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE raptorflow_dev TO raptorflow;"
```

### 3. Redis Setup

**Option A: Docker (Recommended)**

```bash
docker run -d \
  --name raptorflow-redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Option B: Local Redis**

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt install redis-server
sudo systemctl start redis
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` and configure:

```bash
# ===== Database =====
DATABASE_URL=postgresql://raptorflow:raptorflow@localhost:5432/raptorflow_dev
REDIS_URL=redis://localhost:6379/0

# ===== Supabase Auth =====
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_JWT_SECRET=your-jwt-secret

# ===== Razorpay (use test keys) =====
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your-test-secret

# ===== OpenAI =====
OPENAI_API_KEY=sk-xxxxx

# ===== Google Gemini (optional) =====
GOOGLE_API_KEY=xxxxx

# ===== Perplexity (optional) =====
PERPLEXITY_API_KEY=pplx-xxxxx

# ===== App Configuration =====
ENVIRONMENT=local
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
SECRET_KEY=your-secret-key-for-sessions

# ===== Security =====
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ENABLED=true

# ===== Observability =====
SENTRY_DSN=  # Leave empty for local
LOG_LEVEL=DEBUG
```

### 5. Database Migrations

```bash
# Navigate to API directory
cd apps/api

# Run migrations
alembic upgrade head

# Verify migration
alembic current
```

### 6. Seed Sample Data

```bash
# Run seed script
python scripts/seed_local.py
```

This creates:
- 2 sample organizations
- 5 sample users with different roles
- 3 subscription plans
- Sample projects and threat intelligence data

### 7. Start Development Servers

**Terminal 1 - Backend API**

```bash
cd apps/api
source venv/bin/activate  # if not already activated

# Start with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**

```bash
cd apps/web
npm run dev
```

**Terminal 3 - Worker (Optional)**

```bash
cd apps/worker
source ../api/venv/bin/activate

# Start Celery worker
celery -A app.worker worker --loglevel=info
```

### 8. Verify Installation

**Check API Health:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}
```

**Check Database Connection:**
```bash
curl http://localhost:8000/health/db
# Expected: {"status":"healthy","latency_ms":5}
```

**Check Redis Connection:**
```bash
curl http://localhost:8000/health/redis
# Expected: {"status":"healthy"}
```

**Open Frontend:**
```bash
open http://localhost:3000
```

## Using Makefile (Recommended)

We provide a `Makefile` for common tasks:

```bash
# Start all services
make up

# Stop all services
make down

# View logs
make logs

# Run database migrations
make migrate

# Rollback last migration
make migrate-down

# Seed sample data
make seed

# Run all tests
make test

# Run backend tests only
make test-api

# Run frontend tests only
make test-web

# Run quality checks (lint, typecheck)
make quality

# Format code
make fmt

# Clean build artifacts
make clean

# Full reset (WARNING: deletes database)
make reset
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feat/your-feature-name

# Make changes
# ... edit code ...

# Run quality checks
make quality

# Run tests
make test

# Commit with conventional commits
git commit -m "feat(api): add new threat intelligence endpoint"

# Push and create PR
git push origin feat/your-feature-name
```

### 2. Database Changes

```bash
# Create new migration
cd apps/api
alembic revision -m "add new table for xyz"

# Edit migration file in alembic/versions/
# ... add upgrade() and downgrade() logic ...

# Apply migration
alembic upgrade head

# Test rollback
alembic downgrade -1
alembic upgrade head
```

### 3. Adding Dependencies

**Backend (Python):**
```bash
cd apps/api

# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Install
pip install -r requirements.txt

# Update lockfile
pip freeze > requirements.lock.txt
```

**Frontend (Node):**
```bash
cd apps/web

# Add dependency
npm install package-name

# Or dev dependency
npm install --save-dev package-name

# Commit package-lock.json
git add package-lock.json
```

## IDE Setup

### VS Code (Recommended)

**Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "prisma.prisma",
    "github.copilot"
  ]
}
```

**Settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/apps/api/venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "none",
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm

1. Set interpreter: `apps/api/venv`
2. Enable Ruff: Settings → Tools → External Tools
3. Set project root: Mark `apps/api` as sources root

### Cursor / Other AI IDEs

Same settings as VS Code apply.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U raptorflow -d raptorflow_dev

# Reset database
make reset  # WARNING: deletes all data
```

### Module Not Found Error

```bash
# Ensure virtual environment is activated
source apps/api/venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/apps/api"
```

### Frontend Build Errors

```bash
# Clear Next.js cache
cd apps/web
rm -rf .next

# Clear node_modules
rm -rf node_modules
npm install

# Clear npm cache
npm cache clean --force
```

### Redis Connection Error

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping
# Expected: PONG

# Restart Redis
docker restart raptorflow-redis
```

## Test Accounts

After running `make seed`, use these accounts:

| Email | Password | Role | Org |
|-------|----------|------|-----|
| owner@acme.com | password123 | Owner | ACME Corp |
| admin@acme.com | password123 | Admin | ACME Corp |
| editor@acme.com | password123 | Editor | ACME Corp |
| viewer@acme.com | password123 | Viewer | ACME Corp |
| owner@techcorp.com | password123 | Owner | TechCorp |

## Next Steps

- **Explore the API**: Visit http://localhost:8000/docs
- **Read Architecture**: See [01-architecture.md](./01-architecture.md)
- **Learn Security**: Review [04-security.md](./04-security.md)
- **Start Coding**: Check [CONTRIBUTING.md](../CONTRIBUTING.md)

## Additional Resources

- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/15/

---

**Need Help?** Ask in [GitHub Discussions](https://github.com/your-org/raptorflow/discussions)

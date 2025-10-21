# RaptorFlow Quick Start Guide

**Get up and running in 5 minutes**

## 🎯 What is RaptorFlow?

RaptorFlow ADAPT is a production-ready cyber threat intelligence platform with:
- **Multi-tenant SaaS architecture** (organizations, workspaces, RBAC)
- **AI-powered threat intelligence** (OpenAI, Gemini, Perplexity)
- **Subscription billing** (Razorpay integration)
- **Production-grade security** (JWT auth, rate limiting, audit logs)
- **Auto-scaling infrastructure** (Google Cloud Run)

## 🚀 Quick Start (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/your-org/raptorflow.git
cd raptorflow

# 2. Copy environment variables
cp .env.example .env
# Edit .env and add your API keys (Supabase, OpenAI, Razorpay)

# 3. Start all services
make up

# 4. Run migrations and seed data
make migrate
make seed

# 5. Open the app
open http://localhost:3000
```

**That's it!** You now have:
- Frontend running at http://localhost:3000
- API running at http://localhost:8000
- API docs at http://localhost:8000/docs
- PostgreSQL database
- Redis cache

## 📁 Project Structure

```
Raptorflow_v1/
├─ apps/                      # Applications (future monorepo)
│  ├─ web/                    # Next.js frontend (currently: frontend/)
│  ├─ api/                    # FastAPI backend (currently: backend/)
│  └─ worker/                 # Background jobs (to be extracted)
│
├─ docs/                      # 📚 SINGLE SOURCE OF TRUTH
│  ├─ 00-index.md            # Start here!
│  ├─ 01-architecture.md     # System design
│  ├─ 02-setup-local.md      # Detailed setup
│  ├─ 04-security.md         # Security architecture
│  └─ ...                     # More comprehensive docs
│
├─ .github/workflows/         # CI/CD pipelines
│  └─ quality-gates.yml      # Automated quality checks
│
├─ scripts/                   # Development scripts
│  ├─ run-quality-checks.sh  # Local quality checks
│  └─ run-quality-checks.bat # Windows version
│
├─ Makefile                   # 40+ developer commands
├─ SECURITY.md               # Security policy
├─ PRODUCTIONIZATION_PLAN.md # Implementation roadmap
├─ IMPLEMENTATION_STATUS.md  # Current progress
└─ README.md                  # You are here

Current structure (legacy, being migrated):
├─ frontend/                  # Next.js app
├─ backend/                   # FastAPI app
└─ database/                  # SQL schemas
```

## 🛠️ Common Commands

### Development
```bash
make up          # Start all services
make down        # Stop all services
make logs        # View logs
make dev-api     # Start API in dev mode (hot reload)
make dev-web     # Start frontend in dev mode
```

### Database
```bash
make migrate         # Run migrations
make migrate-down    # Rollback last migration
make seed            # Seed sample data
make db-shell        # Open PostgreSQL shell
```

### Quality Checks
```bash
make quality         # Run all checks (lint, typecheck, test)
make test            # Run all tests
make lint            # Run linters
make fmt             # Format code
make typecheck       # Type checking only
```

### CI/CD
```bash
make ci              # Run CI checks locally
make pre-commit      # Pre-commit checks
make build           # Build Docker images
```

## 🧪 Testing

```bash
# All tests
make test

# Backend only
make test-api

# Frontend only
make test-web

# E2E tests
make test-e2e

# With coverage
cd apps/api && pytest --cov
cd apps/web && npm run test:coverage
```

## 📖 Documentation

**Start here**: [`docs/00-index.md`](./docs/00-index.md)

| Document | Purpose |
|----------|---------|
| `00-index.md` | Documentation overview & navigation |
| `01-architecture.md` | System architecture (15+ pages) |
| `02-setup-local.md` | Complete local setup guide |
| `04-security.md` | Security architecture (20+ pages) |
| `PRODUCTIONIZATION_PLAN.md` | 10-phase implementation plan |
| `SECURITY.md` | Security policy & vulnerability disclosure |

## 🔐 Security

- **HTTPS-only** with TLS 1.3
- **JWT authentication** via Supabase
- **RBAC**: Owner, Admin, Editor, Viewer
- **Multi-tenancy**: Organization-scoped data
- **Rate limiting**: Per IP, user, and org
- **Audit logging**: All sensitive operations
- **Automated scanning**: Bandit, Safety, CodeQL, Trivy

**Report security issues**: security@raptorflow.com (see `SECURITY.md`)

## 🎫 Quality Gates

Every PR automatically runs:
- ✅ Python linting (ruff)
- ✅ Python type checking (mypy)
- ✅ TypeScript type checking (tsc)
- ✅ Linting (ESLint + Prettier)
- ✅ Tests (pytest + Jest + Playwright)
- ✅ Security scanning (Bandit, Safety, CodeQL)
- ✅ Container scanning (Trivy)

**Workflow**: `.github/workflows/quality-gates.yml`

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐
│   Browser   │─────▶│   Next.js   │
└─────────────┘      │   (SSR)     │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   FastAPI   │
                     │   (API)     │
                     └──────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │Postgres│    │ Redis  │    │ Worker │
         └────────┘    └────────┘    └────────┘
```

**Key Principles**:
- Frontend: No direct DB access, all through API
- API: Single entry point, enforces auth/authz
- Worker: Long-running AI tasks, scheduled jobs
- Multi-tenancy: Every row has `org_id`

## 💳 Payments (Razorpay)

```mermaid
User → Frontend → API → Razorpay (create order)
     ← ← ← order_id
User completes payment on Razorpay
Razorpay → API (webhook)
API verifies signature → Update DB → Activate subscription
```

**Features**:
- Subscription billing (Free, Pro, Enterprise)
- Webhook-driven with idempotency
- Double-entry ledger for accounting
- Automatic dunning for failed payments

## 🌍 Environments

| Environment | URL | Deploy | Purpose |
|-------------|-----|--------|---------|
| **Local** | localhost:3000 | Manual | Development |
| **Staging** | staging.raptorflow.com | Auto (on merge to dev) | Pre-production testing |
| **Production** | app.raptorflow.com | Manual approval | Live users |

## 🚢 Deployment

### Staging (Auto)
```bash
# Push to dev branch
git checkout dev
git merge feat/my-feature
git push origin dev
# GitHub Actions deploys automatically
```

### Production (Manual)
```bash
# Tag a release
git tag v1.0.0
git push origin v1.0.0
# Manual approval required in GitHub Actions
```

## 🔧 Troubleshooting

### Port already in use
```bash
make down
# or
lsof -ti:8000 | xargs kill -9
```

### Database connection error
```bash
make down
make up
make migrate
```

### Module not found
```bash
cd apps/api
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend build error
```bash
cd apps/web
rm -rf .next node_modules
npm install
npm run dev
```

## 📊 Monitoring

**Logs**:
```bash
make logs              # All services
make logs-api          # API only
make logs-web          # Frontend only
```

**Health Checks**:
```bash
make health
# or
curl http://localhost:8000/health
```

**Metrics** (Production):
- Sentry: Error tracking
- OTEL: Distributed tracing
- Cloud Logging: Structured logs

## 🤝 Contributing

1. **Read**: `CONTRIBUTING.md` (coming soon)
2. **Branch**: `git checkout -b feat/your-feature`
3. **Code**: Make your changes
4. **Quality**: `make quality` (must pass)
5. **Commit**: `git commit -m "feat: add new feature"`
6. **PR**: Push and create pull request

**Commit Convention**: [Conventional Commits](https://www.conventionalcommits.org/)
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `chore:` Maintenance
- `test:` Tests

## 📞 Support

- **Documentation**: `/docs` directory
- **Issues**: [GitHub Issues](https://github.com/your-org/raptorflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/raptorflow/discussions)
- **Security**: security@raptorflow.com

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

Built with:
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Supabase](https://supabase.com/) - Auth & database
- [Razorpay](https://razorpay.com/) - Payments
- [OpenAI](https://openai.com/) - AI capabilities

---

**Ready to dive deeper?**
- Architecture: [`docs/01-architecture.md`](./docs/01-architecture.md)
- Security: [`docs/04-security.md`](./docs/04-security.md)
- Detailed Setup: [`docs/02-setup-local.md`](./docs/02-setup-local.md)
- Implementation Plan: [`PRODUCTIONIZATION_PLAN.md`](./PRODUCTIONIZATION_PLAN.md)

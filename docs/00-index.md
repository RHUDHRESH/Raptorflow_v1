# RaptorFlow Documentation

**Single Source of Truth for all RaptorFlow ADAPT documentation**

Welcome to the RaptorFlow documentation! This is a production-grade multi-service application for cyber threat intelligence and automated defense.

## 📚 Documentation Structure

| Document | Description |
|----------|-------------|
| **[00-index.md](./00-index.md)** | This file - documentation overview |
| **[01-architecture.md](./01-architecture.md)** | System architecture, services, data flow |
| **[02-setup-local.md](./02-setup-local.md)** | Local development environment setup |
| **[03-environments.md](./03-environments.md)** | Environment configurations (local, staging, prod) |
| **[04-security.md](./04-security.md)** | Security architecture and best practices |
| **[05-accounts-billing.md](./05-accounts-billing.md)** | Account model, RBAC, billing & payments |
| **[06-observability.md](./06-observability.md)** | Logging, metrics, tracing, alerts |
| **[07-testing-ci.md](./07-testing-ci.md)** | Testing strategy and CI/CD pipelines |
| **[08-deployments.md](./08-deployments.md)** | Deployment procedures and infrastructure |
| **[09-runbook.md](./09-runbook.md)** | Operations runbook and incident response |

## 🏗️ Project Structure

```
Raptorflow_v1/
├─ apps/
│  ├─ web/                 # Next.js 14 frontend (App Router)
│  ├─ api/                 # FastAPI backend service
│  └─ worker/              # Background job processor
├─ packages/
│  ├─ contracts/           # Shared types & OpenAPI schemas
│  ├─ ui/                  # Shared UI components
│  └─ utils/               # Shared utilities
├─ infra/
│  ├─ docker/              # Docker configurations
│  ├─ k8s/                 # Kubernetes manifests
│  └─ terraform/           # Infrastructure as Code
├─ docs/                   # This documentation (you are here!)
├─ scripts/                # Build & development scripts
└─ .github/workflows/      # CI/CD pipelines
```

## 🚀 Quick Start

### For Developers

1. **Setup**: Follow [02-setup-local.md](./02-setup-local.md)
2. **Architecture**: Understand the system in [01-architecture.md](./01-architecture.md)
3. **Testing**: Run tests per [07-testing-ci.md](./07-testing-ci.md)

### For Operators

1. **Environments**: Review [03-environments.md](./03-environments.md)
2. **Deployment**: Follow [08-deployments.md](./08-deployments.md)
3. **Monitoring**: Set up per [06-observability.md](./06-observability.md)
4. **Incidents**: Use [09-runbook.md](./09-runbook.md) for troubleshooting

### For Security Reviewers

1. **Security Architecture**: See [04-security.md](./04-security.md)
2. **RBAC & Tenancy**: Review [05-accounts-billing.md](./05-accounts-billing.md)
3. **Compliance**: Check [SECURITY.md](../SECURITY.md) and [PRIVACY_POLICY.md](../PRIVACY_POLICY.md)

## 🎯 Core Concepts

### Multi-Tenancy
- **Organizations**: Billing and top-level isolation boundary
- **Workspaces**: Optional sub-grouping within organizations
- **Projects**: Intelligence projects and agent workflows
- Row-level security enforced at database and API layers

### Services
- **Web (apps/web)**: User-facing Next.js application
- **API (apps/api)**: FastAPI service for all business logic
- **Worker (apps/worker)**: Background job processing for AI agents

### Authentication & Authorization
- External authentication via Supabase Auth / OIDC
- JWT validation at API gateway
- Role-based access control (Owner, Admin, Editor, Viewer)
- Resource-scoped permissions per organization

### Payments
- Razorpay integration for Indian market
- Subscription-based billing with multiple tiers
- Double-entry ledger for financial records
- Webhook-driven payment capture with idempotency

## 🔐 Security Highlights

- ✅ HTTPS-only with HSTS
- ✅ JWT authentication with JWKS validation
- ✅ Row-level security (org_id scoping)
- ✅ Rate limiting per IP and per user
- ✅ Secret management via Cloud Secret Manager
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ Audit logging for sensitive operations
- ✅ Automated security scanning (Bandit, Safety, Trivy)

See [04-security.md](./04-security.md) for complete security architecture.

## 📊 Observability

- **Structured Logging**: JSON logs with request IDs and context
- **Metrics**: Latency, throughput, errors, token spend
- **Tracing**: OpenTelemetry across all services
- **Alerting**: Automated alerts for critical issues

See [06-observability.md](./06-observability.md) for details.

## 🧪 Testing

| Level | Tools | Coverage |
|-------|-------|----------|
| **Unit** | pytest, Jest | Pure functions, business logic |
| **Integration** | pytest with TestClient | API contracts, DB operations |
| **E2E** | Playwright | Critical user journeys |
| **Load** | k6 | Performance benchmarks |

See [07-testing-ci.md](./07-testing-ci.md) for testing strategy.

## 🌍 Environments

| Environment | Purpose | Auto-Deploy | URL |
|-------------|---------|-------------|-----|
| **local** | Development | N/A | localhost |
| **staging** | Pre-production testing | ✅ Yes (on merge to dev) | staging.raptorflow.com |
| **production** | Live user traffic | ⚠️ Manual approval | app.raptorflow.com |

See [03-environments.md](./03-environments.md) for configuration details.

## 📦 Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: Tailwind CSS, Framer Motion
- **State**: React Context + Server Components
- **Forms**: React Hook Form + Zod

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2

### Infrastructure
- **Hosting**: Google Cloud Run
- **Database**: Cloud SQL (PostgreSQL 15)
- **Cache/Queue**: Redis (Cloud Memorystore)
- **Storage**: Cloud Storage (GCS)
- **Secrets**: Secret Manager
- **IaC**: Terraform

### AI/ML
- **LLM Providers**: OpenAI, Gemini, Perplexity
- **Orchestration**: LangGraph
- **Vector DB**: Supabase pgvector (optional)

### Observability
- **Logs**: Structured JSON (structlog)
- **Metrics**: OpenTelemetry
- **Tracing**: OpenTelemetry
- **APM**: Sentry
- **Uptime**: Uptimerobot / Better Stack

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development workflow, code style, and PR process.

## 📄 Legal

- **Security Policy**: [SECURITY.md](../SECURITY.md)
- **Privacy Policy**: [PRIVACY_POLICY.md](../PRIVACY_POLICY.md)
- **Terms of Service**: [TERMS_OF_SERVICE.md](../TERMS_OF_SERVICE.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/raptorflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/raptorflow/discussions)
- **Security**: security@raptorflow.com (see [SECURITY.md](../SECURITY.md))

## 📚 Additional Resources

- **API Documentation**: https://api.raptorflow.com/docs (OpenAPI)
- **Changelog**: [GitHub Releases](https://github.com/your-org/raptorflow/releases)
- **Status Page**: https://status.raptorflow.com
- **Blog**: https://raptorflow.com/blog

---

**Last Updated**: 2025-01-20
**Version**: 1.0.0
**Maintained by**: RaptorFlow Team

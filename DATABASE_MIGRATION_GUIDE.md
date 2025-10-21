# Database Migration Guide

**Status**: Migration scripts ready to run
**Date**: 2025-01-20

---

## Overview

This guide walks through setting up the database and running migrations for RaptorFlow.

---

## Prerequisites

### 1. Install PostgreSQL 15+

**Windows**:
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey
choco install postgresql

# Start PostgreSQL service
net start postgresql-x64-15
```

**macOS**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux**:
```bash
sudo apt-get update
sudo apt-get install postgresql-15 postgresql-contrib
sudo systemctl start postgresql
```

### 2. Install Redis

**Windows**:
```bash
# Download from https://redis.io/download
# Or use chocolatey
choco install redis-64

# Start Redis
redis-server
```

**macOS**:
```bash
brew install redis
brew services start redis
```

**Linux**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt

# Additional dependencies for production
pip install alembic asyncpg psycopg2-binary redis
```

---

## Database Setup

### 1. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE raptorflow;

# Create user (optional)
CREATE USER raptorflow WITH ENCRYPTED PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE raptorflow TO raptorflow;

# Exit
\q
```

### 2. Update .env File

Update `backend/.env` with your actual credentials:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/raptorflow

# Supabase (get from https://supabase.com/dashboard/project/_/settings/api)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret

# Razorpay (get from https://dashboard.razorpay.com/app/keys)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx

# Application
SECRET_KEY=$(openssl rand -hex 32)
```

---

## Running Migrations

### 1. Generate Initial Migration

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Initial schema with auth, billing, and threat intel models"
```

This will create a migration file in `backend/alembic/versions/` that looks like:

```python
"""Initial schema with auth, billing, and threat intel models

Revision ID: abc123def456
Revises:
Create Date: 2025-01-20 10:00:00.000000
"""

def upgrade() -> None:
    # Creates all tables:
    # - users, organizations, memberships, workspaces
    # - plans, subscriptions, payments, ledger_entries, invoices
    # - projects, indicators, threat_actors, campaigns, vulnerabilities, threat_reports
    ...

def downgrade() -> None:
    # Drops all tables
    ...
```

### 2. Review Migration

```bash
# View migration file
cat alembic/versions/abc123def456_initial_schema.py

# Check current database version
alembic current

# Check migration history
alembic history
```

### 3. Apply Migration

```bash
# Apply all pending migrations
alembic upgrade head

# Or apply specific migration
alembic upgrade abc123def456
```

### 4. Verify Database Schema

```bash
# Connect to database
psql -U postgres -d raptorflow

# List all tables
\dt

# Should see:
# - users
# - organizations
# - memberships
# - workspaces
# - plans
# - subscriptions
# - payments
# - ledger_entries
# - invoices
# - projects
# - indicators
# - threat_actors
# - campaigns
# - vulnerabilities
# - threat_reports

# Describe a table
\d users

# Exit
\q
```

---

## Seed Data

### 1. Create Subscription Plans

```sql
-- Connect to database
psql -U postgres -d raptorflow

-- Insert plans
INSERT INTO plans (id, name, price_cents, currency, billing_period, api_requests_per_month, ai_tokens_per_month, features)
VALUES
('free', 'Free', 0, 'INR', 'monthly', 10000, 10000, '{"ai_agents": false, "projects": 3}'::jsonb),
('pro', 'Pro', 350000, 'INR', 'monthly', 100000, 500000, '{"ai_agents": true, "projects": 50, "exports": true}'::jsonb),
('enterprise', 'Enterprise', 999900, 'INR', 'monthly', -1, -1, '{"ai_agents": true, "projects": -1, "exports": true, "sla": true, "support": "priority"}'::jsonb);

-- Verify
SELECT * FROM plans;
```

### 2. Create Test User (via Supabase)

Sign up via Supabase Auth UI or API to create test users. The backend will auto-create user records on first sign-in.

---

## Migration Commands Reference

### Common Operations

```bash
# Check current version
alembic current

# View migration history
alembic history --verbose

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision_id>

# Downgrade by 1 version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade all
alembic downgrade base

# Show SQL without executing
alembic upgrade head --sql

# Create empty migration
alembic revision -m "description"

# Create auto-generated migration
alembic revision --autogenerate -m "description"
```

### Rollback Scenarios

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

---

## Database Schema Overview

### Authentication Tables

**users**
- `id` (UUID, PK)
- `auth_sub` (TEXT, unique) - Supabase user ID
- `email` (TEXT)
- `display_name`, `avatar_url`
- `settings` (JSONB)
- `created_at`, `updated_at`

**organizations**
- `id` (UUID, PK)
- `name` (TEXT)
- `slug` (TEXT, unique)
- `description` (TEXT)
- `settings` (JSONB)
- `created_at`, `updated_at`

**memberships**
- `org_id` (UUID, FK to organizations)
- `user_id` (UUID, FK to users)
- `role` (ENUM: viewer, editor, admin, owner)
- `invitation_status`, `invited_by`
- `created_at`, `updated_at`
- Primary Key: (org_id, user_id)

### Billing Tables

**plans**
- `id` (TEXT, PK) - free, pro, enterprise
- `name`, `description`
- `price_cents` (INT)
- `currency` (TEXT)
- `billing_period` (TEXT)
- `api_requests_per_month` (INT)
- `ai_tokens_per_month` (INT)
- `features` (JSONB)

**subscriptions**
- `id` (UUID, PK)
- `org_id` (UUID, FK, unique)
- `plan_id` (TEXT, FK)
- `status` (TEXT) - trialing, active, past_due, canceled
- `current_period_start`, `current_period_end`
- `usage tracking fields`

**payments**
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `subscription_id` (UUID, FK)
- `provider_payment_id` (TEXT, unique)
- `amount_cents` (INT)
- `status` (TEXT) - pending, captured, refunded, failed
- `method` (TEXT)
- `captured_at`, `refunded_at`

**ledger_entries** (double-entry accounting)
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `account` (TEXT) - cash, revenue, refunds
- `direction` (TEXT) - DR or CR
- `amount_cents` (INT)
- `ref_type`, `ref_id` (polymorphic reference)

### Threat Intelligence Tables

**projects**
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `name`, `description`
- `tags` (TEXT[])
- `settings` (JSONB)
- `archived` (BOOLEAN)
- `created_by` (UUID, FK)
- `created_at`, `updated_at`

**indicators**
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `project_id` (UUID, FK, nullable)
- `type` (TEXT) - ip, domain, url, hash, email, etc.
- `value` (TEXT)
- `classification` (TEXT) - malicious, suspicious, benign, unknown
- `confidence` (INT) - 0-100
- `severity` (TEXT) - critical, high, medium, low, info
- `first_seen`, `last_seen`
- `source` (TEXT)
- `tags` (TEXT[])
- `mitre_tactics`, `mitre_techniques` (TEXT[])
- `enrichment` (JSONB)
- `active`, `false_positive` (BOOLEAN)
- `created_by` (UUID, FK)
- `created_at`, `updated_at`

**threat_actors**
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `project_id` (UUID, FK, nullable)
- `name`, `aliases` (TEXT[])
- `type` (TEXT) - apt, cybercrime, nation-state, etc.
- `sophistication` (TEXT)
- `origin_country` (TEXT)
- `motivation` (TEXT[])
- `mitre_tactics`, `mitre_techniques`, `tools` (TEXT[])
- `target_sectors`, `target_countries` (TEXT[])
- `first_seen`, `last_seen`
- `active` (BOOLEAN)

**campaigns**
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `project_id` (UUID, FK, nullable)
- `threat_actor_id` (UUID, FK, nullable)
- `name`, `aliases` (TEXT[])
- `objectives` (TEXT[])
- `mitre_tactics`, `mitre_techniques` (TEXT[])
- `target_sectors`, `target_countries` (TEXT[])
- `indicator_ids` (UUID[])
- `first_seen`, `last_seen`
- `active` (BOOLEAN)
- `severity` (TEXT)

**vulnerabilities**
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `project_id` (UUID, FK, nullable)
- `cve_id` (TEXT, unique, nullable)
- `name`, `description`
- `cvss_score` (INT)
- `severity` (TEXT)
- `affected_products`, `affected_versions` (TEXT[])
- `exploit_available`, `exploited_in_wild`, `patch_available` (BOOLEAN)
- `published_date`, `discovered_date`
- `enrichment` (JSONB)

**threat_reports**
- `id` (UUID, PK)
- `org_id` (UUID, FK)
- `project_id` (UUID, FK, nullable)
- `title`, `summary`, `content` (TEXT)
- `classification` (TEXT) - TLP levels
- `severity` (TEXT)
- `indicator_ids`, `threat_actor_ids`, `campaign_ids`, `vulnerability_ids` (UUID[])
- `published`, `published_at`
- `created_by` (UUID, FK)
- `created_at`, `updated_at`

---

## Indexes

All tables have indexes on:
- Primary keys (automatic)
- Foreign keys (automatic)
- `org_id` (for multi-tenant queries)
- Unique constraints (email, slug, etc.)

Additional indexes to consider for production:
- `indicators.value` (for fast lookups)
- `indicators.type, org_id` (composite for filtered queries)
- `projects.archived, org_id` (for active project queries)
- `threat_actors.name` (for name searches)

---

## Troubleshooting

### Migration Fails

```bash
# Check Alembic version
alembic current

# Verify database connection
psql -U postgres -d raptorflow -c "SELECT 1"

# Check for conflicting migrations
alembic history

# Force version (dangerous - only if you know what you're doing)
alembic stamp head
```

### Connection Errors

```bash
# Test PostgreSQL connection
psql -U postgres -d raptorflow

# Test Redis connection
redis-cli ping

# Check environment variables
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### Schema Conflicts

```bash
# Drop all tables (DANGEROUS - loses all data)
psql -U postgres -d raptorflow -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migrations
alembic upgrade head
```

---

## Production Considerations

### 1. Backup Before Migrations

```bash
# Backup before applying migrations
pg_dump -U postgres raptorflow > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply migration
alembic upgrade head

# Restore if needed
psql -U postgres raptorflow < backup_20250120_100000.sql
```

### 2. Zero-Downtime Migrations

For production, use multi-step migrations:

**Step 1**: Add new column (nullable)
```python
def upgrade():
    op.add_column('users', sa.Column('new_field', sa.String(), nullable=True))
```

**Step 2**: Backfill data
```python
def upgrade():
    op.execute("UPDATE users SET new_field = 'default_value'")
```

**Step 3**: Make non-nullable
```python
def upgrade():
    op.alter_column('users', 'new_field', nullable=False)
```

### 3. Migration Testing

```bash
# Test on staging database first
DATABASE_URL=postgresql://user:pass@staging-db:5432/raptorflow alembic upgrade head

# Verify data integrity
psql -U postgres -d raptorflow -c "SELECT COUNT(*) FROM users"

# Test rollback
alembic downgrade -1
alembic upgrade head
```

---

## Next Steps

Once migrations are applied:

1. **Seed initial data** (plans, etc.)
2. **Create test user** via Supabase Auth
3. **Test API endpoints** (start server, hit /docs)
4. **Set up monitoring** (database metrics, slow queries)
5. **Configure backups** (automated daily backups)

---

**Last Updated**: 2025-01-20
**Migration Version**: Initial schema (all models)

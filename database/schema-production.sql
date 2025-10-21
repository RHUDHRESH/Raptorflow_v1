-- ==========================================
-- RaptorFlow Production Database Schema
-- ==========================================
-- PostgreSQL 15+
-- Multi-tenant SaaS with organization scoping
--
-- Usage:
--   psql -U raptorflow -d raptorflow_prod < schema-production.sql
--
-- Note: This is the complete schema.
--       Use Alembic migrations for incremental changes.

-- ==========================================
-- Extensions
-- ==========================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- Custom Types
-- ==========================================

CREATE TYPE role AS ENUM ('owner', 'admin', 'editor', 'viewer');

-- ==========================================
-- Core Tables
-- ==========================================

-- Users (local profiles linked to Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_sub TEXT UNIQUE NOT NULL,              -- Supabase UID
    email TEXT NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_auth_sub ON users(auth_sub);
CREATE INDEX idx_users_email ON users(email);

-- Organizations (billing entities)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    billing_email TEXT,
    website TEXT,
    industry TEXT,
    size TEXT,                                   -- startup, small, medium, enterprise
    logo_url TEXT,
    settings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_organizations_slug ON organizations(slug);

-- Memberships (user-org-role relationships)
CREATE TABLE memberships (
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role role NOT NULL,
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (org_id, user_id)
);

CREATE INDEX idx_memberships_user_id ON memberships(user_id);
CREATE INDEX idx_memberships_org_id ON memberships(org_id);

-- Workspaces (optional sub-grouping within orgs)
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, name)
);

CREATE INDEX idx_workspaces_org_id ON workspaces(org_id);

-- ==========================================
-- Billing Tables
-- ==========================================

-- Plans (subscription tiers)
CREATE TABLE plans (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    billing_period TEXT NOT NULL,               -- monthly, yearly

    -- Rate limits
    api_requests_per_month INT NOT NULL,
    ai_tokens_per_month INT NOT NULL,

    -- Feature flags
    features JSONB NOT NULL DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    plan_id TEXT NOT NULL REFERENCES plans(id),
    status TEXT NOT NULL,                       -- trialing, active, past_due, canceled

    -- Trial
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,

    -- Billing period
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,

    -- Usage tracking
    api_requests_used INT NOT NULL DEFAULT 0,
    ai_tokens_used INT NOT NULL DEFAULT 0,

    -- Cancellation
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    canceled_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(org_id)
);

CREATE INDEX idx_subscriptions_org_id ON subscriptions(org_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_period_end ON subscriptions(current_period_end);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,

    -- Razorpay details
    provider TEXT NOT NULL DEFAULT 'razorpay',
    provider_payment_id TEXT UNIQUE,
    provider_order_id TEXT NOT NULL,

    -- Amount
    amount_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',

    -- Status
    status TEXT NOT NULL,                       -- pending, captured, refunded, failed

    -- Payment method
    method TEXT,                                 -- card, upi, netbanking, wallet

    -- Metadata
    description TEXT,
    meta JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    captured_at TIMESTAMPTZ,
    refunded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_org_id ON payments(org_id);
CREATE INDEX idx_payments_provider_payment_id ON payments(provider_payment_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- Ledger (double-entry accounting)
CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id),

    -- Transaction
    entry_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account TEXT NOT NULL,
    direction TEXT NOT NULL,

    -- Amount
    amount_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',

    -- Reference
    ref_type TEXT,
    ref_id TEXT,
    description TEXT,

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_direction CHECK (direction IN ('DR', 'CR'))
);

CREATE INDEX idx_ledger_org_id ON ledger_entries(org_id);
CREATE INDEX idx_ledger_entry_at ON ledger_entries(entry_at);
CREATE INDEX idx_ledger_account ON ledger_entries(account);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,

    -- Invoice details
    invoice_number TEXT UNIQUE NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due_at TIMESTAMPTZ,

    -- Amounts
    subtotal_cents INT NOT NULL,
    tax_cents INT NOT NULL DEFAULT 0,
    total_cents INT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',

    -- Status
    status TEXT NOT NULL,                       -- draft, issued, paid, void
    paid_at TIMESTAMPTZ,

    -- PDF
    pdf_url TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invoices_org_id ON invoices(org_id);
CREATE INDEX idx_invoices_invoice_number ON invoices(invoice_number);

-- ==========================================
-- Domain Tables (Threat Intelligence)
-- ==========================================

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_org_id ON projects(org_id);
CREATE INDEX idx_projects_workspace_id ON projects(workspace_id);

-- Threat Actors
CREATE TABLE threat_actors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

    name TEXT NOT NULL,
    aliases TEXT[],
    description TEXT,
    motivation TEXT,
    sophistication TEXT,

    -- Metadata
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    tags TEXT[],
    confidence_score DECIMAL(3,2),              -- 0.00 to 1.00

    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_threat_actors_org_id ON threat_actors(org_id);
CREATE INDEX idx_threat_actors_project_id ON threat_actors(project_id);
CREATE INDEX idx_threat_actors_name ON threat_actors(name);

-- Tactics (MITRE ATT&CK)
CREATE TABLE tactics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

    mitre_id TEXT,                              -- TA0001, etc.
    name TEXT NOT NULL,
    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tactics_org_id ON tactics(org_id);
CREATE INDEX idx_tactics_mitre_id ON tactics(mitre_id);

-- Indicators of Compromise (IOCs)
CREATE TABLE indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

    type TEXT NOT NULL,                         -- ip, domain, hash, url, email
    value TEXT NOT NULL,
    description TEXT,

    -- Enrichment
    tlp TEXT,                                    -- white, green, amber, red
    confidence_score DECIMAL(3,2),
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,

    -- Relationships
    threat_actor_id UUID REFERENCES threat_actors(id) ON DELETE SET NULL,

    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_indicators_org_id ON indicators(org_id);
CREATE INDEX idx_indicators_type ON indicators(type);
CREATE INDEX idx_indicators_value ON indicators(value);
CREATE INDEX idx_indicators_threat_actor_id ON indicators(threat_actor_id);

-- ==========================================
-- API Keys
-- ==========================================

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Key (hashed)
    key_prefix TEXT NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,

    -- Metadata
    name TEXT NOT NULL,
    scopes TEXT[] NOT NULL DEFAULT '{}',

    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    last_used_ip INET,

    -- Lifecycle
    expires_at TIMESTAMPTZ,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(id),

    -- Audit
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_api_keys_org_id ON api_keys(org_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);

-- ==========================================
-- Audit & Logging
-- ==========================================

-- Audit Logs
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    action TEXT NOT NULL,
    resource TEXT,
    resource_id TEXT,

    -- Request context
    ip_address INET,
    user_agent TEXT,

    -- Changes
    old_values JSONB,
    new_values JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_org_id ON audit_logs(org_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- API Usage Logs (for metrics)
CREATE TABLE api_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,

    -- Request
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    status_code INT NOT NULL,

    -- Timing
    duration_ms INT NOT NULL,

    -- Tokens (if AI call)
    ai_tokens_used INT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_api_usage_logs_org_id ON api_usage_logs(org_id);
CREATE INDEX idx_api_usage_logs_created_at ON api_usage_logs(created_at);

-- ==========================================
-- Seed Data (Plans)
-- ==========================================

INSERT INTO plans (id, name, description, price_cents, currency, billing_period, api_requests_per_month, ai_tokens_per_month, features) VALUES
('free', 'Free', 'Basic threat intelligence for small teams', 0, 'INR', 'monthly', 10000, 10000, '{"ai_agents": false, "exports": false, "api_access": false}'::jsonb),
('pro', 'Pro', 'Advanced threat intelligence with AI agents', 350000, 'INR', 'monthly', 100000, 500000, '{"ai_agents": true, "exports": true, "api_access": true, "trend_monitoring": true}'::jsonb),
('enterprise', 'Enterprise', 'Custom solution with dedicated support', 0, 'INR', 'monthly', 999999999, 999999999, '{"ai_agents": true, "exports": true, "api_access": true, "trend_monitoring": true, "priority_support": true, "sla": true}'::jsonb);

-- ==========================================
-- Functions
-- ==========================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threat_actors_updated_at BEFORE UPDATE ON threat_actors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_indicators_updated_at BEFORE UPDATE ON indicators
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- Views (for reporting)
-- ==========================================

-- Monthly Recurring Revenue (MRR)
CREATE VIEW v_mrr AS
SELECT
    DATE_TRUNC('month', s.created_at) as month,
    COUNT(*) as subscriptions,
    SUM(p.price_cents) as mrr_cents
FROM subscriptions s
JOIN plans p ON s.plan_id = p.id
WHERE s.status = 'active'
GROUP BY DATE_TRUNC('month', s.created_at);

-- Active Users by Org
CREATE VIEW v_active_users_by_org AS
SELECT
    o.id as org_id,
    o.name as org_name,
    COUNT(DISTINCT m.user_id) as user_count,
    COUNT(DISTINCT CASE WHEN m.role = 'owner' THEN m.user_id END) as owners,
    COUNT(DISTINCT CASE WHEN m.role = 'admin' THEN m.user_id END) as admins,
    COUNT(DISTINCT CASE WHEN m.role = 'editor' THEN m.user_id END) as editors,
    COUNT(DISTINCT CASE WHEN m.role = 'viewer' THEN m.user_id END) as viewers
FROM organizations o
LEFT JOIN memberships m ON o.id = m.org_id
GROUP BY o.id, o.name;

-- ==========================================
-- Permissions & Security
-- ==========================================

-- Ensure every organization has at least one owner
CREATE OR REPLACE FUNCTION check_org_has_owner()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM memberships
        WHERE org_id = NEW.org_id AND role = 'owner') = 0 THEN
        RAISE EXCEPTION 'Organization must have at least one owner';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: Trigger would be applied carefully in production
-- to avoid blocking valid operations

-- ==========================================
-- Comments (Documentation)
-- ==========================================

COMMENT ON TABLE users IS 'Local user profiles linked to Supabase Auth';
COMMENT ON TABLE organizations IS 'Top-level tenants and billing entities';
COMMENT ON TABLE memberships IS 'User-to-organization relationships with roles';
COMMENT ON TABLE subscriptions IS 'Organization subscription to plans';
COMMENT ON TABLE payments IS 'Payment transactions from Razorpay';
COMMENT ON TABLE ledger_entries IS 'Double-entry accounting ledger';
COMMENT ON TABLE projects IS 'Threat intelligence projects';
COMMENT ON TABLE threat_actors IS 'Threat actor profiles';
COMMENT ON TABLE indicators IS 'Indicators of Compromise (IOCs)';
COMMENT ON TABLE audit_logs IS 'Audit trail for sensitive operations';

-- ==========================================
-- End of Schema
-- ==========================================

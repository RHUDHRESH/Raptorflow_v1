-- ==========================================
-- Migration: Add OAuth Support
-- ==========================================
-- Adds OAuth provider linking and conversation tables
-- For Google OAuth and multi-turn conversations

-- Run with:
--   psql -U raptorflow -d raptorflow_prod < migrations/001_add_oauth_support.sql

-- ==========================================
-- OAuth Accounts Table
-- ==========================================
-- Stores OAuth provider account links for users

CREATE TABLE IF NOT EXISTS oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Provider info
    provider TEXT NOT NULL,              -- 'google', 'github', etc
    provider_user_id TEXT NOT NULL,      -- Sub from Google

    -- User data from OAuth
    email TEXT,
    name TEXT,
    picture TEXT,

    -- Token info
    access_token TEXT,                   -- Encrypted in production
    refresh_token TEXT,                  -- Encrypted in production
    token_expires_at TIMESTAMPTZ,

    -- Metadata
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one account per user per provider
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_oauth_accounts_user_id ON oauth_accounts(user_id);
CREATE INDEX idx_oauth_accounts_provider_user_id ON oauth_accounts(provider, provider_user_id);
CREATE INDEX idx_oauth_accounts_provider ON oauth_accounts(provider);

-- ==========================================
-- Conversations Table
-- ==========================================
-- Stores multi-turn conversations with AI agents

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Metadata
    title TEXT,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active',  -- active, archived, deleted

    -- Type of conversation
    agent_type TEXT,  -- 'research', 'strategy', 'content', etc

    -- Settings
    settings JSONB DEFAULT '{}',  -- Model, temperature, top_k, etc

    -- Metrics
    message_count INT NOT NULL DEFAULT 0,
    token_count INT NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    archived_at TIMESTAMPTZ
);

CREATE INDEX idx_conversations_org_id ON conversations(org_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_conversations_org_user ON conversations(org_id, user_id);

-- ==========================================
-- Conversation Messages Table
-- ==========================================
-- Stores individual messages in conversations

CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Message data
    role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,

    -- Metadata
    metadata JSONB DEFAULT '{}',  -- tokens, model, latency, etc

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_messages_user_id ON conversation_messages(user_id);
CREATE INDEX idx_messages_role ON conversation_messages(role);
CREATE INDEX idx_messages_created_at ON conversation_messages(created_at DESC);
CREATE INDEX idx_messages_conversation_created ON conversation_messages(conversation_id, created_at DESC);

-- ==========================================
-- Message Embeddings Table
-- ==========================================
-- Stores vector embeddings for RAG

CREATE TABLE IF NOT EXISTS message_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES conversation_messages(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Embedding
    embedding VECTOR(1536),  -- OpenAI embedding dimension (requires pgvector extension)

    -- Metadata
    embedding_model TEXT NOT NULL DEFAULT 'text-embedding-ada-002',
    content_length INT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_embeddings_message_id ON message_embeddings(message_id);
CREATE INDEX idx_embeddings_conversation_id ON message_embeddings(conversation_id);
-- Vector similarity search index (L2 distance)
CREATE INDEX idx_embeddings_vector ON message_embeddings USING hnsw (embedding vector_cosine_ops);

-- ==========================================
-- Context Cache Table
-- ==========================================
-- Caches retrieved context for faster response generation

CREATE TABLE IF NOT EXISTS context_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Cache key
    cache_key TEXT NOT NULL,

    -- Cached context
    context_data JSONB NOT NULL,  -- Similar messages, documents, etc
    context_metadata JSONB DEFAULT '{}',

    -- Cache stats
    hit_count INT NOT NULL DEFAULT 0,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),

    -- Expiration
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX idx_context_cache_conversation ON context_cache(conversation_id);
CREATE INDEX idx_context_cache_key ON context_cache(cache_key);
CREATE INDEX idx_context_cache_expires ON context_cache(expires_at);

-- ==========================================
-- Conversation Analytics Table
-- ==========================================
-- Tracks conversation metrics for analytics

CREATE TABLE IF NOT EXISTS conversation_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Counts
    total_messages INT NOT NULL DEFAULT 0,
    total_tokens INT NOT NULL DEFAULT 0,
    total_cost DECIMAL(10, 4) NOT NULL DEFAULT 0,

    -- Performance
    avg_response_time_ms INT,
    min_response_time_ms INT,
    max_response_time_ms INT,

    -- Quality
    avg_confidence FLOAT,
    user_satisfaction FLOAT,  -- Star rating

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analytics_conversation ON conversation_analytics(conversation_id);
CREATE INDEX idx_analytics_org ON conversation_analytics(org_id);
CREATE INDEX idx_analytics_created ON conversation_analytics(created_at DESC);

-- ==========================================
-- Permissions Check
-- ==========================================
-- Ensure RLS is enabled on new tables

ALTER TABLE oauth_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_analytics ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- Migration Status
-- ==========================================
-- Log migration completion

INSERT INTO schema_migrations (name, executed_at)
VALUES ('001_add_oauth_support', NOW())
ON CONFLICT (name) DO UPDATE SET executed_at = NOW();

COMMIT;

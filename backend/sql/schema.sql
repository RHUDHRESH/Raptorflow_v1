-- Supabase / Postgres bootstrap
create extension if not exists vector;

-- Core entities
create table if not exists businesses (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  industry text,
  location text,
  description text,
  goals jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists positioning_analyses (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  options jsonb not null,
  selected_option jsonb,
  created_at timestamptz default now()
);

create table if not exists icps (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  name text not null,
  demographics jsonb,
  psychographics jsonb,
  platforms text[],
  content_preferences jsonb,
  trending_topics text[],
  tags text[],
  embedding vector(1536),
  created_at timestamptz default now()
);

create table if not exists moves (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  goal text not null,
  platform text not null,
  duration_days integer not null,
  calendar jsonb,
  status text default 'active',
  created_at timestamptz default now()
);

create table if not exists platform_specs (
  id uuid primary key default gen_random_uuid(),
  platform text not null unique,
  specs jsonb not null
);

-- Seed a few platform constraints
insert into platform_specs (platform, specs) values
('twitter', '{
  "text": {"max": 280, "optimal": 250},
  "images": {"count": 4, "maxSize": "5MB"},
  "video": {"maxLength": "2:20", "maxSize": "1GB"}
}')
on conflict (platform) do nothing;

insert into platform_specs (platform, specs) values
('linkedin', '{
  "text": {"max": 3000, "optimal": 150},
  "carousel": {"format": "PDF", "maxSize": "100MB", "maxPages": 300},
  "video": {"maxSize": "5GB", "maxLength": "10:00"}
}')
on conflict (platform) do nothing;

insert into platform_specs (platform, specs) values
('instagram', '{
  "caption": {"max": 2200, "optimal": 125},
  "carousel": {"maxSlides": 20},
  "reels": {"maxLength": "90s", "aspectRatio": "9:16"}
}')
on conflict (platform) do nothing;

-- ==================== ADDITIONAL STRATEGIC TABLES ====================

-- Subscriptions
create table if not exists subscriptions (
  id uuid primary key default gen_random_uuid(),
  business_id uuid unique references businesses(id) on delete cascade,
  tier text default 'trial',
  max_icps integer default 3,
  max_moves integer default 5,
  razorpay_subscription_id text,
  razorpay_order_id text,
  status text default 'trial',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Evidence Graph
create table if not exists evidence_nodes (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  node_type text not null,
  content text not null,
  metadata jsonb,
  confidence_score float default 1.0,
  source text,
  embedding vector(768),
  created_at timestamptz default now()
);

create table if not exists evidence_edges (
  id uuid primary key default gen_random_uuid(),
  from_node uuid references evidence_nodes(id) on delete cascade,
  to_node uuid references evidence_nodes(id) on delete cascade,
  relationship_type text,
  strength float,
  created_by_agent text,
  created_at timestamptz default now()
);

-- SOSTAC Analysis
create table if not exists sostac_analyses (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  situation jsonb,
  objectives jsonb,
  strategy jsonb,
  tactics jsonb,
  action jsonb,
  control jsonb,
  created_at timestamptz default now()
);

-- Competitor Ladder
create table if not exists competitor_ladder (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  competitor_name text not null,
  word_owned text,
  position_strength float,
  evidence jsonb,
  created_at timestamptz default now()
);

-- Enhanced Positioning
alter table positioning_analyses add column if not exists inherent_drama text;
alter table positioning_analyses add column if not exists big_idea text;
alter table positioning_analyses add column if not exists visual_hammer jsonb;
alter table positioning_analyses add column if not exists word_to_own text;
alter table positioning_analyses add column if not exists sacrifice jsonb;
alter table positioning_analyses add column if not exists validation_score float;

-- Enhanced ICPs
alter table icps add column if not exists segment_hypothesis text;
alter table icps add column if not exists jtbd jsonb;
alter table icps add column if not exists value_proposition jsonb;
alter table icps add column if not exists fit_score float;
alter table icps add column if not exists urgency_score float;
alter table icps add column if not exists accessibility_score float;
alter table icps add column if not exists monitoring_tags text[];

-- Strategy
create table if not exists strategies (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  seven_ps jsonb,
  north_star_metric text,
  strategic_bets jsonb,
  race_calendar jsonb,
  created_at timestamptz default now()
);

-- Trend Monitoring
create table if not exists trend_checks (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  icp_id uuid references icps(id) on delete cascade,
  search_tags text[],
  trends_found jsonb,
  relevance_scores jsonb,
  calendar_injected boolean default false,
  checked_at timestamptz default now()
);

-- Performance & Learning
create table if not exists performance_metrics (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  entity_type text,
  entity_id uuid,
  metric_name text,
  metric_value float,
  measured_at timestamptz default now()
);

create table if not exists route_back_logs (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  from_stage text,
  to_stage text,
  reason text,
  decision_data jsonb,
  resolved boolean default false,
  created_at timestamptz default now()
);

-- Agent Sessions
create table if not exists agent_sessions (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  agent_name text not null,
  state jsonb not null,
  context jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  status text default 'running'
);

-- ==================== INDEXES ====================

create index if not exists idx_businesses_created on businesses(created_at);
create index if not exists idx_positioning_business on positioning_analyses(business_id);
create index if not exists idx_icps_business on icps(business_id);
create index if not exists idx_moves_business on moves(business_id);
create index if not exists idx_icps_embedding on icps using ivfflat (embedding vector_cosine_ops);
create index if not exists idx_subscriptions_business on subscriptions(business_id);
create index if not exists idx_evidence_nodes_business on evidence_nodes(business_id);
create index if not exists idx_evidence_nodes_embedding on evidence_nodes using ivfflat (embedding vector_cosine_ops);
create index if not exists idx_trend_checks_icp on trend_checks(icp_id);
create index if not exists idx_performance_metrics_business on performance_metrics(business_id);
create index if not exists idx_agent_sessions_business on agent_sessions(business_id);

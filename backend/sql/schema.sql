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

-- Helpful indexes
create index if not exists idx_businesses_created on businesses(created_at);
create index if not exists idx_positioning_business on positioning_analyses(business_id);
create index if not exists idx_icps_business on icps(business_id);
create index if not exists idx_moves_business on moves(business_id);
create index if not exists idx_icps_embedding on icps using ivfflat (embedding vector_cosine_ops);

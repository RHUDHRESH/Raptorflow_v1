# RaptorFlow Mode Switching Guide

## Overview

RaptorFlow now supports two execution modes with a **single configuration file**:

- **Dev Mode** (`EXECUTION_MODE=dev`): Local tools - Ollama, ChromaDB, in-memory cache
- **Cloud Mode** (`EXECUTION_MODE=cloud`): Cloud services - OpenAI, Supabase, Redis

Change one environment variable to switch the entire app between local and cloud infrastructure.

---

## Quick Start

### Dev Mode (Local Development)

```bash
# Copy dev environment template
cp .env.dev .env

# Install local dependencies
pip install ollama chromadb

# Start Ollama (in another terminal)
ollama serve

# Pull a model (if not already present)
ollama pull mistral

# Start the app
uvicorn app.main:app --reload
```

**What happens in Dev Mode:**
- LLM calls use **Ollama** running locally (unlimited, free)
- Embeddings use **Ollama** embeddings (local)
- Vector database is **ChromaDB** (local, file-based)
- Cache is **in-memory** (no Redis needed)
- Database is local **PostgreSQL**
- Payments are **disabled**

---

### Cloud Mode (Production)

```bash
# Copy cloud environment template
cp .env.cloud .env

# Set your cloud credentials in .env
export EXECUTION_MODE=cloud
export OPENAI_API_KEY=sk-...
export SUPABASE_URL=https://...
export SUPABASE_SERVICE_KEY=...

# Install cloud dependencies
pip install openai supabase redis

# Start the app
uvicorn app.main:app
```

**What happens in Cloud Mode:**
- LLM calls use **OpenAI GPT-4-Turbo** (fast, intelligent, low cost)
- Embeddings use **OpenAI Ada** embeddings
- Vector database is **Supabase pgvector** (managed, scalable)
- Cache is **Redis** (cloud-based)
- Database is **Supabase PostgreSQL**
- Payments are **enabled** (Razorpay)
- Budget control enforced ($15/month)

---

## Configuration Files

### `.env.dev` - Development Mode Template

Complete local setup for development. No cloud credentials needed.

```env
EXECUTION_MODE=dev
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
CHROMADB_PATH=./chromadb_data
CACHE_PROVIDER=in_memory
```

### `.env.cloud` - Cloud Mode Template

Production setup with all cloud services configured.

```env
EXECUTION_MODE=cloud
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
REDIS_URL=redis://...
```

---

## Architecture

### Service Factory Pattern

All services are created through a **ServiceFactory** pattern that adapts to the execution mode:

```python
from app.core.service_factories import services

# Automatically gets correct implementation based on EXECUTION_MODE
llm_service = services.llm           # Ollama or OpenAI
embeddings = services.embeddings     # Ollama or OpenAI
vector_db = services.vector_db       # ChromaDB or Supabase
cache = services.cache               # In-Memory or Redis
```

### Configuration Hierarchy

The configuration system auto-configures based on `EXECUTION_MODE`:

```
┌─────────────────────────────────────┐
│  EXECUTION_MODE (single switch)     │
│  ├─ dev  → Auto-configure for local │
│  └─ cloud → Auto-configure for cloud│
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Auto-Configuration                 │
│  ├─ LLM Provider                    │
│  ├─ Embedding Provider              │
│  ├─ Vector DB Provider              │
│  ├─ Cache Provider                  │
│  ├─ Feature Flags                   │
│  └─ Security Settings               │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Service Manager (Singleton)        │
│  ├─ LLM Service                     │
│  ├─ Embedding Service               │
│  ├─ Vector DB Service               │
│  └─ Cache Service                   │
└─────────────────────────────────────┘
```

---

## Service Mapping

### LLM Services

| Mode  | Provider | Model | Cost | Tokens |
|-------|----------|-------|------|--------|
| Dev   | Ollama   | Mistral (default) | Free | Unlimited |
| Cloud | OpenAI   | GPT-4-Turbo | ~$0.0003/1K tokens | Limited (budget) |

### Embedding Services

| Mode  | Provider | Model | Dimension | Cost |
|-------|----------|-------|-----------|------|
| Dev   | Ollama   | nomic-embed-text | 768 | Free |
| Cloud | OpenAI   | text-embedding-ada-002 | 1536 | ~$0.0001/1K tokens |

### Vector Databases

| Mode  | Provider | Storage | Scaling | Setup |
|-------|----------|---------|---------|-------|
| Dev   | ChromaDB | Local Files | Manual | Simple |
| Cloud | Supabase | PostgreSQL + pgvector | Automatic | Managed |

### Cache

| Mode  | Provider | Storage | Persistence | Speed |
|-------|----------|---------|-------------|-------|
| Dev   | In-Memory | RAM | No (per process) | Very Fast |
| Cloud | Redis | Redis Server | Yes | Fast |

---

## Configuration Properties

### Access in Code

```python
from app.core.config import settings

# Check current mode
if settings.is_dev_mode:
    print("Running in dev mode")

if settings.is_cloud_mode:
    print("Running in cloud mode")

# Check service providers
if settings.is_using_ollama:
    print("Using Ollama for LLM")

if settings.is_using_openai:
    print("Using OpenAI for LLM")

# Check cache type
if settings.is_in_memory_cache:
    print("Using in-memory cache")

if settings.is_redis_cache:
    print("Using Redis cache")

# Get service configurations
llm_config = settings.get_llm_config()
vector_db_config = settings.get_vector_db_config()
cache_config = settings.get_cache_config()
db_config = settings.get_database_config()
```

---

## API Endpoints

### Configuration Info (Debug Mode)

```bash
GET /api/v1/config
```

Returns current execution mode and all service configurations.

**Response:**
```json
{
  "execution_mode": "dev",
  "environment": "local",
  "debug": true,
  "services": {
    "llm": {
      "provider": "ollama",
      "model": "mistral"
    },
    "embeddings": {
      "provider": "ollama",
      "model": "nomic-embed-text"
    },
    "vector_db": {
      "provider": "chromadb"
    },
    "cache": {
      "provider": "in_memory"
    }
  },
  "features": {
    "payments_enabled": false,
    "agents_enabled": true
  }
}
```

### Health Checks

```bash
GET /health       # Overall health
GET /health/db    # Database health
GET /health/redis # Redis health (cloud mode only)
```

---

## Environment Variables

### Master Switch

```env
# Single variable controls everything
EXECUTION_MODE=dev|cloud
```

### LLM Configuration

**Ollama (Dev Mode):**
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

**OpenAI (Cloud Mode):**
```env
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=...
OPENAI_MODEL=gpt-4-turbo
OPENAI_FAST_MODEL=gpt-4-turbo
```

### Vector Database Configuration

**ChromaDB (Dev Mode):**
```env
CHROMADB_PATH=./chromadb_data
```

**Supabase (Cloud Mode):**
```env
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
```

### Cache Configuration

**In-Memory (Dev Mode):**
```env
CACHE_PROVIDER=in_memory
```

**Redis (Cloud Mode):**
```env
CACHE_PROVIDER=redis
REDIS_URL=redis://...
```

---

## Migration Workflow

### From Local to Cloud

1. **Export your data from ChromaDB**
   ```python
   from app.core.service_factories import services

   # Get all documents
   results = await services.vector_db.search(...)
   ```

2. **Switch environment**
   ```bash
   cp .env.cloud .env
   ```

3. **Configure cloud credentials**
   ```env
   OPENAI_API_KEY=sk-...
   SUPABASE_URL=https://...
   SUPABASE_SERVICE_KEY=...
   REDIS_URL=redis://...
   ```

4. **Import data to Supabase**
   ```python
   # App automatically uses Supabase vector DB
   await services.vector_db.add_documents(...)
   ```

5. **Restart app**
   ```bash
   uvicorn app.main:app
   ```

### From Cloud to Local

1. **Export data from Supabase**
   ```python
   await services.vector_db.search(...)
   ```

2. **Switch environment**
   ```bash
   cp .env.dev .env
   ```

3. **Ensure local services running**
   ```bash
   ollama serve  # In another terminal
   ```

4. **Import to ChromaDB**
   ```python
   await services.vector_db.add_documents(...)
   ```

5. **Restart app**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## Agents and Tools

### Mode-Aware Agent Development

Agents automatically adapt to the execution mode:

```python
from app.core.service_factories import services

class MyAgent:
    async def run(self):
        # Services automatically use correct provider
        embedding = await services.embeddings.embed_text("query")
        response = await services.llm.generate("prompt")
        results = await services.vector_db.search(embedding)
        cached = await services.cache.get("key")
```

### Tool Development

Tools also benefit from auto-configuration:

```python
from app.core.service_factories import services
from app.core.config import settings

class ResearchTool:
    async def search(self, query: str):
        if settings.is_cloud_mode:
            # Use Perplexity API for cloud
            results = await self.perplexity_search(query)
        else:
            # Use local search for dev
            results = await self.local_search(query)

        return results
```

---

## Monitoring and Logging

### Configuration Logging

On startup, the app logs its configuration:

```
================================================================================
RaptorFlow Configuration - DEV MODE
================================================================================
Execution Mode:    dev
Environment:       local
Debug:             True

── LLM Configuration
Provider:          ollama
Model:             mistral

── Embedding Configuration
Provider:          ollama
Model:             nomic-embed-text

── Vector Database Configuration
Provider:          chromadb

── Cache Configuration
Provider:          in_memory

── Database Configuration
Type:              PostgreSQL
Pool Size:         20

── Security
CORS Enabled:      True
Log Level:         DEBUG

── Feature Flags
Payments Enabled:  False
Agents Enabled:    True
================================================================================
```

### Service Health Monitoring

Check service health via logging:

```python
from app.core.config import settings

logger.info(
    "services_ready",
    llm_provider=settings.LLM_PROVIDER.value,
    embedding_provider=settings.EMBEDDING_PROVIDER.value,
    vector_db_provider=settings.VECTOR_DB_PROVIDER.value,
    cache_provider=settings.CACHE_PROVIDER.value,
)
```

---

## Troubleshooting

### Dev Mode Issues

**Ollama Connection Error**
```
Error: ConnectionRefusedError: [Errno 111] Connection refused
```
- Ensure Ollama is running: `ollama serve`
- Check URL: `OLLAMA_BASE_URL=http://localhost:11434`

**ChromaDB Path Error**
```
Error: No such file or directory
```
- Create the directory: `mkdir -p chromadb_data`
- Ensure write permissions: `chmod 755 chromadb_data`

### Cloud Mode Issues

**OpenAI API Key Error**
```
Error: Invalid API key
```
- Verify key: `echo $OPENAI_API_KEY`
- Check format: Should start with `sk-`
- Test connectivity: `openai api models.list`

**Supabase Connection Error**
```
Error: Connection timed out
```
- Verify URL format: `https://[project].supabase.co`
- Check service key permissions (should have database access)
- Test SQL connection: `psql <DATABASE_URL>`

**Redis Connection Error**
```
Error: ConnectionRefusedError
```
- Ensure Redis is running or accessible
- Check URL format: `redis://host:port/db`
- Test connection: `redis-cli ping`

---

## Production Deployment

### Cloud Mode Best Practices

1. **Use environment variable files**
   ```bash
   export $(cat .env.cloud | xargs)
   ```

2. **Enable production logging**
   ```env
   LOG_LEVEL=INFO
   DEBUG=false
   SENTRY_DSN=https://...
   ```

3. **Set up budget alerts**
   ```env
   MONTHLY_BUDGET_CENTS=1500
   DAILY_BUDGET_CENTS=50
   ```

4. **Use secret management**
   - Google Cloud Secret Manager
   - AWS Secrets Manager
   - Supabase Vault

5. **Monitor performance**
   - Set up Sentry error tracking
   - Enable structured logging
   - Use database query monitoring

---

## Summary

| Aspect | Dev Mode | Cloud Mode |
|--------|----------|-----------|
| **Setup Time** | 5 minutes | 30 minutes |
| **Cost** | Free | ~$15-30/month |
| **LLM** | Ollama (unlimited) | OpenAI (budget-controlled) |
| **Database** | Local PostgreSQL | Supabase |
| **Cache** | In-Memory | Redis |
| **Best For** | Development, Testing | Production, Scaling |
| **Switching** | Change `EXECUTION_MODE=dev` | Change `EXECUTION_MODE=cloud` |

---

## Support

For issues or questions:
1. Check this guide
2. Review configuration files (`.env.dev`, `.env.cloud`)
3. Check logs: `tail -f app.log`
4. Verify service connectivity: `GET /api/v1/config`

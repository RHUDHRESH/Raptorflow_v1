# RaptorFlow Dev/Cloud Mode Implementation Summary

## What Was Done

I've completely refactored your RaptorFlow application to support **Dev Mode** (local) and **Cloud Mode** (cloud services) with a **single configuration file**. Here's what's been implemented:

### 1. ✅ Master Configuration System (backend/app/core/config.py)

**Key Features:**
- **Single Master Switch**: `EXECUTION_MODE=dev|cloud`
- **Auto-Configuration**: Automatically configures all services based on the mode
- **Environment-Specific Defaults**: Different defaults for dev vs cloud
- **Validation**: Ensures required credentials are present for each mode
- **Helper Properties**: Easy mode checking (`is_dev_mode`, `is_cloud_mode`, etc.)

**What Gets Auto-Configured:**
```
EXECUTION_MODE=dev  →  Ollama + ChromaDB + In-Memory Cache + Local PostgreSQL
EXECUTION_MODE=cloud  →  OpenAI + Supabase + Redis + Payments
```

### 2. ✅ Service Factory Pattern (backend/app/core/service_factories.py)

**Services Implemented:**
- **LLM Services**: OllamaLLMService (dev) & OpenAILLMService (cloud)
- **Embedding Services**: OllamaEmbeddingService (dev) & OpenAIEmbeddingService (cloud)
- **Vector Database Services**: ChromaDBVectorService (dev) & SupabaseVectorService (cloud)
- **Cache Services**: InMemoryCacheService (dev) & RedisCacheService (cloud)

**Usage in Code:**
```python
from app.core.service_factories import services

llm_response = await services.llm.generate(prompt)
embedding = await services.embeddings.embed_text(text)
results = await services.vector_db.search(embedding)
cached_value = await services.cache.get("key")
```

### 3. ✅ Mode-Aware Database Layer (backend/app/db/session.py)

- Dev mode: Simple PostgreSQL setup
- Cloud mode: Optimized for Supabase serverless
- Auto-initialization & cleanup

### 4. ✅ Enhanced Main Application (backend/app/main.py)

- Mode-aware service initialization
- Service health checks based on mode
- Configuration logging on startup
- New `/api/v1/config` endpoint for monitoring

### 5. ✅ Environment Configuration Files

**`.env.dev`** - Development Mode Template
**`.env.cloud`** - Cloud Mode Template

### 6. ✅ Comprehensive Documentation

**`MODE_SWITCHING_GUIDE.md`** - Complete user guide
- Quick start for both modes
- Architecture explanation
- Service mapping
- Troubleshooting

---

## Architecture

```
EXECUTION_MODE (single switch)
    ↓
Configuration System (auto-configure)
    ↓
Service Factory (create correct implementations)
    ↓
Dev Mode                        Cloud Mode
- Ollama LLM                   - OpenAI LLM
- Ollama Embeddings            - OpenAI Embeddings
- ChromaDB                      - Supabase pgvector
- In-Memory Cache              - Redis Cache
```

---

## Quick Start

### Dev Mode
```bash
cp .env.dev .env
ollama serve &  # In another terminal
python -m uvicorn app.main:app --reload
```

### Cloud Mode
```bash
cp .env.cloud .env
# Set your OpenAI and Supabase credentials
python -m uvicorn app.main:app
```

---

## Files Created/Modified

### Created:
- ✅ `backend/app/core/service_factories.py` - Service factory pattern
- ✅ `.env.dev` - Dev mode configuration template
- ✅ `.env.cloud` - Cloud mode configuration template
- ✅ `MODE_SWITCHING_GUIDE.md` - Complete user guide

### Modified:
- ✅ `backend/app/core/config.py` - Master configuration system
- ✅ `backend/app/db/session.py` - Mode-aware database layer
- ✅ `backend/app/main.py` - Mode-aware initialization & endpoints

---

## Next Steps for Integration

### 1. Update Agents
```python
# All agents should use service factories instead of hardcoded providers
from app.core.service_factories import services

class ResearchAgent:
    async def run(self):
        response = await services.llm.generate(prompt)
        embedding = await services.embeddings.embed_text(response)
```

### 2. Update Tools
```python
# Tools should check mode for mode-specific implementations
from app.core.config import settings

class ResearchTool:
    async def search(self, query: str):
        if settings.is_cloud_mode:
            # Use Perplexity API
        else:
            # Use local search
```

### 3. Update Middleware
```python
# Budget controller and other middleware should be mode-aware
if settings.is_cloud_mode:
    await self.check_budget()
```

---

## Key Configuration Properties

```python
from app.core.config import settings

# Mode checks
settings.is_dev_mode           # True if dev mode
settings.is_cloud_mode         # True if cloud mode

# Provider checks
settings.is_using_ollama       # Using Ollama for LLM
settings.is_using_openai       # Using OpenAI for LLM
settings.is_in_memory_cache    # Using in-memory cache
settings.is_redis_cache        # Using Redis cache

# Get configurations
settings.get_llm_config()      # LLM-specific config
settings.get_vector_db_config() # Vector DB config
settings.get_cache_config()    # Cache config
settings.get_database_config() # Database config
```

---

## Environment Variables

### Essential Variables

**Dev Mode:**
```env
EXECUTION_MODE=dev
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/raptorflow
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

**Cloud Mode:**
```env
EXECUTION_MODE=cloud
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://...@supabase.co:5432/postgres
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
REDIS_URL=redis://...
```

See `.env.dev` and `.env.cloud` for complete options.

---

## Verification

### Check Configuration
```bash
curl http://localhost:8000/api/v1/config
```

### Check Database Connection
```bash
curl http://localhost:8000/health/db
```

### Check Cache (Cloud Mode)
```bash
curl http://localhost:8000/health/redis
```

---

## What Still Needs To Be Done

1. **Update all agents** to use `services` from service factories
2. **Update all tools** to be mode-aware
3. **Update middleware** for mode-specific logic
4. **Write integration tests** for both modes
5. **Update API documentation** with mode examples
6. **Test end-to-end** in both dev and cloud modes

The core refactoring is complete and ready for agent/tool integration!

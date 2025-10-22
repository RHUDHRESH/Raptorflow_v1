"""
Guide for refactoring existing agents and tools to support Dev/Cloud modes.
"""

# Agent & Tool Refactoring Guide

## Overview

This guide shows how to refactor your existing agents and tools to use the new mode-aware service factory pattern.

**Key Principle**: Use `services` from `service_factories.py` instead of directly initializing providers.

---

## Pattern 1: Basic Agent Refactoring

### Before (Hardcoded OpenAI)

```python
# backend/agents/research.py
from openai import AsyncOpenAI
from app.core.config import settings

class ResearchAgent:
    def __init__(self):
        self.llm_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo"

    async def generate_research(self, topic: str) -> str:
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"Research: {topic}"}],
            max_tokens=2000,
        )
        return response.choices[0].message.content
```

### After (Mode-Aware)

```python
# backend/agents/research.py
from app.core.service_factories import services

class ResearchAgent:
    async def generate_research(self, topic: str) -> str:
        # Automatically uses Ollama (dev) or OpenAI (cloud)
        response = await services.llm.generate(
            f"Research: {topic}",
            max_tokens=2000
        )
        return response
```

**Changes:**
- Removed hardcoded OpenAI client
- Removed explicit model selection
- Uses `services.llm` which automatically adapts
- Cleaner, simpler code

---

## Pattern 2: Agent with Embeddings

### Before

```python
class PositioningAgent:
    def __init__(self):
        from openai import AsyncOpenAI
        self.llm = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def process(self, content: str):
        # Generate embeddings
        response = await self.embedding_client.embeddings.create(
            model="text-embedding-ada-002",
            input=content
        )
        embedding = response.data[0].embedding

        # Generate text
        llm_response = await self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": content}]
        )
        return llm_response.choices[0].message.content
```

### After

```python
from app.core.service_factories import services

class PositioningAgent:
    async def process(self, content: str):
        # Get embeddings - automatically Ollama (dev) or OpenAI (cloud)
        embedding = await services.embeddings.embed_text(content)

        # Generate text - automatically Ollama (dev) or OpenAI (cloud)
        response = await services.llm.generate(content)

        return response
```

---

## Pattern 3: Agent with Vector Database

### Before

```python
from app.utils.supabase_client import supabase_client
from app.core.service_factories import services

class ICPAgent:
    def __init__(self):
        self.supabase = supabase_client

    async def store_icp(self, icp_data: dict):
        # Store in Supabase
        response = await self.supabase.table("icps").insert({
            "data": icp_data,
            "embedding": await self.get_embedding(icp_data)
        }).execute()
        return response
```

### After

```python
from app.core.service_factories import services

class ICPAgent:
    async def store_icp(self, icp_data: dict):
        # Serialize data
        icp_text = str(icp_data)

        # Get embedding - automatically Ollama (dev) or OpenAI (cloud)
        embedding = await services.embeddings.embed_text(icp_text)

        # Store in vector DB - automatically ChromaDB (dev) or Supabase (cloud)
        await services.vector_db.add_documents(
            documents=[icp_text],
            embeddings=[embedding],
            metadatas=[{"type": "icp", **icp_data}]
        )
```

---

## Pattern 4: Mode-Aware Tools

### Before (Only Works with Perplexity - Cloud)

```python
# backend/tools/research_tools.py
import requests
from app.core.config import settings

class PerplexitySearchTool:
    async def search(self, query: str) -> list[str]:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}"},
            json={
                "model": "pplx-7b-online",
                "messages": [{"role": "user", "content": query}]
            }
        )
        return [response.json()["choices"][0]["message"]["content"]]
```

### After (Works in Both Modes)

```python
# backend/tools/research_tools.py
from app.core.config import settings
from app.core.service_factories import services

class ResearchTool:
    async def search(self, query: str) -> list[str]:
        if settings.is_cloud_mode and settings.PERPLEXITY_API_KEY:
            # Cloud: Use real-time Perplexity API
            results = await self._perplexity_search(query)
        else:
            # Dev: Use local search with LLM
            results = await self._local_search(query)

        return results

    async def _perplexity_search(self, query: str) -> list[str]:
        """Cloud-only: Real-time Perplexity API search"""
        import requests
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}"},
            json={
                "model": "pplx-7b-online",
                "messages": [{"role": "user", "content": query}]
            }
        )
        return [response.json()["choices"][0]["message"]["content"]]

    async def _local_search(self, query: str) -> list[str]:
        """Dev: Use local LLM for search simulation"""
        # Get results from local LLM
        response = await services.llm.generate(
            f"Search and summarize information about: {query}",
            max_tokens=500
        )
        return [response]
```

---

## Pattern 5: Tool with Caching

### Before

```python
from app.core.redis import redis_client

class AnalyticsTool:
    async def get_metrics(self, project_id: str):
        # Try Redis
        cached = await redis_client.get(f"metrics:{project_id}")
        if cached:
            return cached

        # Compute metrics
        metrics = await self.compute_metrics(project_id)

        # Store in Redis
        await redis_client.set(
            f"metrics:{project_id}",
            metrics,
            ex=3600
        )
        return metrics
```

### After (Works with In-Memory in Dev, Redis in Cloud)

```python
from app.core.service_factories import services

class AnalyticsTool:
    async def get_metrics(self, project_id: str):
        cache_key = f"metrics:{project_id}"

        # Try cache - automatically in-memory (dev) or Redis (cloud)
        cached = await services.cache.get(cache_key)
        if cached:
            return cached

        # Compute metrics
        metrics = await self.compute_metrics(project_id)

        # Store in cache - automatically in-memory (dev) or Redis (cloud)
        await services.cache.set(cache_key, metrics, ttl=3600)

        return metrics
```

---

## Pattern 6: Orchestrator with Mode Awareness

### Before

```python
class OrchestratorV2:
    def __init__(self):
        self.llm = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.supabase = supabase_client

    async def route(self, state):
        # Cost calculation (only makes sense for OpenAI)
        if self.is_expensive_operation(state):
            # ... cost checking logic
            pass

        # Route to appropriate agent
        agent = self.select_agent(state)
        result = await agent.run(state)

        # Store result
        await self.supabase.table("results").insert(result).execute()
```

### After

```python
from app.core.config import settings
from app.core.service_factories import services

class OrchestratorV2:
    async def route(self, state):
        # Mode-aware cost checking
        if settings.is_cloud_mode:
            if self.is_expensive_operation(state):
                # Check budget
                available_budget = await self.check_budget()
                if available_budget < self.estimate_cost(state):
                    return {"error": "Insufficient budget"}

        # Select and run agent (agent uses services automatically)
        agent = self.select_agent(state)
        result = await agent.run(state)

        # Store result in appropriate database
        # (automatically ChromaDB in dev, Supabase in cloud via services)
        await services.vector_db.add_documents(
            documents=[str(result)],
            embeddings=[await services.embeddings.embed_text(str(result))],
            metadatas=[{"type": "result", **result}]
        )

        return result
```

---

## Pattern 7: Budget Control (Cloud Mode Only)

### Before

```python
class BaseAgent:
    async def check_budget_before_call(self):
        from middleware.budget_controller import budget_controller
        can_make_call = await budget_controller.can_make_request()
        if not can_make_call:
            raise BudgetExceededError("Monthly budget exceeded")

    async def run(self, prompt: str):
        await self.check_budget_before_call()
        # ... rest of agent logic
```

### After

```python
from app.core.config import settings

class BaseAgent:
    async def run(self, prompt: str):
        # Budget check only in cloud mode
        if settings.is_cloud_mode:
            from app.middleware.budget_controller import budget_controller
            can_make_call = await budget_controller.can_make_request()
            if not can_make_call:
                raise BudgetExceededError("Monthly budget exceeded")

        # Run agent logic using services
        response = await services.llm.generate(prompt)
        return response
```

---

## Pattern 8: Multi-Provider Fallback

### Before

```python
class FallbackAgent:
    async def run(self, prompt: str):
        try:
            # Try OpenAI
            from openai import AsyncOpenAI
            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception:
            # Fallback to GPT-3.5
            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
```

### After

```python
from app.core.config import settings
from app.core.service_factories import services

class FallbackAgent:
    async def run(self, prompt: str):
        try:
            # Try primary model
            response = await services.llm.generate(prompt)
            return response
        except Exception as e:
            # Log error
            logger.error(f"Primary LLM failed: {e}")

            # In cloud mode: might want to try different model
            if settings.is_cloud_mode:
                # Could create OpenAILLMService with different model
                # But for now, services.llm handles model selection
                raise

            # Dev mode: Ollama will fallback internally
            raise
```

---

## Refactoring Checklist

For each agent/tool, check off:

### Agent Refactoring

- [ ] Remove hardcoded OpenAI client imports
- [ ] Remove hardcoded model names
- [ ] Replace with `services.llm.generate()`
- [ ] Replace embedding calls with `services.embeddings.embed_text()`
- [ ] Replace vector DB calls with `services.vector_db.*`
- [ ] Replace cache calls with `services.cache.*`
- [ ] Add mode checks where needed (Perplexity, budget, etc.)
- [ ] Test in both dev and cloud modes

### Tool Refactoring

- [ ] Remove provider-specific imports
- [ ] Add mode checking for cloud-only tools
- [ ] Implement dev-mode fallback
- [ ] Replace with services where applicable
- [ ] Update documentation with mode info

---

## Quick Reference: Service Methods

### LLM Service

```python
from app.core.service_factories import services

# Generate text
response = await services.llm.generate(prompt, max_tokens=2000)

# Stream text (cloud mode)
async for chunk in services.llm.generate_streaming(prompt):
    print(chunk)

# Count tokens (for budget tracking)
token_count = await services.llm.count_tokens(text)
```

### Embedding Service

```python
# Embed single text
embedding = await services.embeddings.embed_text("text")

# Embed multiple texts
embeddings = await services.embeddings.embed_texts(["text1", "text2"])
```

### Vector DB Service

```python
# Add documents
await services.vector_db.add_documents(
    documents=["doc1", "doc2"],
    embeddings=[[...], [...]],
    metadatas=[{"type": "type1"}, {"type": "type2"}],
    ids=["id1", "id2"]
)

# Search
results = await services.vector_db.search(
    query_embedding=[...],
    top_k=5,
    filters={"type": "type1"}
)

# Delete
await services.vector_db.delete(["id1", "id2"])
```

### Cache Service

```python
# Get
value = await services.cache.get("key")

# Set
await services.cache.set("key", "value", ttl=3600)

# Delete
await services.cache.delete("key")

# Clear all
await services.cache.clear()
```

---

## Testing Mode-Aware Code

### Test Utilities

```python
# conftest.py
import pytest
from app.core.config import settings, ExecutionMode

@pytest.fixture
def dev_mode(monkeypatch):
    """Force dev mode for tests"""
    monkeypatch.setenv("EXECUTION_MODE", "dev")

@pytest.fixture
def cloud_mode(monkeypatch):
    """Force cloud mode for tests"""
    monkeypatch.setenv("EXECUTION_MODE", "cloud")

@pytest.fixture
def mock_services(mocker):
    """Mock services for testing"""
    from app.core.service_factories import services
    mocker.patch.object(services, 'llm')
    mocker.patch.object(services, 'embeddings')
    mocker.patch.object(services, 'vector_db')
    mocker.patch.object(services, 'cache')
    return services
```

### Test Examples

```python
@pytest.mark.asyncio
async def test_agent_dev_mode(dev_mode):
    from agents.research import ResearchAgent
    agent = ResearchAgent()
    result = await agent.generate_research("topic")
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_agent_cloud_mode(cloud_mode):
    from agents.research import ResearchAgent
    agent = ResearchAgent()
    result = await agent.generate_research("topic")
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_tool_mode_aware(monkeypatch):
    from tools.research_tools import ResearchTool
    tool = ResearchTool()

    # Test dev mode
    monkeypatch.setenv("EXECUTION_MODE", "dev")
    result = await tool.search("query")
    assert isinstance(result, list)

    # Test cloud mode
    monkeypatch.setenv("EXECUTION_MODE", "cloud")
    result = await tool.search("query")
    assert isinstance(result, list)
```

---

## Common Mistakes to Avoid

❌ **Don't** hardcode provider names:
```python
# WRONG
model_name = "gpt-4-turbo"
llm = OpenAI()
```

✅ **Do** use services:
```python
# RIGHT
response = await services.llm.generate(prompt)
```

---

❌ **Don't** import specific clients:
```python
# WRONG
from openai import AsyncOpenAI
from supabase import create_client
```

✅ **Do** import services:
```python
# RIGHT
from app.core.service_factories import services
```

---

❌ **Don't** hardcode API keys:
```python
# WRONG
client = OpenAI(api_key=settings.OPENAI_API_KEY)
```

✅ **Do** let services handle it:
```python
# RIGHT
response = await services.llm.generate(prompt)
```

---

## Refactoring Order

1. **Start with base classes**
   - `BaseAgent` → Use services
   - `BaseTool` → Use services

2. **Refactor core agents** (most used first)
   - Research agent
   - Positioning agent
   - ICP agent

3. **Refactor specialized agents**
   - Strategy agent
   - Content agent
   - Analytics agent

4. **Refactor tools** (by dependency)
   - Research tools
   - Content tools
   - Analytics tools

5. **Refactor middleware**
   - Budget controller
   - Rate limiter
   - Subscription middleware

6. **Test and deploy**

---

## Summary

The refactoring pattern is simple:

1. **Remove** provider-specific imports and clients
2. **Replace** with `services.llm`, `services.embeddings`, etc.
3. **Add** mode checks where needed (Perplexity, budget, etc.)
4. **Test** in both dev and cloud modes

This makes your code:
- ✅ Cleaner and simpler
- ✅ Mode-agnostic
- ✅ Easier to test
- ✅ More maintainable

Happy refactoring!

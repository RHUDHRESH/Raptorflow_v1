# RaptorFlow LLM Architecture: Complete Technical Reference

**Last Updated:** 2025-10-25
**Status:** Production-Ready with Extended Thinking Support
**Scope:** LLM Models, Embeddings, RAG Pipeline, Extended Thinking Capabilities

---

## Table of Contents

1. [Current LLM Architecture](#current-llm-architecture)
2. [Embedding System](#embedding-system)
3. [RAG Pipeline (Retrieval-Augmented Generation)](#rag-pipeline)
4. [Model/Embedding Mixing](#modelembedding-mixing)
5. [Extended Thinking Capabilities](#extended-thinking-capabilities)
6. [Cloud-Only Architecture](#cloud-only-architecture)
7. [Complete Configuration](#complete-configuration)

---

## Current LLM Architecture

### Service Manager (backend/core/service_factories.py)

The backend uses a **centralized ServiceManager** (singleton pattern) for all LLM and embedding initialization.

```python
ServiceManager
├─ .llm (LLM instance - lazy loaded)
│  ├─ Primary: OpenAI API (gpt-4-turbo)
│  ├─ Fallback: Google Gemini (gemini-2.0-flash)
│  └─ Dev Mode: Ollama (mistral)
│
└─ .embeddings (Embedding instance - lazy loaded)
   ├─ Primary: OpenAI Embeddings (text-embedding-3-small)
   ├─ Fallback: Google Embeddings
   └─ Last Resort: HuggingFace (all-MiniLM-L6-v2)
```

### LLM Selection Logic (Priority Order)

```
┌─ Check OPENAI_API_KEY
│  ├─ If set: Use ChatOpenAI (gpt-4-turbo)
│  │  Config: temperature=0.7, max_tokens=2000
│  └─ Return
│
└─ Check GEMINI_API_KEY
   ├─ If set: Use ChatGoogleGenerativeAI (gemini-2.0-flash)
   │  Config: temperature=0.7, max_tokens=2000
   └─ Return

   └─ If APP_MODE == "dev"
      ├─ Try Ollama (mistral)
      └─ Return

      └─ Else: RAISE RuntimeError
```

**Current Configuration (service_factories.py:44-82):**

```python
@staticmethod
def _init_llm():
    """Initialize the primary LLM based on configured providers"""
    app_mode = os.getenv("APP_MODE", "dev").lower()

    # Priority 1: OpenAI (if key present)
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_key:
        return ChatOpenAI(
            model="gpt-4-turbo",
            api_key=openai_key,
            temperature=0.7,
            max_tokens=2000
        )

    # Priority 2: Gemini (if key present)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=gemini_key,
            temperature=0.7
        )

    # Priority 3: Ollama (dev mode only)
    if app_mode == "dev":
        from langchain_ollama import OllamaLLM
        return OllamaLLM(model="mistral")

    raise RuntimeError("No LLM provider configured...")
```

---

## Embedding System

### Current Embedding Architecture

The backend uses **OpenAI embeddings** as primary with fallback chain:

```
┌─ OpenAI Embeddings (PRIMARY)
│  Model: text-embedding-3-small
│  Dimensions: 1536
│  Cost: $0.02 per 1M tokens
│  Speed: ~100ms per batch
│
└─ Google Embeddings (FALLBACK 1)
   Model: embedding-gecko-001
   Dimensions: 768
   Cost: ~$0.0001 per 1K tokens
   Speed: Variable

   └─ HuggingFace Embeddings (FALLBACK 2)
      Model: all-MiniLM-L6-v2
      Dimensions: 384
      Cost: FREE (local)
      Speed: ~10ms (local CPU)
```

### Embedding Service (backend/utils/embedding_service.py)

**Key Class: EmbeddingService**

```python
class EmbeddingService:
    """Manages vector embeddings for semantic search"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
```

**Key Methods:**

```python
async def generate_embedding(
    text: str,
    model: Optional[str] = None,
) -> Optional[EmbeddingResult]:
    """
    Generate embedding using OpenAI API
    Returns: EmbeddingResult(text, embedding, model, tokens)
    """

async def store_embedding(
    message_id: str,
    conversation_id: str,
    embedding: List[float],
    model: str = "text-embedding-3-small",
) -> bool:
    """Store embedding in pgvector (Supabase)"""

async def semantic_search(
    query: str,
    conversation_id: str,
    limit: int = 5,
    threshold: float = 0.6,
) -> List[SearchResult]:
    """Find similar messages via cosine similarity"""
```

### Vector Storage (pgvector in Supabase)

**Tables:**
```sql
message_embeddings
├─ message_id (UUID)
├─ conversation_id (UUID)
├─ embedding (VECTOR(1536)) ← pgvector type
├─ embedding_model (VARCHAR)
└─ created_at (TIMESTAMP)

conversations
├─ id (UUID)
├─ business_id (UUID)
├─ user_id (UUID)
└─ ...

messages
├─ id (UUID)
├─ conversation_id (UUID)
├─ content (TEXT)
├─ role (VARCHAR)
├─ embedding (VECTOR(1536)) ← Optional denormalization
└─ created_at (TIMESTAMP)
```

---

## RAG Pipeline

### RAG Overview

The **Retrieval-Augmented Generation (RAG) Pipeline** enhances LLM responses with context from previous conversations and external knowledge bases.

**Location:** `backend/utils/rag_pipeline.py`

**Flow:**
```
User Query
    ↓
┌─ Retrieve Context ──────────────────────┐
│  ├─ Recent Messages (last 5)            │
│  ├─ Semantic Search (top 3 similar)     │
│  └─ Conversation Metadata               │
└──────────────────────────────────────────┘
    ↓
┌─ Augment Prompt ────────────────────────┐
│  ├─ Insert Retrieved Context            │
│  ├─ Format as System Message            │
│  └─ Calculate Context Tokens            │
└──────────────────────────────────────────┘
    ↓
LLM Inference
    ↓
Store Embedding of Response
    ↓
Return to User
```

### RAGPipeline Class

```python
class RAGPipeline:
    """Retrieval-Augmented Generation pipeline"""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.conversation_manager = get_conversation_manager()
        self.max_context_tokens = 2000
        self.recent_messages_window = 5
```

### Retrieve Context (Step 1)

```python
async def retrieve_context(
    query: str,
    conversation_id: str,
    include_recent: bool = True,
    include_semantic: bool = True,
    semantic_limit: int = 3,
    semantic_threshold: float = 0.6,
) -> RetrievedContext:
    """
    Retrieve context for RAG

    Returns:
        RetrievedContext {
            query: str,
            similar_messages: List[SearchResult],  # Semantic search results
            recent_messages: List[Message],         # Last N messages
            conversation_metadata: Dict,
            total_tokens: int
        }
    """
```

**What Happens:**
1. Get last 5 messages from conversation (recency)
2. Embed the user query
3. Search pgvector for similar messages (semantic search)
4. Filter by similarity threshold (0.6 default)
5. Combine results into RetrievedContext

### Augment Prompt (Step 2)

```python
async def augment_prompt(
    query: str,
    context: RetrievedContext,
    augmentation_type: str = "hybrid",  # 'recent', 'semantic', 'hybrid'
) -> AugmentedPrompt:
    """
    Augment prompt with retrieved context

    Returns:
        AugmentedPrompt {
            original_query: str,
            context_summary: str,          # Formatted context
            full_prompt: str,              # Complete prompt with context
            context_sources: int,          # How many sources included
            context_tokens: int,           # Token count of context
            augmentation_type: str         # Type used
        }
    """
```

**Augmentation Types:**

```
1. Recent: Use only recent messages (conversation continuity)
2. Semantic: Use only semantic search results (relevant context)
3. Hybrid (DEFAULT): Combine both approaches
```

**Example Augmented Prompt:**
```
System: You are a helpful marketing AI assistant.

Recent Context:
- User asked about positioning options
- You provided 3 options
- User selected option #1

Semantic Context (similar to current query):
- Message: "How do we differentiate from competitors?"
- Response: "Key differentiators are speed and affordability"

User Query: "What's the next step after positioning?"

Answer: ...
```

### Generate Response

```python
async def generate_with_rag(
    query: str,
    conversation_id: str,
    system_prompt: str = "You are a helpful marketing AI...",
) -> Dict[str, Any]:
    """
    Complete RAG pipeline: retrieve → augment → generate

    Returns:
        {
            "response": "AI response text",
            "context_used": int,
            "sources": List[str],
            "tokens_used": int
        }
    """
    # Step 1: Retrieve context
    context = await self.retrieve_context(query, conversation_id)

    # Step 2: Augment prompt
    augmented = await self.augment_prompt(query, context)

    # Step 3: Generate with LLM
    response = await llm.ainvoke(augmented.full_prompt)

    # Step 4: Store response + embedding
    await embedding_service.generate_and_store(response, conversation_id)

    return response
```

---

## Model/Embedding Mixing

### Question: Can We Use Gemini Models + OpenAI Embeddings?

**Answer: YES, fully supported.**

### Current Architecture Allows

```
┌─ LLM Layer (can be any)
│  ├─ OpenAI (gpt-4-turbo)
│  ├─ Gemini (gemini-2.0-flash)
│  └─ Ollama (mistral)
│
└─ Embedding Layer (independent)
   ├─ OpenAI (text-embedding-3-small) ← Recommended
   ├─ Google (embedding-gecko-001)
   └─ HuggingFace (all-MiniLM-L6-v2)

These are COMPLETELY DECOUPLED.
```

### Why Mixing is Safe

**Embeddings are just vectors.** They don't care which LLM generates the text. As long as:
1. Vector dimension matches (1536 for OpenAI)
2. Similarity search uses same metric (cosine)
3. Both use same embedding model consistently

### Recommended Configuration: Gemini LLM + OpenAI Embeddings

```
Development:
├─ LLM: Gemini (fast, free tier)
└─ Embeddings: OpenAI (stable, proven)

Production:
├─ LLM: OpenAI GPT-4 Turbo (best quality)
└─ Embeddings: OpenAI (consistency)
```

### Implementation Example

```python
# backend/core/service_factories.py

class ServiceManager:
    @staticmethod
    def _init_llm():
        """Use Gemini for LLM"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
            )

    @staticmethod
    def _init_embeddings():
        """Always use OpenAI for embeddings"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return OpenAIEmbeddings(api_key=openai_key)
```

### Cost Comparison: Gemini LLM + OpenAI Embeddings

```
Gemini Models:
├─ Gemini 1.5 Flash: FREE (1M tokens/month)
├─ Gemini 2.0 Flash: FREE (1M tokens/month)
└─ Gemini Pro: $0.00125/1K tokens

OpenAI Embeddings:
├─ text-embedding-3-small: $0.02/1M tokens
└─ text-embedding-3-large: $0.13/1M tokens

Monthly Cost (100K API calls, avg 500 tokens/call):
├─ Gemini 1.5 Flash + OpenAI Embeddings: ~$3.00
├─ GPT-4 Turbo + OpenAI Embeddings: ~$75-150
└─ Gemini + Google Embeddings: ~$3.00
```

---

## Extended Thinking Capabilities

### What is Extended Thinking?

**Extended Thinking** = AI models that can "think" through complex problems step-by-step before answering, like a human thinking out loud.

### Available Extended Thinking Models

#### 1. **OpenAI o1 & o1-mini** (BEST FOR RAPTORFLOW)

**Model:** `o1` (reasoning), `o1-mini` (fast)

**Capabilities:**
- Multi-step reasoning
- Complex problem solving
- Mathematical proofs
- Code generation
- Scientific analysis

**Example Use Case in RaptorFlow:**
```python
# Deep positioning analysis with extended thinking
result = await llm.ainvoke(
    model="o1",  # Extended thinking enabled
    prompt="""
    Given this market data:
    - Competitors: [list]
    - Our features: [list]
    - Customer feedback: [list]

    Reason through:
    1. What is our inherent drama?
    2. Which market segments are underserved?
    3. What's our defensible moat?
    """,
    temperature=1,  # Required for reasoning models
    max_completion_tokens=8000  # Thinking token budget
)
```

**Specs:**
```
o1: 200K context, excellent reasoning, slower
├─ Input: $15/1M tokens
├─ Output: $60/1M tokens
└─ Response time: 30-60 seconds

o1-mini: 128K context, good reasoning, faster
├─ Input: $3/1M tokens
├─ Output: $12/1M tokens
└─ Response time: 5-10 seconds
```

#### 2. **Claude 3.5 Sonnet (Extended Thinking)**

**Model:** `claude-3-7-sonnet-20250219` (with extended thinking)

**Not currently in RaptorFlow** but available if we add Anthropic.

**Capabilities:** Similar to o1, built-in thinking blocks.

#### 3. **Gemini 2.0 Deep Research**

**Model:** `gemini-2.0-flash-thinking-exp-01-21`

**Currently Available** (Gemini 2.0 models in service_factories.py)

**Use Case:**
```python
# Deep research with extended thinking
result = await gemini_client.generate(
    model="gemini-2.0-flash-thinking-exp-01-21",
    prompt="Conduct deep research on market trends...",
    temperature=1
)
```

---

## Integrating Extended Thinking into RaptorFlow

### Option 1: OpenAI o1-mini for Complex Analysis

**Best for:** Positioning analysis, strategy formulation, route-back decisions

```python
# backend/agents/positioning.py - UPDATED

async def _identify_inherent_drama(self, state: PositioningState) -> PositioningState:
    """Identify inherent drama using extended thinking"""

    from langchain_openai import ChatOpenAI

    # Use o1-mini for reasoning
    reasoning_llm = ChatOpenAI(
        model="o1-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=1,  # Required for reasoning
        max_tokens=8000  # Thinking budget
    )

    prompt = f"""
    You are a positioning strategist. Think through the inherent drama in this business.

    Business: {business['name']}
    Industry: {business['industry']}
    Description: {business['description']}

    Step-by-step reasoning:
    1. What is the human truth or emotional need this product taps into?
    2. What is the natural story here?
    3. What makes this special in the market?

    Provide your thinking process first, then conclusions.
    """

    response = await reasoning_llm.ainvoke(prompt)
    state['inherent_drama'] = response.content
    return state
```

### Option 2: Multi-Agent Extended Thinking

```python
# backend/agents/analytics.py - UPDATED

async def _decide_route_back(self, state: AnalyticsState) -> AnalyticsState:
    """Decide if campaign needs repositioning using extended thinking"""

    from langchain_openai import ChatOpenAI

    # o1 for complex decision-making
    decision_llm = ChatOpenAI(
        model="o1",  # Full o1 for best reasoning
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=1,
        max_tokens=8000
    )

    prompt = f"""
    Analyze this campaign performance and decide if we need to pivot.

    Campaign: {state['campaign_name']}
    Original Goal: {state['goal']}
    Performance:
    - CTR: {state['metrics']['ctr']}
    - CVR: {state['metrics']['cvr']}
    - ROAS: {state['metrics']['roas']}
    - Positioning: {state['positioning']}

    Reasoning framework:
    1. Is the core positioning wrong?
    2. Is the execution (channel, timing) wrong?
    3. Is the target audience wrong?
    4. What evidence supports each hypothesis?
    5. What's our recommended action?

    Be thorough in your analysis.
    """

    response = await decision_llm.ainvoke(prompt)

    # Parse recommendation
    state['route_back_recommendation'] = parse_recommendation(response.content)
    return state
```

### Option 3: Hybrid Approach (Fast LLM + Thinking for Complex Tasks)

```python
# backend/core/service_factories.py - UPDATED

class ServiceManager:
    @staticmethod
    def _init_llm():
        """Initialize fast LLM"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return ChatOpenAI(
                model="gpt-4-turbo",  # Fast for most tasks
                api_key=openai_key,
                temperature=0.7
            )

    @staticmethod
    def _init_reasoning_llm():
        """Initialize extended thinking LLM"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return ChatOpenAI(
                model="o1-mini",  # Extended thinking for complex analysis
                api_key=openai_key,
                temperature=1  # Required for reasoning
            )

# Usage in agents
llm = service_manager.llm  # Fast GPT-4 for basic tasks
reasoning_llm = service_manager.get_reasoning_llm()  # o1 for complex reasoning
```

### Cost Implications

**Current Setup (GPT-4 Turbo):**
```
100K API calls, 500 tokens avg:
├─ Input tokens: 50M × $0.01/1M = $500
├─ Output tokens: 50M × $0.03/1M = $1,500
└─ Monthly: ~$2,000
```

**With Extended Thinking (Hybrid):**
```
90% fast tasks (GPT-4) + 10% complex (o1-mini):

Fast tasks (90K calls):
├─ Input: 45M × $0.01/1M = $450
├─ Output: 45M × $0.03/1M = $1,350

Complex tasks (10K calls, 8K tokens):
├─ Input: 10M × $3/1M = $30
├─ Output: 80M × $12/1M = $960

Total Monthly: ~$2,790 (39% increase)
```

---

## Cloud-Only Architecture

### Current Setup (backend/utils/cloud_provider.py)

```python
class CloudProviderService:
    """
    Unified cloud AI provider with automatic fallback.

    Modes:
    - dev: Gemini (primary) → OpenRouter (fallback)
    - prod: OpenAI GPT-5 series (primary) → OpenRouter (fallback)

    NO LOCAL MODELS. NO OFFLINE MODE.
    """
```

### Production Mode Configuration

```
APP_MODE=prod

Primary LLM:
├─ Model: gpt-5-standard (future)
├─ API Key: OPENAI_API_KEY
├─ Provider: OpenAI API

Fallback:
├─ Model: openai/gpt-5-nano (via OpenRouter)
├─ API Key: OPENROUTER_API_KEY
└─ When: OpenAI fails

Embeddings:
├─ Model: text-embedding-3-small
├─ API Key: OPENAI_API_KEY
└─ Vector DB: Supabase pgvector
```

### Development Mode Configuration

```
APP_MODE=dev

Primary LLM:
├─ Model: gemini-2.0-flash
├─ API Key: GEMINI_API_KEY
├─ Provider: Google Generative AI

Fallback:
├─ Model: openai/gpt-5-mini (via OpenRouter)
├─ API Key: OPENROUTER_API_KEY
└─ When: Gemini fails

Embeddings:
├─ Model: text-embedding-3-small
├─ API Key: OPENAI_API_KEY
└─ Vector DB: Supabase pgvector
```

### No Local Models Policy

**Stated Requirement:** Cloud-only, no Ollama, no local inference

**Why:**
1. Consistency across environments
2. Auto-scaling without infrastructure
3. Latest model updates automatically
4. No GPU management
5. Predictable costs

**Trade-off:** Requires internet, API costs, but scalability

---

## Complete Configuration

### Environment Variables Required

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...                    # OpenAI API key
GEMINI_API_KEY=AIzaSy...                 # Google Gemini API key
OPENROUTER_API_KEY=sk-or-...             # OpenRouter fallback

# App Mode
APP_MODE=prod                             # 'dev' or 'prod'

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
SUPABASE_ANON_KEY=eyJhbGc...

# Vector Search
CHROMA_HOST=localhost                     # or cloud endpoint
CHROMA_PORT=8001

# Costs
OPENAI_COST_LIMIT=1000                    # Monthly cost limit (USD)
```

### Initialization Order

```
1. ServiceManager.llm
   └─ Lazy-loads LLM on first request
   └─ Selection: OpenAI → Gemini → Ollama

2. ServiceManager.embeddings
   └─ Lazy-loads embeddings on first request
   └─ Selection: OpenAI → Google → HuggingFace

3. RAGPipeline()
   └─ Gets LLM from ServiceManager
   └─ Gets embeddings from ServiceManager
   └─ Ready for retrieval-augmented generation

4. Agents
   └─ All agents use ServiceManager singleton
   └─ Consistent LLM/embeddings across app
```

### Data Flow

```
User Input
    ↓
API Endpoint
    ↓
Middleware (security, auth, cost control)
    ↓
Orchestrator Agent
    ↓
Specialist Agent (Research, Positioning, etc.)
    ↓
Tools (multiple)
    ↓
ServiceManager.llm.ainvoke(prompt)
    ├─ Goes to OpenAI/Gemini API
    └─ Returns completion

    AND/OR

ServiceManager.embeddings.embed(text)
    ├─ Goes to OpenAI Embedding API
    └─ Returns vector

    ↓
pgvector (Supabase)
    └─ Stores embeddings

    ↓
RAG Pipeline (next request)
    └─ Retrieves similar context
    └─ Augments prompt
    └─ Sends to LLM

    ↓
Return to User
```

---

## Summary: What's Possible

| Capability | Current | Possible | Recommended |
|-----------|---------|----------|-------------|
| **LLM** | GPT-4, Gemini | + Claude, o1, o3 | Gemini (dev), GPT-4 (prod) |
| **Embeddings** | OpenAI, Google, HF | Cohere, Voyager | OpenAI (consistent) |
| **Mix LLM + Embeddings** | Yes | Yes | Gemini + OpenAI |
| **RAG** | ✅ DONE | ✅ Ready to use | Use in all agents |
| **Extended Thinking** | Not enabled | ✅ Can add o1/o1-mini | Add for positioning, analytics |
| **Vector DB** | pgvector | + Pinecone, Weaviate | pgvector (we have it) |
| **Multi-turn Chat** | ✅ DONE | ✅ Using RAG | Already implemented |
| **Semantic Search** | ✅ DONE | ✅ Conversation-wide | Working with RAG |

---

## Recommendations

### Short Term (This Week)
1. ✅ RAG is DONE - start using in all agents
2. Use Gemini + OpenAI Embeddings for cost efficiency
3. Add extended thinking to positioning agent (o1-mini)

### Medium Term (This Month)
1. Integrate o1-mini for complex strategy decisions
2. Add extended thinking to route-back logic
3. Monitor costs, adjust model selection

### Long Term (Roadmap)
1. Consider Claude if Anthropic availability improves
2. Evaluate new models as they release
3. Fine-tune models on RaptorFlow-specific tasks
4. Implement local embedding cache for speed

---

## Files to Review

- `backend/core/service_factories.py` - LLM/embedding initialization
- `backend/utils/embedding_service.py` - Embedding generation & storage
- `backend/utils/rag_pipeline.py` - RAG implementation
- `backend/utils/cloud_provider.py` - Cloud provider configuration

---

**Status:** RAG is ready. Extended thinking can be added. Model mixing is supported.

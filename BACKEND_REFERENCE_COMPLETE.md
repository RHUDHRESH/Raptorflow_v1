# RaptorFlow Backend - Complete Reference Guide

**Last Updated:** 2025-10-25
**Status:** Production-Ready (Cloud-Only Architecture)
**Total:** 19 agents + 35 tools + 6 integrations + 30+ API endpoints

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Complete Agent Map](#complete-agent-map)
3. [Complete Tool Map](#complete-tool-map)
4. [API Routes & Endpoints](#api-routes--endpoints)
5. [Integration Endpoints](#integration-endpoints)
6. [Complete Workflow](#complete-workflow)
7. [Database Schema](#database-schema)
8. [Middleware Stack](#middleware-stack)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │   FastAPI (main.py)        │
        │   - OAuth Routes           │
        │   - Conversation Routes    │
        │   - Budget Routes          │
        │   - Research Routes        │
        └────────────────────────────┘
                     │
        ┌────────────┴─────────────┐
        ↓                          ↓
   ┌─────────────┐      ┌──────────────────┐
   │ Orchestrator│      │ Specialized Agents│
   │   Agent     │      │                   │
   │ (Routes)    │      │ - Research        │
   │             │      │ - Positioning     │
   │             │      │ - ICP             │
   │             │      │ - Strategy        │
   │             │      │ - Content         │
   │             │      │ - Analytics       │
   │             │      │ - Trend Monitor   │
   └─────────────┘      │ - 12+ Specialized│
        │               └──────────────────┘
        │                    │
        ├────────────────────┴──────────────┐
        ↓                                   ↓
   ┌─────────────────┐      ┌──────────────────────────┐
   │ 35 Specialized  │      │  External Services       │
   │ Tools           │      │ - OpenAI (GPT-4 Turbo)   │
   │                 │      │ - Google Gemini          │
   │ - Research      │      │ - Perplexity Search      │
   │ - Strategy      │      │ - Exa Search            │
   │ - Content       │      │ - Chroma Vector DB       │
   │ - Analytics     │      │ - Razorpay              │
   └─────────────────┘      │ - OAuth (Google)        │
        │                   └──────────────────────────┘
        ↓
   ┌─────────────────────────────────────┐
   │        SUPABASE                      │
   │ - PostgreSQL Database               │
   │ - Auth & RLS                        │
   │ - pgvector (Embeddings)             │
   │ - Real-time subscriptions           │
   └─────────────────────────────────────┘
```

### Technology Stack

- **Framework:** FastAPI (async/await, dependency injection)
- **Agent Framework:** LangGraph (state machines, multi-agent orchestration)
- **LLMs:** OpenAI (GPT-4 Turbo), Google Generative AI (Gemini)
- **Vector DB:** Chroma (semantic search)
- **Database:** Supabase (PostgreSQL + pgvector)
- **Search:** Perplexity API, Exa Search
- **Payments:** Razorpay
- **Auth:** Google OAuth 2.0, JWT
- **Message Queue:** (Optional Redis for caching)

---

## Complete Agent Map

### 🔴 CORE AGENTS (7 Total)

These are the main business-logic agents that orchestrate the platform.

#### 1. **Orchestrator Agent** (backend/agents/orchestrator.py)
**Purpose:** Router that determines which specialist agent to call

**Responsibilities:**
- Load business context and subscription tier
- Verify feature access based on tier
- Determine which stage (research/positioning/icp/strategy/content/analytics)
- Route to appropriate specialist agent
- Handle prerequisites (do we have required data?)
- Execute route-back logic if needed
- Finalize and save results

**Key Methods:**
```
_initialize()              # Load business + tier
_check_tier_access()       # Verify tier allows feature
_determine_stage()         # Map action to stage
_check_prerequisites()     # Ensure required data exists
_route_by_stage()         # Conditional routing
_handle_route_back()      # Campaign optimization loops
_finalize()               # Save results to DB
```

**State TypedDict:**
```python
business_id: str
current_stage: str
user_input: Dict
context: Dict
route_back_needed: bool
route_back_to: str
subscription_tier: str
specialist_results: Dict
error: str
```

---

#### 2. **Research Agent** (backend/agents/research.py)
**Purpose:** Comprehensive business intelligence gathering

**Responsibilities:**
- Analyze market situation (SWOT, market size, trends)
- Research competitors and build competitor ladder
- Gather evidence (claims, proof points, testimonials)
- Validate evidence for credibility
- Link claims to Reasons-To-Believe (RTBs)
- Check completeness and iterate if needed
- Save research to database

**Workflow:**
```
analyze_situation()
    ↓
research_competitors()
    ↓
build_competitor_ladder() ← Uses CompetitorLadderTool
    ↓
gather_evidence() ← Uses PerplexitySearchTool, EvidenceDBTool
    ↓
validate_evidence() ← Checks source credibility
    ↓
link_claims_to_rtbs() ← Uses RTBLinkerTool
    ↓
check_completeness() ← Decides if loop again
    ↓
save_results() ← Supabase
```

**Key Tools Used:**
- PerplexitySearchTool (web search)
- CompetitorLadderTool
- EvidenceDBTool
- SOSTACAnalyzerTool
- RTBLinkerTool

**Outputs:**
- SOSTAC analysis (Situation, Objective, Strategy, Tactics, Actions)
- Competitor ladder (positioning map)
- Evidence database (citations, sources, credibility scores)

---

#### 3. **Positioning Agent** (backend/agents/positioning.py)
**Purpose:** Generate 3 differentiated positioning options

**Responsibilities:**
- Identify inherent drama (Leo Burnett concept)
- Generate 3 unique positioning options
- Evaluate differentiation (vs. competitors)
- Calculate sacrifices (what we won't do)
- Create visual hammers (memorable visual/verbal assets)
- Validate options against criteria
- Loop back if validation score < 75%

**Workflow:**
```
identify_inherent_drama() ← Uses PositioningKnowledgeBaseTool
    ↓
generate_positioning_options() ← LLM + positioning KB
    ↓
evaluate_differentiation() ← Uses DifferentiationAnalyzerTool
    ↓
calculate_sacrifices() ← Uses SacrificeCalculatorTool
    ↓
create_visual_hammers() ← Uses VisualHammerTool
    ↓
validate_options() → if score > 0.75: END else: loop
```

**Key Concepts:**
- **Inherent Drama:** The natural story/human truth in the product
- **Point of View (POV):** What we stand for, what we promise, how we prove it
- **Sacrifice:** What we explicitly don't do (clears confusion)
- **Visual Hammer:** One unique visual that encapsulates positioning

**Outputs:**
3 positioning options, each with:
- Inherent drama identified
- Differentiation analysis
- Sacrifices (what we won't do)
- Visual hammer concept

---

#### 4. **ICP Agent** (backend/agents/icp.py)
**Purpose:** Generate Ideal Customer Profiles (personas)

**Responsibilities:**
- Take positioning and extract target personas
- Build complete persona profiles (demographics, psychographics)
- Identify platforms where ICPs congregate
- Find content preferences
- Identify trending topics relevant to each ICP
- Tag ICPs for easy recall
- Generate embeddings for semantic search

**Workflow:**
```
extract_from_positioning()
    ↓
build_persona_profiles() ← Uses PersonaGeneratorTool
    ↓
identify_platforms() ← Uses AudienceMatchingTool
    ↓
find_content_preferences()
    ↓
generate_embeddings() ← Uses embedding service
    ↓
save_to_db()
```

**Persona Structure:**
```json
{
  "name": "Early Adopter Eva",
  "demographics": {
    "age": "28-35",
    "income": "$75k-150k",
    "location": "US Tech Hubs"
  },
  "psychographics": {
    "values": "innovation, efficiency, community",
    "behaviors": "early adopter, tech-savvy, social"
  },
  "platforms": ["Twitter", "Product Hunt", "LinkedIn"],
  "content_preferences": ["case studies", "how-to", "trends"],
  "trending_topics": ["AI adoption", "productivity", "automation"]
}
```

**Outputs:**
- 3-5 detailed personas (based on tier)
- Platform mapping for each
- Content preference profiles
- Embeddings for semantic search

---

#### 5. **Content Agent** (backend/agents/content.py)
**Purpose:** Generate content calendars and creative briefs

**Responsibilities:**
- Generate content calendar based on duration + goal
- Validate content against platform specs
- Create asset briefs for designers/creators
- Adapt messaging for multiple channels
- Save move/campaign to database

**Workflow:**
```
generate_calendar() ← Uses CalendarGeneratorTool
    ↓
validate_content() ← Uses PlatformValidatorTool
    ↓
create_asset_briefs() ← Uses AssetFactoryTool
    ↓
adapt_for_channels() ← Uses MultiChannelAdapterTool
    ↓
save_move()
```

**Calendar Output:**
```json
{
  "move_id": "uuid",
  "duration_days": 30,
  "calendar": [
    {
      "date": "2025-11-01",
      "posts": [
        {
          "platform": "LinkedIn",
          "text": "...",
          "hashtags": ["#growth"],
          "tone": "professional",
          "valid": true
        }
      ]
    }
  ]
}
```

---

#### 6. **Analytics Agent** (backend/agents/analytics.py)
**Purpose:** Measure campaign performance and optimize

**Responsibilities:**
- Analyze campaign performance metrics
- Calculate marketing effectiveness (AMEC)
- Compute Customer Lifetime Value (CLV)
- Calculate North Star metric progress
- Determine if route-back is needed
- Recommend kill/scale actions
- Save analytics to database

**Workflow:**
```
get_campaign_data()
    ↓
run_amec_analysis() ← Uses AMECEvaluatorTool
    ↓
calculate_clv() ← Uses CLVCalculatorTool
    ↓
calculate_north_star() ← Uses NorthStarCalculatorTool
    ↓
decide_route_back() ← Uses RouteBackLogicTool
    ↓
save_analysis()
```

**Key Metrics:**
- **AMEC:** Awareness, Consideration, Preference, Action, Loyalty
- **CLV:** Revenue per customer lifetime
- **North Star:** Single metric that defines success (CTR, CVR, retention, etc.)
- **Route-back:** Need to revisit positioning/messaging?

---

#### 7. **Trend Monitor Agent** (backend/agents/trend_monitor.py)
**Purpose:** Monitor market trends on schedule

**Responsibilities:**
- Run on cron schedule (daily/weekly)
- Search for trending topics in industry
- Analyze competitor announcements
- Flag emerging threats/opportunities
- Store trend data for historical tracking
- Notify users of significant shifts

**Trigger:** Cron job scheduled in backend

---

### 🟠 SUPPORTING AGENTS (12 Total)

These agents provide specialized analysis and processing.

#### 8. **AI Reasoning Engine** (backend/agents/ai_reasoning_engine.py)
**Purpose:** Complex reasoning and decision-making

**Responsibilities:**
- Take complex business questions
- Break down into sub-questions
- Reason through each step
- Synthesize conclusions
- Explain reasoning chain

---

#### 9. **Strategy Orchestrator** (backend/agents/strategy_orchestrator.py)
**Purpose:** Advanced multi-step strategy building

**Responsibilities:**
- Orchestrate complex strategy workflows
- Handle RACE framework (Reach-Act-Convert-Engage)
- Link strategy to execution
- Track dependencies between strategy elements

---

#### 10. **Content Router Agent** (backend/agents/content_router_agent.py)
**Purpose:** Route content to appropriate channels

**Responsibilities:**
- Take message + platform set
- Route to optimal channel
- Adapt tone/format per channel
- Maximize performance per platform

---

#### 11. **ICP Builder Agent** (backend/agents/icp_builder_agent.py)
**Purpose:** Deep ICP profiling

**Responsibilities:**
- Build detailed buyer personas
- Identify job-to-be-done
- Map buying journey
- Find key influencers in ICP

---

#### 12. **JTBD Extraction Agent** (backend/agents/jtbd_extraction_agent.py)
**Purpose:** Extract Jobs-to-Be-Done insights

**Responsibilities:**
- Identify functional/emotional/social jobs
- Map job outcomes
- Find competing alternatives
- Understand decision criteria

---

#### 13. **Channel Mapper Agent** (backend/agents/channel_mapper_agent.py)
**Purpose:** Map optimal marketing channels

**Responsibilities:**
- Profile each marketing channel
- Score fit with target audience
- Recommend channel mix
- Estimate reach/cost

---

#### 14. **Context Processor Agent** (backend/agents/context_processor_agent.py)
**Purpose:** Process and manage strategic context

**Responsibilities:**
- Extract context from user input
- Structure for agent consumption
- Maintain context consistency

---

#### 15. **Explanation Agent** (backend/agents/explanation_agent.py)
**Purpose:** Explain AI recommendations

**Responsibilities:**
- Take any AI output
- Generate human-readable explanations
- Cite evidence
- Explain reasoning

---

#### 16-19. **Other Specialized Agents**
- Base Agent (backend/agents/base_agent.py) - Abstract base class
- Orchestration V2 (backend/agents/orchestration_v2.py) - Updated orchestration logic
- Positioning Agent (already listed above)

---

## Complete Tool Map

### 🔧 RESEARCH & INTELLIGENCE TOOLS (5 Total)

#### 1. **PerplexitySearchTool**
**What it does:** Web search using Perplexity API
**Returns:** Structured search results with sources
**Used by:** Research Agent

#### 2. **CompetitorLadderTool**
**What it does:** Builds positioning ladder showing competitors
**Returns:** Competitor positioning map
**Output example:**
```json
{
  "competitors": [
    {"name": "Competitor A", "positioning": "...", "price": "$X"},
    {"name": "Us", "positioning": "...", "price": "$Y"},
    {"name": "Competitor B", "positioning": "...", "price": "$Z"}
  ]
}
```
**Used by:** Research Agent

#### 3. **EvidenceDBTool**
**What it does:** Stores/retrieves proof points and citations
**Operations:** add, retrieve, search, validate
**Stores:** URLs, PDFs, reviews, quotes, statistics
**Used by:** Research Agent, Content Agent

#### 4. **SOSTACAnalyzerTool**
**What it does:** Analyzes market using SOSTAC framework
**Returns:**
- **Situation:** Market analysis, trends, SWOT
- **Objective:** Goals and KPIs
- **Strategy:** Approach and positioning
- **Tactics:** Specific actions
- **Actions:** Execution details
**Used by:** Research Agent, Strategy Agent

#### 5. **RTBLinkerTool**
**What it does:** Links marketing claims to Reasons-To-Believe (proof)
**Returns:** Claim-to-proof mappings
**Example:**
```json
{
  "claim": "Fastest solution",
  "rtbs": [
    {"evidence": "48ms response time", "source": "benchmark.pdf"},
    {"evidence": "User rating 4.9/5", "source": "G2 Reviews"}
  ]
}
```
**Used by:** Research Agent

---

### 🎯 POSITIONING & STRATEGY TOOLS (8 Total)

#### 6. **PositioningKnowledgeBaseTool**
**What it does:** Stores positioning frameworks and principles
**Contains:** Leo Burnett (Inherent Drama), STP, Differentiation, etc.
**Operations:** get_principle, query_framework, list_all
**Used by:** Positioning Agent, Strategy Agent

#### 7. **DifferentiationAnalyzerTool**
**What it does:** Analyzes differentiation vs. competitors
**Returns:** Differentiation matrix with competitive gaps
**Used by:** Positioning Agent

#### 8. **SacrificeCalculatorTool**
**What it does:** Identifies what we won't do (sacrifice = clarity)
**Returns:** List of sacrifices (market segments, features, etc.)
**Used by:** Positioning Agent

#### 9. **VisualHammerTool**
**What it does:** Creates visual/verbal metaphors for positioning
**Returns:** Visual concept descriptions, metaphors, mnemonics
**Used by:** Positioning Agent

#### 10. **JTBDMapperTool**
**What it does:** Maps Jobs-To-Be-Done for product
**Returns:** Functional, emotional, social jobs + outcomes
**Used by:** Strategy Agent, ICP Agent

#### 11. **SevenPsBuilderTool**
**What it does:** Builds 7Ps marketing mix (Product, Price, Place, Promotion, People, Process, Physical)
**Returns:** Detailed 7Ps analysis
**Used by:** Strategy Agent

#### 12. **SegmentScorerTool**
**What it does:** Scores market segments for attractiveness
**Returns:** Scoring matrix for segments
**Used by:** Strategy Agent, ICP Agent

#### 13. **RACEPlannerTool**
**What it does:** Plans using RACE framework
- **Reach:** Build awareness
- **Act:** Drive consideration
- **Convert:** Close sales
- **Engage:** Build loyalty
**Returns:** RACE strategy with tactics for each stage
**Used by:** Strategy Agent

---

### 👥 AUDIENCE & CONTENT TOOLS (8 Total)

#### 14. **PersonaGeneratorTool**
**What it does:** Generates detailed buyer personas
**Returns:** Demographics, psychographics, behaviors, motivations
**Used by:** ICP Agent

#### 15. **AudienceMatchingTool**
**What it does:** Matches ICPs to platforms where they congregate
**Returns:** Platform rankings for each ICP
**Used by:** ICP Agent, Content Agent

#### 16. **SentimentToneAnalyzerTool**
**What it does:** Analyzes sentiment and tone of content
**Returns:** Sentiment score, tone classification
**Used by:** Content Agent, Quality Control

#### 17. **ToneAdjustmentTool**
**What it does:** Adjusts copy tone to match ICP preferences
**Returns:** Tone-adjusted copy
**Used by:** Content Agent

#### 18. **PlatformRecommendationTool**
**What it does:** Recommends best platforms for content
**Returns:** Platform recommendations with score
**Used by:** Content Agent

#### 19. **ContentOptimizationTool**
**What it does:** Optimizes content for platform specs
**Returns:** Platform-compliant content
**Used by:** Content Agent

#### 20. **RelevanceScorerTool**
**What it does:** Scores content relevance to audience
**Returns:** Relevance score 0-100
**Used by:** Content Agent

#### 21. **TagExtractorTool**
**What it does:** Extracts hashtags, keywords, entities from content
**Returns:** Structured tags and metadata
**Used by:** Content Agent

---

### 📅 CAMPAIGN MANAGEMENT TOOLS (6 Total)

#### 22. **CalendarGeneratorTool**
**What it does:** Generates content calendars
**Inputs:** Duration, goal, platform, personas, positioning
**Returns:** Day-by-day content calendar with posts
**Used by:** Content Agent

#### 23. **PlatformValidatorTool**
**What it does:** Validates content against platform rules
**Checks:** Length, hashtag limits, formatting, banned words
**Returns:** Validation results + suggestions
**Used by:** Content Agent

#### 24. **AssetFactoryTool**
**What it does:** Creates creative briefs for assets
**Returns:** Structured briefs for: images, videos, copy, carousel decks
**Used by:** Content Agent

#### 25. **MultiChannelAdapterTool**
**What it does:** Adapts content for different channels
**Transforms:** 1 message → LinkedIn + Twitter + Email versions
**Returns:** Channel-specific content variations
**Used by:** Content Agent

#### 26. **CalendarInjectorTool**
**What it does:** Injects events/promotions into calendar
**Operations:** Add holiday, add campaign milestone, add promotion
**Returns:** Updated calendar
**Used by:** Content Agent

#### 27. **MultiPlatformOrchestratorTool**
**What it does:** Coordinates multi-platform campaigns
**Returns:** Integrated campaign plan
**Used by:** Content Agent, Strategy Agent

---

### 📊 ANALYTICS & MEASUREMENT TOOLS (7 Total)

#### 28. **AMECEvaluatorTool**
**What it does:** Measures marketing effectiveness using AMEC model
**Metrics:**
- **Awareness:** Reach, impressions, brand recall
- **Consideration:** CTR, time on page, engagement
- **Preference:** Lead quality, conversion rate
- **Action:** Sales, subscriptions
- **Loyalty:** Retention, repeat purchase, NPS
**Returns:** AMEC scorecard
**Used by:** Analytics Agent

#### 29. **CLVCalculatorTool**
**What it does:** Calculates Customer Lifetime Value
**Formula:** (Average Transaction × Transactions Per Year × Years) - Customer Acquisition Cost
**Returns:** CLV per segment, payback period
**Used by:** Analytics Agent

#### 30. **NorthStarCalculatorTool**
**What it does:** Tracks progress toward single north star metric
**Returns:** Goal progress, trajectory, forecast
**Used by:** Analytics Agent

#### 31. **SacrificeCalculatorTool**
**What it does:** Evaluates what we gained by saying "no" to market segments
**Returns:** Opportunity cost analysis, focus benefits
**Used by:** Analytics Agent, Positioning Agent

#### 32. **BetEvaluatorTool**
**What it does:** Evaluates campaign as "bet" - risk vs. reward
**Returns:** Expected value, confidence level, recommendation
**Used by:** Analytics Agent

#### 33. **RouteBackLogicTool**
**What it does:** Decides if campaign needs re-positioning
**Returns:** Boolean + recommendation (stay, iterate, pivot)
**Used by:** Analytics Agent

#### 34. **SegmentScorerTool**
**What it does:** Scores segment performance vs. expectations
**Returns:** Score per segment, kill/scale recommendations
**Used by:** Analytics Agent

---

### 🛠️ UTILITY TOOLS (6 Total)

#### 35. **StateManagerTool**
**What it does:** Persists and retrieves agent state between runs
**Operations:** save, load, clear, archive
**Used by:** All agents (framework-level)

#### 36. **TierValidatorTool**
**What it does:** Checks if tier allows feature access
**Returns:** Boolean + required tier
**Used by:** Orchestrator Agent, Middleware

#### 37. **PositioningKnowledgeBaseTool**
**What it does:** Retrieves positioning frameworks
**Already listed above (Tool #6)**

#### Plus supporting tools: AddContextTool, ListContextItemsTool, DeleteContextItemTool, LockJobsTool, MergeJobsTool, SplitJobTool (from strategy_context_tools.py)

---

## API Routes & Endpoints

### Authentication Endpoints (OAuth 2.0)

```
POST /api/auth/google/callback
  Input: { code, state }
  Returns: { access_token, user_id, user_email }
  Description: Handle Google OAuth callback

POST /api/auth/verify-token
  Input: { token }
  Returns: { valid, user_id, expires_at }
  Description: Verify JWT token validity

POST /api/auth/logout
  Returns: { status: "success" }
  Description: Revoke user session

GET /api/auth/me
  Returns: { user_id, email, name, picture }
  Description: Get current user info
```

### Business Management

```
POST /api/intake
  Input: { name, industry, location, description, goals }
  Returns: { business_id, subscription_tier }
  Description: Create new business (also creates trial subscription)

GET /api/business/{business_id}
  Returns: { id, name, industry, description, goals, created_at }
  Description: Get business details

GET /api/subscription/{business_id}
  Returns: { tier, max_icps, max_assets, max_projects, status }
  Description: Get subscription/tier info
```

### Research Pipeline

```
POST /api/research/{business_id}
  Trigger: Research agent
  WebSocket: /ws/research/{business_id} for streaming
  Returns: { sostac, competitor_ladder, evidence_count, completeness_score }
  Description: Run comprehensive market research

GET /api/research/{business_id}
  Returns: { sostac, competitor_ladder, evidence, raw_research }
  Description: Retrieve saved research
```

### Positioning

```
POST /api/positioning/{business_id}
  Trigger: Positioning agent (generates 3 options)
  Returns: { options: [3 positioning options], validation_score }
  Description: Generate positioning options

POST /api/positioning/{business_id}/select
  Input: { option_index: 0-2 }
  Returns: { selected_positioning }
  Description: Select one positioning option

GET /api/positioning/{business_id}
  Returns: { selected_option, all_options, created_at }
  Description: Get positioning analysis
```

### ICPs (Ideal Customer Profiles)

```
POST /api/icps/{business_id}
  Input: { max_icps: 3-5 }
  Trigger: ICP agent
  Returns: { icps: [personas], platform_mapping }
  Description: Generate personas from positioning

GET /api/icps/{business_id}
  Returns: { icps: [all personas], count }
  Description: Get all personas
```

### Content Moves (Campaigns)

```
POST /api/moves/{business_id}
  Input: { goal, platform, duration_days }
  Trigger: Content agent
  Returns: { move_id, calendar, asset_briefs }
  Description: Generate content calendar

GET /api/moves/{move_id}
  Returns: { move_id, calendar, briefs, platform, status }
  Description: Get campaign details

GET /api/moves/business/{business_id}
  Returns: { moves: [all campaigns] }
  Description: Get all campaigns for business
```

### Analytics

```
POST /api/analytics/measure
  Input: { move_id, metrics: { CTR, CVR, conversions, spend } }
  Trigger: Analytics agent
  Returns: { amec_score, clv, route_back_needed, recommendations }
  Description: Analyze campaign performance

POST /api/analytics/lift
  Input: { asset_id_a, asset_id_b }
  Returns: { winner, lift_percent, confidence }
  Description: Compare two assets' performance
```

### Budget & Payments

```
POST /api/budget/set-limit
  Input: { monthly_limit_usd, hard_limit: boolean }
  Returns: { status, current_spend, remaining }
  Description: Set monthly cost limit

GET /api/budget/usage
  Returns: { spend_this_month, limit, percent_used, forecast }
  Description: Get cost usage stats

POST /api/razorpay/checkout
  Input: { business_id, tier }
  Returns: { order_id, amount, currency }
  Description: Create Razorpay checkout for upgrade

POST /api/razorpay/webhook
  Trigger: Razorpay callback
  Action: Update subscription tier in DB
  Description: Handle payment confirmation
```

### Conversations (Multi-turn dialogue)

```
POST /api/conversations
  Input: { title, business_id }
  Returns: { conversation_id }
  Description: Start new conversation

POST /api/conversations/{id}/messages
  Input: { content, role: "user" | "assistant" }
  Returns: { message_id, response }
  Description: Send message + get AI response

GET /api/conversations/{id}/messages
  Returns: { messages: [chronological messages] }
  Description: Get conversation history

DELETE /api/conversations/{id}
  Returns: { status: "deleted" }
  Description: Delete conversation (soft delete)
```

### Embeddings & Semantic Search

```
POST /api/embeddings/search
  Input: { query, business_id, limit: 10 }
  Returns: { results: [{ text, source, similarity_score }] }
  Description: Semantic search across evidence/conversations

POST /api/embeddings/batch
  Input: { texts: [...], metadata: {...} }
  Returns: { embedding_ids: [...] }
  Description: Batch embed multiple texts

GET /api/embeddings/{id}
  Returns: { text, embedding, metadata }
  Description: Get single embedding
```

### OCR & Document Processing

```
POST /api/ocr
  Input: FormData with image/PDF
  Returns: { text, confidence, tables, entities }
  Description: Extract text from images/PDFs

GET /api/ocr/{id}
  Returns: { text, metadata, processing_status }
  Description: Get OCR results
```

### Admin & Health

```
GET /health
  Returns: {
    status: "healthy",
    services: {
      database: "healthy",
      ai_services: "healthy",
      chroma_db: "healthy",
      redis: "healthy"
    }
  }
  Description: Full system health check

POST /api/admin/run-trend-monitor
  Trigger: Trend Monitor agent
  Returns: { status: "started" }
  Description: Manually trigger trend monitoring
```

---

## Integration Endpoints

### Slack Integration

```
POST /slack/notify
  Input: { webhook_url, message_type, data }
  Action: Send RaptorFlow updates to Slack
  Scenarios:
    - Research complete
    - Positioning generated
    - Calendar published
    - Campaign performance alert
```

### Email Automation

```
POST /email/send-campaign
  Input: { recipient_list, subject, template, scheduling }
  Action: Schedule and send emails
  Features:
    - HTML templates
    - Personalization
    - A/B subject lines
    - Send time optimization
```

### Google Sheets Integration

```
POST /sheets/sync
  Input: { business_id, sheet_id, data_type }
  Action: Export data to Google Sheet
  Exports:
    - ICPs and personas
    - Content calendar
    - Analytics reports
    - Competitor analysis
```

### Google Forms Integration

```
POST /forms/collect
  Input: { form_id, business_id }
  Action: Collect responses → process as evidence
  Workflow:
    - Fetch form responses
    - Extract insights
    - Feed into Research Agent
```

### GitHub Integration

```
POST /github/sync
  Input: { repo, business_id }
  Action: Sync issues/PRs as customer feedback
  Uses:
    - Issue comments as evidence
    - PR discussions for voice-of-customer
    - Release notes for feature announcements
```

### Zapier/Make Integration

```
POST /zapier/webhook
  Input: { event_type, payload }
  Action: Trigger RaptorFlow actions or send data to tools
  Bidirectional:
    - Create RaptorFlow research runs from external events
    - Send calendar to external CRM
    - Trigger analytics on campaign completion
```

---

## Complete Workflow

### User Journey: From Intake to Analytics

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: INTAKE (User creates business)                     │
└─────────────────────────────────────────────────────────────┘

Frontend: User fills form (name, industry, location, goals)
API: POST /api/intake
Backend:
  ├─ SecurityMiddleware validates input
  ├─ Create: businesses table entry
  ├─ Create: subscriptions table (trial tier)
  └─ Return: business_id
Database:
  ├─ INSERT businesses (name, industry, description, goals)
  └─ INSERT subscriptions (tier: trial, max_icps: 3, max_assets: 40)

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: RESEARCH (Orchestrator → Research Agent)           │
└─────────────────────────────────────────────────────────────┘

Frontend: User clicks "Run Research"
API: POST /api/research/{business_id}
  Optional: WebSocket for streaming updates

Backend Orchestrator:
  1. Load business + tier
  2. Check tier allows 'research' feature
  3. Determine stage = "research"
  4. Check prerequisites (all data available)
  5. Delegate to Research Agent

Research Agent Workflow:
  1. analyze_situation()
     - Uses SOSTACAnalyzerTool
     - Analyzes market, competitors, SWOT
     - Output: situation_analysis

  2. research_competitors()
     - Uses PerplexitySearchTool
     - Searches for competitor info
     - Output: competitor_list

  3. build_competitor_ladder()
     - Uses CompetitorLadderTool
     - Maps competitive positions
     - Output: competitor_ladder { rank: [comp1, comp2, us, comp3] }

  4. gather_evidence()
     - Uses PerplexitySearchTool + EvidenceDBTool
     - Searches for proof points, testimonials, data
     - Output: evidence_list

  5. validate_evidence()
     - Scores source credibility
     - Removes weak evidence
     - Output: validated_evidence

  6. link_claims_to_rtbs()
     - Uses RTBLinkerTool
     - Links claims → supporting proof
     - Output: claim_to_proof_mapping

  7. check_completeness()
     - Calculates completeness_score (0-100)
     - If score < 80 AND iterations < 3: loop back to step 2
     - Else: proceed to step 8

  8. save_results()
     - INSERT sostac_analyses table
     - INSERT competitor_ladder table
     - INSERT evidence table
     - Return to API

API Response:
  {
    "success": true,
    "sostac": { situation, objective, strategy, tactics, actions },
    "competitor_ladder": [{ rank, name, positioning, price }],
    "evidence_count": 47,
    "completeness_score": 87.5
  }

Database:
  ├─ INSERT sostac_analyses (business_id, data, completeness_score)
  ├─ INSERT competitor_ladder (business_id, rank, data)
  └─ INSERT evidence (business_id, claim, rtb, source, credibility)

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: POSITIONING (Orchestrator → Positioning Agent)     │
└─────────────────────────────────────────────────────────────┘

Frontend: User clicks "Generate Positioning"
API: POST /api/positioning/{business_id}

Backend Orchestrator:
  1. Check prerequisites: research completed? (GET sostac_analyses)
  2. Delegate to Positioning Agent

Positioning Agent Workflow:
  1. identify_inherent_drama()
     - Uses PositioningKnowledgeBaseTool (Leo Burnett principles)
     - Questions: What human truth? What emotional need?
     - Output: inherent_drama_identified

  2. generate_positioning_options()
     - LLM generates 3 unique positioning options
     - Uses business data + competitor_ladder + research insights
     - Output: options = [option1, option2, option3]

  3. evaluate_differentiation()
     - Uses DifferentiationAnalyzerTool
     - Scores vs. each competitor
     - Output: differentiation_score for each option

  4. calculate_sacrifices()
     - Uses SacrificeCalculatorTool
     - What market segments we won't pursue
     - What features we won't build
     - Output: sacrifices list

  5. create_visual_hammers()
     - Uses VisualHammerTool
     - Creates memorable visual/verbal asset for each
     - Output: visual_hammer descriptions

  6. validate_options()
     - Calculates validation_score (0-100)
     - If score < 75: loop back to step 2
     - Else: END

  Final Output (each option contains):
  {
    "inherent_drama": "...",
    "positioning": "...",
    "differentiation": { vs_competitor1: 87, vs_competitor2: 62 },
    "sacrifices": ["SMB market", "freemium model"],
    "visual_hammer": "Tiger metaphor"
  }

API Response:
  {
    "success": true,
    "options": [option1, option2, option3],
    "validation_score": 82.5
  }

Database:
  INSERT positioning_analyses (business_id, options, validation_score)

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: SELECT POSITIONING                                 │
└─────────────────────────────────────────────────────────────┘

Frontend: User selects 1 of 3 options
API: POST /api/positioning/{business_id}/select
  Input: { option_index: 0 }

Backend:
  - Update positioning_analyses: selected_option = options[0]
  - Save to DB

Database:
  UPDATE positioning_analyses SET selected_option = {...} WHERE business_id = ...

┌─────────────────────────────────────────────────────────────┐
│ STEP 5: ICPs (Orchestrator → ICP Agent)                    │
└─────────────────────────────────────────────────────────────┘

Frontend: User clicks "Generate ICPs"
API: POST /api/icps/{business_id}

Backend Orchestrator:
  1. Check prerequisites: positioning selected?
  2. Check tier allows ICPs (Breeze: 3, Glide: 3, Soar: 5)
  3. Delegate to ICP Agent

ICP Agent Workflow:
  1. extract_from_positioning()
     - Parse selected positioning
     - Identify implicit target segments

  2. build_persona_profiles()
     - Uses PersonaGeneratorTool
     - Creates detailed personas
     - Captures: demographics, psychographics, motivations, pain points

  3. identify_platforms()
     - Uses AudienceMatchingTool
     - Where does each persona spend time?
     - Output: persona → [LinkedIn 87%, Twitter 65%, etc.]

  4. find_content_preferences()
     - What content does each persona prefer?
     - Case studies? Tutorials? Product news?
     - Output: content_type → preference_score

  5. generate_embeddings()
     - Uses embedding service (OpenAI)
     - Creates vector for each persona
     - Enables semantic search later

  6. save_to_db()
     - INSERT icps table

Final Output (each ICP):
  {
    "name": "Early Adopter Eva",
    "demographics": { age, income, location },
    "psychographics": { values, behaviors },
    "platforms": ["LinkedIn", "Twitter"],
    "content_preferences": { "case_studies": 0.9, "tutorials": 0.7 },
    "embedding": [...vector...]
  }

API Response:
  {
    "success": true,
    "icps": [icp1, icp2, icp3],
    "count": 3
  }

Database:
  INSERT icps (business_id, name, demographics, psychographics, platforms, content_prefs, embedding)

┌─────────────────────────────────────────────────────────────┐
│ STEP 6: CONTENT MOVE (Orchestrator → Content Agent)        │
└─────────────────────────────────────────────────────────────┘

Frontend: User clicks "Create Content Move"
API: POST /api/moves/{business_id}
  Input: { goal: "Launch product", platform: "LinkedIn", duration_days: 30 }

Backend Orchestrator:
  1. Check prerequisites: ICPs generated?
  2. Check tier allows moves (Breeze: 5/mo, Glide: 15/mo, Soar: unlimited)
  3. Check quota: has user exceeded monthly asset limit?
  4. Delegate to Content Agent

Content Agent Workflow:
  1. generate_calendar()
     - Uses CalendarGeneratorTool
     - Inputs: goal, platform, duration_days, personas, positioning
     - Generates: 30-day calendar with daily posts
     - Output: calendar { date: [{ post1, post2 }] }

  2. validate_content()
     - Uses PlatformValidatorTool
     - Checks each post against platform specs
     - LinkedIn: max 1000 chars, allowed links, hashtag limits
     - Output: validation_results (some posts may be flagged)

  3. create_asset_briefs()
     - Uses AssetFactoryTool
     - For each post, creates brief for designer:
       { headline, body, tone, image_style, cta }
     - Output: asset_briefs

  4. adapt_for_channels()
     - Uses MultiChannelAdapterTool
     - Takes calendar for LinkedIn
     - Adapts for: Twitter, Email, Slack
     - Output: multi_channel_calendar

  5. finalize_calendar()
     - Compile all posts + briefs + metadata
     - Save to database
     - Return to API

Final Output (Move/Campaign):
  {
    "move_id": "uuid",
    "goal": "Launch product",
    "platform": "LinkedIn",
    "duration_days": 30,
    "calendar": [
      {
        "date": "2025-11-01",
        "posts": [
          {
            "text": "...",
            "tone": "professional",
            "hashtags": ["#growth"],
            "image_brief": "..."
          }
        ]
      }
    ],
    "asset_briefs": [...]
  }

API Response:
  {
    "success": true,
    "move_id": "uuid-123",
    "calendar": {...},
    "total_posts": 30
  }

Database:
  INSERT moves (business_id, goal, platform, calendar, status: "draft")

┌─────────────────────────────────────────────────────────────┐
│ STEP 7: PUBLISH CALENDAR (Manual or Scheduled)             │
└─────────────────────────────────────────────────────────────┘

Frontend: User clicks "Publish" on calendar
API: POST /api/dispatch/{move_id}
  Action: Schedule posts to platform (via social media API or Zapier)

Backend:
  - For each post in calendar:
    1. Generate UTM parameters (auto-tracking)
    2. Schedule post to LinkedIn
    3. Log dispatch event
    4. Update move status to "published"

Database:
  INSERT dispatches (move_id, post_id, platform, scheduled_at, utm_params)

┌─────────────────────────────────────────────────────────────┐
│ STEP 8: MONITOR PERFORMANCE (30 days pass)                 │
└─────────────────────────────────────────────────────────────┘

Frontend: User navigates to Analytics
API: GET /api/analytics/{move_id}

Backend:
  1. Fetch actual metrics from platform (or manual input)
  2. Calculate baseline metrics (before campaign)
  3. Calculate lift metrics (during campaign)
  4. Return performance data

Example Metrics:
  - Impressions: 50,000
  - Clicks: 2,500 (CTR: 5%)
  - Traffic: 1,800 visits
  - Conversions: 45 (CVR: 2.5%)
  - Revenue: $4,500

┌─────────────────────────────────────────────────────────────┐
│ STEP 9: ANALYTICS & RECOMMENDATIONS                        │
└─────────────────────────────────────────────────────────────┘

Frontend: User submits performance data
API: POST /api/analytics/measure
  Input: {
    move_id,
    metrics: { impressions, clicks, conversions, revenue, spend }
  }

Backend Orchestrator:
  1. Delegate to Analytics Agent

Analytics Agent Workflow:
  1. get_campaign_data()
     - Fetch move details
     - Fetch performance metrics

  2. run_amec_analysis()
     - Uses AMECEvaluatorTool
     - Analyzes: Awareness, Consideration, Preference, Action, Loyalty
     - Scores each stage
     - Output: amec_scorecard

  3. calculate_clv()
     - Uses CLVCalculatorTool
     - How much revenue per customer acquired?
     - Lifetime value trajectory
     - Output: clv_analysis

  4. calculate_north_star()
     - Uses NorthStarCalculatorTool
     - Primary metric for business success
     - Output: north_star_progress

  5. decide_route_back()
     - Uses RouteBackLogicTool
     - Did campaign meet expectations?
     - Do we need to re-position, re-message, or pivot?
     - Output: route_back_recommendation {
         stay: "continue as-is",
         iterate: "tweak messaging",
         pivot: "major repositioning needed"
       }

  6. generate_kill_scale_recommendations()
     - Which posts underperformed? (KILL)
     - Which posts overperformed? (SCALE)
     - Output: kill_list, scale_list

  7. save_analysis()
     - INSERT analytics table

API Response:
  {
    "success": true,
    "amec_analysis": { awareness: 85, consideration: 62, ... },
    "clv": { per_customer: $500, lifetime_value: $5000 },
    "north_star_progress": { target: 100, actual: 87, progress: "on track" },
    "route_back_needed": false,
    "kill_posts": [post_ids...],
    "scale_posts": [post_ids...]
  }

Database:
  INSERT analytics (move_id, amec_scores, clv, north_star, recommendations)

┌─────────────────────────────────────────────────────────────┐
│ STEP 10: ROUTE-BACK (If needed)                            │
└─────────────────────────────────────────────────────────────┘

If Analytics Agent recommends "pivot":
  1. Trigger new Positioning analysis
  2. Same as STEP 3, but refining based on learnings
  3. Loop back to Step 4 (select new positioning)
  4. Create new Content Move (Step 6)
  5. Repeat cycle

```

---

## Database Schema

### Core Tables

**businesses**
```sql
id UUID PRIMARY KEY
name VARCHAR(255)
industry VARCHAR(100)
location VARCHAR(255)
description TEXT
goals TEXT (JSON)
user_id UUID (RLS)
created_at TIMESTAMP
updated_at TIMESTAMP
```

**subscriptions**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
user_id UUID (RLS)
tier VARCHAR(50) -- 'breeze', 'glide', 'soar'
status VARCHAR(50) -- 'trial', 'active', 'cancelled'
max_icps INT
max_moves INT
max_assets INT
max_research_runs INT
created_at TIMESTAMP
expires_at TIMESTAMP
razorpay_subscription_id VARCHAR(255)
```

**research_analyses** (SOSTAC)
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
situation TEXT (JSON)
objective TEXT (JSON)
strategy TEXT (JSON)
tactics TEXT (JSON)
actions TEXT (JSON)
completeness_score FLOAT
iterations INT
created_at TIMESTAMP
```

**competitor_ladder**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
rank INT (1-10)
competitor_name VARCHAR(255)
positioning TEXT
price DECIMAL
features TEXT (JSON)
created_at TIMESTAMP
```

**evidence**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
claim TEXT
reason_to_believe TEXT
source VARCHAR(500)
credibility_score FLOAT (0-1)
source_type VARCHAR(50) -- 'review', 'stat', 'testimonial', 'case_study'
created_at TIMESTAMP
```

**positioning_analyses**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
options TEXT (JSON -- array of 3)
selected_option TEXT (JSON)
validation_score FLOAT
created_at TIMESTAMP
```

**icps**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
name VARCHAR(255)
demographics TEXT (JSON)
psychographics TEXT (JSON)
platforms TEXT[] (ARRAY)
content_preferences TEXT (JSON)
trending_topics TEXT[] (ARRAY)
embedding VECTOR(1536) -- pgvector
created_at TIMESTAMP
```

**moves**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
goal VARCHAR(255)
platform VARCHAR(50)
duration_days INT
calendar TEXT (JSON)
asset_briefs TEXT (JSON)
status VARCHAR(50) -- 'draft', 'published', 'completed'
created_at TIMESTAMP
```

**dispatches**
```sql
id UUID PRIMARY KEY
move_id UUID (FK)
post_id VARCHAR(255)
platform VARCHAR(50)
scheduled_at TIMESTAMP
posted_at TIMESTAMP
utm_params TEXT (JSON)
created_at TIMESTAMP
```

**analytics**
```sql
id UUID PRIMARY KEY
move_id UUID (FK)
amec_scores TEXT (JSON) -- awareness, consideration, preference, action, loyalty
clv DECIMAL
north_star_metric VARCHAR(100)
north_star_value FLOAT
route_back_needed BOOLEAN
kill_posts TEXT[] (ARRAY)
scale_posts TEXT[] (ARRAY)
created_at TIMESTAMP
```

**conversations**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
user_id UUID (RLS)
title VARCHAR(255)
is_deleted BOOLEAN DEFAULT FALSE
created_at TIMESTAMP
updated_at TIMESTAMP
```

**messages**
```sql
id UUID PRIMARY KEY
conversation_id UUID (FK)
role VARCHAR(20) -- 'user', 'assistant'
content TEXT
tokens_used INT
response_time_ms INT
model_used VARCHAR(100)
created_at TIMESTAMP
```

**embeddings**
```sql
id UUID PRIMARY KEY
business_id UUID (FK)
text TEXT
embedding VECTOR(1536)
metadata TEXT (JSON)
created_at TIMESTAMP
```

---

## Middleware Stack

```
                          ↓ Request
        ┌─────────────────────────────────┐
        │  SecurityHeadersMiddleware       │ ← Adds security headers
        └─────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  AuditLoggingMiddleware          │ ← Logs all requests
        └─────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  InputValidationMiddleware       │ ← Sanitizes inputs
        │  - HTML bleach                   │
        │  - SQL injection prevention      │
        │  - XSS protection                │
        └─────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  AuthenticationMiddleware        │ ← Verifies JWT/OAuth
        │  - Checks authorization header   │
        │  - Validates token              │
        │  - Sets request.state.user_id   │
        └─────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  AISafetyMiddleware              │ ← Prompt injection detection
        │  - 13+ malicious patterns       │
        │  - Prompt injection detection    │
        │  - Output sanitization          │
        └─────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  CostControlMiddleware           │ ← Cost tracking
        │  - Track API costs              │
        │  - Enforce cost limits          │
        │  - Warn on overages            │
        └─────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  Rate Limiter (slowapi)          │ ← Request throttling
        │  - Per-endpoint limits          │
        │  - Redis-backed                 │
        └─────────────────────────────────┘
                          ↓
                    ↓ To Route Handler
```

### Middleware Details

**SecurityHeadersMiddleware**
- Adds: X-Content-Type-Options: nosniff
- Adds: X-Frame-Options: DENY
- Adds: X-XSS-Protection: 1; mode=block

**InputValidationMiddleware**
- Sanitizes HTML with Bleach library
- Strips dangerous tags (script, iframe, etc.)
- Validates JSON schema
- Enforces max field lengths

**AuthenticationMiddleware**
- Extracts JWT from Authorization header
- Verifies signature with JWT_SECRET_KEY
- Sets request.state.user_id
- Returns 401 if invalid

**AISafetyMiddleware**
- Detects patterns:
  - "ignore previous instructions"
  - "expose data"
  - "bypass security"
  - JNDI injection attempts
  - JavaScript injection
- Input length limits: 50KB
- Output sanitization (removes API keys, credentials)

**CostControlMiddleware**
- Tracks cost of API calls (OpenAI, Google, Perplexity)
- Maintains running total per user/month
- Enforces hard limit or warns on soft limit
- Raises CostLimitExceeded exception

**Rate Limiter**
- Per-endpoint limits (e.g., research: 2/min, assets: 10/min)
- Uses Redis for tracking
- Returns 429 Too Many Requests if exceeded

---

Done! This is your complete backend mapped out. What would you like me to dive deeper into?

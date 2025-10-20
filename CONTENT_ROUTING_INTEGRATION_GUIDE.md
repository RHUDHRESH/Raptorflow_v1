# Content Routing System - Integration Guide

**Purpose:** How to integrate the new Content Routing System with existing RaptorFlow components
**Audience:** Developers, DevOps, System Architects

---

## 🔗 Integration Points

### 1. Frontend Integration

#### Include the Component
```typescript
// frontend/app/dashboard/moves/page.tsx
import ContentRouter from '@/components/ContentRouter';

export default function MovesPage() {
  return (
    <div>
      <ContentRouter />
    </div>
  );
}
```

#### Alternative: Embed in Dashboard
```typescript
// frontend/app/dashboard/page.tsx
import { ContentRouter } from '@/components/ContentRouter';

export default function Dashboard() {
  return (
    <div>
      <div className="grid grid-cols-3">
        <ContentRouter />
      </div>
    </div>
  );
}
```

### 2. API Integration

#### Add Routes to Main Router
```python
# backend/api/main.py
from fastapi import FastAPI
from backend.api.content_routing_routes import router as content_router

app = FastAPI()

# Include content routing routes
app.include_router(content_router)

# Other routes...
app.include_router(research_router)
app.include_router(positioning_router)
```

#### Environment Setup
```bash
# .env
CONTENT_ROUTING_ENABLED=true
TWITTER_API_KEY=xxx
LINKEDIN_API_KEY=xxx
FACEBOOK_API_KEY=xxx
# ... other platform keys
```

### 3. Agent Integration

#### Use Enhanced Agent in Workflow
```python
# backend/agents/workflow.py
from backend.agents.moves_content_agent_enhanced import moves_content_agent_enhanced

async def publish_content(business_id, content, platforms):
    """Publish content using enhanced agent"""

    result = await moves_content_agent_enhanced.create_and_route_content(
        business_id=business_id,
        content=content,
        content_type="venting",
        business_data={...},
        icps=[...],
        auto_publish=True
    )

    return result
```

#### Integrate with Existing Moves Agent
```python
# backend/agents/base_agent.py
from backend.agents.content_router_agent import content_router

class BaseAgent:
    def __init__(self):
        self.router = content_router

    async def route_content(self, content, business_id, icps):
        """Use router for content distribution"""
        return await self.router.analyze_and_route(
            business_id=business_id,
            content=content,
            content_type="text",
            business_data={},
            icps=icps
        )
```

### 4. Database Integration

#### Store Distribution History
```python
# Create table for tracking distributions
CREATE TABLE content_distributions (
    id UUID PRIMARY KEY,
    business_id UUID NOT NULL,
    original_content TEXT NOT NULL,
    platforms JSONB NOT NULL,
    results JSONB NOT NULL,
    created_at TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id)
);

# Track platform-specific posts
CREATE TABLE platform_posts (
    id UUID PRIMARY KEY,
    distribution_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    post_id VARCHAR(255),
    url TEXT,
    status VARCHAR(20),
    metrics JSONB,
    FOREIGN KEY (distribution_id) REFERENCES content_distributions(id)
);
```

#### Supabase Integration
```python
# backend/api/client.py
from supabase import create_client

class RaptorflowAPIClient:
    def __init__(self):
        self.supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    async def save_distribution(self, business_id, results):
        """Save distribution results to database"""

        response = self.supabase.table('content_distributions').insert({
            'business_id': business_id,
            'platforms': results['platforms'],
            'results': results['results'],
            'created_at': datetime.now().isoformat()
        }).execute()

        return response
```

---

## 🔌 Platform API Integration

### Twitter/X Integration
```python
# backend/integrations/twitter_publisher.py
import tweepy

class TwitterPublisher:
    def __init__(self, api_key, api_secret):
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret
        )

    async def publish(self, content):
        """Publish to Twitter"""
        response = self.client.create_tweet(text=content)
        return {
            "platform": "Twitter",
            "post_id": response.data['id'],
            "url": f"https://twitter.com/i/web/status/{response.data['id']}"
        }
```

### LinkedIn Integration
```python
# backend/integrations/linkedin_publisher.py
from linkedin_api import Linkedin

class LinkedInPublisher:
    def __init__(self, email, password):
        self.api = Linkedin(email, password)

    async def publish(self, content):
        """Publish to LinkedIn"""
        response = self.api.create_post(text=content)
        return {
            "platform": "LinkedIn",
            "post_id": response['id'],
            "url": f"https://linkedin.com/feed/update/{response['id']}"
        }
```

### Slack Integration
```python
# backend/integrations/slack_publisher.py
from slack_sdk import WebClient

class SlackPublisher:
    def __init__(self, token):
        self.client = WebClient(token=token)

    async def publish(self, content, channel):
        """Publish to Slack"""
        response = self.client.chat_postMessage(
            channel=channel,
            text=content
        )
        return {
            "platform": "Slack",
            "post_id": response['ts'],
            "channel": channel
        }
```

---

## 📊 Metrics & Analytics

### Track Performance
```python
# backend/analytics/content_analytics.py
from datetime import datetime, timedelta

class ContentAnalytics:
    async def get_platform_metrics(self, business_id, days=7):
        """Get performance metrics by platform"""

        start_date = datetime.now() - timedelta(days=days)

        metrics = {}

        # Query each platform's metrics
        for platform in ['twitter', 'linkedin', 'facebook']:
            metrics[platform] = await self._get_platform_stats(
                business_id, platform, start_date
            )

        return metrics

    async def _get_platform_stats(self, business_id, platform, start_date):
        """Get stats for specific platform"""

        # Query database or platform API
        return {
            "platform": platform,
            "impressions": 1234,
            "engagements": 56,
            "engagement_rate": 0.045,
            "period": "7d"
        }
```

### Dashboard Integration
```typescript
// frontend/components/ContentAnalyticsDashboard.tsx
import { useQuery } from '@tanstack/react-query';

export function ContentAnalyticsDashboard({ businessId }) {
  const { data: metrics } = useQuery({
    queryKey: ['content-metrics', businessId],
    queryFn: () => fetch(
      `/api/content/analytics?business_id=${businessId}`
    ).then(r => r.json())
  });

  return (
    <div>
      <h2>Content Performance</h2>
      {metrics?.platforms.map(metric => (
        <PlatformMetricCard key={metric.platform} metric={metric} />
      ))}
    </div>
  );
}
```

---

## 🔄 Workflow Integration

### Complete Content Publishing Workflow
```python
# backend/workflow/content_workflow.py
from backend.agents.moves_content_agent_enhanced import moves_content_agent_enhanced
from backend.api.client import RaptorflowAPIClient

class ContentPublishingWorkflow:
    def __init__(self):
        self.agent = moves_content_agent_enhanced
        self.api_client = RaptorflowAPIClient()

    async def execute(self, business_id, content, auto_publish=False):
        """Execute complete publishing workflow"""

        # Step 1: Route content
        routing_result = await self.agent.create_and_route_content(
            business_id=business_id,
            content=content,
            content_type="text",
            business_data=await self._get_business_data(business_id),
            icps=await self._get_icps(business_id),
            auto_publish=auto_publish
        )

        # Step 2: Save to database
        await self.api_client.save_distribution(
            business_id,
            routing_result
        )

        # Step 3: Notify user
        await self._notify_user(business_id, routing_result)

        # Step 4: Update analytics
        await self._update_analytics(business_id, routing_result)

        return routing_result

    async def _get_business_data(self, business_id):
        """Fetch business data from database"""
        # Implementation
        pass

    async def _get_icps(self, business_id):
        """Fetch ICP personas from database"""
        # Implementation
        pass

    async def _notify_user(self, business_id, result):
        """Send notification to user"""
        # Send email, Slack, or in-app notification
        pass

    async def _update_analytics(self, business_id, result):
        """Update analytics records"""
        # Store metrics for dashboard
        pass
```

---

## 🛠️ Configuration

### Config File Example
```python
# backend/config/content_routing_config.py
from pydantic import BaseSettings

class ContentRoutingConfig(BaseSettings):
    # Platform API Keys
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    LINKEDIN_API_KEY: str
    FACEBOOK_API_KEY: str

    # Feature Flags
    ENABLE_AUTO_PUBLISH: bool = False
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    ENABLE_AUDIENCE_MATCHING: bool = True

    # Limits
    MAX_PLATFORMS_PER_REQUEST: int = 10
    MAX_CONTENT_LENGTH: int = 10000

    # Scheduling
    DEFAULT_POSTING_INTERVAL: int = 60  # seconds
    OPTIMAL_TIME_CALCULATION: bool = True

    class Config:
        env_file = ".env"
        env_prefix = "CONTENT_ROUTING_"

config = ContentRoutingConfig()
```

---

## 🧪 Testing

### Unit Tests
```python
# backend/tests/test_sentiment_analyzer.py
import pytest
from backend.tools.sentiment_tone_analyzer import sentiment_tone_analyzer

@pytest.mark.asyncio
async def test_sentiment_analysis():
    """Test sentiment analysis"""

    result = await sentiment_tone_analyzer._execute(
        content="I love this feature! It's amazing!",
        detailed=True
    )

    assert result['success'] == True
    assert result['sentiment']['type'] == 'positive'
    assert result['sentiment']['confidence'] > 0.7

@pytest.mark.asyncio
async def test_venting_detection():
    """Test venting tone detection"""

    result = await sentiment_tone_analyzer._execute(
        content="I hate this! This is terrible!",
        detailed=True
    )

    assert result['success'] == True
    assert result['tone']['primary_tone'] == 'venting'
```

### Integration Tests
```python
# backend/tests/test_content_routing_api.py
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_route_content_endpoint():
    """Test content routing endpoint"""

    response = client.post(
        "/api/content/route-content",
        json={
            "business_id": "test_123",
            "content": "I'm frustrated with this!",
            "content_type": "venting",
            "auto_publish": False
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert len(data['recommendations']) > 0
```

---

## 🚀 Deployment

### Docker Setup
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# .env.production
DATABASE_URL=postgresql://user:pass@localhost/raptorflow
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxx
TWITTER_API_KEY=xxxxx
LINKEDIN_API_KEY=xxxxx
FACEBOOK_API_KEY=xxxxx
CONTENT_ROUTING_ENABLED=true
```

### Kubernetes Deployment
```yaml
# k8s/content-routing-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: raptorflow-content-routing
spec:
  replicas: 3
  selector:
    matchLabels:
      app: content-routing
  template:
    metadata:
      labels:
        app: content-routing
    spec:
      containers:
      - name: api
        image: raptorflow:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: raptorflow-secrets
              key: database-url
```

---

## 🔐 Security Considerations

### API Key Management
```python
# backend/security/key_manager.py
from cryptography.fernet import Fernet
import os

class APIKeyManager:
    def __init__(self):
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY'))

    def encrypt_key(self, key):
        """Encrypt API key before storage"""
        return self.cipher.encrypt(key.encode())

    def decrypt_key(self, encrypted_key):
        """Decrypt API key for use"""
        return self.cipher.decrypt(encrypted_key).decode()
```

### Rate Limiting
```python
# backend/middleware/rate_limiting.py
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.util import get_redis

async def startup():
    redis = await get_redis()
    await FastAPILimiter.init(redis)

# Apply to routes
from fastapi_limiter.depends import RateLimiter

@app.post("/api/content/route-content")
@FastAPILimiter.limit("10/minute")
async def route_content(request: ContentRoutingRequest):
    # Route content
    pass
```

### Input Validation
```python
# backend/validators/content_validator.py
from pydantic import BaseModel, validator

class ContentRoutingRequest(BaseModel):
    business_id: str
    content: str
    platforms: List[str]

    @validator('content')
    def content_not_empty(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Content must be at least 3 characters')
        return v

    @validator('platforms')
    def platforms_valid(cls, v):
        valid = ['twitter', 'linkedin', 'facebook', 'instagram', 'slack']
        for p in v:
            if p.lower() not in valid:
                raise ValueError(f'Invalid platform: {p}')
        return v
```

---

## 📚 Recommended Integration Order

1. **Phase 1: Core Setup**
   - Add API routes to FastAPI app
   - Set up database tables
   - Configure environment variables

2. **Phase 2: Backend Integration**
   - Import tools and agents
   - Integrate with moves workflow
   - Add database storage

3. **Phase 3: Frontend Integration**
   - Add ContentRouter component to pages
   - Connect to API endpoints
   - Add to navigation

4. **Phase 4: Platform APIs**
   - Implement Twitter publisher
   - Implement LinkedIn publisher
   - Implement Slack publisher
   - (Other platforms as needed)

5. **Phase 5: Analytics**
   - Set up metrics tracking
   - Create analytics dashboard
   - Set up performance monitoring

6. **Phase 6: Testing & Launch**
   - Run unit tests
   - Run integration tests
   - Deploy to staging
   - Launch to production

---

## 📞 Support

For integration help:
- Check `CONTENT_ROUTING_SESSION_SUMMARY.md` for feature overview
- Review specific tool files for implementation details
- Refer to type hints and docstrings in code
- Check API endpoint documentation

---

**Last Updated:** October 19, 2024
**Version:** 1.0
**Status:** Ready for Integration

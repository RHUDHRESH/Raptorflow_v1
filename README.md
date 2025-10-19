# RaptorFlow ADAPT 🚀

**AI-Powered Marketing Intelligence Platform**
Transform business confusion into strategic clarity in minutes.

**Status:** Production-Ready | **Version:** 1.0.0 | **License:** MIT

## What Is RaptorFlow?

RaptorFlow is a **multi-agent AI system** that automates what normally requires 3 expensive consultants:

1. **Brand Strategist** → Positioning Agent (Ries, Trout, Godin principles)
2. **Market Researcher** → Research Agent (Evidence graph + Perplexity deep research)
3. **Content Strategist** → Content Agent (RACE calendar generation)
4. **Customer Psychologist** → ICP Agent (Psychographics + JTBD)
5. **Analytics Expert** → Analytics Agent (AMEC ladder + route-back logic)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase Account (free)
- API Keys: OpenAI/Gemini + Perplexity + Razorpay

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env with your API keys
cp .env.example .env

# Start
uvicorn main:app --reload
```

### 2. Database Setup
- Create Supabase project
- Run SQL from `backend/sql/schema.sql`
- Add credentials to .env

### 3. Frontend Setup
```bash
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### 4. Visit App
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📖 Full Documentation
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[Context Document](./context/overall.txt)** - Full architecture and principles
- Backend Docs: http://localhost:8000/docs (interactive API)

## 🏗️ Architecture

```
Frontend (Next.js) → Backend (FastAPI) → Supabase (PostgreSQL + pgvector)
                                      ↓
                            LangGraph Agents
                          (Research, Positioning, ICP, Strategy, Content, Analytics)
                                      ↓
                       External APIs (OpenAI, Perplexity, Razorpay)
```

## 🎯 Key Features

- ✅ Strategic positioning analysis (3 options)
- ✅ Customer intelligence (3-9 ICPs with psychographics)
- ✅ Content calendar generation (platform-specific)
- ✅ Trend monitoring (daily Perplexity searches)
- ✅ Performance measurement (AMEC ladder)
- ✅ Route-back logic (learning from results)
- ✅ Payment gating (Razorpay integration)

## 💰 Subscription Tiers

- **Basic (₹2,000):** 3 ICPs, 5 moves
- **Pro (₹3,500):** 6 ICPs, 15 moves, trend monitoring
- **Enterprise (₹5,000):** 9 ICPs, unlimited moves, all features

## 🧪 Testing

```bash
# Test API
curl -X POST http://localhost:8000/api/intake \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Co",
    "industry": "SaaS",
    "location": "Singapore",
    "description": "A cool app",
    "goals": "100 customers"
  }'
```

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for:
- Docker setup
- Google Cloud Run deployment
- Custom domain configuration
- Monitoring and logs
- Security checklist

## 📊 Tech Stack

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, LangGraph, Python
- **Database:** Supabase (PostgreSQL + pgvector)
- **AI:** OpenAI GPT-5 / Gemini 2.0
- **Research:** Perplexity Sonar API
- **Payments:** Razorpay
- **Deployment:** Google Cloud Run

## 🤝 Contributing

Suggestions and improvements welcome! Open an issue or submit a PR.

## 📝 License

MIT License - See LICENSE file

---

**Built with ❤️ for marketing-focused founders**
Version 1.0.0 | Production Ready | October 2024

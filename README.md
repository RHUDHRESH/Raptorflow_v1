# RaptorFlow ADAPT

AI-Powered Marketing Intelligence Platform - Cloud-Native Architecture

## Quick Start

### Docker (Recommended)
```bash
cp .env.cloud.example .env
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Local Development
```bash
cp .env.cloud.example .env

# Backend
cd backend && pip install -r requirements.cloud.txt && python main.py

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

See [DOCKER.md](DOCKER.md) for more details.

## Architecture

**Development**: Gemini → OpenRouter
**Production**: OpenAI GPT-5 (nano/mini/std) → OpenRouter

Switch with `APP_MODE=dev` or `APP_MODE=prod`

## Structure

```
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── database/         # SQL schemas
├── scripts/          # Quality checks
├── load-tests/       # k6 load tests
├── cloudbuild.yaml   # CI/CD
└── Dockerfile        # Production build
```

## Deploy

```bash
./deploy-cloud-run.sh
```

## Environment Variables

Required:
- `APP_MODE` - dev or prod
- `OPENAI_API_KEY` - GPT-5 access (prod)
- `GEMINI_API_KEY` - Gemini access (dev)
- `OPENROUTER_API_KEY` - Fallback
- `SUPABASE_URL` - Database
- `SUPABASE_KEY` - Database auth

See `.env.cloud.example` for all variables.

## Health Check

```bash
curl http://localhost:8080/health
```

## License

Proprietary

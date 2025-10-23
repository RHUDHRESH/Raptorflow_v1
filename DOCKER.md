# Docker Deployment Guide

## Local Development

```bash
# 1. Configure environment
cp .env.cloud.example .env

# 2. Start all services
docker-compose up --build

# 3. Access services
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Health: http://localhost:8000/health

# 4. Stop services
docker-compose down
```

## Production Build

### Backend Only
```bash
docker build -t raptorflow-api:latest .
docker run -p 8080:8080 --env-file .env raptorflow-api:latest
```

### Frontend Only
```bash
docker build -t raptorflow-web:latest -f Dockerfile.frontend .
docker run -p 3000:3000 raptorflow-web:latest
```

## Google Cloud Run Deployment

```bash
# Build
docker build -t gcr.io/PROJECT_ID/raptorflow:latest .

# Push
docker push gcr.io/PROJECT_ID/raptorflow:latest

# Deploy
gcloud run deploy raptorflow \
  --image gcr.io/PROJECT_ID/raptorflow:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars APP_MODE=prod
```

Or use automated deployment:
```bash
gcloud builds submit
```

## Docker Images

**Backend**
- Base: python:3.11-slim
- Size: ~500MB
- Multi-stage build (builder + runtime)
- Non-root user
- Health checks

**Frontend**
- Base: node:20-alpine
- Size: ~300MB
- Multi-stage build (builder + runtime)
- Non-root user
- Health checks

## Environment Files

- **Root**: `.dockerignore` - Global build ignore rules
- **Backend**: `backend/.dockerignore` - Python-specific ignores
- **Frontend**: `frontend/.dockerignore` - Node-specific ignores

## Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000/api/health
```

## Debugging

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Interactive shell
docker-compose exec backend sh
docker-compose exec frontend sh

# Build details
docker images
docker ps
```

Done.

#!/bin/sh

# Startup script for combined RaptorFlow deployment (backend + frontend).
# Designed for Google Cloud Run and other container platforms.

set -eu

PORT="${PORT:-8080}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
BACKEND_HEALTH_PATH="${BACKEND_HEALTH_PATH:-/health}"
FRONTEND_HEALTH_PATH="${FRONTEND_HEALTH_PATH:-/health}"
BACKEND_HEALTH_URL="${BACKEND_HEALTH_URL:-http://127.0.0.1:${BACKEND_PORT}${BACKEND_HEALTH_PATH}}"
FRONTEND_HEALTH_URL="${FRONTEND_HEALTH_URL:-http://127.0.0.1:${PORT}${FRONTEND_HEALTH_PATH}}"
STARTUP_TIMEOUT="${STARTUP_TIMEOUT:-60}"

log() {
    printf '%s %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*"
}

wait_for_service() {
    service_url="$1"
    timeout_seconds="$2"
    elapsed=0

    while ! curl -fsS "$service_url" >/dev/null 2>&1; do
        if [ "$elapsed" -ge "$timeout_seconds" ]; then
            log "Service check failed for ${service_url} after ${timeout_seconds}s"
            return 1
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done

    log "Service healthy at ${service_url}"
    return 0
}

log "Starting RaptorFlow services (PORT=${PORT}, BACKEND_PORT=${BACKEND_PORT})"

# Start Python backend
cd /backend
log "Booting FastAPI backend..."
ENVIRONMENT="${ENVIRONMENT:-production}" PORT="$BACKEND_PORT" python main.py &
BACKEND_PID=$!

shutdown() {
    log "Shutting down services…"
    kill "$BACKEND_PID" "$NGINX_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
    log "Shutdown complete"
    exit 0
}

trap shutdown INT TERM

if ! wait_for_service "$BACKEND_HEALTH_URL" "$STARTUP_TIMEOUT"; then
    log "Backend failed to become healthy"
    kill "$BACKEND_PID" 2>/dev/null || true
    exit 1
fi

log "Starting nginx frontend reverse proxy..."
nginx -g 'daemon off;' &
NGINX_PID=$!

if ! wait_for_service "$FRONTEND_HEALTH_URL" "$STARTUP_TIMEOUT"; then
    log "Frontend failed health check"
    shutdown
fi

log "RaptorFlow is up and serving traffic"
wait "$BACKEND_PID" "$NGINX_PID"

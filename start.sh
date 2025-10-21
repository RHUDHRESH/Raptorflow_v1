#!/bin/sh

# Startup script for RaptorFlow production deployment
# Starts both nginx (frontend) and Python backend

set -e

echo "🚀 Starting RaptorFlow Production Deployment..."

# Function to check if service is healthy
check_health() {
    local service_url=$1
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking health of $service_url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$service_url" > /dev/null; then
            echo "✅ $service_url is healthy"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - $service_url not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_url failed health check after $max_attempts attempts"
    return 1
}

# Start Python backend in background
echo "🐍 Starting Python backend..."
cd /backend
python main.py &
BACKEND_PID=$!

# Wait for backend to be healthy
echo "⏳ Waiting for backend to start..."
sleep 5

# Check backend health
if ! check_health "http://localhost:8000/health"; then
    echo "❌ Backend failed to start properly"
    exit 1
fi

# Start nginx in foreground
echo "🌐 Starting nginx frontend..."
nginx -g 'daemon off;' &
NGINX_PID=$!

# Wait a moment for nginx to start
sleep 2

# Check overall health
if ! check_health "http://localhost/health"; then
    echo "❌ Overall health check failed"
    kill $BACKEND_PID $NGINX_PID
    exit 1
fi

echo "✅ RaptorFlow is running successfully!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost"
echo "💰 Budget Controller: Active"
echo "🤖 AI Agents: GPT-5 Nano + GPT-5"

# Function to handle shutdown
shutdown() {
    echo "🛑 Shutting down RaptorFlow..."
    kill $BACKEND_PID $NGINX_PID
    echo "✅ Shutdown complete"
    exit 0
}

# Trap signals for graceful shutdown
trap shutdown TERM INT

# Wait for processes
wait $BACKEND_PID $NGINX_PID

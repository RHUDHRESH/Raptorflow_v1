# ==============================================
# Backend Dockerfile - Production Ready
# ==============================================
# Multi-stage build for minimal image size
# Optimized for Google Cloud Run

# Stage 1: Builder
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
WORKDIR /build
COPY requirements.cloud.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8080

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv

# Create app user and set working directory
WORKDIR /app
RUN adduser --disabled-password --gecos '' appuser

# Copy application code
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE 8080

# Start command
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1"]

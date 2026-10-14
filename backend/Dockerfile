# ==============================================================================
# Stage 1: Build Dependencies
# ==============================================================================
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# Install compilation packages required for wheel builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy package requirements
COPY backend/pyproject.toml ./

# Install dependencies into virtualenv
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# ==============================================================================
# Stage 2: Minimal Production Runtime
# ==============================================================================
FROM python:3.11-slim-bookworm AS runner

# Pinned metadata
LABEL maintainer="LOTM Tarot Development Team" \
      version="0.1.0" \
      description="Production container for LOTM Tarot FastAPI backend"

WORKDIR /app

# Install minimal runtime libraries (e.g. libpq for postgres if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root dedicated application user & group
RUN groupadd -g 10001 lotmgroup && \
    useradd -u 10001 -g lotmgroup -s /bin/sh -m lotmuser

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Copy application source code and database migrations
COPY backend/app /app/app
COPY backend/run.py /app/run.py
COPY backend/docker-entrypoint.sh /app/docker-entrypoint.sh
COPY db /app/db

# Make entrypoint executable and grant ownership to non-root user
RUN chmod +x /app/docker-entrypoint.sh && \
    chown -R lotmuser:lotmgroup /app

# Switch to non-root execution
USER lotmuser

# Healthcheck targeting FastAPI liveness probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')" || exit 1

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# AI-MILO Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies (ffmpeg required for audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition
COPY pyproject.toml uv.lock* ./

# Install project dependencies
RUN uv pip install --system -r pyproject.toml

# Copy project directories
COPY app/ ./app/
COPY frontend/ ./frontend/
COPY knowledge_base/ ./knowledge_base/
COPY "Knowledge Base MILO/" "./Knowledge Base MILO/"
COPY scripts/ ./scripts/

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start production uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

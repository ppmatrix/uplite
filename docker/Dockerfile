# UpLite Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy all necessary files for building
COPY pyproject.toml uv.lock* README.md ./
COPY src/ ./src/

# Install Python dependencies with PostgreSQL and Redis support
RUN uv sync --frozen --no-dev --extra postgres --extra redis

# Copy remaining files including management scripts
COPY .env* ./
COPY manage.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash uplite && \
    chown -R uplite:uplite /app
USER uplite

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run application
CMD ["uv", "run", "uplite"]

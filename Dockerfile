# ---- Base (runtime) ----
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# System deps (only what we really need)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Build deps layer (cache Poetry install) ----
FROM base AS builder

# Install Poetry (no venvs inside container)
RUN pip install "poetry==1.8.3" && poetry config virtualenvs.create false

# Copy only project metadata first to leverage Docker layer caching
COPY pyproject.toml README.md /app/

# Install runtime deps only (no dev)
RUN poetry install --only main --no-root

# ---- Final image ----
FROM base AS final

# Create app user (non-root)
RUN useradd -u 10001 -ms /bin/bash appuser
USER appuser

# Copy installed site-packages from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY src /app/src

EXPOSE 8000

# Simple healthcheck hitting list endpoint (versioned)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/v1/notes >/dev/null || exit 1

# Default command (prod-ish)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]

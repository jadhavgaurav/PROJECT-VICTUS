# Dockerfile for Project VICTUS
# Stage 1: Build stage with Poetry
FROM python:3.11-slim as builder

# Install system dependencies (for Piper TTS) and Poetry
RUN apt-get update && apt-get install -y curl build-essential espeak-ng && rm -rf /var/lib/apt/lists/*
ENV POETRY_HOME="/opt/poetry"
RUN python3 -m venv $POETRY_HOME
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN pip install --no-cache-dir poetry

WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# Install dependencies into a virtual environment
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root --no-interaction --no-ansi

# ---
# Stage 2: Final application stage
FROM python:3.11-slim

RUN apt-get update && apt-get install -y espeak-ng && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code and assets
COPY . .
RUN mkdir -p /app/static/audio /app/uploads /app/faiss_index

EXPOSE 8000

# Use the new entry point
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

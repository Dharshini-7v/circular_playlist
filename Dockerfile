# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Render provides $PORT; default to 8000 for local dev
ENV PORT=8000
EXPOSE 8000

# Start the FastAPI server
CMD ["sh", "-c", "uvicorn playlist_api.server:app --host 0.0.0.0 --port ${PORT}"]

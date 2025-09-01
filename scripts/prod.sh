#!/bin/bash

# Production deployment script
echo "🚀 Starting production environment..."

# Load production environment
export $(cat .env.production | xargs)

# Run migrations
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
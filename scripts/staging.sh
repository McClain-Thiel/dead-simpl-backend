#!/bin/bash

# Staging deployment script
echo "🚀 Starting staging environment..."

# Load staging environment
export $(cat .env.staging | xargs)

# Run migrations
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
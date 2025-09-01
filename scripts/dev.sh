#!/bin/bash

# Development startup script
echo "🚀 Starting development environment..."

# Load local environment
if [ -f ".env.local" ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
else
    echo "❌ .env.local file not found. Please copy .env.example to .env.local and configure it."
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    # Start PostgreSQL container if not running
    if ! docker ps | grep -q aipocket_postgres_dev; then
        echo "📦 Starting PostgreSQL container..."
        ./scripts/start-local-db.sh
    else
        echo "✅ PostgreSQL container is already running"
    fi
else
    echo "⚠️  Docker not found. Please ensure PostgreSQL is running on localhost:5432"
    echo "   Database: aipocket_local, User: postgres, Password: postgres"
fi

# Wait a moment for database to be ready
sleep 2

# Run migrations
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Start the FastAPI server with hot reload
echo "🌟 Starting FastAPI server with hot reload..."
echo "   API docs: http://127.0.0.1:8000/docs"
uv run uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
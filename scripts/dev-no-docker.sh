#!/bin/bash

# Development startup script without Docker
echo "🚀 Starting development environment (no Docker)..."

# Load local environment
if [ -f ".env.local" ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
else
    echo "❌ .env.local file not found. Please copy .env.example to .env.local and configure it."
    exit 1
fi

echo "⚠️  Make sure you have PostgreSQL running locally on localhost:5432"
echo "   Database: aipocket_local"
echo "   User: postgres" 
echo "   Password: postgres"
echo ""
echo "   You can install PostgreSQL locally or use a cloud database for development."
echo ""

# Wait for user confirmation
read -p "Press Enter when your database is ready, or Ctrl+C to cancel..."

# Run migrations
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Start the FastAPI server with hot reload
echo "🌟 Starting FastAPI server with hot reload..."
echo "   API docs: http://127.0.0.1:8000/docs"
uv run uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
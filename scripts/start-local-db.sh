#!/bin/bash

# Start local PostgreSQL database using Docker
echo "📦 Starting local PostgreSQL database..."

# Stop and remove existing container if it exists
docker stop aipocket_postgres_dev 2>/dev/null || true
docker rm aipocket_postgres_dev 2>/dev/null || true

# Start PostgreSQL container
docker run -d \
  --name aipocket_postgres_dev \
  -e POSTGRES_DB=aipocket_local \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v aipocket_postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if container is running
if docker ps | grep -q aipocket_postgres_dev; then
    echo "✅ PostgreSQL is running on localhost:5432"
    echo "   Database: aipocket_local"
    echo "   User: postgres"
    echo "   Password: postgres"
else
    echo "❌ Failed to start PostgreSQL container"
    exit 1
fi
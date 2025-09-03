#!/bin/bash

# Check if Supabase containers are running
echo "Checking if Supabase containers are running..."

SUPABASE_CONTAINERS=$(docker ps --filter "name=supabase" --format "table {{.Names}}" | grep -v NAMES | wc -l)

if [ "$SUPABASE_CONTAINERS" -eq 0 ]; then
    echo "❌ No Supabase containers are running locally."
    echo "Please start your local Supabase instance first:"
    echo "  supabase start"
    exit 1
fi

echo "✅ Found $SUPABASE_CONTAINERS Supabase container(s) running"

# Ensure admin user exists
echo "Ensuring admin user exists..."
npx supabase db execute --query "
INSERT INTO users (id, firebase_uid, email, name, rank, created_at, updated_at)
VALUES (gen_random_uuid(), 'admin_mcclain_thiel_gmail_com', 'mcclain.thiel@gmail.com', 'Admin User', 'admin', NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET rank = 'admin', updated_at = NOW();
" --local || echo "⚠️ Admin user creation failed (may already exist)"

# Build the Docker container
echo "Building Docker container..."
docker build -t dead-simpl-backend .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker build successful"

# Run the container with hot reload
echo "Starting FastAPI app with hot reload..."
docker run -it --rm \
    -p 8000:8000 \
    --network supabase_network_dead-simpl-backend \
    --env-file .env \
    -v "$(pwd)/app:/app/app" \
    dead-simpl-backend \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo "🚀 Application started at http://localhost:8000"
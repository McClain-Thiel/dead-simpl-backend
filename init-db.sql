-- Initialize the database for local development
-- This script runs when the PostgreSQL container starts for the first time

-- Create the auth schema (to mimic Supabase structure)
CREATE SCHEMA IF NOT EXISTS auth;

-- Create a basic users table in auth schema (simplified version of Supabase auth.users)
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create some sample users for development
INSERT INTO auth.users (id, email, encrypted_password) 
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'hashed_password_here'),
    ('550e8400-e29b-41d4-a716-446655440001', 'dev@example.com', 'hashed_password_here')
ON CONFLICT (email) DO NOTHING;

-- The public schema tables will be created by Alembic migrations
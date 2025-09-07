-- Insert admin user
-- This script creates an admin user with the specified Firebase UID and email

INSERT INTO users (
    id,
    firebase_uid,
    email,
    name,
    rank,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'dX4U6sbQgcQWy7bMtPsLIMuptkn1',
    'mcclain.thiel@gmail.com',
    'McClain Thiel',
    'admin',
    NOW(),
    NOW()
) ON CONFLICT (firebase_uid) 
DO UPDATE SET 
    rank = 'admin',
    email = 'mcclain.thiel@gmail.com',
    name = 'McClain Thiel',
    updated_at = NOW();
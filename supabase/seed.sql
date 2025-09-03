-- Seed data for development
-- Insert admin user if they do not already exist
INSERT INTO users (
    id,
    firebase_uid,
    email,
    name,
    rank,
    created_at,
    updated_at
)
SELECT
    gen_random_uuid(),
    'dX4U6sbQgcQWy7bMtPsLIMuptkn1',
    'mcclain.thiel@gmail.com',
    'McClain Thiel',
    'ADMIN'::userrank,
    NOW(),
    NOW()
WHERE
    NOT EXISTS (
        SELECT 1 FROM users WHERE firebase_uid = 'dX4U6sbQgcQWy7bMtPsLIMuptkn1'
    );

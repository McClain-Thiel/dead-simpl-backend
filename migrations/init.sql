CREATE TYPE userrank AS ENUM ('admin', 'user', 'expired', 'waitlist');

CREATE TABLE users (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    firebase_uid VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL,
    name VARCHAR,
    rank userrank NOT NULL DEFAULT 'waitlist',
    deleted_at TIMESTAMP
);

CREATE INDEX ix_users_firebase_uid ON users(firebase_uid);
CREATE INDEX ix_users_email ON users(email);

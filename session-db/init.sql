CREATE SCHEMA IF NOT EXISTS session_schema;
SET search_path TO session_schema;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp"
SCHEMA session_schema;

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    expires_at TIMESTAMP
);

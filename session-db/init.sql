CREATE SCHEMA IF NOT EXISTS session_schema;
SET search_path TO session_schema;

CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,  -- Unique session identifier
    -- user_id INT,                       -- Optional: if sessions are user-specific
    session_data JSONB,                    -- Serialized session data (JSON, base64, or other)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Session creation time
    updated_at TIMESTAMP,                 -- Last time the session was updated
    expires_at TIMESTAMP,                 -- When the session expires
    -- user_agent VARCHAR(255),              -- Optional: store user-agent or device info
    -- ip_address VARCHAR(45),               -- Optional: store the user's IP address (IPv4/IPv6)
    INDEX (expires_at)                    -- Index for quick session cleanup of expired sessions
);

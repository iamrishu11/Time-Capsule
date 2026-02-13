-- ============================================
-- Time Capsule PostgreSQL DDL Script
-- Azure PostgreSQL Database Schema
-- ============================================
-- Run this script directly on your Azure PostgreSQL database
-- Database: postgres
-- ============================================

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS delivery_logs CASCADE;
DROP TABLE IF EXISTS capsule_recipients CASCADE;
DROP TABLE IF EXISTS capsule_guardians CASCADE;
DROP TABLE IF EXISTS attachments CASCADE;
DROP TABLE IF EXISTS heartbeat_checks CASCADE;
DROP TABLE IF EXISTS capsules CASCADE;
DROP TABLE IF EXISTS guardians CASCADE;
DROP TABLE IF EXISTS recipients CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- USERS TABLE
-- Account owners who create and manage time capsules
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_users_email ON users(email);

-- ============================================
-- RECIPIENTS TABLE
-- People who will receive time capsules
-- ============================================
CREATE TABLE recipients (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    relation VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_recipients_owner_id ON recipients(owner_id);

-- ============================================
-- GUARDIANS TABLE
-- Trusted verifiers for event-based capsule releases
-- ============================================
CREATE TABLE guardians (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    relation VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_guardians_owner_id ON guardians(owner_id);

-- ============================================
-- CAPSULES TABLE
-- Core entity containing encrypted messages
-- ============================================
CREATE TABLE capsules (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message_encrypted TEXT NOT NULL,
    release_type VARCHAR(20) NOT NULL DEFAULT 'TIME',
    release_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    requires_guardian BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_release_type CHECK (release_type IN ('TIME', 'EVENT')),
    CONSTRAINT chk_status CHECK (status IN ('DRAFT', 'SCHEDULED', 'SENT', 'CANCELLED'))
);

CREATE INDEX ix_capsule_owner_status ON capsules(owner_id, status);
CREATE INDEX ix_capsule_release ON capsules(release_type, release_at);

-- ============================================
-- CAPSULE_RECIPIENTS TABLE
-- Junction table for Capsule-Recipient many-to-many relationship
-- ============================================
CREATE TABLE capsule_recipients (
    id SERIAL PRIMARY KEY,
    capsule_id INTEGER NOT NULL REFERENCES capsules(id) ON DELETE CASCADE,
    recipient_id INTEGER NOT NULL REFERENCES recipients(id) ON DELETE CASCADE,
    
    CONSTRAINT uq_capsule_recipient UNIQUE (capsule_id, recipient_id)
);

CREATE INDEX ix_capsule_recipients_capsule_id ON capsule_recipients(capsule_id);
CREATE INDEX ix_capsule_recipients_recipient_id ON capsule_recipients(recipient_id);

-- ============================================
-- CAPSULE_GUARDIANS TABLE
-- Junction table for Capsule-Guardian many-to-many relationship
-- ============================================
CREATE TABLE capsule_guardians (
    id SERIAL PRIMARY KEY,
    capsule_id INTEGER NOT NULL REFERENCES capsules(id) ON DELETE CASCADE,
    guardian_id INTEGER NOT NULL REFERENCES guardians(id) ON DELETE CASCADE,
    
    CONSTRAINT uq_capsule_guardian UNIQUE (capsule_id, guardian_id)
);

CREATE INDEX ix_capsule_guardians_capsule_id ON capsule_guardians(capsule_id);
CREATE INDEX ix_capsule_guardians_guardian_id ON capsule_guardians(guardian_id);

-- ============================================
-- ATTACHMENTS TABLE
-- Files (photos, videos, documents) linked to capsules
-- ============================================
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    capsule_id INTEGER NOT NULL REFERENCES capsules(id) ON DELETE CASCADE,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100),
    size_bytes BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_attachments_capsule_id ON attachments(capsule_id);
CREATE INDEX ix_attachments_owner_id ON attachments(owner_id);

-- ============================================
-- DELIVERY_LOGS TABLE
-- Records of capsule delivery attempts
-- ============================================
CREATE TABLE delivery_logs (
    id SERIAL PRIMARY KEY,
    capsule_id INTEGER NOT NULL REFERENCES capsules(id) ON DELETE CASCADE,
    recipient_id INTEGER REFERENCES recipients(id) ON DELETE SET NULL,
    scheduled_for TIMESTAMP NOT NULL,
    delivered_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    error_message TEXT,
    
    CONSTRAINT chk_delivery_status CHECK (status IN ('PENDING', 'SENT', 'FAILED'))
);

CREATE INDEX ix_delivery_status_scheduled ON delivery_logs(status, scheduled_for);

-- ============================================
-- HEARTBEAT_CHECKS TABLE
-- Periodic "still alive?" pings for inactivity-based triggers
-- ============================================
CREATE TABLE heartbeat_checks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ping_sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ping_confirmed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'AWAITING',
    
    CONSTRAINT chk_heartbeat_status CHECK (status IN ('AWAITING', 'CONFIRMED', 'EXPIRED'))
);

CREATE INDEX ix_heartbeat_status ON heartbeat_checks(status);
CREATE INDEX ix_heartbeat_user_id ON heartbeat_checks(user_id);

-- ============================================
-- TRIGGER FUNCTION: Update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recipients_updated_at
    BEFORE UPDATE ON recipients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_guardians_updated_at
    BEFORE UPDATE ON guardians
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_capsules_updated_at
    BEFORE UPDATE ON capsules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- GRANT PERMISSIONS (adjust as needed)
-- ============================================
-- These commands grant permissions to the database user
-- You may need to modify based on your Azure PostgreSQL setup

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO prodtestdb;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO prodtestdb;

-- ============================================
-- VERIFICATION QUERY
-- Run this to verify all tables were created
-- ============================================
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

COMMENT ON TABLE users IS 'Account owners who create and manage time capsules';
COMMENT ON TABLE recipients IS 'People who will receive capsules (e.g., children, friends)';
COMMENT ON TABLE guardians IS 'Trusted verifiers for event-based capsule releases';
COMMENT ON TABLE capsules IS 'Core entity containing encrypted messages and metadata';
COMMENT ON TABLE capsule_recipients IS 'Junction table for Capsule-Recipient many-to-many relationship';
COMMENT ON TABLE capsule_guardians IS 'Junction table for Capsule-Guardian many-to-many relationship';
COMMENT ON TABLE attachments IS 'Files (photos, videos, documents) linked to capsules';
COMMENT ON TABLE delivery_logs IS 'Records of capsule delivery attempts';
COMMENT ON TABLE heartbeat_checks IS 'Periodic still alive pings for inactivity-based triggers';

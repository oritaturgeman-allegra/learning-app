-- Supabase Schema for Capital Market Newsletter
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/[your-project]/sql
--
-- Tables are created in order to respect foreign key constraints.
-- This schema matches the SQLAlchemy models in backend/models/

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
-- Stores user accounts with email/password and Google OAuth support

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    preferred_categories TEXT DEFAULT '["us","israel","ai","crypto"]' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_login_at TIMESTAMPTZ,
    password_hash VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    verification_token VARCHAR(64) UNIQUE,
    verification_token_expires_at TIMESTAMPTZ,
    email_notifications BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for email lookups (login, verification)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- 2. NEWSLETTERS TABLE
-- ============================================================================
-- Stores generated newsletter metadata and AI content

CREATE TABLE IF NOT EXISTS newsletters (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    sentiment TEXT,  -- JSON: {"us": 65, "israel": 48, "ai": 72, "crypto": 55}
    language VARCHAR(5) DEFAULT 'en' NOT NULL,
    podcast_dialog TEXT,  -- JSON: [["female", "Hello..."], ["male", "Today..."]]
    llm_provider VARCHAR(50),
    tts_provider VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for user newsletters and ordering
CREATE INDEX IF NOT EXISTS idx_newsletters_user_id ON newsletters(user_id);
CREATE INDEX IF NOT EXISTS idx_newsletters_created_at ON newsletters(created_at DESC);

-- ============================================================================
-- 3. ARTICLES TABLE
-- ============================================================================
-- Stores individual news articles linked to newsletters

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    newsletter_id INTEGER NOT NULL REFERENCES newsletters(id) ON DELETE CASCADE,
    category VARCHAR(20) NOT NULL,  -- us, israel, ai, crypto
    source VARCHAR(100) NOT NULL,   -- Yahoo Finance, Globes, etc.
    confidence_score FLOAT DEFAULT 0.0 NOT NULL,  -- LLM-assigned quality score (0.0-1.0)
    ai_title TEXT NOT NULL,
    text TEXT,
    link VARCHAR(1000) NOT NULL,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for filtering and ordering
CREATE INDEX IF NOT EXISTS idx_articles_newsletter_id ON articles(newsletter_id);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_fetched_at ON articles(fetched_at);

-- ============================================================================
-- 4. FEED PROVIDERS TABLE
-- ============================================================================
-- Tracks RSS feed reliability statistics over time

CREATE TABLE IF NOT EXISTS feed_providers (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    feed_url VARCHAR(500),
    category VARCHAR(20) NOT NULL,
    success_count INTEGER DEFAULT 0 NOT NULL,
    total_runs INTEGER DEFAULT 0 NOT NULL,
    reliability FLOAT DEFAULT 0.0 NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(source_name, category)
);

-- ============================================================================
-- 5. PODCAST GENERATIONS TABLE
-- ============================================================================
-- Tracks on-demand podcast generation for daily limits

CREATE TABLE IF NOT EXISTS podcast_generations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    categories TEXT NOT NULL,  -- JSON: ["us", "ai"]
    cache_key VARCHAR(64) NOT NULL,
    cached BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for user lookup and date filtering
CREATE INDEX IF NOT EXISTS idx_podcast_generations_user_id ON podcast_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_podcast_generations_created_at ON podcast_generations(created_at);

-- ============================================================================
-- VERIFICATION QUERIES (run after creation to verify)
-- ============================================================================

-- Check all tables were created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check foreign key constraints
-- SELECT
--     tc.table_name,
--     kcu.column_name,
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name
-- FROM information_schema.table_constraints AS tc
-- JOIN information_schema.key_column_usage AS kcu
--     ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--     ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY';

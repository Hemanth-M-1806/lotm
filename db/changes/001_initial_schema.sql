-- 001_initial_schema.sql
-- Description: Initial schema for LOTM Tarot application
-- Applied: In transaction

BEGIN;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Migration version tracker
CREATE TABLE IF NOT EXISTS schema_versions (
    version VARCHAR(50) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Canonical Lore Tables (Read-Heavy / Immutable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS pathways (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    chinese_name VARCHAR(50),
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sequences (
    id SERIAL PRIMARY KEY,
    pathway_id INT NOT NULL REFERENCES pathways(id) ON DELETE RESTRICT,
    sequence_number SMALLINT NOT NULL CHECK (sequence_number BETWEEN 0 AND 9),
    name VARCHAR(50) NOT NULL,
    acting_method_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_pathway_sequence UNIQUE (pathway_id, sequence_number)
);

CREATE INDEX IF NOT EXISTS idx_sequences_pathway_id ON sequences(pathway_id);

CREATE TABLE IF NOT EXISTS tarot_cards (
    id SMALLINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    arcana_type VARCHAR(10) NOT NULL CHECK (arcana_type IN ('major', 'minor')),
    suit VARCHAR(20) CHECK (suit IN ('wands', 'cups', 'swords', 'pentacles')),
    card_number SMALLINT NOT NULL,
    pathway_id INT REFERENCES pathways(id) ON DELETE SET NULL,
    upright_meaning TEXT NOT NULL,
    reversed_meaning TEXT NOT NULL,
    mystical_lore TEXT,
    image_asset_path VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tarot_cards_pathway_id ON tarot_cards(pathway_id);

-- ============================================================================
-- User & Preference Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(50) NOT NULL DEFAULT 'backlund_dark',
    preferred_deck_style VARCHAR(50) NOT NULL DEFAULT 'victorian_anime',
    default_spread VARCHAR(50) NOT NULL DEFAULT 'three_card',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Consultation & Reading Tables (User-Generated)
-- ============================================================================

CREATE TABLE IF NOT EXISTS readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    spread_type VARCHAR(50) NOT NULL,
    question TEXT,
    interpretation TEXT,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_readings_user_created ON readings(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS reading_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reading_id UUID NOT NULL REFERENCES readings(id) ON DELETE CASCADE,
    card_id SMALLINT NOT NULL REFERENCES tarot_cards(id) ON DELETE RESTRICT,
    position_index SMALLINT NOT NULL,
    position_name VARCHAR(50) NOT NULL,
    is_reversed BOOLEAN NOT NULL DEFAULT FALSE,
    card_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_reading_position UNIQUE (reading_id, position_index)
);

CREATE INDEX IF NOT EXISTS idx_reading_cards_reading_id ON reading_cards(reading_id);

-- Record version in registry
INSERT INTO schema_versions (version, description)
VALUES ('001', 'Initial schema: lore, users, readings')
ON CONFLICT (version) DO NOTHING;

COMMIT;

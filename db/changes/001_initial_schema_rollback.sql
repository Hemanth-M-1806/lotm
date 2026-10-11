-- 001_initial_schema_rollback.sql
-- Description: Rollback for initial schema
-- WARNING: Destructive. Drops all core tables and data.
-- Applied: In transaction

BEGIN;

DROP TABLE IF EXISTS reading_cards CASCADE;
DROP TABLE IF EXISTS readings CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS tarot_cards CASCADE;
DROP TABLE IF EXISTS sequences CASCADE;
DROP TABLE IF EXISTS pathways CASCADE;

DELETE FROM schema_versions WHERE version = '001';

COMMIT;

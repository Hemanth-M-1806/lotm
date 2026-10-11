-- 001_initial_schema_verify.sql
-- Verification queries to validate schema integrity and seed completeness

-- 1. Check schema versions table
SELECT version, description, applied_at FROM schema_versions WHERE version = '001';

-- 2. Verify table existence
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('schema_versions', 'pathways', 'sequences', 'tarot_cards', 'users', 'user_preferences', 'readings', 'reading_cards')
ORDER BY table_name;

-- 3. Verify canonical seeds counts
SELECT 
    (SELECT COUNT(*) FROM pathways) AS pathways_count,
    (SELECT COUNT(*) FROM tarot_cards WHERE arcana_type = 'major') AS major_arcana_count;

-- 4. Verify indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND tablename IN ('sequences', 'tarot_cards', 'readings', 'reading_cards')
ORDER BY tablename, indexname;

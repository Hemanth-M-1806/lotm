from pathlib import Path
import unittest

class TestSQLMigrations(unittest.TestCase):
    def setUp(self):
        # Resolve repo root relative to this test file
        self.repo_root = Path(__file__).resolve().parent.parent.parent

    def test_initial_schema_migration_files_exist(self):
        schema_file = self.repo_root / "db" / "changes" / "001_initial_schema.sql"
        rollback_file = self.repo_root / "db" / "changes" / "001_initial_schema_rollback.sql"
        seed_file = self.repo_root / "db" / "seeds" / "001_canonical_lore.sql"

        self.assertTrue(schema_file.exists(), f"Missing {schema_file}")
        self.assertTrue(rollback_file.exists(), f"Missing {rollback_file}")
        self.assertTrue(seed_file.exists(), f"Missing {seed_file}")

    def test_sql_files_are_transactional(self):
        sql_files = [
            self.repo_root / "db" / "changes" / "001_initial_schema.sql",
            self.repo_root / "db" / "changes" / "001_initial_schema_rollback.sql",
            self.repo_root / "db" / "seeds" / "001_canonical_lore.sql",
        ]
        for sql_path in sql_files:
            content = sql_path.read_text(encoding="utf-8")
            self.assertIn("BEGIN;", content, f"{sql_path.name} missing BEGIN transaction")
            self.assertIn("COMMIT;", content, f"{sql_path.name} missing COMMIT transaction")

    def test_schema_defines_all_domain_tables(self):
        schema_file = self.repo_root / "db" / "changes" / "001_initial_schema.sql"
        content = schema_file.read_text(encoding="utf-8")
        expected_tables = [
            "schema_versions",
            "pathways",
            "sequences",
            "tarot_cards",
            "users",
            "user_preferences",
            "readings",
            "reading_cards",
        ]
        for table in expected_tables:
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", content)

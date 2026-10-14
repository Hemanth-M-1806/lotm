import os
import unittest
from unittest.mock import patch

class TestConfig(unittest.TestCase):
    def test_settings_load_defaults(self):
        from app.core.config import Settings
        settings = Settings(
            _env_file=None,
            DATABASE_URL="postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot",
            SECRET_KEY="supersecretkeythatislongerthanthirtytwochars"
        )
        self.assertEqual(settings.ENVIRONMENT, "development")
        self.assertEqual(settings.API_V1_PREFIX, "/api/v1")
        self.assertEqual(settings.DB_POOL_SIZE, 5)
        self.assertTrue(settings.DB_POOL_PRE_PING)

    def test_settings_fail_on_invalid_db_scheme(self):
        from app.core.config import Settings
        with self.assertRaises(ValueError):
            Settings(
                DATABASE_URL="mysql://root:secret@localhost/db",
                SECRET_KEY="supersecretkeythatislongerthanthirtytwochars"
            )

    def test_settings_fail_on_short_secret_key(self):
        from app.core.config import Settings
        with self.assertRaises(ValueError):
            Settings(
                DATABASE_URL="postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot",
                SECRET_KEY="short"
            )

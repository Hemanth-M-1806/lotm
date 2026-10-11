import unittest
from unittest.mock import patch, MagicMock
from app.core.config import Settings
from app.core.database import get_engine, get_sessionmaker, close_db_engine, _engine

class TestDatabaseInfrastructure(unittest.TestCase):
    def tearDown(self):
        import app.core.database as db_mod
        db_mod._engine = None
        db_mod._sessionmaker = None

    @patch("app.core.database.get_settings")
    @patch("app.core.database.create_async_engine")
    def test_engine_initialization_with_settings(self, mock_create_engine, mock_get_settings):
        mock_settings = Settings(
            DATABASE_URL="postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot",
            SECRET_KEY="supersecretkeythatislongerthanthirtytwochars",
            DB_POOL_SIZE=12,
            DB_MAX_OVERFLOW=6
        )
        mock_get_settings.return_value = mock_settings
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        engine = get_engine()
        self.assertEqual(engine, mock_engine)
        mock_create_engine.assert_called_once_with(
            mock_settings.DATABASE_URL,
            echo=False,
            pool_size=12,
            max_overflow=6,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )

        session_factory = get_sessionmaker()
        self.assertIsNotNone(session_factory)

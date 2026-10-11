import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

class TestAPIFoundations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set dummy env vars for testing
        import os
        os.environ["DATABASE_URL"] = "postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot"
        os.environ["SECRET_KEY"] = "supersecretkeythatislongerthanthirtytwochars"

    def test_liveness_probe_returns_200(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/health/live")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("timestamp", data)
        self.assertIn("x-request-id", response.headers)

    def test_request_id_header_propagated(self):
        from app.main import app
        client = TestClient(app)
        custom_id = "test-request-id-12345"
        response = client.get("/health/live", headers={"X-Request-ID": custom_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("x-request-id"), custom_id)

    @patch("app.api.health.get_engine")
    def test_readiness_probe_healthy(self, mock_get_engine):
        from app.main import app
        client = TestClient(app)

        # Mock successful database ping
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        mock_conn.__aenter__.return_value = mock_conn
        mock_conn.__aexit__.return_value = None

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        response = client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ready")
        self.assertEqual(data.get("database"), "healthy")

    @patch("app.api.health.get_engine")
    def test_readiness_probe_unhealthy_returns_503(self, mock_get_engine):
        from app.main import app
        client = TestClient(app)

        # Mock database connection failure
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = Exception("Connection refused")
        mock_get_engine.return_value = mock_engine

        response = client.get("/health/ready")
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data.get("status"), "not_ready")
        self.assertEqual(data.get("database"), "unreachable")

    def test_centralized_error_envelope_on_404(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/v1/nonexistent-route")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "NOT_FOUND")
        self.assertIn("request_id", data["error"])

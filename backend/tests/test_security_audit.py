import os
import time
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot"
os.environ["SECRET_KEY"] = "supersecretkeythatislongerthanthirtytwochars"

from app.core.database import get_db_session
from app.core.rate_limit import auth_rate_limiter
from app.core.security import create_access_token, decode_access_token
from app.main import app
from app.models.card import TarotCard
from app.models.reading import Reading, ReadingCard
from app.models.user import User


class TestSecurityAuditAndBoundaries(unittest.TestCase):
    def setUp(self):
        auth_rate_limiter.reset()
        self.client = TestClient(app)
        self.user_a_id = uuid.uuid4()
        self.user_b_id = uuid.uuid4()
        self.token_a = create_access_token(subject=str(self.user_a_id))
        self.token_b = create_access_token(subject=str(self.user_b_id))

        self.mock_user_a = User(
            id=self.user_a_id,
            username="klein_moretti",
            email="klein@backlund.mysteries",
            display_name="The Fool",
            password_hash="fakehash",
            email_verified=True,
            created_at=datetime.now(timezone.utc),
        )
        self.mock_user_b = User(
            id=self.user_b_id,
            username="amon_error",
            email="amon@marauder.lore",
            display_name="Blasphemer",
            password_hash="fakehash",
            email_verified=True,
            created_at=datetime.now(timezone.utc),
        )

    def tearDown(self):
        app.dependency_overrides.clear()
        auth_rate_limiter.reset()

    # ─────────────────────────────────────────────────────────────
    # OWASP A05: Security Headers & Error Envelopes
    # ─────────────────────────────────────────────────────────────
    def test_security_headers_present_on_responses(self):
        res = self.client.get("/health/live")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(res.headers.get("X-XSS-Protection"), "0")
        self.assertEqual(res.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("default-src 'self'", res.headers.get("Content-Security-Policy", ""))
        self.assertIn("X-Request-ID", res.headers)

    # ─────────────────────────────────────────────────────────────
    # OWASP A07: Rate Limiting on Authentication Endpoints
    # ─────────────────────────────────────────────────────────────
    def test_auth_rate_limiting_enforcement(self):
        """Verify that requests exceeding 10 per minute receive HTTP 429."""
        # 10 allowed requests (which will fail validation or auth, but pass rate limiter)
        for i in range(10):
            res = self.client.post(
                "/api/v1/auth/login",
                json={"identifier": f"user_{i}", "password": "password"},
                headers={"X-Forwarded-For": "192.168.1.100"},
            )
            self.assertNotEqual(res.status_code, 429)

        # 11th request from the same IP must be rejected with 429
        blocked_res = self.client.post(
            "/api/v1/auth/login",
            json={"identifier": "user_overflow", "password": "password"},
            headers={"X-Forwarded-For": "192.168.1.100"},
        )
        self.assertEqual(blocked_res.status_code, 429)
        data = blocked_res.json()
        self.assertEqual(data["error"]["code"], "RATE_LIMIT_EXCEEDED")
        self.assertIn("Rate limit exceeded", data["error"]["message"])

        # Different IP address is not blocked
        other_ip_res = self.client.post(
            "/api/v1/auth/login",
            json={"identifier": "user_other", "password": "password"},
            headers={"X-Forwarded-For": "192.168.1.101"},
        )
        self.assertNotEqual(other_ip_res.status_code, 429)

    # ─────────────────────────────────────────────────────────────
    # OWASP A01: Broken Access Control & IDOR Protection
    # ─────────────────────────────────────────────────────────────
    def test_idor_reading_isolation_between_users(self):
        """User B cannot view or modify User A's private divination reading."""
        reading_id = uuid.uuid4()

        async def override_db():
            mock_session = AsyncMock()
            mock_res_user = MagicMock()
            # Returns User B as authenticated caller
            mock_res_user.scalar_one_or_none.return_value = self.mock_user_b

            mock_res_reading = MagicMock()
            # Database query filters by (id == reading_id) AND (user_id == user_b_id), returning None
            mock_res_reading.scalar_one_or_none.return_value = None

            mock_session.execute.side_effect = [mock_res_user, mock_res_reading]
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db

        # User B attempts to access reading belonging to User A
        res = self.client.get(
            f"/api/v1/readings/{reading_id}",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["error"]["code"], "NOT_FOUND")

    def test_idor_reading_favorite_isolation(self):
        """User B cannot favorite/unfavorite User A's reading."""
        reading_id = uuid.uuid4()

        async def override_db():
            mock_session = AsyncMock()
            mock_res_user = MagicMock()
            mock_res_user.scalar_one_or_none.return_value = self.mock_user_b

            mock_res_reading = MagicMock()
            mock_res_reading.scalar_one_or_none.return_value = None

            mock_session.execute.side_effect = [mock_res_user, mock_res_reading]
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db

        res = self.client.patch(
            f"/api/v1/readings/{reading_id}/favorite",
            json={"is_favorite": True},
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["error"]["code"], "NOT_FOUND")

    def test_unauthenticated_user_cannot_access_reading_history(self):
        res = self.client.get("/api/v1/readings")
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()["error"]["code"], "UNAUTHORIZED")

    # ─────────────────────────────────────────────────────────────
    # OWASP A02: Cryptographic Token Integrity & Tampering
    # ─────────────────────────────────────────────────────────────
    def test_tampered_token_signature_rejected(self):
        tampered_token = self.token_a[:-5] + "aaaaa"
        with self.assertRaises(Exception):
            decode_access_token(tampered_token)

        res = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tampered_token}"},
        )
        self.assertEqual(res.status_code, 401)

    def test_expired_token_rejected(self):
        expired_token = create_access_token(
            subject=str(self.user_a_id),
            expires_minutes=-10,
        )
        res = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        self.assertEqual(res.status_code, 401)

    def test_malformed_token_header_rejected(self):
        for bad_header in ["Bearer", "NotBearer token123", "Bearer ", ""]:
            res = self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": bad_header} if bad_header else {},
            )
            self.assertEqual(res.status_code, 401)

    # ─────────────────────────────────────────────────────────────
    # OWASP A03: SQL Injection Safety
    # ─────────────────────────────────────────────────────────────
    def test_sql_injection_payloads_in_reading_inputs(self):
        """Verify SQL injection strings are treated strictly as literals."""
        sqli_payloads = [
            "'; DROP TABLE readings; --",
            "' OR '1'='1",
            "admin' --",
            "1; SELECT pg_sleep(5); --",
            "UNION ALL SELECT NULL, username, password_hash FROM users --",
        ]
        card = TarotCard(
            id=1,
            name="The Fool",
            arcana_type="major",
            card_number=0,
            upright_meaning="Beginnings",
            reversed_meaning="Folly",
        )

        for payload in sqli_payloads:
            async def override_db():
                mock_session = AsyncMock()
                mock_session.add = MagicMock()
                mock_res_cards = MagicMock()
                mock_res_cards.scalars.return_value.all.return_value = [card]
                mock_session.execute.return_value = mock_res_cards
                mock_session.flush = AsyncMock()
                mock_session.commit = AsyncMock()
                mock_session.refresh = AsyncMock()
                yield mock_session

            app.dependency_overrides[get_db_session] = override_db

            # Question contains SQL injection vectors
            res = self.client.post(
                "/api/v1/readings",
                json={
                    "spread_type": "single_card",
                    "question": payload,
                },
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()
            # Verifies string was cleanly preserved as literal text without database interpretation
            self.assertEqual(data["question"], payload)

    # ─────────────────────────────────────────────────────────────
    # OWASP A04: Mass Assignment Protection
    # ─────────────────────────────────────────────────────────────
    def test_mass_assignment_fields_ignored_in_registration(self):
        """Client cannot elevate privileges or set protected user fields."""
        async def override_db():
            mock_session = AsyncMock()
            mock_session.add = MagicMock()
            mock_res = MagicMock()
            mock_res.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_res
            mock_session.flush = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db

        res = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": "miss_justice",
                "email": "justice@backlund.nobles",
                "display_name": "Audrey",
                "password": "SpectatorPathway123!",
                "id": str(uuid.uuid4()),
                "email_verified": True,
                "role": "admin",
                "is_superuser": True,
                "password_hash": "$2b$12$maliciousprecomputedhashhere",
            },
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()["user"]
        # In Pydantic schema UserRead, email_verified defaults to False for fresh user
        self.assertFalse(data["email_verified"])
        self.assertNotIn("role", data)
        self.assertNotIn("password_hash", data)

    # ─────────────────────────────────────────────────────────────
    # Negative Input Boundary Tests
    # ─────────────────────────────────────────────────────────────
    def test_invalid_spread_type_rejected(self):
        res = self.client.post(
            "/api/v1/readings",
            json={"spread_type": "astrology_wheel_nonexistent"},
        )
        self.assertEqual(res.status_code, 422)

    def test_oversized_question_rejected(self):
        res = self.client.post(
            "/api/v1/readings",
            json={
                "spread_type": "single_card",
                "question": "A" * 501,  # Exceeds max_length 500
            },
        )
        self.assertEqual(res.status_code, 422)

    def test_pagination_boundary_limits(self):
        """Negative or excessive pagination values are rejected by FastAPI validation."""
        from app.api.deps import get_current_user
        app.dependency_overrides[get_current_user] = lambda: self.mock_user_a

        # Page size > 50 (le=50)
        res = self.client.get(
            "/api/v1/readings?page_size=51",
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        self.assertEqual(res.status_code, 422)

        # Page size <= 0 (ge=1)
        res = self.client.get(
            "/api/v1/readings?page_size=0",
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        self.assertEqual(res.status_code, 422)

        # Page < 1 (ge=1)
        res = self.client.get(
            "/api/v1/readings?page=0",
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        self.assertEqual(res.status_code, 422)

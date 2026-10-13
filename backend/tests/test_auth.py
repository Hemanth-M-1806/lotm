import os
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot"
os.environ["SECRET_KEY"] = "supersecretkeythatislongerthanthirtytwochars"

from app.core.database import get_db_session
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User


class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_user_id = uuid.uuid4()
        self.hashed_pw = hash_password("ValidPass123!")
        from datetime import datetime, timezone
        self.mock_user = User(
            id=self.mock_user_id,
            username="klein_moretti",
            email="klein@backlund.mysteries",
            display_name="The Fool",
            password_hash=self.hashed_pw,
            email_verified=False,
            created_at=datetime.now(timezone.utc),
        )

    def test_registration_validation_errors(self):
        # Invalid email
        res = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": "klein",
                "email": "not-an-email",
                "display_name": "Klein",
                "password": "Password123!",
            },
        )
        self.assertEqual(res.status_code, 422)

        # Password too short (< 8 chars)
        res = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": "klein",
                "email": "klein@backlund.com",
                "display_name": "Klein",
                "password": "short",
            },
        )
        self.assertEqual(res.status_code, 422)

        # Username with invalid characters
        res = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": "klein moretti!",
                "email": "klein@backlund.com",
                "display_name": "Klein",
                "password": "Password123!",
            },
        )
        self.assertEqual(res.status_code, 422)

    def test_registration_success(self):
        async def override_db():
            mock_session = AsyncMock()
            mock_session.add = MagicMock()
            # Username and email check queries return None (no collision)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            mock_session.flush = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.post(
                "/api/v1/auth/register",
                json={
                    "username": "audrey_hall",
                    "email": "audrey@backlund.nobles",
                    "display_name": "Miss Justice",
                    "password": "SpectatorPathway123!",
                },
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()
            self.assertIn("access_token", data)
            self.assertEqual(data["token_type"], "bearer")
            self.assertEqual(data["user"]["username"], "audrey_hall")
            self.assertEqual(data["user"]["display_name"], "Miss Justice")
            self.assertNotIn("password_hash", data["user"])
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_registration_duplicate_username_conflict(self):
        async def override_db():
            mock_session = AsyncMock()
            mock_result = MagicMock()
            # Returns existing user on first check (username)
            mock_result.scalar_one_or_none.return_value = self.mock_user
            mock_session.execute.return_value = mock_result
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.post(
                "/api/v1/auth/register",
                json={
                    "username": "klein_moretti",
                    "email": "another@backlund.com",
                    "display_name": "Klein",
                    "password": "ValidPassword123!",
                },
            )
            self.assertEqual(res.status_code, 409)
            data = res.json()
            self.assertEqual(data["error"]["code"], "CONFLICT")
            self.assertIn("Username is already taken", data["error"]["message"])
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_login_success(self):
        async def override_db():
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = self.mock_user
            mock_session.execute.return_value = mock_result
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.post(
                "/api/v1/auth/login",
                json={
                    "username_or_email": "klein_moretti",
                    "password": "ValidPass123!",
                },
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("access_token", data)
            self.assertEqual(data["token_type"], "bearer")
            self.assertEqual(data["user"]["username"], "klein_moretti")
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_login_failure_invalid_password_returns_401(self):
        async def override_db():
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = self.mock_user
            mock_session.execute.return_value = mock_result
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.post(
                "/api/v1/auth/login",
                json={
                    "username_or_email": "klein_moretti",
                    "password": "WrongPassword999!",
                },
            )
            self.assertEqual(res.status_code, 401)
            data = res.json()
            self.assertEqual(data["error"]["code"], "UNAUTHORIZED")
            self.assertEqual(data["error"]["message"], "Invalid username or password")
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_login_failure_nonexistent_user_returns_identical_401(self):
        async def override_db():
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.post(
                "/api/v1/auth/login",
                json={
                    "username_or_email": "ghost_user",
                    "password": "SomePassword123!",
                },
            )
            self.assertEqual(res.status_code, 401)
            data = res.json()
            self.assertEqual(data["error"]["code"], "UNAUTHORIZED")
            # Uniform error prevents account enumeration
            self.assertEqual(data["error"]["message"], "Invalid username or password")
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_me_endpoint_with_valid_token(self):
        token = create_access_token(subject=str(self.mock_user_id))

        async def override_db():
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = self.mock_user
            mock_session.execute.return_value = mock_result
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["id"], str(self.mock_user_id))
            self.assertEqual(data["username"], "klein_moretti")
            self.assertNotIn("password_hash", data)
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_me_endpoint_without_token_returns_401(self):
        res = self.client.get("/api/v1/auth/me")
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertEqual(data["error"]["code"], "UNAUTHORIZED")

    def test_me_endpoint_with_expired_token_returns_401(self):
        expired_token = create_access_token(
            subject=str(self.mock_user_id),
            expires_minutes=-5,
        )
        res = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertEqual(data["error"]["code"], "UNAUTHORIZED")

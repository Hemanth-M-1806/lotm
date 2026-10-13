import os
import time
import unittest

os.environ["DATABASE_URL"] = "postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot"
os.environ["SECRET_KEY"] = "supersecretkeythatislongerthanthirtytwochars"

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_dummy_password,
    verify_password,
)


class TestSecurityUnit(unittest.TestCase):
    def test_password_hash_and_verify(self):
        password = "MysticalKleinMoretti123!"
        hashed = hash_password(password)

        self.assertTrue(hashed.startswith("$2b$12$"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))

    def test_password_length_cap_prevents_dos(self):
        huge_password = "A" * 150
        with self.assertRaises(ValueError):
            hash_password(huge_password)

    def test_verify_dummy_password_does_not_raise(self):
        try:
            verify_dummy_password("test_dummy_pass")
        except Exception as exc:
            self.fail(f"verify_dummy_password raised an unexpected exception: {exc}")

    def test_create_and_decode_access_token(self):
        subject = "00000000-0000-0000-0000-000000000001"
        token = create_access_token(subject=subject, expires_minutes=15)

        self.assertEqual(len(token.split(".")), 3)
        payload = decode_access_token(token)

        self.assertEqual(payload["sub"], subject)
        self.assertEqual(payload["type"], "access")
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)

    def test_expired_token_raises_authentication_error(self):
        subject = "00000000-0000-0000-0000-000000000001"
        # Expired 10 minutes ago
        token = create_access_token(subject=subject, expires_minutes=-10)

        with self.assertRaises(AuthenticationError) as ctx:
            decode_access_token(token)
        self.assertIn("expired", str(ctx.exception))

    def test_tampered_token_signature_fails(self):
        subject = "00000000-0000-0000-0000-000000000001"
        token = create_access_token(subject=subject, expires_minutes=15)
        header, payload, signature = token.split(".")

        # Tamper with signature
        tampered_sig = signature[:-4] + "AAAA"
        tampered_token = f"{header}.{payload}.{tampered_sig}"

        with self.assertRaises(AuthenticationError):
            decode_access_token(tampered_token)

    def test_tampered_payload_fails(self):
        subject = "00000000-0000-0000-0000-000000000001"
        token = create_access_token(subject=subject, expires_minutes=15)
        header, payload, signature = token.split(".")

        # Alter payload
        tampered_payload = payload[:-2] + "AA"
        tampered_token = f"{header}.{tampered_payload}.{signature}"

        with self.assertRaises(AuthenticationError):
            decode_access_token(tampered_token)

    def test_malformed_token_rejected(self):
        with self.assertRaises(AuthenticationError):
            decode_access_token("not-a-token")

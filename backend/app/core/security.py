import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional
import bcrypt

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

# Pre-computed dummy bcrypt hash (cost 12) used to equalize timing on non-existent accounts
_DUMMY_BCRYPT_HASH = b"$2b$12$e80eX8y7O5oZ9pW6B4qOoeY3fP0v6t9uR1m4qN7sA0c2d3e4f5g6h"


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with 12 rounds."""
    if len(password) > 128:
        raise ValueError("Password exceeds maximum allowed length of 128 characters.")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash in constant time."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def verify_dummy_password(plain_password: str) -> None:
    """Runs a constant-time check on a dummy hash to prevent account enumeration via timing."""
    try:
        bcrypt.checkpw(plain_password.encode("utf-8"), _DUMMY_BCRYPT_HASH)
    except Exception:
        pass


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4)) if (len(data) % 4) != 0 else ""
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def create_access_token(
    subject: str,
    expires_minutes: Optional[int] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Creates a signed HMAC-SHA256 compact JWT token."""
    settings = get_settings()
    now = int(time.time())
    ttl_seconds = (
        expires_minutes * 60
        if expires_minutes is not None
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    exp = now + ttl_seconds

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": exp,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes, verifies signature, and validates expiration for an HMAC-SHA256 JWT."""
    settings = get_settings()
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthenticationError("Invalid token format")

    encoded_header, encoded_payload, encoded_signature = parts

    try:
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        actual_sig = _base64url_decode(encoded_signature)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise AuthenticationError("Token signature verification failed")

        payload_bytes = _base64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except AuthenticationError:
        raise
    except Exception as exc:
        raise AuthenticationError(f"Malformed authentication token: {str(exc)}") from exc

    # Validate expiration
    exp = payload.get("exp")
    if not exp or not isinstance(exp, (int, float)):
        raise AuthenticationError("Token missing expiration claim")
    if int(time.time()) > exp:
        raise AuthenticationError("Authentication token has expired")

    return payload

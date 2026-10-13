# LOTM Tarot App — Security Architecture & Threat Model

## 1. Overview and Threat Model

This document establishes the security baseline and threat model for the Lord of the Mysteries Tarot web application in accordance with §7 and §7.2 of `LOTM_MASTER_PROMPT.md`.

### 1.1 Assets
1. **User Credentials & Passwords**: Highly sensitive; must never be leaked, stored in plaintext, logged, or enumerated.
2. **Personal Tarot Readings & Inquiries**: Private user data and personal reflection history; subject to strict ownership boundaries (anti-IDOR).
3. **Canonical Lore & Card Data**: Intellectual integrity of the 22 Pathways and 22 Major Arcana cards; read-heavy public reference data.
4. **Server Environment Secrets (`SECRET_KEY`, `DATABASE_URL`)**: Server-side confidential material.

### 1.2 Actors
- **Anonymous Visitor / Querent**: Can view public pathways/tarot lore, test health probes, register an account, or authenticate.
- **Authenticated User**: Can initiate tarot readings, review past readings, and manage user preferences.
- **Malicious Threat Actor / Attacker**: Attempts credential stuffing, account enumeration, token tampering, privilege escalation (IDOR), or denial-of-service.

### 1.3 Trust Boundaries & STRIDE Analysis
| Threat Category | Potential Attack Vector | Mitigation in LOTM Architecture |
|---|---|---|
| **Spoofing** | Forged tokens, impersonating user identity | Cryptographically signed tokens (HMAC-SHA256) with strict expiration, signature verification, and secret keys ≥ 32 chars. |
| **Tampering** | Modifying user IDs in tokens or reading requests | Signed tokens protect payload integrity; server-side database ownership checks on every user record. |
| **Repudiation** | Denying authentication or data operations | Structured correlation logging (`X-Request-ID`), tracking timestamp of `last_login` and reading events. |
| **Information Disclosure** | Credential leaks, user enumeration, internal stack traces | Uniform login failure responses ("Invalid username or password"); constant-time verification; centralized error envelope with no internal leakage. |
| **Denial of Service** | bcrypt computation flood, huge payload memory exhaustion | Strict input size limits (e.g. password max 128 chars); connection pool caps; timeout controls. |
| **Elevation of Privilege** | Accessing another user's readings or modifying admin fields | Strict Pydantic input schemas preventing mass-assignment; dependency-based authentication guards enforcing record ownership. |

---

## 2. Authentication Architecture

### 2.1 Password Hashing & Verification
- **Algorithm**: `bcrypt` (adaptive hashing function, cost factor / rounds = 12).
- **Per-Password Salt**: Automatically generated cryptographically random salt per user password.
- **Constant-Time Verification**: Verification executes via `bcrypt.checkpw()` to prevent timing side-channel attacks.
- **Mitigation against User Enumeration**: When a non-existent username/email is provided during login, a dummy bcrypt verification is executed against a pre-computed hash to ensure indistinguishable response time.
- **Password Policy**: Minimum 8 characters, maximum 128 characters (preventing algorithmic complexity attacks).

### 2.2 Token & Session Mechanism
- **Format**: High-integrity compact Bearer tokens encoded with URL-safe Base64 and signed with HMAC-SHA256 (`SECRET_KEY`).
- **Claims**:
  - `sub`: User UUID string
  - `iat`: Unix timestamp of issuance
  - `exp`: Expiration timestamp (default configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
  - `type`: Token category (`access`)
- **Validation**:
  - Signature integrity checked using `hmac.compare_digest` in constant time.
  - Expiration verified against current UTC timestamp.
  - Revocation/User verification: Active user verified in database session.

---

## 3. OWASP Top 10 & API Security Mapping

| Standard | Vulnerability | Applied Architectural Control |
|---|---|---|
| **A01:2021** / **API1:2023** | Broken Access Control / Broken Object Level Auth (BOLA) | Every reading and user record lookup is filtered by authenticated `user_id`. No client-supplied IDs override session identity. |
| **A02:2021** | Cryptographic Failures | Strong secret key validation (≥ 32 chars enforced at startup); HMAC-SHA256 token signatures; bcrypt password hashing. |
| **A03:2021** / **API8:2023** | Injection | Strict SQLAlchemy 2.0 ORM parameterized queries (`select()`). No dynamic string interpolation in SQL. |
| **A04:2021** | Insecure Design | Threat model established before coding; rate-limiting awareness; separation of public lore from user data. |
| **A05:2021** | Security Misconfiguration | Strict CORS origins configured in `.env`; security headers; standardized error envelope masking internal exceptions. |
| **A07:2021** / **API2:2023** | Identification and Authentication Failures | Uniform error messages on auth failure; bounded token expiration; password complexity constraints. |
| **API3:2023** | Broken Object Property Level Auth | Pydantic input schemas separate from ORM models; `password_hash` never returned in schemas. |

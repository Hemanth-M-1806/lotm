# Architecture Decision Log

### ADR-0001: Backend Technology Stack and Driver Selection
- **Context:** The application requires high performance, robust asynchronous I/O, strict validation, and production-grade PostgreSQL support.
- **Decision:** Use Python 3, FastAPI, SQLAlchemy 2.0 (async engine), and Psycopg 3 (`psycopg` binary with `postgresql+psycopg://` async driver).
- **Consequence:** Clean typing via Pydantic v2 and modern SQLAlchemy 2.x declarative syntax; zero reliance on deprecated asyncpg quirks.

### ADR-0002: Direct PostgreSQL Schema Management without Alembic
- **Context:** Per §1.1 permanent constraints, Alembic is omitted unless explicitly requested by the user.
- **Decision:** Manage database migrations through sequential, numbered SQL scripts (`sql/migrations/001_initial.sql`) executed deterministically against PostgreSQL, with recorded version tracking in a dedicated `schema_versions` table.
- **Consequence:** Full transparency over exact DDL, zero framework abstraction friction, strictly reversible changes where feasible.

### ADR-0003: Segregation of Canonical Content from User Readings
- **Context:** Pathways, Sequences, and Tarot Cards represent immutable/canonical world lore, whereas Readings, Querent questions, and Interpretations represent user-generated and privacy-sensitive data.
- **Decision:** Model Pathways, Sequences, and Tarot Cards as reference tables seeded with idempotent versioned scripts. Readings and Reading Cards link to reference data via foreign keys with cascade safety (`ON DELETE RESTRICT` for cards/pathways to protect historical readings).
- **Consequence:** Prevents accidental modification or deletion of canonical divination data while keeping user reading histories intact.

### ADR-0004: Decoupled API Contracts and Victorian Backlund Frontend Presentation
- **Context:** The frontend requires an immersive Victorian Backlund aesthetic with anime-style presentation (§8.2), while backend services must remain portable, secure, and decoupled from UI representation.
- **Decision:** Backend will expose RESTful JSON APIs adhering to strict Pydantic schemas (OpenAPI specification). The frontend will consume these contracts without relying on internal database structures.
- **Consequence:** Frontend and backend can be tested and developed independently without schema leaking into the presentation tier.

### ADR-0005: Standardized API Error Envelope and Correlation Tracking
- **Context:** Production observability and frontend error handling require consistent error formats and distributed request tracing.
- **Decision:** Implement centralized exception handling returning a standard error schema (`error: {code, message, request_id, details}`) with an `X-Request-ID` middleware that attaches and propagates correlation IDs across all request/response cycles.
- **Consequence:** Eliminates internal stack trace leakage, ensures uniform client error handling, and enables end-to-end request tracing.

### ADR-0006: Timing-Safe Authentication and Token Integrity
- **Context:** §7.1 and §7.2 require portfolio-grade authentication resistant to account enumeration, timing attacks, and credential stuffing.
- **Decision:** Use `bcrypt` (12 rounds) with constant-time dummy hash verification for non-existent users during login. Issue signed HMAC-SHA256 compact JWT access tokens validated with constant-time signature comparison (`hmac.compare_digest`) and strict expiration checking.
- **Consequence:** Uniform failure responses prevent user enumeration; cryptographic signing protects token integrity with zero unvetted external runtime dependencies.

### ADR-0007: Cryptographic Unbiased Tarot Draws and Anti-IDOR Ownership Isolation
- **Context:** §9.1 and §7.1 require fair, non-predictable card draws without replacement, independent reversal distribution, and complete user privacy on divination inquiries.
- **Decision:** Implement Fisher-Yates shuffle powered by Python's `secrets` module (OS entropy) over the canonical Major Arcana cards. Restrict reading history and detail lookups to the authenticated querent, returning uniform 404s on unauthorized resource access.
- **Consequence:** Eliminates draw predictability, guarantees absence of duplicate cards in any spread, and prevents enumeration or leaking of private reading consultations.

### ADR-0008: Windows Async Event Loop Policy and Post-Commit Relationship Lifecycle
- **Context:** When integrating FastAPI with Psycopg 3 async engine on Windows, Uvicorn 0.36+ defaults to `ProactorEventLoop`, which is incompatible with Psycopg 3's asynchronous socket polling. Furthermore, in SQLAlchemy 2.0 async mode, calling `db.refresh()` post-commit expires loaded relationships, causing `MissingGreenlet` errors during Pydantic model serialization.
- **Decision:** (1) Implement a custom Uvicorn runner (`backend/run.py`) utilizing `asyncio.SelectorEventLoop` on Windows. (2) Configure the async sessionmaker with `expire_on_commit=False` and preserve the eagerly populated relationship graph post-commit rather than invoking blank attribute refreshes.
- **Consequence:** Guarantees seamless async PostgreSQL I/O under Windows development environments and prevents lazy-loading race conditions during REST response serialization.

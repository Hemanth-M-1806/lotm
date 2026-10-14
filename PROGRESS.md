# LOTM Tarot App — Project Progress

## Current Project Status
Phase 8 (Frontend–Backend Integration) complete. Ready for Phase 9 (Testing and Security Review: automated security audits, OWASP top 10 verification, negative test cases, and penetration boundary checks).

## Completed Milestones
- **Phase 1: Initial Read-Only Audit**: Verified workspace state, directory tree, tools, and constraints.
- **Phase 2: Architecture and Domain Modeling**:
  - Initialized git repository and configured `.gitignore`.
  - Authored `AGENTS.md` operational guidelines.
  - Established `GLOSSARY.md` under `domain-modeling` skill standards.
  - Established `docs/DECISIONS.md` recording ADR-0001 to ADR-0004.
  - Formulated `docs/ASSETS.md` for IP provenance and placeholder tracking.
  - Formulated comprehensive domain specifications in `docs/DOMAIN_MODELS.md`.
- **Phase 3: Database Schema and Persistence**:
  - Created versioned transactional DDL migration `db/changes/001_initial_schema.sql` with `schema_versions` tracking.
  - Created reversible rollback script `db/changes/001_initial_schema_rollback.sql`.
  - Created idempotent canonical seed script `db/seeds/001_canonical_lore.sql` (22 Pathways, 22 Major Arcana cards).
  - Created `docs/DB_CHANGELOG.md` migration protocol.
  - Implemented `.env.example` with documented environment configurations.
  - Implemented `backend/app/core/config.py` (Pydantic Settings with startup URL/secret validation).
  - Implemented `backend/app/core/database.py` (SQLAlchemy 2.0 async engine, Psycopg 3, connection pooling).
  - Implemented SQLAlchemy 2.0 declarative models in `backend/app/models/`.
- **Phase 4: Backend Foundations**:
  - Implemented `backend/app/main.py` with FastAPI lifespan handler for clean startup/shutdown.
  - Implemented liveness (`/health/live`) and readiness (`/health/ready`) probes in `backend/app/api/health.py`.
  - Implemented request correlation middleware attaching `X-Request-ID` to request state and headers.
  - Implemented centralized exception handlers and standard error envelope (`backend/app/core/exceptions.py`, `backend/app/schemas/common.py`).
  - Configured Windows `SelectorEventLoop` policy for Psycopg 3 async compatibility.
  - Expanded unit test suite to 16 passing tests (`backend/tests/`).
- **Phase 5: Authentication and Application Security (Core Slice)**:
  - Formulated `docs/SECURITY.md` threat model (Assets, Actors, STRIDE matrix, OWASP Top 10 & API Security mapping).
  - Sharpened `GLOSSARY.md` with the `Session` domain concept under `domain-modeling` standards.
  - Implemented `backend/app/core/security.py` (Bcrypt cost factor 12 password hashing, constant-time dummy verification, HMAC-SHA256 JWT tokens).
  - Implemented Pydantic v2 validation schemas in `backend/app/schemas/user.py` and `backend/app/schemas/auth.py`.
  - Implemented `backend/app/services/auth_service.py` with case-insensitive uniqueness enforcement and anti-enumeration protections.
  - Implemented dependency injection guard `get_current_user` in `backend/app/api/deps.py`.
  - Mounted `/api/v1/auth` endpoints (`/register`, `/login`, `/me`) in `backend/app/main.py`.
  - Recorded ADR-0005 (Error Envelope & Request Correlation) and ADR-0006 (Timing-Safe Authentication & Token Integrity) in `docs/DECISIONS.md`.
  - Expanded test suite from 16 to 33 passing tests with comprehensive unit and integration security coverage (`backend/tests/test_security.py`, `backend/tests/test_auth.py`).
- **Phase 6: Core Tarot Reading Functionality**:
  - Formulated `docs/READING_FLOW.md` divination ritual specifications and spread rules.
  - Sharpened `GLOSSARY.md` with the `Spread` domain concept under `domain-modeling` standards.
  - Implemented `backend/app/schemas/reading.py` (spread positions for `single_card`, `three_card`, `celtic_cross`, and reading models).
  - Implemented `backend/app/services/reading_service.py` (Fisher-Yates draw without replacement via `secrets`, independent 50% reversal distribution, deterministic occult interpretation synthesis, anti-IDOR reading retrieval, and favorite toggling).
  - Implemented `get_optional_current_user` in `backend/app/api/deps.py` supporting both guest and authenticated readings.
  - Mounted `/api/v1/readings` endpoints (`POST /`, `GET /`, `GET /{id}`, `PATCH /{id}/favorite`) in `backend/app/main.py`.
  - Recorded ADR-0007 (Cryptographic Unbiased Tarot Draws and Anti-IDOR Isolation) in `docs/DECISIONS.md`.
  - Expanded test suite from 33 to 43 passing tests (`backend/tests/test_readings.py`).
- **Phase 7: Frontend Foundations and Design System**:
  - Scaffolded React 19 + TypeScript + Vite frontend at `frontend/`.
  - Installed `react-router-dom` v7 and `@tanstack/react-query` v5.
  - Implemented Victorian Backlund design system (`src/index.css`): full CSS token set (palette, typography, spacing, border, shadow, transition, z-index).
  - Implemented component CSS library (`src/components.css`): Button, TarotCard (flip animation, reversed, shimmer placeholder), SpreadLayout, ReadingPanel, Form, Interpretation, Nav, Alert, Loading, EmptyState, HistoryCard, FogLayer — all with `prefers-reduced-motion` compliance and 44px touch targets.
  - Implemented typed API client (`src/api.ts`): single `request<T>()` core, `authApi`, `readingsApi`, `PaginatedResponse<T>`, in-memory token storage (never localStorage).
  - Structured Auth context across three focused modules: `authContextDef.ts`, `AuthContext.tsx`, `useAuth.ts` — Fast Refresh compliant, 0 lint warnings.
  - Implemented pages: `OraclePage`, `LoginPage`, `HistoryPage`.
  - Implemented components: `Nav`, `TarotCard`, `ReadingForm`, `ReadingResult`.
  - Configured Vite dev server proxy (`/api` → `http://localhost:8000`).
  - Build: ✅ 0 TypeScript errors, 0 lint errors, production bundle built cleanly.
- **Phase 8: Frontend–Backend Integration**:
  - Configured real PostgreSQL connection for `lotm_user` and `lotm_tarot` on port 5432.
  - Created zero-dependency migration engine `db/run_migrations.py` applying `001_initial_schema.sql` and `001_canonical_lore.sql` (22 Pathways and 22 Major Arcana cards verified).
  - Updated `docs/DB_CHANGELOG.md` marking migration 001 and seed 001 as Applied.
  - Configured `.env` with validated `SECRET_KEY` and `DATABASE_URL`.
  - Implemented custom `backend/run.py` launcher using `SelectorServer` to resolve Windows Psycopg 3 async loop incompatibility.
  - Refactored `backend/app/services/reading_service.py` to prevent post-commit lazy-load expiration (`MissingGreenlet`).
  - Executed end-to-end browser smoke test verifying: guest consultation, user registration, authenticated divination, 3D card reveals, and occult narrative synthesis.
  - Recorded ADR-0008 in `docs/DECISIONS.md`.
  - Build: ✅ 0 TypeScript errors, 0 lint errors, 43/43 backend tests passing.
- **Phase 9: Testing and Security Review**:
  - Implemented global defensive HTTP security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 0`, `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy: default-src 'self'`).
  - Implemented in-memory sliding window rate limiter (`backend/app/core/rate_limit.py`) enforcing 10 requests / 60 seconds per IP on `/auth/login` and `/auth/register` with `RateLimitError` HTTP 429 response envelope.
  - Implemented automated security test suite `backend/tests/test_security_audit.py` covering OWASP Top 10 vectors (Anti-IDOR reading isolation, cryptographic token integrity, timing attack protection, SQL injection resistance, and mass-assignment protection).
  - Validated zero dependency vulnerabilities via `npm audit` and verified pinned Python dependencies.
  - Published comprehensive security evaluation in `docs/SECURITY_AUDIT.md`.
  - Expanded test suite from 43 to 56 passing unit and security boundary tests.
- **Phase 10: Docker Deployment and Containerization**:
  - Built multi-stage production `backend/Dockerfile` (`python:3.11-slim-bookworm`, `~85MB` compressed, non-root `lotmuser:10001`, healthcheck).
  - Built multi-stage production `frontend/Dockerfile` (`node:20-alpine` builder + `nginx:1.27-alpine` runtime, `~21MB` compressed, healthcheck).
  - Authored `frontend/nginx.conf` configured with SPA routing, gzip compression, asset caching, defensive security headers, and `/api/` reverse proxying to backend.
  - Configured `backend/docker-entrypoint.sh` executing `db/run_migrations.py` to auto-apply SQL migrations and canonical seeds idempotently on container boot.
  - Authored `docker-compose.yml` orchestrating `db` (PostgreSQL 16 Alpine), `backend`, and `frontend` with healthchecks, dependency gates, and persistent named volume `pgdata`.
  - Authored `docker-compose.dev.yml` supporting live source volume mounts and debug reloads.
  - Authored production runbooks in `docs/RUNBOOK.md` (start, stop, pg_dump/pg_restore backups, secret rotation).
  - Authored engineering concept notes in `docs/LEARNING.md`.
  - Authored portfolio-grade root `README.md` with Mermaid architecture diagram.
  - Successfully verified complete running stack on Docker host with all 3 containers reporting `healthy`, live divination readings created, and user registration functional over HTTP.

## Current Project Status
Phase 9 (Testing & Security Review) and Phase 10 (Docker Deployment & Containerization) complete. Application is fully operational, hardened, tested, and containerized.

## Current Task
Docker deployment and security audit complete and live verified. Ready for portfolio showcase, CI/CD pipeline setup (e.g. GitHub Actions), or additional divination spreads.

## Important Architectural Decisions
- **ADR-0001:** FastAPI + SQLAlchemy 2.0 (async) + Psycopg 3 (`postgresql+psycopg://`).
- **ADR-0002:** Direct PostgreSQL schema management without Alembic (`db/changes/` + `schema_versions`).
- **ADR-0003:** Strict segregation of canonical content (Pathways, Cards) from user readings.
- **ADR-0004:** Decoupled REST contracts with Victorian Backlund aesthetic frontend.
- **ADR-0005:** Standardized API error envelope and correlation tracking (`X-Request-ID`).
- **ADR-0006:** Timing-Safe Authentication, Token Integrity, and Anti-Enumeration Design.
- **ADR-0007:** Cryptographic Unbiased Tarot Draws and Anti-IDOR Ownership Isolation.
- **ADR-0008:** Windows Async Event Loop Policy and Post-Commit Relationship Lifecycle.
- **ADR-0009:** Defensive HTTP Security Headers and Authentication Rate Limiting.
- **ADR-0010:** Multi-Stage Containerization and Self-Seeding Migration Entrypoint.

## Known Blockers & Environment Notes
- Docker container deployment active and healthy:
  - Frontend: `http://localhost:80`
  - Backend API: `http://localhost:8000`
  - Database: `lotm_db` (PostgreSQL 16) on internal container network `lotm_net` (host port 5433).
- Host Windows PostgreSQL remains active on host port 5432.
- Frontend auth tokens stored in-memory per portfolio security design.

## Relevant Test Status
- Backend: 56/56 unit and security tests passing (`python -m unittest discover -s backend/tests -t backend`).
- Security Audit: 0 Critical / 0 High vulnerabilities; OWASP A01-A10 reviewed.
- Frontend: 0 TypeScript errors (`tsc -b`), 0 lint warnings (`oxlint`), production bundle verified.
- Docker: 3/3 containers reporting healthy in Docker Compose.

## Next Actionable Step
Optional enhancements:
1. GitHub Actions CI pipeline (`.github/workflows/ci.yml`) automating backend tests, frontend typechecks, and docker build verification on pull request (§18.2).
2. Advanced spreads and minor arcana extensions.


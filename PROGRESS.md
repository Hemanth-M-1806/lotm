# LOTM Tarot App — Project Progress

## Current Project Status
Phase 4 (Backend Foundations) complete. Ready for Phase 5 (Authentication and Authorization).

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

## Current Task
Beginning Phase 5: Authentication and Authorization (§7, §7.1, §7.2). Implementing secure password hashing, user registration/login, session handling, token validation, and auth dependencies.

## Important Architectural Decisions
- **ADR-0001:** FastAPI + SQLAlchemy 2.0 (async) + Psycopg 3 (`postgresql+psycopg://`).
- **ADR-0002:** Direct PostgreSQL schema management without Alembic (`db/changes/` + `schema_versions`).
- **ADR-0003:** Strict segregation of canonical content (Pathways, Cards) from user readings.
- **ADR-0004:** Decoupled REST contracts with Victorian Backlund aesthetic frontend.
- **ADR-0005 (Proposed):** Standardized API error envelope and correlation tracking (`X-Request-ID`).

## Known Blockers & Environment Notes
- Local Docker daemon is stopped; PostgreSQL connection will need active service or Docker container start before live DB queries against real Postgres.
- `psql` binary is not in Windows system PATH.

## Relevant Test Status
16/16 tests passing (`python -m unittest discover -s backend/tests -t backend`).

## Next Actionable Step
Phase 5: Implement User Schemas, password hashing (`bcrypt`), JWT/session tokens, authentication endpoints (`/api/v1/auth/register`, `/api/v1/auth/login`), current user dependency, and unit tests.

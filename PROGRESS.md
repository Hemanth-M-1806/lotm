# LOTM Tarot App — Project Progress

## Current Project Status
Phase 3 (Database Schema and Persistence) complete. Ready for Phase 4 (Backend Foundations).

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
  - Implemented SQLAlchemy 2.0 declarative models in `backend/app/models/` (`Pathway`, `Sequence`, `TarotCard`, `User`, `UserPreferences`, `Reading`, `ReadingCard`).
  - Added unit test suite in `backend/tests/` (11 tests passing covering config, domain models, database engine pooling, and SQL migration scripts).

## Current Task
Beginning Phase 4: Backend Foundations (§6, §6.1). Building FastAPI application, lifespan connection lifecycle, liveness & readiness health checks, centralized exception envelope, and structured correlation logging.

## Important Architectural Decisions
- **ADR-0001:** FastAPI + SQLAlchemy 2.0 (async) + Psycopg 3 (`postgresql+psycopg://`).
- **ADR-0002:** Direct PostgreSQL schema management without Alembic (`db/changes/` + `schema_versions`).
- **ADR-0003:** Strict segregation of canonical content (Pathways, Cards) from user readings.
- **ADR-0004:** Decoupled REST contracts with Victorian Backlund aesthetic frontend.

## Known Blockers & Environment Notes
- Local Docker daemon is stopped; PostgreSQL connection will need active service or Docker container start before live DB queries against real Postgres.
- `psql` binary is not in Windows system PATH.

## Relevant Test Status
11/11 tests passing (`python -m unittest discover -s backend/tests -t backend`).

## Next Actionable Step
Phase 4: Implement FastAPI lifespan app, liveness (`/health/live`) and readiness (`/health/ready`) probes, error envelope middleware, and test with `unittest`.

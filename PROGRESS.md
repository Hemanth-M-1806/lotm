# LOTM Tarot App — Project Progress

## Current Project Status
Phase 2 (Architecture and Domain Modeling) complete. Ready for Phase 3 (Database Schema and Persistence).

## Completed Milestones
- **Phase 1: Initial Read-Only Audit**: Verified workspace state, directory tree, tools, and constraints.
- **Phase 2: Architecture and Domain Modeling**:
  - Initialized git repository and configured `.gitignore`.
  - Authored `AGENTS.md` operational guidelines.
  - Established `GLOSSARY.md` under `domain-modeling` skill standards.
  - Established `docs/DECISIONS.md` recording ADR-0001 to ADR-0004.
  - Formulated `docs/ASSETS.md` for IP provenance and placeholder tracking.
  - Formulated comprehensive domain specifications in `docs/DOMAIN_MODELS.md`.

## Current Task
Beginning Phase 3: Database Schema and Persistence (§5, §13). Formulating reversible SQL DDL, seed data, and schema version management.

## Important Architectural Decisions
- **ADR-0001:** FastAPI + SQLAlchemy 2.0 (async) + Psycopg 3 (`postgresql+psycopg://`).
- **ADR-0002:** Direct PostgreSQL schema management without Alembic (`sql/migrations/` + `schema_versions`).
- **ADR-0003:** Strict segregation of canonical content (Pathways, Cards) from user readings.
- **ADR-0004:** Decoupled REST contracts with Victorian Backlund aesthetic frontend.

## Known Blockers & Environment Notes
- Local Docker daemon is stopped; PostgreSQL connection will need active service or Docker container start before live DB validation.
- `psql` binary is not in Windows system PATH.

## Relevant Test Status
No code or tests written yet. Model constraints and relational integrity validated against §5.2 checklist.

## Next Actionable Step
Phase 3: Create initial DDL migration (`sql/migrations/001_initial_schema.sql`), schema runner, and canonical seed scripts.

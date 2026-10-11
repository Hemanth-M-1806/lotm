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

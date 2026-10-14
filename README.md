# Lord of the Mysteries Tarot Oracle

> An immersive, Victorian Backlund-themed tarot divination and pathway lore web application inspired by *Lord of the Mysteries*. Built as a portfolio project showcasing modern asynchronous Python, React 19, defense-in-depth application security, and production containerization.

---

## Architecture Overview

```mermaid
graph TD
    Client[Browser / Querent] -->|HTTP / SPA Traffic| Nginx[Frontend: Nginx 1.27 Alpine]
    Nginx -->|Static Assets| ReactApp[React 19 + Vite SPA]
    Nginx -->|/api/* Reverse Proxy| FastAPI[Backend: FastAPI + Uvicorn]
    FastAPI -->|Async SQLAlchemy 2.0 / Psycopg 3| Postgres[(Database: PostgreSQL 16)]
    
    subgraph Container Network (lotm_net)
        Nginx
        FastAPI
        Postgres
    end
```

### Key Engineering Features
- **Backend Architecture**: FastAPI with Python 3.11, async SQLAlchemy 2.0 declarative models, Psycopg 3 binary driver, connection pooling (`pre-ping`, pool timeout, recycle).
- **Database & Lore Management**: Direct versioned SQL migrations and idempotent seed scripts without Alembic (`db/changes/`, `db/seeds/`), self-executing at container boot.
- **Divination Ritual Engine**: Cryptographic card draws via OS entropy (`secrets.randbelow`), Fisher-Yates sampling without replacement, 50% independent card reversal distribution, and deterministic occult narrative interpretation synthesis.
- **Security & Hardening**:
  - Bcrypt (12 rounds) password hashing with constant-time dummy verification on nonexistent accounts to prevent user enumeration.
  - Signed HMAC-SHA256 compact JWT access tokens.
  - Strict anti-IDOR isolation on private readings (`(id == reading_id) & (user_id == caller_id)`).
  - Defensive HTTP security headers (`CSP`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`).
  - Sliding-window in-memory rate limiting on authentication routes (`/api/v1/auth/login`, `/api/v1/auth/register`).
  - Zero raw SQL string interpolation; 100% parameterized SQLAlchemy 2.0 statements.
- **Victorian Backlund Frontend**: Custom CSS design system inspired by gaslit 19th-century industrial aesthetic with crimson moon motifs, 3D CSS card flip animations, TanStack Query v5 state management, and strict in-memory token lifecycle.
- **Containerization**: Minimal multi-stage Dockerfiles (`~85MB` backend, `~21MB` frontend), non-root execution (`lotmuser:10001`), Docker Compose orchestration with integrated healthchecks and named volumes.

---

## Quick Start (Docker)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose v2+

### 1. Launch the Stack
```bash
# Clone the repository and configure environment
cp .env.docker.example .env

# Build and start all services in the background
docker compose up -d --build
```

### 2. Verify Health
```bash
docker compose ps
```
All services (`lotm_db`, `lotm_backend`, `lotm_frontend`) will start, run automatic database migrations/seeds, and report `healthy`.

### 3. Open in Browser
- **Application**: [http://localhost](http://localhost)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Liveness Probe**: [http://localhost/health/live](http://localhost/health/live)
- **Readiness Probe**: [http://localhost/health/ready](http://localhost/health/ready)

---

## Local Development (Without Docker)

### Backend Setup
```bash
# Setup Python 3.11+ virtual environment
python -m venv .venv
source .venv/bin/activate  # Or: .venv\Scripts\activate on Windows

# Install dependencies
pip install -e backend

# Run database migrations
python db/run_migrations.py

# Start development server
python backend/run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Testing & Quality Assurance

### Run Backend Unit & Security Tests
```bash
python -m unittest discover -s backend/tests -t backend
```
- **56 passing tests** covering domain divination rules, authentication timing safety, anti-IDOR checks, rate limiting, and negative boundary validation.

### Run Frontend Typecheck & Linter
```bash
cd frontend
npm run build   # TypeScript type check (tsc -b) & Vite build
npm run lint    # Oxlint (0 errors, 0 warnings)
```

---

## Documentation Index

- [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md): Detailed OWASP Top 10 evaluation, methodology, and negative boundary test matrix.
- [docs/DECISIONS.md](docs/DECISIONS.md): Architectural Decision Records (ADR-0001 through ADR-0010).
- [docs/RUNBOOK.md](docs/RUNBOOK.md): Operational playbooks for starting, stopping, backups, and secret rotation.
- [docs/LEARNING.md](docs/LEARNING.md): Compact glossary of engineering and DevOps production patterns.
- [docs/DOMAIN_MODELS.md](docs/DOMAIN_MODELS.md): Domain entity models and database relational schema.
- [docs/READING_FLOW.md](docs/READING_FLOW.md): Divination ritual lifecycle and spread specifications.

# LOTM Tarot App — DevOps & Engineering Learning Notes

A compact reference glossary of architecture, security, and DevOps concepts applied in this project.

---

### In-Memory Sliding Window Rate Limiting
- **What it is**: Throttles incoming client requests within a bounded historical time window (e.g. 10 hits / 60 seconds) tracked by client IP.
- **Why it matters in production**: Protects authentication endpoints from automated brute-force attacks and credential stuffing without the latency or complexity of external caching systems in single-instance topologies.
- **Reference**: [rate_limit.py](file:///d:/Projects/lotm/backend/app/core/rate_limit.py), [ADR-0009](file:///d:/Projects/lotm/docs/DECISIONS.md).

### Insecure Direct Object Reference (IDOR) Protection
- **What it is**: Access control pattern where every resource fetch or modification enforces that the resource's owner matches the cryptographically verified session caller.
- **Why it matters in production**: Prevents malicious actors from scraping or tampering with other users' private readings simply by guessing or iterating database UUIDs.
- **Reference**: [reading_service.py](file:///d:/Projects/lotm/backend/app/services/reading_service.py), [ADR-0007](file:///d:/Projects/lotm/docs/DECISIONS.md).

### Multi-Stage Container Builds
- **What it is**: Dockerfile pattern that isolates compilers, dev headers, and build tools in temporary builder stages, copying only compiled binaries and wheels into a minimal runner image.
- **Why it matters in production**: Radically shrinks image size (backend ~85MB, frontend ~21MB) and eliminates attack surface by removing compilers (`gcc`, `npm`, `apt`) from the running container.
- **Reference**: [backend/Dockerfile](file:///d:/Projects/lotm/backend/Dockerfile), [frontend/Dockerfile](file:///d:/Projects/lotm/frontend/Dockerfile), [ADR-0010](file:///d:/Projects/lotm/docs/DECISIONS.md).

### Non-Root Container Execution
- **What it is**: Enforcing that the container runtime runs as an unprivileged user/group (`lotmuser:lotmgroup`, UID 10001) rather than root (UID 0).
- **Why it matters in production**: Defense-in-depth against container breakout vulnerabilities; an exploited process cannot easily modify host devices or access root-restricted filesystem nodes.
- **Reference**: [backend/Dockerfile](file:///d:/Projects/lotm/backend/Dockerfile).

### Self-Seeding Migration Entrypoint
- **What it is**: An orchestration entrypoint script that executes idempotent database schema migrations and seed scripts before launching application servers.
- **Why it matters in production**: Ensures that fresh staging, preview, or production instances are immediately functional without manual DBA execution, preventing race conditions or uninitialized database errors.
- **Reference**: [docker-entrypoint.sh](file:///d:/Projects/lotm/backend/docker-entrypoint.sh), [run_migrations.py](file:///d:/Projects/lotm/db/run_migrations.py).

### Liveness vs Readiness Probes
- **What it is**: Separate health endpoints: `/health/live` reports that the process is responsive; `/health/ready` reports that external dependencies (PostgreSQL database pool) are connected and accepting queries.
- **Why it matters in production**: Container orchestrators (Docker, Kubernetes) restart unresponsive processes via liveness checks, but temporarily route traffic away from unready processes without killing them during transient database reconnections.
- **Reference**: [health.py](file:///d:/Projects/lotm/backend/app/api/health.py), [ADR-0001](file:///d:/Projects/lotm/docs/DECISIONS.md).

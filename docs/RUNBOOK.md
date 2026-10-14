# LOTM Tarot App — Operations & Runbook

Operational runbooks for managing, deploying, and operating the Lord of the Mysteries Tarot web application.

---

## 1. Quick Start & Service Orchestration

### 1.1 Local Docker Compose Deployment (Production Mode)

1. Configure environment variables (ensure `SECRET_KEY` is set):
   ```bash
   cp .env.docker.example .env
   ```
2. Build and launch all services (`db`, `backend`, `frontend`):
   ```bash
   docker compose up -d --build
   ```
3. Verify running service health:
   ```bash
   docker compose ps
   ```
4. Access the application:
   - **Frontend UI**: [http://localhost](http://localhost)
   - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Liveness Probe**: [http://localhost/health/live](http://localhost/health/live)
   - **Readiness Probe**: [http://localhost/health/ready](http://localhost/health/ready)

### 1.2 Development Mode with Live Code Reload

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```
- Frontend mapped to port `3000`.
- Backend source code mounted with live auto-reload on changes.

### 1.3 Stopping the Services

```bash
# Graceful shutdown (preserves persistent database volume)
docker compose down

# Teardown with database volume destruction (destructive)
docker compose down -v
```

---

## 2. Database Maintenance & Backups

### 2.1 Performing a Database Backup

> **DevOps Rule (§18.4)**: An untested backup is not a backup.

Execute `pg_dump` within the active database container:
```bash
docker compose exec db pg_dump -U lotm_user -d lotm_tarot -Fc > backups/lotm_tarot_$(date +%Y%m%d_%H%M%S).dump
```

### 2.2 Restoring from Backup

1. Place the database into single-user or isolated maintenance mode.
2. Restore the schema and data using `pg_restore`:
   ```bash
   cat backups/lotm_tarot_backup.dump | docker compose exec -T db pg_restore -U lotm_user -d lotm_tarot --clean --if-exists
   ```
3. Run verification check:
   ```bash
   docker compose exec backend python db/run_migrations.py --check-only
   ```

---

## 3. Secret & Credential Rotation

### 3.1 Rotating `SECRET_KEY`

1. Generate a new cryptographically secure 48-byte token:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
2. Update `SECRET_KEY` in `.env`.
3. Perform a zero-downtime rolling restart of backend instances:
   ```bash
   docker compose up -d --no-deps backend
   ```
> *Note*: Rotating `SECRET_KEY` invalidates currently issued access tokens, requiring querents to re-authenticate.

### 3.2 Rotating Database Password (`DB_PASSWORD`)

1. Connect to PostgreSQL and update the user role password:
   ```bash
   docker compose exec db psql -U lotm_user -d lotm_tarot -c "ALTER USER lotm_user WITH PASSWORD 'NewSecurePassword123!';"
   ```
2. Update `DB_PASSWORD` in `.env`.
3. Restart `backend` service:
   ```bash
   docker compose up -d --no-deps backend
   ```

---

## 4. Troubleshooting & Diagnostic Playbooks

### Issue 1: Backend container shows `unhealthy` status
- **Symptom**: `docker compose ps` reports `lotm_backend` is `unhealthy`.
- **Diagnostic Command**:
  ```bash
  docker logs lotm_backend --tail 50
  ```
- **Remediation**:
  - Verify PostgreSQL container is healthy: `docker compose ps db`.
  - Check for database connection timeout: verify `DATABASE_URL` format.

### Issue 2: Frontend returns HTTP 502 Bad Gateway
- **Symptom**: Nginx displays `502 Bad Gateway` on `/api/*`.
- **Diagnostic Command**:
  ```bash
  docker logs lotm_frontend --tail 20
  ```
- **Remediation**: Ensure the `backend` container is running and healthy on the internal `lotm_net` network.

#!/bin/sh
set -e

echo "[LOTM Container] Initializing backend container..."

# 1. Execute database migrations and idempotent lore seeding
if [ -n "$DATABASE_URL" ]; then
    echo "[LOTM Container] Running database migrations & canonical seeds..."
    python db/run_migrations.py --url "$DATABASE_URL" || echo "[WARN] Migration runner returned non-zero. Continuing to startup..."
fi

# 2. Exec into the main container command
echo "[LOTM Container] Starting application server..."
exec "$@"

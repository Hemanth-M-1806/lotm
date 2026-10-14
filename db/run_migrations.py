"""
Database migration & seed runner for LOTM Tarot.
Applies versioned SQL migrations and seeds using psycopg.
Usage:
    python db/run_migrations.py [--url postgresql://...] [--check-only]
"""
import argparse
import os
import re
import sys
from pathlib import Path

# Add project root and backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))


def load_env_file(filepath: Path) -> dict[str, str]:
    env_vars: dict[str, str] = {}
    if not filepath.exists():
        return env_vars
    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            env_vars[key.strip()] = val.strip().strip("'\"")
    return env_vars


def get_connection_url(cli_url: str | None) -> str:
    if cli_url:
        return cli_url

    # Check env vars
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    # Check root .env
    root_env = load_env_file(PROJECT_ROOT / ".env")
    if "DATABASE_URL" in root_env:
        return root_env["DATABASE_URL"]

    # Check backend/.env
    backend_env = load_env_file(PROJECT_ROOT / "backend" / ".env")
    if "DATABASE_URL" in backend_env:
        return backend_env["DATABASE_URL"]

    # Default fallback
    return "postgresql://lotm_user:change_me_password@localhost:5432/lotm_tarot"


def normalize_conn_string(url: str) -> str:
    # psycopg expects standard postgresql:// or conninfo
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql://", 1)
    return url


def run_migrations(db_url: str, check_only: bool = False) -> None:
    try:
        import psycopg
    except ImportError:
        print("[ERROR] psycopg is not installed. Install with: pip install psycopg[binary]")
        sys.exit(1)

    clean_url = normalize_conn_string(db_url)
    # Mask password for display
    display_url = re.sub(r":([^:@]+)@", ":****@", clean_url)
    print(f"[*] Connecting to database: {display_url}")

    try:
        with psycopg.connect(clean_url, autocommit=True) as conn:
            print("[+] Connection established successfully.")

            with conn.cursor() as cur:
                # 1. Check or initialize schema_versions table
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'schema_versions'
                    );
                    """
                )
                has_versions_table = cur.fetchone()[0]

                applied_versions: set[str] = set()
                if has_versions_table:
                    cur.execute("SELECT version FROM schema_versions;")
                    applied_versions = {row[0] for row in cur.fetchall()}
                    print(f"[*] Currently applied versions: {applied_versions or 'None'}")

                if check_only:
                    print("[*] Check-only mode requested. Existing tables:")
                    cur.execute(
                        """
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' ORDER BY table_name;
                        """
                    )
                    for (tbl,) in cur.fetchall():
                        print(f"    - {tbl}")
                    return

                # 2. Run initial schema if not applied
                if "001" not in applied_versions:
                    schema_file = PROJECT_ROOT / "db" / "changes" / "001_initial_schema.sql"
                    print(f"[*] Applying migration: {schema_file.name}")
                    sql_content = schema_file.read_text(encoding="utf-8")
                    cur.execute(sql_content)
                    print(f"[+] Applied {schema_file.name}")
                else:
                    print("[✓] Migration 001 already applied.")

                # 3. Seed canonical lore if not already seeded
                cur.execute("SELECT COUNT(*) FROM tarot_cards;")
                cards_count = cur.fetchone()[0]
                if cards_count == 0:
                    seed_file = PROJECT_ROOT / "db" / "seeds" / "001_canonical_lore.sql"
                    print(f"[*] Applying seed data: {seed_file.name}")
                    seed_content = seed_file.read_text(encoding="utf-8")
                    cur.execute(seed_content)
                    print(f"[+] Applied {seed_file.name}")
                else:
                    print(f"[✓] Canonical lore already seeded ({cards_count} tarot cards present).")

                # 4. Verify integrity
                cur.execute("SELECT COUNT(*) FROM pathways;")
                pathways_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM tarot_cards WHERE arcana_type = 'major';")
                major_count = cur.fetchone()[0]

                print("\n=== Verification Summary ===")
                print(f"Pathways loaded:     {pathways_count} / 22")
                print(f"Major Arcana loaded: {major_count} / 22")
                if pathways_count == 22 and major_count == 22:
                    print("[SUCCESS] Database schema and canonical seeds verified!")
                else:
                    print(f"[WARNING] Expected 22 pathways and 22 cards, found {pathways_count} & {major_count}")

    except Exception as exc:
        print(f"[ERROR] Database operation failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LOTM database migrations")
    parser.add_argument("--url", help="PostgreSQL connection URL", default=None)
    parser.add_argument("--check-only", action="store_true", help="Only verify existing connection and tables")
    args = parser.parse_args()

    url = get_connection_url(args.url)
    run_migrations(url, check_only=args.check_only)


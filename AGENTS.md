# LOTM Tarot App — Agent Instructions

## Overview
This repository contains the Lord of the Mysteries Tarot web application. It is being developed following strict architectural, security, and DevOps portfolio standards outlined in `LOTM_MASTER_PROMPT.md`.

## Permanent Constraints (§1.1)
- **Backend:** Python, FastAPI, SQLAlchemy 2.x (async), Psycopg 3.
- **Database:** PostgreSQL (`lotm_tarot`, user `lotm_user`).
- **Migrations:** Direct versioned SQL scripts (`sql/migrations/`), no Alembic unless explicitly approved.
- **Frontend Aesthetic:** Victorian Backlund theme with anime-style presentation (§8.2).
- **Secrets:** Environment variables only via `.env` (never commit secrets or print secret values).
- **DevOps Focus:** Priority on robustness, test coverage, legible architecture decisions (`docs/DECISIONS.md`), and container readiness.

## Working Conventions
1. **Direct Action:** Do not write plan documents or enter Plan mode unless requested.
2. **Incremental Slices:** Work one small slice at a time in the §15 phase order with focused diffs.
3. **Evidence-Based:** Use shell inspection before assumptions; cite exact file paths.
4. **Response Format:** Keep reports strictly adhering to §16 format.
5. **Safety Boundaries:** Always request explicit user approval before destructive actions (§17.2).
6. **Skills Usage:** Only declare/use skills whose `SKILL.md` was read during the session.

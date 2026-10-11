# Database Migration Changelog

This changelog records all direct PostgreSQL schema changes in adherence with §13 of `LOTM_MASTER_PROMPT.md` and ADR-0002.

## Migrations

| Migration ID | File | Rollback File | Description | Status |
|---|---|---|---|---|
| `001` | `db/changes/001_initial_schema.sql` | `db/changes/001_initial_schema_rollback.sql` | Initial schema: canonical lore (pathways, sequences, tarot_cards), users & preferences, readings & reading_cards, and schema_versions table. | Pending execution |

## Seeds

| Seed ID | File | Description | Status |
|---|---|---|---|
| `001` | `db/seeds/001_canonical_lore.sql` | Canonical 22 Pathways and 22 Major Arcana Tarot Cards with Lord of the Mysteries lore correspondences. | Pending execution |

## Execution Protocol
Migrations must be executed sequentially wrapped in transactions:
```bash
psql -d lotm_tarot -U lotm_user -f db/changes/001_initial_schema.sql
psql -d lotm_tarot -U lotm_user -f db/seeds/001_canonical_lore.sql
```

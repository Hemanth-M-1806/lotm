# Domain Models and Data Specifications

## Overview
This document specifies the core domain models for the LOTM Tarot Application developed under Phase 2 (§5 of `LOTM_MASTER_PROMPT.md`), incorporating the vocabulary defined in [GLOSSARY.md](../GLOSSARY.md).

---

## 1. Canonical Lore Models (Read-Heavy / Immutable)

### Pathway (`pathways`)
Represents the 22 mystical pathways of the Lord of the Mysteries universe.
- **`id`** (`SERIAL` / `INT`, PK)
- **`name`** (`VARCHAR(50)`, NOT NULL, UNIQUE) - e.g. "Fool", "Door", "Error"
- **`chinese_name`** (`VARCHAR(50)`, NULLABLE) - Canonical title (e.g. "愚者")
- **`description`** (`TEXT`, NOT NULL) - Mystical authority, divine domain, and characteristics
- **`created_at`** (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)

### Sequence (`sequences`)
Represents an individual potion tier (Sequence 9 down to Sequence 0) in a Pathway.
- **`id`** (`SERIAL` / `INT`, PK)
- **`pathway_id`** (`INT`, NOT NULL, FK `pathways.id` ON DELETE RESTRICT)
- **`sequence_number`** (`SMALLINT`, NOT NULL, CHECK `sequence_number BETWEEN 0 AND 9`)
- **`name`** (`VARCHAR(50)`, NOT NULL) - e.g. "Seer", "Clown", "Magician"
- **`acting_method_summary`** (`TEXT`, NULLABLE) - Lore guidance and acting principles
- **`created_at`** (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)
- **Constraints:** `UNIQUE (pathway_id, sequence_number)`

### TarotCard (`tarot_cards`)
Represents an arcana card in the deck and its correspondence to pathways and symbolism.
- **`id`** (`SMALLINT`, PK) - Standard numbering (0-21 for Major Arcana)
- **`name`** (`VARCHAR(50)`, NOT NULL, UNIQUE) - e.g. "The Fool", "The Magician"
- **`arcana_type`** (`VARCHAR(10)`, NOT NULL) - `'major'` or `'minor'`
- **`suit`** (`VARCHAR(20)`, NULLABLE) - `'wands'`, `'cups'`, `'swords'`, `'pentacles'` (NULL for Major)
- **`card_number`** (`SMALLINT`, NOT NULL)
- **`pathway_id`** (`INT`, NULLABLE, FK `pathways.id` ON DELETE SET NULL)
- **`upright_meaning`** (`TEXT`, NOT NULL) - Core divination meaning upright
- **`reversed_meaning`** (`TEXT`, NOT NULL) - Core divination meaning reversed
- **`mystical_lore`** (`TEXT`, NULLABLE) - Lord of the Mysteries flavor and occult symbolism
- **`image_asset_path`** (`VARCHAR(255)`, NULLABLE) - Relative asset URI
- **`created_at`** (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)

---

## 2. User & Identity Models

### User (`users`)
Represents an authenticated user with reading history and preferences.
- **`id`** (`UUID`, PK, DEFAULT `gen_random_uuid()`)
- **`username`** (`VARCHAR(50)`, NOT NULL, UNIQUE)
- **`email`** (`VARCHAR(255)`, NOT NULL, UNIQUE)
- **`display_name`** (`VARCHAR(100)`, NOT NULL)
- **`password_hash`** (`VARCHAR(255)`, NOT NULL) - Argon2id or bcrypt hash
- **`email_verified`** (`BOOLEAN`, NOT NULL, DEFAULT `FALSE`)
- **`created_at`** (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)
- **`last_login`** (`TIMESTAMPTZ`, NULLABLE)

### UserPreferences (`user_preferences`)
Per-user display and consultation preferences.
- **`user_id`** (`UUID`, PK, FK `users.id` ON DELETE CASCADE)
- **`theme`** (`VARCHAR(50)`, NOT NULL, DEFAULT `'backlund_dark'`)
- **`preferred_deck_style`** (`VARCHAR(50)`, NOT NULL, DEFAULT `'victorian_anime'`)
- **`default_spread`** (`VARCHAR(50)`, NOT NULL, DEFAULT `'three_card'`)
- **`updated_at`** (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)

---

## 3. Divination & Consultation Models (User-Generated)

### Reading (`readings`)
A completed or active tarot consultation session.
- **`id`** (`UUID`, PK, DEFAULT `gen_random_uuid()`)
- **`user_id`** (`UUID`, NULLABLE, FK `users.id` ON DELETE CASCADE) - NULL indicates anonymous/guest reading
- **`spread_type`** (`VARCHAR(50)`, NOT NULL) - e.g. `'single_card'`, `'three_card'`, `'celtic_cross'`
- **`question`** (`TEXT`, NULLABLE) - Querent inquiry
- **`interpretation`** (`TEXT`, NULLABLE) - Divination synthesis / guidance
- **`is_favorite`** (`BOOLEAN`, NOT NULL, DEFAULT `FALSE`)
- **`created_at`** (`TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`)
- **Indexes:** `CREATE INDEX idx_readings_user_created ON readings(user_id, created_at DESC)`

### ReadingCard (`reading_cards`)
The specific card instances drawn in a spread.
- **`id`** (`UUID`, PK, DEFAULT `gen_random_uuid()`)
- **`reading_id`** (`UUID`, NOT NULL, FK `readings.id` ON DELETE CASCADE)
- **`card_id`** (`SMALLINT`, NOT NULL, FK `tarot_cards.id` ON DELETE RESTRICT)
- **`position_index`** (`SMALLINT`, NOT NULL) - 0-indexed position within spread
- **`position_name`** (`VARCHAR(50)`, NOT NULL) - e.g. "Past", "Present", "Future"
- **`is_reversed`** (`BOOLEAN`, NOT NULL, DEFAULT `FALSE`)
- **`card_notes`** (`TEXT`, NULLABLE)
- **Constraints:** `UNIQUE (reading_id, position_index)`
- **Indexes:** `CREATE INDEX idx_reading_cards_reading ON reading_cards(reading_id)`

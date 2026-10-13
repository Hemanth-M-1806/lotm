# LOTM Tarot App — Tarot Divination Workflow

## Overview
This document specifies the divination ritual lifecycle and technical reading workflow for the Lord of the Mysteries Tarot application, adhering to §9 and §9.1 of `LOTM_MASTER_PROMPT.md`.

---

## 1. Ritual Lifecycle Stages

```
   +--------------------------------------------------------+
   | 1. Initiation: Querent submits question & spread type  |
   +--------------------------------------------------------+
                               |
                               v
   +--------------------------------------------------------+
   | 2. Validation: Boundary validation (spread enum, text) |
   +--------------------------------------------------------+
                               |
                               v
   +--------------------------------------------------------+
   | 3. Cryptographic Draw: Secrets-based Fisher-Yates      |
   |    - Cards drawn without replacement                   |
   |    - Independent 50% reversal probability               |
   +--------------------------------------------------------+
                               |
                               v
   +--------------------------------------------------------+
   | 4. Interpretation Synthesis: Deterministic alignment   |
   |    of card upright/reversed meanings and LOTM lore     |
   +--------------------------------------------------------+
                               |
                               v
   +--------------------------------------------------------+
   | 5. Persistence: Transactional write to DB              |
   |    - Reading record with user ownership link           |
   |    - ReadingCard records with position metadata        |
   +--------------------------------------------------------+
                               |
                               v
   +--------------------------------------------------------+
   | 6. Presentation: Victorian Backlund ritual display     |
   +--------------------------------------------------------+
                               |
                               v
   +--------------------------------------------------------+
   | 7. Archive: Historical consultation review with anti-  |
   |    IDOR ownership verification                         |
   +--------------------------------------------------------+
```

---

## 2. Spread Specifications

| Spread Type | Card Count | Spread Positions |
|---|---|---|
| `single_card` | 1 | `0`: "Guidance" |
| `three_card` | 3 | `0`: "Past / Cause", `1`: "Present / Catalyst", `2`: "Future / Outcome" |
| `celtic_cross` | 10 | `0`: "Present Condition", `1`: "Obstacle / Challenge", `2`: "Subconscious Foundation", `3`: "Recent Past", `4`: "Conscious Goal", `5`: "Near Future", `6`: "The Querent / Attitude", `7`: "External Environment", `8`: "Hopes and Doubts", `9`: "Ultimate Culmination" |

---

## 3. Deterministic Drawing Rules

1. **Card Pool**: Drawn exclusively from the 22 Major Arcana tarot cards (Cards 0 to 21).
2. **Without Replacement**: A card drawn in position $i$ is removed from the available pool and cannot appear in position $j$ ($i \neq j$) within the same reading.
3. **Randomness Source**: Uses Python's `secrets` module (cryptographically secure pseudo-random number generator backed by OS entropy) via Fisher-Yates shuffle.
4. **Orientation**: Reversal orientation is determined per card via `secrets.randbelow(2) == 1`. Upright uses `upright_meaning`, reversed uses `reversed_meaning`.
5. **Separation of Concerns**: Deterministic draw results (card IDs, positions, orientations) are stored independently from the synthesis text (`interpretation`).

---

## 4. Security & Access Control

- **Guest vs. Authenticated Readings**:
  - Unauthenticated users can perform ephemeral guest consultations (`user_id = None`).
  - Authenticated users have readings automatically linked to their profile (`user_id = current_user.id`).
- **Ownership Boundaries (Anti-IDOR)**:
  - Reading history (`GET /api/v1/readings`) returns only records belonging to the authenticated querent.
  - Detail lookup (`GET /api/v1/readings/{id}`) and modification (`PATCH /api/v1/readings/{id}/favorite`) reject unauthorized access with uniform `404 Not Found` to prevent record enumeration.

# Source of Truth

This document identifies the authoritative files, settings, and database structures for various aspects of the Ankimon system. When making changes, it is critical to modify the *source of truth* rather than a downstream wrapper, helper, or cached value.

---

## Startup and Orchestration
**Authoritative File:** `__init__.py`
- **Why:** It contains the root hook registrations (`addHook("profileLoaded", ...)` and `gui_hooks.reviewer_did_answer_card.append(...)`). No other file dictates *when* the add-on runs.
- **Distinction:** Files like `hooks.py` exist but are mostly wrappers or secondary setup. `__init__.py` is the ultimate arbiter of the lifecycle.
- **Confidence:** High

---

## Configuration & Reward Bounds
**Authoritative File:** `pyobj/settings.py` (The `Settings` class) and validated in `ankimon_items_web/settings_schema.py` under `validate_and_clamp()`.
Any read/write to user preferences must go through `settings_obj.get()` or `settings_obj.set()`. Configuration changes are backed up within the SQLite `config` table.

### Fair-Play Validation Ranges
The web settings screen automatically enforces and self-corrects rewards configuration to stay within these bounds:

| Configuration Key | Allowed Range | Default Value | Description / Validation Logic |
| :--- | :--- | :--- | :--- |
| `trainer.cash_reward_interval` | `[5, 250]` | `10` | The card interval $X$ before receiving a payout. Enforced in `validate_and_clamp()`. |
| `trainer.cash_reward_amount` | `[10, 2000]` | `100` | The cash amount $Y$ rewarded per interval. |
| **Cheat-Prevention Threshold** | `Ratio <= 100:1` | — | Cash payout is capped at a maximum of **100¥ per card** (e.g. to earn 1,000¥, interval must be at least 10 cards). Violations are automatically scaled down in `validate_and_clamp()`. |
| **Always Catch Tiers** | `[True, False]` | `True` | Replaces `battle.automatic_catch_special` with 7 individual tier keys: `auto_catch_legendary`, `auto_catch_mythical`, `auto_catch_ultra`, `auto_catch_starter`, `auto_catch_mega`, `auto_catch_gmax`, `auto_catch_regional`. |
| **Friendship & Time Evolution** | Permanently `True` | `True` | Friendship and time-based evolution mechanics are always active; the toggle to disable them has been removed from settings. |

---

## Encounter Gating & Weighting Pool constants
**Authoritative File:** `functions/encounter_data.py`
This file is the absolute source of truth for encounter tiers, prerequisites, and regional form replacements. Dynamic disk reads are prohibited; edits must happen directly in this file.

### Authoritative Pool Constants
- **`LEGENDARY` / `MYTHICAL`:** Rarity sets for high-tier encounters.
- **`MEGA` / `GMAX`:** Custom IDs >= 10000 (e.g. `mewtwomegay` mapped to `10065`). Mega/Gmax encounters check the base `species_id` against generation toggles.
- **`STARTERS`:** Authoritative list of starter evolution IDs (from Bulbasaur Gen 1 to Quaxly Gen 9) gated at main level 40.
- **`PREREQUISITES`:** Gating evolution dictionary mapping IDs to caught requirements:
  - Bulbasaur family: `1 -> 2` (Ivysaur), `2 -> 3` (Venusaur).
  - Legendary chains: Mewtwo requires Mew (`150: 151`); Lugia requires Articuno, Zapdos, and Moltres (`249: [144, 145, 146]`).
  - Supports complex logic gates, including "OR" conditions (e.g., Terapagos requires Koraidon OR Miraidon).

### Regional Form Mappings
- **`REGIONAL_FORM_LOOKUP`:** Unified post-selection variant replacements. Mapped as `base_species_id -> [variant_ids]` (e.g. Meowth `52 -> [10098, 10161, 10248]` for Alolan, Galarian, Hisuian forms).
- **`ACTIVE_REGION_BOOSTS`:** Maps active region settings (Alola, Galar, Hisui, Paldea) to boosted introduction generations and explicit variant lists.

---

## Pokédex V2 Terminology Standards
To maintain complete consistency across the PC, Pokédex, and Discovery Map views, the following terms are standard:
1. **"Capture Requirements"** (replaces "Prerequisites" or "Capture Prerequisites"): The explicit list of Pokémon that must be registered in the SQLite database before a target species can spawn.
2. **"Registry Progress"** (replaces "Completion Status" or "Caught Status"): The calculated caught/registered percentage represented in the sidebar navigation.
3. **"Unseen"** (replaces "Not Seen" or "Locked"): Hidden Pokedex entries.
4. **State Badges:** Consolidates status colors:
   - Caught/Completed: `--accent-green`
   - Available (Unlocked): `--accent-blue`
   - In Progress: `--accent-gold`
   - Locked (Missing): `--text-muted` (Grey)

---

## Persistence (SQLite Database Schema)
**Authoritative File:** `ankimon.db` (SQLite database) managed exclusively by `pyobj/database_manager.py` (`AnkimonDB` class).

### AUTHORITATIVE DB SCHEMAS

#### 1. `captured_pokemon`
Tracks the collection of all caught Pokémon and identifies the active main Pokémon.
```sql
CREATE TABLE captured_pokemon (
    individual_id TEXT PRIMARY KEY,
    is_main INTEGER DEFAULT 0,  -- 0 = in box, 1 = active main pokemon
    data TEXT NOT NULL,         -- Obfuscated JSON representation of the Pokemon object
    name TEXT GENERATED ALWAYS AS (json_extract(data, '$.name')) VIRTUAL,
    pokedex_id INTEGER GENERATED ALWAYS AS (json_extract(data, '$.id')) VIRTUAL,
    shiny BOOLEAN GENERATED ALWAYS AS (json_extract(data, '$.shiny')) VIRTUAL,
    level INTEGER GENERATED ALWAYS AS (json_extract(data, '$.level')) VIRTUAL
);
CREATE INDEX idx_pokemon_name ON captured_pokemon(name);
CREATE INDEX idx_pokemon_pokedex_id ON captured_pokemon(pokedex_id);
CREATE INDEX idx_pokemon_shiny ON captured_pokemon(shiny);
CREATE INDEX idx_pokemon_level ON captured_pokemon(level);
```

#### 2. `team`
Maintains the player's current active battle team roster.
```sql
CREATE TABLE team (
    slot_position INTEGER PRIMARY KEY, -- 1 to 6
    individual_id TEXT NOT NULL        -- Foreign key to captured_pokemon(individual_id)
);
```

#### 3. `items`
Roster of all inventory items and attributes.
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    item_name TEXT UNIQUE,
    quantity INTEGER DEFAULT 0,
    data TEXT,
    category_id INTEGER,
    cost INTEGER,
    fling_power INTEGER,
    fling_effect_id INTEGER
);
```

#### 4. `badges`
Completed achievement milestones.
```sql
CREATE TABLE badges (
    badge_id TEXT PRIMARY KEY,
    achieved BOOLEAN DEFAULT 0
);
```

#### 5. `pokemon_history`
Historical collection statistics for released or faint actions.
```sql
CREATE TABLE pokemon_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    individual_id TEXT UNIQUE,
    data TEXT NOT NULL
);
```

#### 6. `user_data`
Auth and account credential values.
```sql
CREATE TABLE user_data (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

#### 7. `config`
Add-on setting backups.
```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

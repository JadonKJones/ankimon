# Source of Truth

This document identifies the authoritative files that govern specific behavioral domains. Editing wrapper or adapter files while missing these sources of truth will cause regressions.

## 1. Startup
*   **Candidates**: `src/Ankimon/__init__.py`, `src/Ankimon/startup.py`.
*   **Authoritative File**: `src/Ankimon/__init__.py`.
*   **Why**: `__init__.py` is the absolute boundary between Anki's host process and the Ankimon plugin. It determines the order in which all other files execute. `startup.py` is merely a helper invoked by the init process.
*   **Confidence**: High.

## 2. Configuration
*   **Candidates**: `addon.json`, `config.json`, `src/Ankimon/pyobj/settings.py`.
*   **Authoritative File**: `src/Ankimon/pyobj/settings.py`.
*   **Why**: While `config.json` stores the raw text, `settings.py` enforces validation logic, default fallbacks, and runtime type coercion. Any attempt to read configuration bypassing `settings_obj.get()` risks reading stale or invalid data.
*   **Confidence**: High.

## 3. Domain Logic (Battle Mechanics)
*   **Candidates**: `src/Ankimon/battle_loop.py`, `src/Ankimon/poke_engine/evaluate.py`.
*   **Authoritative File**: `src/Ankimon/poke_engine/evaluate.py` (and the `poke_engine/` directory).
*   **Why**: `battle_loop.py` is an orchestrator; it decides *when* a battle occurs. The `poke_engine` submodule defines *what* happens in the battle (damage calculation, speed ties, status application).
*   **Confidence**: High.

## 4. State Transitions (Memory)
*   **Candidates**: `src/Ankimon/pyobj/pokemon_obj.py`, `src/Ankimon/singletons.py`.
*   **Authoritative File**: `src/Ankimon/singletons.py`.
*   **Why**: The `PokemonObject` class defines the schema, but `singletons.py` holds the active pointers (`main_pokemon`, `enemy_pokemon`). Mutating an object that isn't referenced in `singletons.py` achieves nothing.
*   **Confidence**: High.

## 5. Persistence
*   **Candidates**: Legacy JSON files, `src/Ankimon/pyobj/database_manager.py`.
*   **Authoritative File**: `src/Ankimon/pyobj/database_manager.py`.
*   **Why**: Since the migration, SQLite is the sole physical storage mechanism. This file contains the DAOs responsible for converting objects to SQL and executing transactions safely.
*   **Confidence**: High.

## 6. UI Rendering
*   **Candidates**: `src/Ankimon/functions/reviewer_iframe.py`, `src/Ankimon/user_files/web/ankimon_hud_portal.js`.
*   **Authoritative File**: `src/Ankimon/user_files/web/ankimon_hud_portal.js`.
*   **Why**: `reviewer_iframe.py` generates string payloads, but the JavaScript portal is the ultimate arbiter of how that HTML is attached to the DOM, handling isolation via Shadow DOM and preventing CSS leakage.
*   **Confidence**: High.

## 7. Orchestration
*   **Candidates**: `src/Ankimon/battle_loop.py`.
*   **Authoritative File**: `src/Ankimon/battle_loop.py`.
*   **Why**: It dictates the chronological sequence of evaluating multipliers, executing sounds, updating trackers, executing the engine, and updating the UI during the critical `on_review_card` event.
*   **Confidence**: High.

## If a future agent edits only one file per category, start here:
*   **Startup**: `src/Ankimon/__init__.py`
*   **Configuration**: `src/Ankimon/pyobj/settings.py`
*   **Domain Logic**: `src/Ankimon/poke_engine/evaluate.py`
*   **State Transitions**: `src/Ankimon/singletons.py`
*   **Persistence**: `src/Ankimon/pyobj/database_manager.py`

# Architecture Map

## 1. Entrypoints
*   **Anki Add-on Loader**: `src/Ankimon/__init__.py` is executed by Anki on startup.
*   **Review Gameloop**: `src/Ankimon/battle_loop.py:on_review_card()` is the entrypoint triggered by user interactions (answering cards).

## 2. Initialization Flow
**Directly evidenced by `src/Ankimon/startup.py`**:
1. Checks if the database is migrated (`ankimon_db.is_migrated()`).
2. Creates backups.
3. Checks asset existence (`_check_assets()`).
4. Generates initial enemy (`_init_first_enemy()`).
5. Checks if user needs a starter (`_check_starter()`).

## 3. Module Boundaries
*   `src/Ankimon/pyobj/`: PyQt6 UI classes and core domain entities (`pokemon_obj.py`, `ankimon_tracker.py`).
*   `src/Ankimon/gui_classes/`: Complex UI dialogs (Team overview, details).
*   `src/Ankimon/functions/`: Helper logic and glue code (e.g., `encounter_functions.py`, `sprite_functions.py`).
*   `src/Ankimon/poke_engine/`: Independent battle simulator submodule.
*   `src/Ankimon/user_files/`: Static assets (sprites, data JSONs, web JS/CSS).

## 4. Orchestration Model
The system uses an **event-driven orchestration model** bound to Anki's lifecycle hooks. `hook_registry.py` and `__init__.py` act as the primary orchestrators, connecting Anki's events (`reviewer_did_answer_card`, `sync_did_finish`) to Ankimon's domain logic.

## 5. State Flow
In-memory state is heavily centralized.
*   **Current Battle**: `enemy_pokemon` and `main_pokemon` singletons represent active participants.
*   **Tracking**: `ankimon_tracker_obj` manages multipliers, streaks, and session stats.
State mutates during `on_review_card`, applying engine outputs to `main_pokemon.hp`, then flushing changes periodically or on Anki close to SQLite.

## 6. Persistence Model
*   **Source of Truth**: `ankimon.db` (SQLite).
*   **Adapter**: `src/Ankimon/pyobj/database_manager.py`. Uses an in-memory cache for fast reads, but relies on explicit `.save_pokemon()` calls to write.

## 7. Configuration Model
*   Managed by `src/Ankimon/pyobj/settings.py`.
*   Data is stored in `config.json` via Anki's add-on config system. Settings are accessible globally via `settings_obj`.

## 8. Error/Side-Effect Boundaries
*   Errors in Anki hooks are wrapped in `try...except` blocks that call `show_warning_with_traceback` to prevent breaking Anki itself.
*   The `poke_engine` is strictly sandboxed. Errors there are caught in the bridge (`ankimon_hooks_to_poke_engine.py`).

## 9. External Integrations
*   **Discord**: Rich Presence via `pypresence`.
*   **Pokemon Showdown**: Export format generation.

## 10. Important Abstractions
*   `PokemonObject`: A massive data class holding all properties (stats, IVs, EVs, ID, moves) of a Pokémon.

## 11. High-confidence findings
*   The project has completed a major migration from JSON to SQLite for primary data storage.
*   The battle logic is entirely decoupled into `poke_engine` and only interfaces via a specific bridge function.

## 12. Open questions and ambiguous areas
*   How frequently is the global memory state explicitly synced to `ankimon_db`? Are there edge cases where `main_pokemon` changes are lost if Anki crashes?
*   The lifecycle of `poke_engine` mutator objects between turns.

## 13. Change-risk hotspots
*   `singletons.py`: Adding imports here easily causes circular dependency hell.
*   `battle_loop.py`: Modifying the main `on_review_card` loop can cause severe UI lag or crash the review process.

## 14. Likely architectural intent
The architecture evolved from a simple script to a complex application. The intent is clearly moving towards structured MVC, separating UI (`pyobj/`, `reviewer_iframe.py`), State (`singletons.py`, `database_manager.py`), and Logic (`poke_engine/`).

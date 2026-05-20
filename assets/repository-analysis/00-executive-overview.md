# Executive Overview: Ankimon Repository

## 1. What This Repository Appears To Be
Ankimon is a highly complex, event-driven Python application operating as an Anki add-on. It bridges the spaced-repetition software domain with a complete Pokémon RPG gameloop. By hooking into Anki's review cycle (specifically `reviewer_did_answer_card`), it triggers combat turns within a deeply integrated battle engine (`poke_engine`). The repository demonstrates a monolithic architecture where Anki's UI is manipulated via injected JavaScript/HTML, while a centralized SQLite database manages persistent state tracking captured Pokémon, items, and trainer progression.

## 2. How It Likely Starts
The startup sequence is explicitly defined and anchored in the repository entrypoints:
*   **Directly evidenced by:** `src/Ankimon/__init__.py`. When Anki loads the `src/Ankimon/` directory as an add-on, Python executes `__init__.py`.
*   **Initialization Flow:**
    1.  Singleton Initialization: `from .singletons import ...` instantiates the database, settings, global tracking objects, and mock/starting Pokémon states.
    2.  Infrastructure Checks: `ensure_ankimon_infrastructure()` creates necessary directories (`user_files/data_files`).
    3.  Database Migration: `run_startup_sequence()` in `startup.py` calls `show_migration_dialog_if_needed()`, aggressively attempting to move legacy JSON data (`mypokemon.json`) into the new SQLite format.
    4.  Hook Binding: `register_card_hooks()`, `setup_reviewer_ui()`, and `setupHooks()` attach Ankimon's execution paths to Anki's internal lifecycle events.

## 3. Major Subsystems
*   **The Orchestrator Layer**: Consists of `__init__.py`, `singletons.py`, and `startup.py`. Responsibilities include wiring the application to the host process (Anki) and maintaining the globally accessible state context.
*   **The Gameloop Controller**: Located primarily in `battle_loop.py` and `ankimon_tracker.py`. Responsibilities include reacting to card reviews, managing timers, calculating experience multipliers, and deciding when a combat turn should occur.
*   **The Domain Logic Engine (`poke_engine/`)**: A massive, isolated submodule handling the pure mathematics of Pokémon battles. It is completely decoupled from Anki. Responsibilities include calculating damage (`damage_calculator.py`), managing turn evaluation (`evaluate.py`), and managing volatile state (`objects.py`).
*   **The Persistence Adapter**: Encapsulated in `pyobj/database_manager.py`. Responsibilities include bridging the gap between in-memory `PokemonObject` representations and the physical SQLite file (`ankimon.db`).
*   **The UI Surface**: A hybrid of native PyQt6 Dialogs (e.g., `gui_classes/pokemon_team_window.py`) and injected web views (`user_files/web/ankimon_hud_portal.js`, `functions/reviewer_iframe.py`). Responsibilities include rendering the visual state of the game without breaking Anki's native rendering logic.

## 4. State and Persistence at a Glance
*   **State:** The application's active state is highly mutable and localized in global variables, specifically `main_pokemon` and `enemy_pokemon` housed in `singletons.py`.
*   **Persistence:** The definitive source of truth is the SQLite database. However, there is a recognized latency between mutating an in-memory `PokemonObject` and persisting it via `AnkimonDB.save_pokemon()`. Synchronization occurs aggressively at key lifecycle events (e.g., capturing a pokemon, ending a battle, closing Anki).

## 5. Integration Boundaries
*   **Anki Framework Boundary:** Exists primarily within `hooks.py`, `card_hooks.py`, and `reviewer_ui.py`. This is where the application depends on `aqt` and `anki` modules.
*   **Battle Simulation Boundary:** Exists at `functions/ankimon_hooks_to_poke_engine.py`. This single file acts as the translation layer between Ankimon's data models and `poke_engine`'s data models.
*   **Web Asset Boundary:** Exists between the Python backend and the injected JavaScript (`ankimon_hud_portal.js`), relying on Anki's `setWebExports` to serve local assets securely.

## 6. Top Risks
*   **State Desynchronization:** Because global instances are modified dynamically throughout the Gameloop Controller layer, failing to call the Persistence Adapter before application exit results in guaranteed data loss.
*   **Performance Bottlenecking the Review Cycle:** The gameloop executes synchronously during `reviewer_did_answer_card`. If `poke_engine` calculations or database writes block this thread, Anki's core functionality (rapid card reviewing) degrades to an unacceptable user experience.
*   **Circular Dependency Fragility:** The massive reliance on `singletons.py` means adding new imports across the codebase frequently results in `ImportError: cannot import name`.

## 7. What to Read First
Future agents must familiarize themselves with these files to understand the core control flow before attempting implementation changes:
1.  `src/Ankimon/__init__.py` - to understand the boundaries.
2.  `src/Ankimon/singletons.py` - to understand the state landscape.
3.  `src/Ankimon/battle_loop.py` - to understand the event loop.
4.  `src/Ankimon/pyobj/database_manager.py` - to understand data mutation safely.

## 8. Ranked List of the Top 15 Most Important Files
1. `src/Ankimon/__init__.py`
2. `src/Ankimon/singletons.py`
3. `src/Ankimon/battle_loop.py`
4. `src/Ankimon/pyobj/database_manager.py`
5. `src/Ankimon/startup.py`
6. `src/Ankimon/card_hooks.py`
7. `src/Ankimon/pyobj/pokemon_obj.py`
8. `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`
9. `src/Ankimon/poke_engine/battle.py`
10. `src/Ankimon/reviewer_ui.py`
11. `src/Ankimon/functions/reviewer_iframe.py`
12. `src/Ankimon/pyobj/ankimon_tracker.py`
13. `src/Ankimon/resources.py`
14. `src/Ankimon/utils.py`
15. `src/Ankimon/user_files/web/ankimon_hud_portal.js`

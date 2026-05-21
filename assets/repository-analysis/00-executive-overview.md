# Executive Overview: Ankimon Repository

## 1. What This Repository Appears To Be
Ankimon is a highly complex, event-driven Python application operating as an Anki add-on. It bridges the spaced-repetition software domain with a complete Pokémon RPG gameloop. By hooking into Anki's review cycle, it triggers combat turns within a deeply integrated, highly rigorous battle engine (`poke_engine`). The repository demonstrates a dual architecture: the outer shell (Ankimon) acts as an MVC application bridging Anki UI to an SQLite database, while the inner core (`poke_engine`) acts as a pure functional physics simulator for Pokémon combat mechanics.

## 2. How It Likely Starts
*   **Directly evidenced by:** `src/Ankimon/__init__.py`. When Anki loads the `src/Ankimon/` directory as an add-on, Python executes `__init__.py`.
*   **Initialization Flow:**
    1.  Singleton Initialization: `from .singletons import ...` instantiates the database, settings, global tracking objects, and mock/starting Pokémon states.
    2.  Infrastructure Checks: `ensure_ankimon_infrastructure()` creates necessary directories.
    3.  Database Migration: `run_startup_sequence()` aggressive moves legacy JSON data into the new SQLite format.
    4.  Hook Binding: `register_card_hooks()`, `setup_reviewer_ui()` attach Ankimon's execution paths to Anki's internal lifecycle events.

## 3. Major Subsystems
*   **The Orchestrator Layer**: `__init__.py`, `singletons.py`, and `startup.py`. Wires the application to Anki.
*   **The Gameloop Controller**: `battle_loop.py` and `ankimon_tracker.py`. Reacts to card reviews and dictates when a combat turn occurs.
*   **The Persistence Adapter**: `pyobj/database_manager.py`. Bridges the gap between in-memory `PokemonObject` representations and the physical SQLite file.
*   **The UI Surface**: A hybrid of native PyQt6 Dialogs and injected web views (`ankimon_hud_portal.js`).
*   **The Domain Logic Engine (`poke_engine/`)**: A massive, self-contained submodule that calculates combat. It consists of:
    *   **The Evaluator**: `evaluate.py` and `find_state_instructions.py` determine turn order, speed ties, and priority brackets.
    *   **The Physics Core**: `damage_calculator.py` and `instruction_generator.py` handle STAB, type effectiveness, and parsing raw attacks into discrete status/damage instructions.
    *   **The Effects Engine**: The `special_effects/` directory houses lifecycle hooks for abilities and items (e.g., `on_switch_in`, `end_of_turn`).

## 4. State and Persistence at a Glance
*   **Outer State:** Highly mutable and localized in global variables (`main_pokemon`, `enemy_pokemon` in `singletons.py`), periodically flushed to `ankimon.db` SQLite.
*   **Inner State (Engine):** The `poke_engine` operates on immutable `State` objects (`objects.py`), parsing inputs and returning a diff without mutating the outer database directly.

## 5. Integration Boundaries
*   **Anki Framework Boundary**: `hooks.py`, `card_hooks.py`.
*   **Battle Simulation Boundary**: `functions/ankimon_hooks_to_poke_engine.py`. This crucial adapter translates Ankimon's loose dictionaries into the strict `State` classes required by the engine.

## 6. Top Risks
*   **State Desynchronization:** Failing to call the Persistence Adapter before Anki exits results in guaranteed data loss.
*   **Performance Bottlenecking:** If `poke_engine` calculations (especially deep JSON lookups in `poke_engine/data/`) block the main UI thread during `reviewer_did_answer_card`, Anki freezes.
*   **Circular Dependency Fragility:** Massive reliance on `singletons.py` means adding new imports across the codebase frequently results in `ImportError`.

## 7. What to Read First
1.  `src/Ankimon/__init__.py` (Boundaries)
2.  `src/Ankimon/singletons.py` (State)
3.  `src/Ankimon/battle_loop.py` (Event Loop)
4.  `src/Ankimon/poke_engine/evaluate.py` (Combat Math Entrypoint)

## 8. Ranked List of the Top 15 Most Important Files
1. `src/Ankimon/__init__.py`
2. `src/Ankimon/singletons.py`
3. `src/Ankimon/battle_loop.py`
4. `src/Ankimon/pyobj/database_manager.py`
5. `src/Ankimon/startup.py`
6. `src/Ankimon/card_hooks.py`
7. `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`
8. `src/Ankimon/poke_engine/evaluate.py`
9. `src/Ankimon/poke_engine/instruction_generator.py`
10. `src/Ankimon/poke_engine/damage_calculator.py`
11. `src/Ankimon/pyobj/pokemon_obj.py`
12. `src/Ankimon/reviewer_ui.py`
13. `src/Ankimon/user_files/web/ankimon_hud_portal.js`
14. `src/Ankimon/pyobj/ankimon_tracker.py`
15. `src/Ankimon/resources.py`

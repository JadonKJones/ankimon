# Executive Overview: Ankimon Repository

## 1. What This Repository Appears to Be
Ankimon is a Python-based Anki add-on (using PyQt6 and QtWebEngine) that gamifies spaced-repetition flashcards by integrating a full-fledged Pokémon RPG loop. Answering flashcards correctly triggers attacks, heals, and state changes in a battle between the user's active Pokémon and wild encounters. It features persistence via SQLite, dynamic UI injection into Anki's reviewer window, and a complex embedded battle engine (`poke_engine`).

## 2. How It Likely Starts
**Directly evidenced by:** `src/Ankimon/__init__.py` and `src/Ankimon/startup.py`.
The add-on initializes when Anki loads it.
1. `__init__.py` runs first, importing singletons (`singletons.py`).
2. `singletons.py` instantiates the database manager (`AnkimonDB`), settings, and global state objects (`PokemonObject` for main and enemy).
3. `run_startup_sequence()` in `startup.py` executes, checking file integrity, running DB migrations from legacy JSON, and initializing the first enemy.
4. Hooks are registered via `aqt.gui_hooks`, primarily binding `on_review_card` to `reviewer_did_answer_card`.

## 3. Major Subsystems
*   **Core Orchestration**: `__init__.py` and `singletons.py` tie the system together.
*   **Anki Integration**: `card_hooks.py` and `hooks.py` interface with Anki's review cycle.
*   **Battle Logic (Domain)**: `battle_loop.py` serves as the glue between Anki and the battle engine. `poke_engine/` is the core simulation logic, isolated as an independent submodule. Bridge logic exists in `ankimon_hooks_to_poke_engine.py`.
*   **UI/HUD**: `reviewer_iframe.py` and `user_files/web/ankimon_hud_portal.js` handle injecting the visual battle representation into Anki. PyQt6 dialogs (`gui_classes/`, `pyobj/`) handle menus like Pokedex, PC Box, and Settings.
*   **Persistence**: `pyobj/database_manager.py` (SQLite) is the definitive storage backend.

## 4. State and Persistence at a Glance
**State**: In-memory state is heavily reliant on singletons (`main_pokemon`, `enemy_pokemon`, `ankimon_tracker_obj`) initialized in `singletons.py`.
**Persistence**: State is flushed to a SQLite database (`ankimon.db`) managed by `AnkimonDB`. This is a recent migration from legacy JSON files (`mypokemon.json`, `mainpokemon.json`).

## 5. Integration Boundaries
*   **Anki App**: `aqt` module dependencies (`mw`, `gui_hooks`).
*   **PokeAPI / Showdown**: Evidence suggests external integrations for sprites and showdown exports (`export_to_pkmn_showdown`).
*   **Discord**: Rich presence integration via `discord_integration.py`.

## 6. Top Risks
1.  **Singleton Mutability**: Global state in `singletons.py` is mutated widely. Desync between in-memory `PokemonObject` and `ankimon.db` is a high risk if saves are missed.
2.  **Hook Recursion/Performance**: Heavy logic inside `on_review_card` can lag Anki's review interface.
3.  **UI Injection Fragility**: Injecting CSS/JS via `ankimon_hud_portal.js` into Anki's webview is sensitive to Anki version updates.

## 7. What to Read First
1.  `src/Ankimon/__init__.py` (Entrypoint wiring)
2.  `src/Ankimon/singletons.py` (Global state map)
3.  `src/Ankimon/battle_loop.py` (Core gameloop execution)
4.  `src/Ankimon/pyobj/database_manager.py` (Data storage layer)

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

# Architecture Map

## 1. Entrypoints
*   **Anki Bootstrap Hook**: `src/Ankimon/__init__.py`. This script is executed by the Anki host environment upon startup. It binds the addon to the UI context.
*   **The Gameloop Trigger**: `src/Ankimon/battle_loop.py:on_review_card()`. While technically a callback, this function is the logical entrypoint for 90% of the addon's business logic, executing every time a user answers a card.

## 2. Initialization Flow
The application initializes via a strictly procedural path designed to validate data integrity before proceeding:
1.  **Environment Check**: `ensure_ankimon_infrastructure` creates required static directories.
2.  **Singleton Construction**: `singletons.py` is evaluated, instantiating `AnkimonDB`, which immediately attempts to connect to `ankimon.db`.
3.  **Migration and Backup**: `run_startup_sequence` in `startup.py` checks `ankimon_db.is_migrated()`. If false, a complex PyQT dialog prompts the user to migrate legacy `.json` files to SQLite. Backups are also triggered here.
4.  **Asset Verification**: `_check_assets()` verifies the existence of thousands of sprite files, triggering a download sequence if missing.
5.  **State Hydration**: `_init_first_enemy()` and `update_main_pokemon()` load the active fighting entities into the `PokemonObject` memory representations.

## 3. Module Boundaries
*   **`src/Ankimon/pyobj/`**: The Core Domain Entities layer. Contains class definitions for structural objects (`PokemonObject`, `AnkimonTracker`, `Settings`) and the SQLite adapter.
*   **`src/Ankimon/gui_classes/`**: The Complex UI layer. Contains robust PyQT Dialogs (e.g., `PokemonTeamDialog`) that handle user interaction outside the main gameloop.
*   **`src/Ankimon/functions/`**: The Utility and Glue layer. Procedural functions grouped by domain (e.g., `battle_functions.py`, `sprite_functions.py`) that lack persistent state.
*   **`src/Ankimon/poke_engine/`**: The Battle Simulator Submodule. A highly complex, isolated physics engine for Pokémon battles. It is strictly separated from the Anki context.
*   **`src/Ankimon/pokedex/`**: Specific encapsulation for the Pokédex UI and data retrieval.

## 4. Orchestration Model
The system operates on an **event-driven orchestration model**, specifically leveraging the Observer pattern via Anki's hook system.
*   Anki acts as the primary Subject.
*   Ankimon registers Observers (functions) via `aqt.gui_hooks.append()`.
*   When a state change occurs in Anki (a card is shown, a card is answered, sync finishes), the corresponding Observer in Ankimon executes.

## 5. State Flow
Data flows in a rigid cycle:
1.  **Read**: `database_manager.py` loads persistent data from SQLite into memory.
2.  **Hydrate**: Data is bound to `PokemonObject` instances in `singletons.py`.
3.  **Mutate**: `battle_loop.py` executes, modifying the `hp`, `xp`, and `level` attributes of the in-memory `PokemonObject`s based on user performance.
4.  **Persist**: Explicit calls to `ankimon_db.save_pokemon()` flush the mutated state back to SQLite.

## 6. Persistence Model
*   **Storage Medium**: SQLite (`ankimon.db`).
*   **Schema Design**: A primary `captured_pokemon` table using a generic schema, where complex attributes (like IV/EV spreads) are serialized as JSON strings within text columns.
*   **Caching Strategy**: `database_manager.py` implements an in-memory `_all_pokemon_cache` to minimize disk I/O, explicitly invalidated upon mutations.

## 7. Configuration Model
*   **Source**: Anki's native Addon Configuration schema (`config.json`).
*   **Access**: Wrapped by `src/Ankimon/pyobj/settings.py` providing a type-safe getter/setter interface globally available via `settings_obj`.

## 8. Error and Side-Effect Boundaries
*   **Anki Protection**: All hook callbacks are wrapped in `try...except` blocks utilizing `show_warning_with_traceback`. This ensures that a failure in the Gameloop Controller does not crash Anki itself.
*   **Engine Isolation**: The `poke_engine` is strictly functional regarding state. It accepts an input state, applies mutations via an instruction generator, and returns an output state diff. It performs no I/O operations.

## 9. External Integrations
*   **Discord Rich Presence**: `discord_integration.py` utilizes `pypresence` to broadcast the user's active gameloop state to Discord.
*   **Showdown Export**: `pokemon_showdown_functions.py` formats the user's SQLite data into standard Smogon formats for external competitive play.

## 10. Important Abstractions
*   **`PokemonObject`**: The central data structure holding combat and identification metadata.
*   **`AnkimonDB`**: The DAO (Data Access Object) abstracting direct SQL queries.
*   **`State` (poke_engine)**: The immutable representation of a battle phase before instructions are applied.

## 11. High-Confidence Findings
*   The system has successfully completed a massive architectural shift from flat-file JSON persistence to SQLite.
*   The Gameloop Controller is extremely tightly coupled to the Anki review window lifecycle.
*   The Battle Simulator is effectively a black-box submodule to the rest of the application.

## 12. Open Questions and Ambiguous Areas
*   **State Race Conditions**: What occurs if `on_review_card` fires rapidly in succession before the previous database write completes? The synchronicity of the SQLite connection in the context of PyQt's event loop is unclear.
*   **Memory Leaks**: `ankimon_hud_portal.js` continuously modifies the DOM. It is ambiguous whether Anki aggressively garbage collects the iframe contents between reviews.

## 13. Change-Risk Hotspots
*   `src/Ankimon/singletons.py`: Modifying imports here has a 90% probability of creating circular dependencies.
*   `src/Ankimon/battle_loop.py`: Modifying the synchronous logic here directly impacts the perceived responsiveness of Anki's flashcard review interface.

## 14. Likely Architectural Intent
The repository demonstrates a transition from a procedural script to an MVC-inspired application. The intent is clear: decouple data persistence (`database_manager.py`) from rendering (`reviewer_iframe.py`) and business logic (`poke_engine`), though significant technical debt remains in the form of `singletons.py` acting as a global namespace.

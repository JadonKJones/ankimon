# Architecture Map

## 1. Entrypoints
*   **Anki Bootstrap Hook**: `src/Ankimon/__init__.py`.
*   **The Gameloop Trigger**: `src/Ankimon/battle_loop.py:on_review_card()`.
*   **The Engine Trigger**: `src/Ankimon/poke_engine/evaluate.py`. The gateway into the isolated combat simulation.

## 2. Initialization Flow
1.  **Environment Check**: `ensure_ankimon_infrastructure`.
2.  **Singleton Construction**: `singletons.py` instantiates `AnkimonDB`.
3.  **Migration and Backup**: `run_startup_sequence` checks `ankimon_db.is_migrated()`.
4.  **Engine Hydration**: Large JSON datasets within `src/Ankimon/poke_engine/data/` (like `moves.json` and `pokedex.json`) are loaded into memory for rapid parsing during combat turns.

## 3. Module Boundaries
*   **`src/Ankimon/pyobj/`**: Core Domain Entities (`PokemonObject`) and SQLite adapter.
*   **`src/Ankimon/gui_classes/`**: Complex PyQT Dialogs.
*   **`src/Ankimon/poke_engine/`**: The Battle Simulator Submodule.
    *   *Boundary Sub-layer (`evaluate.py`, `battle.py`)*: Manages macro board state and turn ordering.
    *   *Physics Sub-layer (`instruction_generator.py`, `damage_calculator.py`)*: Applies STAB, crits, and converts moves to raw events.
    *   *Lifecycle Sub-layer (`special_effects/`)*: Handles isolated triggers for items and abilities.
    *   *Data Sub-layer (`data/`)*: Massive JSON stores acting as the physics constants.

## 4. Orchestration Model
*   **Outer Model**: Event-driven via Anki's hook system (`aqt.gui_hooks`).
*   **Inner Model (Engine)**: Functional Evaluation Pipeline. The engine takes an immutable `State` object and an Action, runs it through speed/priority resolution (`find_state_instructions.py`), generates discrete effect payloads (`instruction_generator.py`), and returns a modified `State`.

## 5. State Flow
1.  **Read**: `database_manager.py` loads persistent data into `singletons.py`.
2.  **Translate**: `ankimon_hooks_to_poke_engine.py` converts `PokemonObject` into the engine's `State` class.
3.  **Evaluate**: `poke_engine` parses the state and applies mathematical instructions.
4.  **Re-Hydrate**: The output `State` diff is translated back into the global `PokemonObject` attributes (hp, volatile status).
5.  **Persist**: Explicit calls to `ankimon_db.save_pokemon()` flush to SQLite.

## 6. Persistence Model
*   **Storage Medium**: SQLite (`ankimon.db`) via `database_manager.py`.

## 7. Configuration Model
*   **Source**: Anki's native `config.json` wrapped by `src/Ankimon/pyobj/settings.py`.

## 8. Error and Side-Effect Boundaries
*   **Anki Protection**: Gameloop errors are trapped via `show_warning_with_traceback`.
*   **Engine Isolation**: The `poke_engine` performs no I/O operations (after initial data load) and relies entirely on passed-in arguments, ensuring combat logic never accidentally crashes the database.

## 9. External Integrations
*   **Discord Rich Presence**: `discord_integration.py`.
*   **Showdown Export**: `pokemon_showdown_functions.py`.

## 10. Important Abstractions
*   **`PokemonObject` (Outer)**: The central data structure holding combat metadata.
*   **`State` (Inner Engine)**: The immutable representation of a battle phase before instructions are applied (`poke_engine/objects.py`).

## 11. High-Confidence Findings
*   The battle simulator is incredibly robust and strictly isolated from Anki's context. It functions identically to a headless Pokémon Showdown server implementation.

## 12. Open Questions and Ambiguous Areas
*   **Memory Footprint of Engine Data**: The `poke_engine/data/` JSON files are massive. It is unclear if these are lazily loaded or if they sit permanently in RAM while Anki is running.

## 13. Change-Risk Hotspots
*   `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`: This single file bears the entire weight of translating between the Outer and Inner architectures. Modifying a class in `poke_engine` without updating this adapter will shatter the gameloop.

## 14. Likely Architectural Intent
To completely decouple the complex mathematics of Pokémon from the fragile UI rendering of Anki, allowing the engine to be tested in isolation (`poke_engine/tests/`) while Ankimon handles user progression.

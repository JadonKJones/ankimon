# File Cards

## 1. `src/Ankimon/__init__.py`
*   **Primary responsibility**: Plugin entrypoint. Bootstraps the application, registers hooks, and ties modules together.
*   **Why it matters**: It is the first code executed. Understanding Ankimon starts here.
*   **Major symbols**: `run_startup_sequence`, `setup_reviewer_ui`, `on_review_card`.
*   **Key imports**: `aqt`, `singletons`, `startup`, `battle_loop`.
*   **File role**: Entrypoint / Orchestrator.
*   **Confidence level**: High.

## 2. `src/Ankimon/singletons.py`
*   **Primary responsibility**: Initializes and stores global instances.
*   **Why it matters**: Contains the in-memory source of truth for the active session (`main_pokemon`, `ankimon_db`).
*   **Major symbols**: `ankimon_db`, `settings_obj`, `main_pokemon`, `enemy_pokemon`, `ankimon_tracker_obj`.
*   **Key imports**: `pyobj.database_manager`, `pyobj.pokemon_obj`.
*   **File role**: State container / Glue.
*   **Confidence level**: High.

## 3. `src/Ankimon/battle_loop.py`
*   **Primary responsibility**: Handles what happens when a card is answered.
*   **Why it matters**: This is the core domain logic loop. It triggers the battle engine, updates health, and triggers UI updates.
*   **Major symbols**: `on_review_card`, `BattleState`.
*   **Key imports**: `functions.ankimon_hooks_to_poke_engine`.
*   **File role**: Domain logic / Orchestrator.
*   **Confidence level**: High.

## 4. `src/Ankimon/pyobj/database_manager.py`
*   **Primary responsibility**: SQLite storage adapter.
*   **Why it matters**: Definitive persistence layer. Replaced old JSON system.
*   **Major symbols**: `AnkimonDB`.
*   **File role**: Persistence.
*   **Confidence level**: High.

## 5. `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`
*   **Primary responsibility**: Bridges Ankimon's state to `poke_engine`'s state.
*   **Why it matters**: Translates `PokemonObject` into simulator `State` objects, runs the simulation, and translates damage/status back.
*   **Major symbols**: `simulate_battle_with_poke_engine`, `diff_states`.
*   **File role**: Integration adapter.
*   **Confidence level**: High.

## 6. `src/Ankimon/user_files/web/ankimon_hud_portal.js`
*   **Primary responsibility**: Injects the visual HUD into Anki's reviewer.
*   **Why it matters**: Uses Shadow DOM to isolate CSS/JS, representing the primary visual output during study.
*   **Major symbols**: `initAnkimonHUD`, `window.__ankimonHud.update`.
*   **File role**: UI surface.
*   **Confidence level**: High.

## 7. `src/Ankimon/pyobj/pokemon_obj.py`
*   **Primary responsibility**: Defines the data structure of a Pokémon in memory.
*   **Why it matters**: Everything revolves around mutating instances of this class.
*   **Major symbols**: `PokemonObject`.
*   **File role**: Domain logic / State container.
*   **Confidence level**: High.

## Secondary files worth checking later
*   `src/Ankimon/poke_engine/battle.py`
*   `src/Ankimon/pyobj/settings.py`

## Probably low-priority areas
*   `src/Ankimon/addon_files/`
*   `src/Ankimon/texts.py` (Mostly HTML templates)

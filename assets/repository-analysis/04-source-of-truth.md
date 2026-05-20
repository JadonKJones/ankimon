# Source of Truth

## 1. Startup and Orchestration
*   **Authoritative file**: `src/Ankimon/__init__.py`
*   **Why**: It is the explicit hook registration point for Anki.
*   **Confidence**: High.

## 2. Configuration
*   **Authoritative file**: `src/Ankimon/pyobj/settings.py` backed by Anki's `config.json`.
*   **Why**: `SettingsWindow` and all core functions rely on `settings_obj.get()`.
*   **Confidence**: High.

## 3. State Transitions (Memory)
*   **Authoritative file**: `src/Ankimon/singletons.py`
*   **Why**: Instances like `main_pokemon` initialized here are imported and mutated globally.
*   **Confidence**: High.

## 4. Persistence
*   **Authoritative file**: `src/Ankimon/pyobj/database_manager.py`
*   **Why**: Manages `ankimon.db`. Bypassing this file to modify data will cause desync.
*   **Confidence**: High.

## 5. Domain Logic (Battle Mechanics)
*   **Authoritative file**: `src/Ankimon/poke_engine/` (specifically `evaluate.py`, `battle.py`, `damage_calculator.py`).
*   **Why**: All damage math and type effectiveness are delegated here.
*   **Confidence**: High.

## If a future agent edits only one file per category, start here
*   **Orchestration**: `__init__.py`
*   **Persistence**: `database_manager.py`
*   **Battle Flow**: `battle_loop.py`

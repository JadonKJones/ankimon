# Import and Call Hotspots

Structural centers of gravity in the codebase identified via AST analysis.

## 1. High Fan-In (The Chokepoints)
Files that are imported by a massive number of other modules.
*   **`src/Ankimon/singletons.py`**: The absolute center of gravity. Exporting `main_pokemon`, `settings_obj`, and `ankimon_db`, it is imported by almost every GUI class, utility function, and hook orchestrator. It represents a massive coupling risk.
*   **`src/Ankimon/resources.py`**: Contains hardcoded file paths (`addon_dir`, `user_path`), constants, and Pokémon tier lists. High fan-in, but acceptable as it acts purely as a static configuration provider.
*   **`src/Ankimon/utils.py`**: Provides generic helper functions (`play_sound`, `get_tier_by_id`, random number generators). Safely relied upon across the application.
*   **`src/Ankimon/pyobj/database_manager.py`**: All modules requiring persistent data must route through the `AnkimonDB` class defined here.

## 2. High Fan-Out (The Orchestrators)
Files that coordinate many sub-dependencies to execute complex flows.
*   **`src/Ankimon/__init__.py`**: Imports nearly the entire `pyobj/` and `gui_classes/` trees to wire them into the Anki toolbar and hook system.
*   **`src/Ankimon/battle_loop.py`**: Coordinates `ankimon_tracker`, `singletons`, `ankimon_hooks_to_poke_engine`, `reviewer_iframe`, and `utils.play_sound` to execute a single turn of combat.
*   **`src/Ankimon/startup.py`**: Coordinates migrations, backups, asset downloads, and initial state generation.

## 3. Suspicious Dependency Concentrations
*   **The `gui_classes/` and `pyobj/` UI overlapping**: UI dialogs frequently import *other* UI dialogs to open sub-menus, creating tightly bound visual logic instead of relying on a centralized navigation controller.
*   **`ankimon_hooks_to_poke_engine.py`**: This single file bears the entire weight of translating Ankimon's vast, loosely-typed dictionaries and `PokemonObject` attributes into the highly strict, deeply nested class structures of the `poke_engine`. It is a massive structural chokepoint; any change to either domain model requires editing this specific file.

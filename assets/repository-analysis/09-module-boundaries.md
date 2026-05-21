# Module Boundaries

## Major Subsystems and Responsibilities

### 1. Host Integration Subsystem
*   **Files**: `__init__.py`, `hooks.py`, `card_hooks.py`, `startup.py`.
*   **Responsibilities**: Hooks into Anki's PyQt lifecycle. Manages application startup, dependency injection of menus into Anki's toolbar, and listens for flashcard answers.
*   **Dependencies**: Highly dependent on `aqt` and `anki`. Acceptable dependency.

### 2. Global State Registry
*   **Files**: `singletons.py`.
*   **Responsibilities**: Houses references to `main_pokemon`, `enemy_pokemon`, `ankimon_db`.
*   **Boundary Violations**: Severe. This subsystem violates encapsulation by allowing UI layers to directly mutate domain objects without going through a controller.

### 3. Domain Controller
*   **Files**: `battle_loop.py`, `ankimon_tracker.py`.
*   **Responsibilities**: Dictates the flow of time (ticks). Decides when a gameloop turn executes based on Anki card reviews.

### 4. Battle Engine Subsystem (`src/Ankimon/poke_engine/`)
This is the most structurally complex module in the repository, operating as a fully isolated pure-Python functional core. It breaks down into internal boundaries:
*   **The Outer Boundary (Adapter)**: `functions/ankimon_hooks_to_poke_engine.py`. This is the *only* file allowed to talk to the engine. It translates Ankimon's state.
*   **The Evaluator Core**: `evaluate.py`, `battle.py`, `battle_modifier.py`. Manages the macro board state, weather, turn ordering, and priority brackets (like Prankster or Grassy Glide).
*   **The Physics Core**: `damage_calculator.py`, `instruction_generator.py`. Contains the raw mathematics. It takes an action and returns a diff instruction (e.g., how much HP to deduct, what stats to drop).
*   **The Lifecycle Hooks (`special_effects/`)**: Contains logic for abilities and items that trigger passively (e.g., Leftovers healing at `end_of_turn`, or Intimidate triggering `on_switch_in`).
*   **The Static Physics Data (`data/`)**: Massive JSON files (`moves.json`, `pokedex.json`) that act as the physical laws of the universe for the evaluator.
*   **Dependencies**: Zero outward dependencies. It knows nothing about Anki or SQLite. Excellent encapsulation.

### 5. Persistence Subsystem
*   **Files**: `pyobj/database_manager.py`.
*   **Responsibilities**: Abstracts SQLite read/write operations.

### 6. Interactive UI Subsystem
*   **Files**: `gui_classes/`, `pyobj/*_window.py`.
*   **Responsibilities**: Renders interactive menus (Team, Pokedex, Settings) using PyQt6.

## Where future architecture cleanup would likely pay off most
Replacing `singletons.py` with a formal `GameStateManager` class. This class should encapsulate `main_pokemon` and provide explicit `.apply_damage()`, `.heal()`, and `.add_xp()` methods that automatically trigger `database_manager.py` syncs.

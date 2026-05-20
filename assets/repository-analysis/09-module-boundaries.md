# Module Boundaries

## Major Subsystems and Responsibilities

### 1. Host Integration Subsystem
*   **Files**: `__init__.py`, `hooks.py`, `card_hooks.py`, `startup.py`.
*   **Responsibilities**: Hooks into Anki's PyQt lifecycle. Manages application startup, dependency injection of menus into Anki's toolbar, and listens for flashcard answers.
*   **Communication**: Calls downward into the Domain Controller subsystem.
*   **Dependencies**: Highly dependent on `aqt` and `anki`. Acceptable dependency.

### 2. Global State Registry
*   **Files**: `singletons.py`.
*   **Responsibilities**: Houses references to `main_pokemon`, `enemy_pokemon`, `ankimon_db`, and `settings_obj`.
*   **Communication**: Exported and imported by nearly every other subsystem.
*   **Boundary Violations**: Severe. This subsystem violates encapsulation by allowing UI layers to directly mutate domain objects without going through a controller.

### 3. Domain Controller
*   **Files**: `battle_loop.py`, `ankimon_tracker.py`.
*   **Responsibilities**: Dictates the flow of time (ticks). Decides when a gameloop turn executes based on Anki card reviews.
*   **Communication**: Passes state objects to the Battle Engine, receives diffs, mutates the State Registry, and triggers UI updates.

### 4. Battle Engine Subsystem
*   **Files**: `poke_engine/` directory.
*   **Responsibilities**: Pure mathematical and logical evaluation of combat rules.
*   **Communication**: Isolated. Only communicates upward via return values from `evaluate.py`.
*   **Dependencies**: Zero outward dependencies. Excellent encapsulation.

### 5. Persistence Subsystem
*   **Files**: `pyobj/database_manager.py`.
*   **Responsibilities**: Abstracts SQLite read/write operations.
*   **Communication**: Called by the Domain Controller and UI components to flush state to disk.

### 6. Interactive UI Subsystem
*   **Files**: `gui_classes/`, `pyobj/*_window.py`.
*   **Responsibilities**: Renders interactive menus (Team, Pokedex, Settings) using PyQt6.
*   **Boundary Violations**: Frequent direct mutation of `singletons.py` data instead of dispatching intents to a controller.

## Where future architecture cleanup would likely pay off most
Replacing `singletons.py` with a formal `GameStateManager` class. This class should encapsulate `main_pokemon` and provide explicit `.apply_damage()`, `.heal()`, and `.add_xp()` methods that automatically trigger `database_manager.py` syncs. This would eliminate the silent data-loss bugs inherent in arbitrary UI layers directly mutating object properties.

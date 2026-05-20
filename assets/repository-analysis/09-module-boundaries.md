# Module Boundaries

## Subsystems
1.  **Anki Integration Layer (`__init__.py`, `hooks.py`, `card_hooks.py`)**: Responsible solely for registering callbacks with Anki. Should contain minimal business logic.
2.  **Global State (`singletons.py`)**: A monolithic registry of active objects. Highly coupled.
3.  **Domain Controller (`battle_loop.py`, `ankimon_tracker.py`)**: Manages the flow of time and state transitions based on flashcard reviews.
4.  **Battle Engine (`poke_engine/`)**: Pure domain logic. Isolated, calculates math, returns state diffs.
5.  **Persistence (`database_manager.py`)**: Abstracted SQLite access.

## Boundary Violations
*   UI dialogs (`pyobj/`, `gui_classes/`) frequently mutate `main_pokemon` directly instead of passing commands through a controller or the database manager.

## Where future architecture cleanup would likely pay off most
Replacing `singletons.py` with a structured State Manager class passed via dependency injection would massively reduce circular import risks and make testing easier.

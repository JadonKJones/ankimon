# Conventions Observed

This document details the practical, established coding patterns actively used within the repository, verified by structural evidence.

## 1. Global State Mutation via Singletons
*   **Evidence**: `main_pokemon.hp -= damage` occurs directly in `battle_loop.py` using variables imported from `singletons.py`.
*   **Strength**: Strong.
*   **Guidance for future edits**: While an anti-pattern in modern architecture, this is the established norm here. Do not attempt to refactor the entire system to use dependency injection in a single PR. Accept the singleton pattern but ensure synchronization with persistence.

## 2. Deferred Imports for Circular Dependency Resolution
*   **Evidence**: Functions like `_check_starter()` in `startup.py` explicitly declare `from .pyobj.database_manager import get_db` inside the function body rather than at the top of the file.
*   **Strength**: Strong.
*   **Guidance for future edits**: When importing `singletons`, `settings`, or complex UI objects into helper functions, place the import inside the executing block to prevent import resolution crashes during Python initialization.

## 3. UI Error Suppression
*   **Evidence**: Pervasive use of `try...except Exception as e: show_warning_with_traceback(parent=mw, exception=e)` wrapping hook callbacks in `battle_loop.py` and `startup.py`.
*   **Strength**: Strong.
*   **Guidance for future edits**: Never allow an exception to escape a hook bound to an Anki event. Doing so breaks Anki's native functionality. Always catch generic `Exception` at the top level of the hook and delegate to the custom warning logger.

## 4. Dictionary vs Object Polymorphism
*   **Evidence**: The codebase frequently transitions between pure Python `dict`s and instantiated `PokemonObject`s. `AnkimonDB` methods expect dictionaries (`pokemon_data: Dict[str, Any]`), requiring `.to_dict()` serialization.
*   **Strength**: Moderate.
*   **Guidance for future edits**: Be hyper-aware of whether a variable holds a dict or an object instance. Do not attempt dot-notation (`pokemon.hp`) on data freshly queried from the database; it must be hydrated first.

## 5. UI Layer Injection vs Native Rendering
*   **Evidence**: The primary combat HUD is rendered via injected HTML/JS (`ankimon_hud_portal.js`), whereas menus (Settings, Team, Pokedex) use native PyQt6 `QDialog`s.
*   **Strength**: Strong.
*   **Guidance for future edits**: If a feature needs to be visible *during* a flashcard review, build it in HTML/JS. If a feature pauses the review or requires complex interactive data entry, build it in PyQt6.

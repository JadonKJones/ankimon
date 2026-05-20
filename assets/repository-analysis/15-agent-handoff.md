# Agent Handoff

*   **What is well understood**: The macro architecture is solidly mapped. Anki hooks trigger `battle_loop.py`. The loop translates `PokemonObject` singletons into `State` objects for the `poke_engine`. The engine calculates damage. The loop updates the HUD via injected JS and mutates the singletons. Finally, `database_manager.py` flushes the changes to SQLite.
*   **What is partially understood**: The exact synchronization boundaries. It is clear that the database is flushed aggressively, but the specific edge cases where an in-memory mutation might bypass a `.save()` call require manual tracing of the UI dialogs (`gui_classes/`).
*   **What files should be consulted first for future work**:
    1. `battle_loop.py` (Gameloop logic)
    2. `singletons.py` (State reference)
    3. `database_manager.py` (Schema/Persistence)
*   **What edits would be safest**: Modifying pure mathematical logic inside `poke_engine/` or altering HTML templates in `texts.py`.
*   **What edits would be riskiest**: Modifying import orders anywhere near `singletons.py`, or adding heavy I/O operations inside `on_review_card`.
*   **Do Not Overlook**: Python booleans subclass integers. When comparing configuration states, always use strict `type()` checking to avoid `True == 1` collisions.

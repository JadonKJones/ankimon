# Event Hooks and Side Effects

*   **`gui_hooks.reviewer_did_answer_card`**:
    *   **Side Effects**: Increments internal session counters, calculates XP/damage, executes `poke_engine`, mutates singleton `PokemonObject`s, triggers audio playback, and dispatches HTML updates to the DOM.
*   **`gui_hooks.sync_did_finish`**:
    *   **Side Effects**: Flushes the `database_manager` in-memory cache to the SQLite physical file to ensure data safety before Anki closes.
*   **`gui_hooks.webview_will_set_content`**:
    *   **Side Effects**: Modifies the DOM tree of Anki's reviewer window to inject the Shadow DOM container for the gameloop HUD.

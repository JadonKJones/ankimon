# Unknowns and Questions

1.  **Question**: How does Ankimon handle concurrent database access if the user clicks through flashcards faster than SQLite can flush to disk?
    *   **Why it matters**: Rapid asynchronous reviews could trigger SQLite locking errors (`database is locked`) or result in dropped updates.
    *   **Missing Evidence**: The exact thread safety mechanisms inside `database_manager.py` regarding Anki's GUI event loop are not definitively established.
    *   **Priority**: High.

2.  **Question**: What is the garbage collection behavior of the injected `ankimon_hud_portal.js`?
    *   **Why it matters**: Re-injecting the massive base64 sprite payloads into the Anki webview every flashcard review might cause memory leaks over a long session.
    *   **Missing Evidence**: Profiling data of the Anki QtWebEngine process during a 500-card review session.
    *   **Priority**: Medium.

3.  **Question**: How much of `poke_engine` is proprietary vs a direct port of Pokémon Showdown?
    *   **Why it matters**: If it's a direct port, future agents could leverage Showdown's documentation for mechanics. If heavily modified, agents must rely solely on the engine's internal code.
    *   **Priority**: Low.

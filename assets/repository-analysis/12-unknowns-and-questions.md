# Unknowns and Questions

1.  **Question**: How exactly is `poke_engine` synchronized with upstream changes (if it's a fork of showdown logic)?
    *   **Why it matters**: Updating the engine might break the `ankimon_hooks_to_poke_engine.py` bridge.
    *   **Priority**: Medium.

2.  **Question**: Does the SQLite migration process handle all edge cases from older JSON formats gracefully?
    *   **Why it matters**: Data loss on update is a severe user impact.
    *   **File**: `startup.py` and `migration.py`.
    *   **Priority**: High.

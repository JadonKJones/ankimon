# Test Intelligence

*   **Test locations**: `tests/` and `src/Ankimon/poke_engine/tests/`.
*   **Behavior Defined**: Tests exist but are difficult to run due to heavy `aqt` (Anki) and `PyQt6` mocking requirements.
*   **Specification**: The `poke_engine` has its own isolated tests, indicating strong behavioral specification for battle mechanics (damage math, effectiveness).
*   **Gaps**: The integration between Anki hooks and the UI rendering appears largely untested programmatically, relying on manual verification.

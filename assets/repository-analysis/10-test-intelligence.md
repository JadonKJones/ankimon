# Test Intelligence

*   **Major Test Locations**:
    *   `tests/` (Root level): Intended for Ankimon integration tests.
    *   `src/Ankimon/poke_engine/tests/`: Dedicated unit tests for the combat engine.
*   **Behavior Defined by Tests**: The `poke_engine` tests define the explicit mathematical bounds of combat: validating STAB (Same Type Attack Bonus), type effectiveness multipliers, critical hit ratios, and status condition application.
*   **Strong Specification Areas**: Core combat math (`damage_calculator.py`, `instruction_generator.py`) is highly specified by the engine tests.
*   **Weak Specification Areas**: The integration layer (`ankimon_hooks_to_poke_engine.py`) and the persistence layer (`database_manager.py`) appear to lack comprehensive programmatic test coverage.
*   **Missing Coverage Zones**: The injection of the HUD payload via `reviewer_iframe.py` and the handling of Anki hooks (`card_hooks.py`) are virtually untestable via standard Python unit tests without heavy, complex mocking of the PyQt6 `aqt` framework. These areas are fragile and rely on manual regression testing by developers.

# Test Intelligence

This document outlines the testing architecture, mock environments, and verification strategies established in the Ankimon fork codebase.

---

## Testing Infrastructure

### 1. Structural Smoke Tests (`tests/`)
- Checked using `pytest`: `python -m pytest tests/`
- Unit testing mocks Anki's modules (`aqt` and `anki` via `sys.modules` monkeypatching) to allow importing the addon code outside of the live Anki application.
- UI tests require `QT_QPA_PLATFORM=offscreen` to execute PyQt6 headless windows.
- Major files:
  - `test_addon_integrity.py`: Import checks.
  - `test_settings_consistency.py`: Confirms configuration keys have valid defaults and types.

### 2. Comprehensive Encounter Simulation Suite (`scratch/encounter_weighting_simulations/`)
A robust, offline testing and behavioral verification pipeline is implemented in:
- **Test File:** `scratch/encounter_weighting_simulations/test_encounter_simulation.py`
- **Purpose:** Simulates, asserts, and verifies all 11 core encounter systems under 22 specialized test suites.

This simulation suite runs 10,000 mock generations to verify:
- **Pool Weights:** Verifies exact tier percentage rolls (Legendary, Starter, Regional, Rare, Common).
- **Active Region Weighting:** Verifies Alola/Hisui pools spawn at exactly Hisui: 40%, Others: 30% frequency when regional boosts are toggled.
- **Starter Pokémon Gating:** Asserts that starters do not spawn below trainer level 40 (or a hard level floor of 30), and that rarity is capped at 2.5%.
- **Capture Requirements (Prerequisite) Gating:** Verifies recursion chains (e.g. Ivysaur cannot spawn unless Bulbasaur has been marked as registered in SQLite).
- **Post-Selection Substitution:** Asserts that selected base species roll `7 * n %` replacement rates into their regional variants correctly.
- **Base Generational Check:** Confirms special form IDs (IDs >= 10000) check the base `species_id` against enabled generation toggles.

---

## Mocking & Database Isolation Strategy

To verify state persistence and progression without altering or corrupting the user's active player profile, tests utilize isolated databases:

```
                  [Run pytest / Simulation]
                              │
             Isolate Anki mw environment references
                              │
                              ▼
          Create an In-Memory SQLite database (:memory:)
            or write to temp test_ankimon.db file
                              │
                              ▼
          Call AnkimonDB.create_tables() to hydrate schema
                              │
                              ▼
          Inject mock trainer level & caught entries
                              │
                              ▼
          Execute encounter rolls & assert behaviors
```

---

## Guidelines for Extending Tests

When implementing new features or adding new regional variant pools:
1. **Never perform dynamic I/O tests:** Ensure tests use memory structures rather than loading physical JSON files repeatedly.
2. **Update the Simulation Suite:** Add a corresponding check in `test_encounter_simulation.py` to assert that the new species, variants, or settings caps behave as expected.
3. **Verify Prerequisite DAGs:** Run prerequisite checking tests to guarantee that new gating rules do not create infinite recursion loops.

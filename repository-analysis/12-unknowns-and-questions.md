# Resolved Unknowns & System Specifications

This document catalogs critical codebase uncertainties that have been successfully resolved, providing clear specifications for future developers.

---

## 1. Profile Switching and Runtime SQLite Re-loading (Resolved)
- **Previous Uncertainty:** How does the add-on manage connection pooling and file locks when a user switches profiles inside Anki, or toggles accounts?
- **Resolution & Specification:** The Ankimon fork implements a complete, runtime Database Hot-Swap pipeline. Under `swap_ankimon_account()` (in `singletons.py`) and `switch_database()` (in `pyobj/database_manager.py`), active sqlite3 connections are closed atomically using `conn.close()`. The file path is re-bound (toggling between `ankimon.db` and `ankimonDEV.db`), a new connection opened, and a state refresh cascade is triggered. This dynamically reloads configurations, PC Box grids, and the active user's trainer HUD without requiring an Anki reboot or risking file locks.

---

## 2. Test Completeness & Offline Simulation Environments (Resolved)
- **Previous Uncertainty:** Are complex encounter pools, starter weights, and prerequisite logic verified via automated tests, or are they untested?
- **Resolution & Specification:** Fully verified! The fork features a comprehensive simulation-based testing suite inside `scratch/encounter_weighting_simulations/test_encounter_simulation.py`. Running this script executes 22 advanced offline test suites, asserting the correctness of pool weighting, regional variants post-selection replacement, starter level bounds, and recursive evolutionary prereqs gating using isolated mock tables.

---

## 3. Generational Gating of Custom Form IDs (Resolved)
- **Previous Uncertainty:** How do Megas, Gigantamax, and other special form variants with IDs >= 10000 interact with generational configuration toggles?
- **Resolution & Specification:** Resolved inside `check_id_ok` in `functions/encounter_functions.py`. The generation checker dynamically resolves the base `species_id` of special forms using Pokedex caches. Disabling a generation (e.g. Generation 1) correctly and automatically prevents both base forms (e.g. Mewtwo) and their special forms (e.g. Mewtwo-Mega-Y, ID: 10065) from spawning.

---

## 4. Ephemeral vs. Persistent State in `AnkimonTracker`
- **Specification:** The `AnkimonTracker` maintains the active review countdowns (`cards_battle_round`) and review multipliers in memory. On application teardown or review completion, key progress states are committed to the SQLite `user_data` and `config` tables, ensuring study counts are accurately preserved across restarts.

---

## 5. `poke_engine` Move and PP Status Sync
- **Specification:** Active PP counts and statuses are mapped back and forth in `simulate_battle_with_poke_engine` inside `poke_engine/ankimon_hooks_to_poke_engine.py`. Volatile statuses (confusion, attraction) are cleared at the end of battles, while permanent status conditions (paralyzed, poisoned) are synced to the `PokemonObject` and persisted in the SQLite `captured_pokemon` table.

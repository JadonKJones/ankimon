# Reading Order

Optimized paths for understanding or editing the Ankimon codebase.

---

## 1. Fast Architectural Orientation
*Goal: Understand how the add-on attaches to Anki and drives the main game loop.*

1. **`__init__.py`**: Look at `on_review_card` and `on_profile_did_open`. Understand how Anki hooks drive the logic.
2. **`singletons.py`**: Note the instantiation of `main_pokemon`, `enemy_pokemon`, `ankimon_tracker_obj`, and the database manager `ankimon_db`.
3. **`pyobj/database_manager.py`**: Read `AnkimonDB` schema initialization and SQL helper query pathways.
4. **`pyobj/ankimon_tracker.py`**: See how `cards_battle_round` increments and triggers a battle turn.
5. **`poke_engine/ankimon_hooks_to_poke_engine.py`**: Read `simulate_battle_with_poke_engine` to see how Ankimon state enters the engine.
6. **`functions/battle_functions.py`**: Read `process_battle_data` to see how engine results are formatted for the UI tooltip.
7. **`resources.py`**: Review to understand where database and static files are located.
8. **`.agents/repository-analysis/01-architecture-map.md`**: Synthesize the mental model.

---

## 2. Developer-Mode & Diagnostics Trails
*Goal: Understand how to develop, test, and run encounter simulations offline without booting Anki.*

1. **`reloader.py`**: Read `restart_ankimon` to see how hooks are unregistered, windows are closed, and modules are purged from `sys.modules`.
2. **`singletons.py`**: Study `swap_ankimon_account()` and how it hot-swaps active database paths at runtime.
3. **`scratch/encounter_weighting_simulations/test_encounter_simulation.py`**: Run and inspect the 22 comprehensive simulation suites. This verifies pool weights, active region generation, and starter progression limits without Anki active.
4. **`functions/encounter_functions.py`**: Check `generate_random_pokemon` and its double-pool selection logic.
5. **`functions/encounter_data.py`**: Read `PREREQUISITES` and `REGIONAL_FORM_LOOKUP` definitions.

---

## 3. UI Hooks & Reviewer Layout Gating Trails
*Goal: Trace how the user interface is rendered, how hotkeys are hooked, and how inputs are validated.*

1. **`reviewer_ui.py`**: Read shortcut key bindings and bottom HTML "around" hooks. Notice the `_ui_hooks_installed` guards.
2. **`pyobj/settings_window.py`**: Read the `on_save()` self-correcting validation loops that enforce the **100:1 cash-to-card reward cap** and interval constraints.
3. **`pyobj/pc_box.py`**: Check grid loaders and move picker tables in the modernized 3:2 layout.
4. **Pokedex V2 views**: View how node completeness maps are styled with standard CSS theme variables.

---

## 4. Deep Architecture Study (Battle Engine)
*Goal: Understand the internal mechanics of the battle simulator.*

1. **`poke_engine/battle.py`**: Read the `Battle`, `Pokemon`, and `Move` class definitions. Notice how they differ from the `PokemonObject` in `pyobj/`.
2. **`poke_engine/instruction_generator.py`**: Read `get_instructions_from_damage` and the status immunity functions.
3. **`poke_engine/damage_calculator.py`**: Read `calculate_damage` and its modifier functions (STAB, weather).
4. **`poke_engine/special_effects/moves/move_special_effect.py`**: See how unique move behaviors (like Trick Room) are implemented.
5. **`poke_engine/ankimon_hooks_to_poke_engine.py`**: Study the translation layer that wraps the above files.

---

## 5. Debugging Runtime Behavior (State and SQLite Saves)
*Goal: Trace how data is updated and persisted, especially for "lost progress" or SQL locking bugs.*

1. **`pyobj/pokemon_obj.py`**: Review the `PokemonObject` attributes and update methods.
2. **`pyobj/database_manager.py`**: Look at `save_pokemon`, `get_pokemon`, and database transaction queries.
3. **`functions/update_main_pokemon.py`**: Look at `save_main_pokemon` and `update_main_pokemon`. Note how they invoke `mw.ankimon_db.save_pokemon()`.
4. **`pyobj/ankimon_sync.py`**: Check how AnkiWeb SQLite sync logic is implemented without producing write locks.
5. **`functions/encounter_functions.py`**: Check `catch_pokemon` and `handle_enemy_faint` to see where new database rows are generated.

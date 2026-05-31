# File Cards: Navigation Layer

## Primary Orchestration & Entrypoints

### `__init__.py`
- **Primary Responsibility:** Entrypoint for Anki. Initializes the add-on, sets up review lifecycle hooks, and runs the main battle loop on card review.
- **Why it matters:** It is the primary orchestrator. It connects Anki's events to the internal game state. Editing this affects the entire lifecycle.
- **Major Symbols:** `on_review_card`, `download_changelog`, hook registrations.
- **Dependencies:** `aqt`, `singletons`, `poke_engine`, various `functions`.
- **Role:** Entrypoint / Orchestrator
- **Confidence Level:** High

### `reloader.py`
- **Primary Responsibility:** Core developer-mode module for hot-reloading the Ankimon add-on without restarting Anki.
- **Why it matters:** Cleans up previous application states to prevent memory leaks and duplicate reviewer hook wrapping during dynamic updates.
- **Major Symbols:** `teardown_ankimon`, `restart_ankimon`.
- **Dependencies:** `aqt`, `sys`, `importlib`.
- **Role:** Developer Utility / State Cleaner
- **Confidence Level:** High

### `singletons.py`
- **Primary Responsibility:** Instantiates and holds global, reload-safe references to managers, database connections, settings, and player cards anchored to `mw`.
- **Why it matters:** Central state registry. Almost every UI component and gameplay function relies on the instances created here. Contains the dynamic profile hot-swapper.
- **Major Symbols:** `settings_obj`, `main_pokemon`, `enemy_pokemon`, `ankimon_tracker_obj`, `ankimon_db`, `swap_ankimon_account`.
- **Dependencies:** `pyobj.*`, `gui_entities`, `aqt.mw`.
- **Role:** State Container / Glue
- **Confidence Level:** High

### `pyobj/database_manager.py`
- **Primary Responsibility:** The persistence layer managing the SQLite database files (`ankimon.db` and `ankimonDEV.db`) through the `AnkimonDB` class.
- **Why it matters:** The database serves as the single source of truth for saves, team configurations, items, badges, and metadata.
- **Major Symbols:** `AnkimonDB`, `execute_query`, `save_pokemon`, `load_team`, `save_item`, `create_tables`, `switch_database`.
- **Dependencies:** `sqlite3`, `pyobj/pokemon_obj.py`.
- **Role:** Persistence Manager
- **Confidence Level:** High

### `resources.py`
- **Primary Responsibility:** Defines static file paths, media folders, and config boundaries used across the project.
- **Why it matters:** Central source of truth for where data, sprites, and configs are stored.
- **Major Symbols:** `addon_dir`, `user_path`, `database_path`, `generate_startup_files`.
- **Role:** Config / Utility
- **Confidence Level:** High

---

## Core Domain & State

### `functions/encounter_data.py`
- **Primary Responsibility:** Holds authoritative lists of rarity pools, level thresholds, regional form indexes, and starter prerequisites.
- **Why it matters:** Serving as the single source of truth for encounter properties, eliminating dynamic file reads at runtime.
- **Major Symbols:** `LEGENDARY`, `MYTHICAL`, `MEGA`, `GMAX`, `STARTERS`, `REGIONAL_FORMS`, `PREREQUISITES`, `REGIONAL_FORM_LOOKUP`, `ACTIVE_REGION_BOOSTS`.
- **Role:** Static Domain Database
- **Confidence Level:** High

### `pyobj/pokemon_obj.py`
- **Primary Responsibility:** Defines the `PokemonObject` class, representing a Pokémon's stats, moves, levels, types, and active statuses.
- **Why it matters:** It is the core domain model. All battle logic and UI rendering depend on the structure of this object.
- **Major Symbols:** `PokemonObject`, `update_stats`, `calculate_max_hp`, `reset_bonuses`.
- **Role:** Domain Logic / State Container
- **Confidence Level:** High

### `pyobj/ankimon_tracker.py`
- **Primary Responsibility:** Tracks progress across review sessions (e.g., cards reviewed, encounters, time taken).
- **Why it matters:** Drives the progression of the game; decides when a battle round occurs based on review counts.
- **Major Symbols:** `AnkimonTracker`, `review`, `reset_card_timer`.
- **Role:** State Container / Orchestrator
- **Confidence Level:** High

---

## Battle Engine (`poke_engine/`)

### `poke_engine/ankimon_hooks_to_poke_engine.py`
- **Primary Responsibility:** Translates Ankimon's `PokemonObject` into the format expected by the `poke_engine`, runs the simulation, and translates the result back.
- **Why it matters:** The bridge between the user's state and the complex battle simulator.
- **Major Symbols:** `simulate_battle_with_poke_engine`.
- **Role:** Integration Adapter
- **Confidence Level:** High

### `poke_engine/battle.py`
- **Primary Responsibility:** Defines the core data structures for the battle engine (`Battle`, `Pokemon`, `Move`).
- **Why it matters:** Source of truth for how the simulator views the battle state.
- **Major Symbols:** `Battle`, `Pokemon`, `Move`.
- **Role:** Domain Logic
- **Confidence Level:** High

### `poke_engine/instruction_generator.py`
- **Primary Responsibility:** Evaluates moves and status effects to generate mutation instructions for the battle state.
- **Why it matters:** Source of truth for battle mechanics and rules (e.g., immunities, damage application).
- **Major Symbols:** `get_instructions_from_damage`, `immune_to_status`.
- **Role:** Domain Logic
- **Confidence Level:** High

---

## UI & Interactions

### `ankimon_items_web/shop_obj.py`
- **Primary Responsibility:** Controls the unified HTML5/QtWebEngine web-based shell window (`AnkimonItemsWeb`), which acts as a multi-view host for Items, Ankidex, Settings, Profile, and Team screens.
- **Why it matters:** It manages QWebChannel bridge callbacks, screen URL loading, shop stock/rerolls, and key state transitions, removing visual flicker during navigation.
- **Major Symbols:** `AnkimonItemsWeb`, `ItemsBridge`, `SettingsBridge`, `NavBridge`, `TrainerBridge`, `TeamBridge`, `load_screen`, `push_screen_data`, `refresh_live_screen`.
- **Role:** Web Shell Orchestrator / Bridge Controller
- **Confidence Level:** High

### `ankimon_profile_web/profile_data.py`
- **Primary Responsibility:** Extracts, transforms, and loads trainer profile statistics and team rosters from the SQLite database to supply the web views.
- **Why it matters:** Serves as the business data layer for the web Profile and Team views, performing CP computations, sprite path resolution, and move catalog modifications.
- **Major Symbols:** `ProfileData`, `get_profile_data`, `get_team_data`, `get_roster_data`, `handle_save_team`, `change_pokemon_move`.
- **Role:** Web Data Provider
- **Confidence Level:** High

### `functions/encounter_functions.py`
- **Primary Responsibility:** Generates wild Pokémon encounters, catches them, handles auto-capturing special tiers, and handles faints.
- **Why it matters:** Manages the core gameplay loop and probability selection pools outside of combat.
- **Major Symbols:** `generate_random_pokemon`, `catch_pokemon`, `handle_enemy_faint`, `check_id_ok`, `modify_percentages`, `_meets_prerequisites`, `get_regional_substitute`.
- **Role:** Gameplay Domain Controller
- **Confidence Level:** High

### `reviewer_ui.py`
- **Primary Responsibility:** Connects and attaches HUD elements, custom buttons, and hotkeys to Anki's reviewer layout.
- **Why it matters:** Binds team cycling hotkeys and forced test encounters safely without multiple wrapping leaks.
- **Major Symbols:** `cycle_team_pokemon`, `setup_hotkeys`, `linkHandler`, `_ui_hooks_installed`, `_original_shortcutkeys_wrapped`.
- **Role:** UI Hook Orchestrator
- **Confidence Level:** High

### `pyobj/pc_box.py`
- **Primary Responsibility:** Modernized 3:2 layout window for managing captured Pokémon (The PC Box).
- **Why it matters:** Provides search filtration, multi-column move tables with type highlights, and nature indicator stats. Features aggressive caching of filter results to eliminate SQLite disk reads when paging.
- **Major Symbols:** `PokemonPC`, `load_pc_box`, `filter_pc_box`, `update_move_table`.
- **Role:** UI Surface
- **Confidence Level:** High

### `pyobj/settings_window.py`
- **Primary Responsibility:** Legacy configuration settings GUI, retained for backward-compatibility. Settings are now primary-loaded and validated inside `settings_schema.py` and saved via the `SettingsBridge` in `shop_obj.py`.
- **Why it matters:** Continues to support older background programmatic operations or legacy fallbacks.
- **Major Symbols:** `SettingsWindow`.
- **Role:** Legacy Configuration GUI
- **Confidence Level:** High

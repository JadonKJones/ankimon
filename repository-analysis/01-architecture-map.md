# Architecture Map: Ankimon Codebase

## Entrypoints
- `__init__.py`: The primary entrypoint. Executed by Anki when the add-on is loaded. It bootstraps the application, registers hooks, initializes singletons, and attaches UI components to Anki's windows.

## Initialization & Lifecycle Flow

### 1. Startup Bootstrap Sequence (Asynchronous & Thread-Safe)
To eliminate Anki's startup latency and prevent blocking the main GUI thread, Ankimon uses an asynchronous boot sequence powered by `aqt.operations.QueryOp`:
1. **Module Import:** Anki loads and executes the root `__init__.py`.
2. **Resource Validation:** `ensure_ankimon_infrastructure` initializes folder directories.
3. **Singleton Anchor:** `singletons.py` instantiates core game models (`settings_obj`, `main_pokemon`, `enemy_pokemon`, `ankimon_tracker_obj`, `trainer_card`) as reload-safe references anchored to the `mw` object.
4. **Asynchronous Background Execution:** `QueryOp` launches `run_startup_background_checks` in a background thread:
   - Performs profile auto-backups (`run_backup`, `BackupManager`).
   - Verifies SQLite migration states (`ankimon_db.is_migrated()`).
   - Checks if static image/sprite assets are complete.
   - Generates the first wild opponent in the background (`generate_random_pokemon`).
   - Computes inventory item metrics (`count_items_and_rewrite`).
5. **Thread-Safe UI Callbacks:** Once checks are complete, `run_startup_ui_callbacks` runs on the main GUI thread:
   - Synchronizes the background-generated enemy's stats and HP into `enemy_pokemon`.
   - Prompts for sprite downloads or SQLite database migration if required.
   - Launches starter selection dialog if no Pokémon are owned.
   - Attaches `create_menu_actions` to the Anki window.
   - Attaches reviewer UI shortcuts and wraps card answer hooks (`gui_hooks.reviewer_did_answer_card.append`).

---

### 2. Developer Hot-Reload Lifecycle (`reloader.py`)
To prevent the 10-second Anki boot penalty during development, a sophisticated modular reloading lifecycle is implemented:

```
[User clicks "Restart Ankimon"]
              │
              ▼
    teardown_ankimon()
              │
              ├──► Unregister custom hooks from aqt.gui_hooks
              ├──► Close all open GUI windows (PC Box, Shop, Pokedex)
              ├──► Remove custom menu buttons from Anki Menu Bar
              └──► Restore original Anki Reviewer method references
              │
              ▼
    restart_ankimon()
              │
              ├──► Purge all add-on modules from sys.modules
              ├──► Trigger deep re-import of __init__.py
              └──► Re-initialize reload-safe singletons on mw
```

---

### 3. Database Hot-Swap / Account Switcher Sequence
Allows toggling between Production (`ankimon.db`) and Testing (`ankimonDEV.db`) accounts at runtime without restarting Anki:

```
[Switch Account triggered] ──► close connection ──► switch path ──► open connection
                                                                         │
    ┌────────────────────────────────────────────────────────────────────┘
    ▼
[Runtime State Refresh Cascade]
    ├──► Settings: refresh in-place config dict from SQLite metadata
    ├──► Trainer Card: invoke refresh() to reload Level, XP, and Cash in HUD
    ├──► PC Box: trigger reload_pc() grid update if window is currently visible
    └──► Main Pokemon: sync active species_id and stats onto Reviewer UI
```

---

## Encounter Weighting & Gating Architecture
Wild Pokémon generation uses an advanced double-pool selection mechanism and uniform post-selection variant trickle-down lookup:

```
                       [Encounter Requested]
                                 │
                        Is active_region set?
                       ├── Yes (Hisui 40%, others 30% Chance) ──► Pick from Boosted Pool
                       │                                           - Regional forms matching region
                       │                                           - Pokemon matching boosted gens
                       │
                       └── No (or empty Boosted Pool) ──────────► Pick from Full Pool
                                                                   - All Pokedex species
                                                                   - Filtered by Generational Toggles
                                                                   - Filtered by Prerequisites (Gating)
                                                                   - Filtered by Min Generation Level
                                 │
                                 ▼
                     [Base Species Selected]
                                 │
                     Unified Post-Selection Check:
              Does selected species have regional variants?
             ├── Yes ──► 7% * n chance to replace with a variant uniformly
             └── No ───► Proceed with selected base species
                                 │
                                 ▼
                    [Auto-Catch Override Check]
              Is target Special (Legendary/Mythical/Starter/Mega/Gmax)
              AND is automatic_catch_special enabled?
             ├── Yes ──►Defeating enemy triggers automatic capture (skip check)
             └── No ───►Normal catch percentage rules apply
```

---

## PC Box Layout & Ankidex Web Structures

### 1. Modernized PC Box View
The PC Box interface uses a robust, stable native layout system rather than crash-prone splitters:
- **Layout:** Replaced `QSplitter` with a static `QHBoxLayout` using a fixed 3:2 grid-to-details ratio to prevent flickering.
- **Move Picker Table:** Displays detailed combat parameters (Power, Accuracy, PP, Description) in a custom multi-column grid with color-coded moves based on type.
- **Nature Stat Indicators:** Stat tabs use nature-based indicators to visually flag boosted stats with green `▲` and lowered stats with red `▼` glyphs.
- **Live Counters & Paging:** Showing live feedback text updating in real-time as search search filters or tier criteria are met.
- **Aggressive Query Caching:** Navigating PC Box views caches database filter results in memory. Re-queries are only executed if filters or database records mutate, avoiding SQL disk lag.

### 2. Ankidex (Pokédex V2) & Unified Web Shell
Ankidex and other user screens are built with modern web technologies and hosted in a unified window:
- **Unified Web Shell:** `AnkimonItemsWeb` (instantiated in `singletons.py`) contains a `QStackedWidget` hosting QWebEngineViews for five core screens: **Items (Mart & Bag)**, **Ankidex**, **Profile**, **Team**, and **Settings**.
- **Navigation Routing:** All shell screens share a responsive, glassmorphic dropdown switcher that sends signals back to Python via `QWebChannel` (`nav.openItems()`, `nav.openAnkidex()`, etc.) to swap screens instantly.
- **Ankidex View:** Displays evolution chains, regional variants, caught ratios ("Registry Progress"), and unlocks ("Capture Requirements").
- **Dynamic Updates:** CATS (Caught, XP, Cash) events trigger `notify_stats_changed()`, which deferred-coalesces UI refreshes onto open web screens with zero lag.
- **Animated Team Sprites:** The Team builder screen features animated sprites with a user toggle synced in real-time with Ankidex preferences.

---

## In-Memory Caching Architecture
To reduce review card execution latency and UI transitions to practically zero, static assets and parsed tables are loaded once on startup and stored in memory:

```
[Startup] ──► Parse and cache pokemon.csv, stats.csv, evolution.csv in memory-resident dicts
          ──► Cache pokedex.json in memory (search_pokedex_by_id)
          ──► Cache learnsets.json in memory (_get_learnset_moves)
          ──► Cache next_lvl.csv in memory (calculate_xp)
          ──► Cache sprite buffers in Reviewer HUD
[PC Box]  ──► Cache last filtered SQLite query results to prevent page-switching disk lag
```

> [!TIP]
> Future coding iterations must strictly access these cached datasets rather than invoking synchronous disk I/O operations inside the review card loop.

---

## Module Boundaries & Decoupling Stack
To achieve a clean separation of concerns and support offscreen testing, the codebase uses a structured decoupling boundary:
- **`services.py` Registry:** Acts as the central composition container. Core logic modules and UI systems look up their dependencies (e.g. database connections, active main pokemon, loggers) through `services` rather than importing hardcoded global singletons or referencing `aqt.mw` directly.
- **UI Presenter Port:** Presenter interfaces (e.g., `services.ui` presenter) abstract GUI alerts, updates, and dialog triggers. 
  - **`QtPresenter`:** In production, coordinates dialogue popups, the evolution window animation triggers, and PC Box UI updates.
  - **`HeadlessPresenter` (and mock fakes):** In headless execution, intercepts these triggers silently, allowing tests to run assertion scripts without UI blocks.

- **Root Workspace:** Orchestration, constant definitions (`const.py`, `resources.py`), and Anki-specific setup (`__init__.py`, `hooks.py`, `menu_buttons.py`).
- **`pyobj/`:** Stateful UI objects and controllers. Includes `pc_box.py`, `settings_window.py`, and `database_manager.py`.
- **`functions/`:** Clean procedural utility scripts. Includes `encounter_functions.py` (weighting logic), `encounter_data.py` (constants), and cached lookups.
- **`poke_engine/`:** Completely isolated, self-contained battle rules and damage calculator.

---

## Change-Risk Hotspots
- **`__init__.py` Hook Wrappers:** Modifications to Anki reviewer methods must use original references stored in `_shortcutKeys`, `_linkHandler`, and `_bottomHTML` to prevent wrapper accumulation when reload scripts are called.
- **SQLite Database Transactions:** Swapping databases requires atomic, synchronous locks to prevent multi-threaded conflicts.
- **Static Encounter Keys:** The Pokedex JSON and SQLite databases use lowercased keys for Mega and Gmax variants (e.g. `mewtwomegay` instead of `Mewtwomegay`). Bypassing lowercasing will cause search lookup failures.
- **Headless Import Violations:** Importing `aqt` or `PyQt6` inside state managers or core logic modules at the top level violates the offscreen runner's import-isolation, causing test suites to fail.


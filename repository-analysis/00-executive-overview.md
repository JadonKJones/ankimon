# Executive Overview: Ankimon Codebase

## What this repository appears to be
This repository contains the source code for **Ankimon**, an Anki add-on that gamifies the flashcard learning experience by integrating a Pokémon-style battle and collection system. Users engage in simulated Pokémon battles, catch Pokémon, level them up, and manage their collection, all driven by their flashcard review activity within Anki.

Directly evidenced by:
- The integration with `aqt` and `anki.hooks` (e.g., `__init__.py`).
- The presence of a `poke_engine/` directory which simulates Pokémon battles based on SirSkaro's Poke-Engine (e.g., `poke_engine/ankimon_hooks_to_poke_engine.py`).
- File names like `pokemon_obj.py`, `pokedex_functions.py`, `ankimon_tracker.py`, and `evolution_window.py`.
- The `addon.json` and `manifest.json` files defining it as an Anki add-on.

## How it likely starts
The primary entrypoint for the Anki add-on system is `__init__.py`. When Anki loads the add-on, this file is executed.
1. It imports dependencies and Anki core modules (`aqt`, `anki`).
2. It generates startup files (`generate_startup_files`).
3. It initializes core singletons via `singletons.py` (e.g., `logger`, `settings_obj`, `main_pokemon`, `ankimon_tracker_obj`).
4. It sets up web exports and UI hooks (`gui_hooks.reviewer_did_show_question`, `gui_hooks.reviewer_did_answer_card`).
5. It checks for the existence of required sprites and data files, triggering downloads if missing (`download_sprites.py`).
6. It hooks into Anki's profile loading (`profileLoaded`) and review events (`reviewer_did_answer_card`), which drives the battle progression.

Directly evidenced by:
- `__init__.py`'s setup code at the module level.
- `singletons.py` instantiating central objects like `Settings`, `PokemonObject`, and `AnkimonTracker`.

## Major subsystems
1. **Add-on Orchestration:** `__init__.py` hooks into Anki, manages initialization, and wires up the review lifecycle to the battle engine.
2. **Encounter Weighting & Gating Engine:** Handled by `functions/encounter_functions.py` and `functions/encounter_data.py`. Manages double-pass probability selection (Boosted vs Full Pool), starter/legendary prerequisites, and active region boosts.
3. **Data & State Management:** `pyobj/pokemon_obj.py` represents individual Pokémon state. `singletons.py` holds global state. `pyobj/database_manager.py` (`AnkimonDB`) and the SQLite database (`ankimon.db` / `ankimonDEV.db`) handle persistence.
4. **In-Memory Caching System:** Central loaders in `functions/pokedex_functions.py` and `functions/learnset_retrieval.py` cache Pokedex data, learnsets, and level charts in memory to eliminate latency.
5. **Battle Engine (`poke_engine/`):** A complex sub-package for simulating Pokémon battles. It calculates damage, determines move effects, and manages battle state. Connected via `poke_engine/ankimon_hooks_to_poke_engine.py`.
6. **GUI Components (`pyobj/` and `gui_classes/`):** PyQt6 windows and dialogs for the user interface, including the modernized 3:2 PC Box, and a unified web-based shell window (`AnkimonItemsWeb`) hosting HTML5/QtWebEngine screens for Items (Mart & Bag), Settings, Profile, Team, and the Ankidex discovery map.
7. **Add-on Reloader Module (`reloader.py`):** Instantly hot-reloads all Ankimon code, tearing down hooks and menu controls and purging `sys.modules` to prevent memory leaks during development.
8. **Mobile Reviews Integration (`functions/mobile_sync.py` & `ankimon_mobile_web/`):** Synchronizes card reviews completed on AnkiMobile/AnkiWeb, queueing them as pending battles. Offers Auto-Resolve (with roster optimization) and turn-based Manual Replay modes.

## State and persistence at a glance
- **State Flow:** The flashcard review (`reviewer_did_answer_card`) triggers an attack in the battle. The battle state is updated in the `poke_engine` and synced back to `PokemonObject` instances (`main_pokemon`, `enemy_pokemon`).
- **Persistence:** All player progression, collection, items, team, badges, settings state, pending mobile battles, and battle history logs are stored inside a single consolidated SQLite database file (`ankimon.db`) managed by `pyobj/database_manager.py`. Connection hot-swapping is supported for switching to `ankimonDEV.db` at runtime.
- **In-Memory Objects:** `singletons.py` maintains the live instances of the user's main Pokémon, the current enemy Pokémon, settings, and the database manager as reload-safe references anchored to `mw`.

Directly evidenced by:
- `pyobj/database_manager.py` implementing database setup, CRUD operations, and `switch_database`.
- `singletons.py` instantiating and anchoring `mw.ankimon_db` and managing hot-swap reloads.

## Integration boundaries
- **Anki Integration:** Uses `aqt.gui_hooks`, `anki.hooks.wrap` (avoiding wrapper leakage), `aqt.mw`, and custom modifications to Anki's UI (e.g., `Reviewer._bottomHTML` with "around" patterns).
- **File System:** Local SQLite database I/O in the profile's app folder and static media files in `addon_sprites/`.
- **Network Integration:**
  - Downloads sprites and updates from GitHub (`raw.githubusercontent.com`).
  - Discord Rich Presence integration (`pypresence` via `discord_function.py`).
  - AnkiWeb Sync hook for synchronizing user files across devices (`ankimon_sync.py`).

## Top risks
- **Circular Prerequisite Chains:** In the gating engine (`encounter_data.py`), if evolution or legendary prerequisites form a cycle, it will result in infinite loops during encounter rolls.
- **Wrapper Hook Leakage:** If reviewer hook methods are wrapped without checking `_ui_hooks_installed` guards, reloading the addon will duplicate hook layers, degrading reviewer performance.
- **Active Database Hot-Swap Lockout:** Switching database connections while database-locked threads or open UI windows are active can lead to corruption or unhandled sqlite3 state exceptions.

## What to read first
- **Entrypoint:** `__init__.py` to understand hooks and review-card battle loop.
- **Hot-Reload:** `reloader.py` for safe development teardown and module purging.
- **Global Singletons:** `singletons.py` to see live memory structures.
- **Mobile Engine:** `functions/mobile_sync.py` for mobile review queueing and companion selectors.

## Top 16 Most Important Files (Ranked)
1. `__init__.py` (Entrypoint and orchestration)
2. `singletons.py` (Global state initialization and hot-swap)
3. `pyobj/database_manager.py` (Persistence layer, schemas, switch_database)
4. `reloader.py` (Addon hot-reloader and hook cleanup)
5. `functions/encounter_functions.py` (Pool selection, region gating, auto-catch)
6. `functions/encounter_data.py` (Authoritative pool constants, starter prerequisites, regional lookups)
7. `pyobj/pokemon_obj.py` (Core domain model)
8. `ankimon_items_web/shop_obj.py` (Unified web shell dialog and bridge orchestrator)
9. `poke_engine/ankimon_hooks_to_poke_engine.py` (Bridge between Anki events and the battle engine)
10. `pyobj/pc_box.py` (Modernized 3:2 layout PC Box and Move Table UI)
11. `ankimon_profile_web/profile_data.py` (Profile & Team web view business data provider)
12. `functions/pokedex_functions.py` (In-memory pokedex cache and lookups)
13. `functions/learnset_retrieval.py` (In-memory movesets cache and generational fallback)
14. `functions/mobile_sync.py` (Mobile review sync, active team loading, and companion selection)
15. `pyobj/ankimon_tracker.py` (Session and progress tracking)
16. `pyobj/ankimon_sync.py` (Data synchronization logic)

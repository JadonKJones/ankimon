# Module Boundaries

This document describes the major subsystem boundaries, interfaces, and responsibilities division in the Ankimon fork codebase.

---

## Subsystem Boundaries and Responsibilities

### 1. The Core Orchestrator (Root Directory)
- **Responsibilities:** Hooks into Anki, sets up the environment, initializes global state, and connects review events to game logic via root files like `__init__.py` and `hooks.py`.
- **Communication:** Calls into `functions/` to execute game events. Calls into `pyobj/` to show UI windows. Injects state from `singletons.py` into almost everything.
- **Dependencies:** Heavily depends on Anki (`aqt`, `anki`), `singletons.py`, and `poke_engine/`.

### 2. Data Caching Layer (`functions/pokedex_functions.py` & `functions/learnset_retrieval.py`)
- **Responsibilities:** Loads and retains static pokedex (`pokedex.json`), movesets (`learnsets.json`), and progression stats (`next_lvl.csv`) in memory. Eliminates disk latency for card-study review runs.
- **Communication:** Other modules (PC Box, Battle Bridge, Gating Engine) must strictly call in-memory cache lookup methods.
- **Dependencies:** None on Anki or PyQt. Directly dependent on static files on boot.

### 3. The Object Model & Persistence Layer (`pyobj/`)
- **Responsibilities:** Holds domain models (`PokemonObject`, `AnkimonTracker`, `Settings`) and `AnkimonDB` database controller (`pyobj/database_manager.py`).
- **Communication:** Consumed by `__init__.py` and `functions/`. Swaps database connections atomically via `singletons.py`'s `swap_ankimon_account()`.
- **Dependencies:** PyQt6 for settings and PC Box views; sqlite3 for persistence.

### 4. The Action Functions & Gating Engine (`functions/`)
- **Responsibilities:** Procedural helper scripts executing game actions (evolving, pool selection, prerequisite checking).
- **Communication:** Called by `__init__.py` or UI triggers. Mutates objects inside `pyobj/`.
- **Dependencies:** Imports from `pyobj/` and static pools inside `functions/encounter_data.py`.

### 5. Developer Hot-Reloader Layer (`reloader.py`)
- **Responsibilities:** Tears down hook integrations, menu items, and active widgets cleanly, and deletes cached modules from `sys.modules` before re-importing the addon package.
- **Communication:** Triggers on menu command; communicates directly with Anki's module registries and Reviewer references.
- **Dependencies:** `sys`, `importlib`, Anki's global hook list.

### 6. The Battle Simulator (`poke_engine/`)
- **Responsibilities:** A pure state machine representing a Pokémon battle. Calculates damage, handles statuses, manages turn order, and enforces Pokémon rules.
- **Communication:** Should only communicate via `poke_engine/ankimon_hooks_to_poke_engine.py`. Takes in initial state, returns instructions/results.
- **Dependencies:** Has *no* dependencies on Anki or the Ankimon UI. Depends on its own internal data files.

---

## Layering Leaks and Rules

### 1. In-Memory Cache Violations
- **Violation:** Reading static database files from disk inside the review loop.
- **Rule:** Direct on-demand file parsing is forbidden. All operations must use the cached module dictionaries (`search_pokedex_by_id`, `_get_learnset_moves`).

### 2. Reviewer Wrap Leaks
- **Violation:** Re-registering hooks on settings updates or reload clicks, creating duplicate wraps in memory.
- **Rule:** All reviewer modifications must check global boolean guards and be cleared/restored completely via `teardown_ankimon` before re-applying.

### 3. Database Connection Collisions
- **Violation:** Open database threads or cursors remaining active during a runtime profile hot-swap.
- **Rule:** Profile swaps must run atomically, closing active sqlite3 connections cleanly before opening new ones, followed immediately by updating memory variables via the state refresh cascade.

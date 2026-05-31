# Risk Register

This document outlines fragile, high-impact, or technically precarious areas of the codebase. Future edits should approach these areas with caution.

---

## 1. Circular Prerequisite Chains (Infinite Recursion)
- **Affected Files:** `functions/encounter_data.py` (`PREREQUISITES` mapping) and `functions/encounter_functions.py` (`_meets_prerequisites`).
- **Why it is risky:** Evolution and Legendary prerequisite gating is evaluated recursively. If a circular chain is introduced (e.g., Pokémon `A` requires Pokémon `B` caught, and Pokémon `B` requires Pokémon `A` caught), `generate_random_pokemon()` will enter an infinite recursion loop during card reviews, causing Anki to hang or crash due to stack overflow.
- **Dangerous Changes:** Adding evolutionary prerequisites or legendary capture requirements without confirming they form a strictly directed, acyclic graph (DAG).
- **Precautions:** Verify all prerequisite chains in `encounter_data.py` lead to a base starter or lower-tier species that requires 0 prerequisites.

---

## 2. Reviewer Hook Wrapper Accumulation & Performance Degradation
- **Affected Files:** `reviewer_ui.py`, `__init__.py`.
- **Why it is risky:** Ankimon intercepts Anki's default reviewer shortcuts, bottom HTML buttons, and URL click handlers by wrapping core classes. If these are wrapped repeatedly on settings changes or hot-reloads without guards, multiple layers of wrapped functions will accumulate in memory. This degrades card review speeds and causes massive lag.
- **Dangerous Changes:** Modifying `Reviewer._shortcutKeys` or `Reviewer._bottomHTML` hooks without checking `_ui_hooks_installed` and `_original_shortcutkeys_wrapped` global guards.
- **Precautions:** Always verify hook wrappings check active guards. When reloading, the addon must restore original references stored before wrapping.

---

## 3. Database Hot-Swap Lockout & Transaction Failures
- **Affected Files:** `pyobj/database_manager.py` (`switch_database`), `singletons.py` (`swap_ankimon_account`).
- **Why it is risky:** Swapping connections between `ankimon.db` and `ankimonDEV.db` requires closing the active SQLite handle. If a transaction is uncommitted or a UI window (e.g., PC Box) retains a stale cursor during the swap, the file can become locked, resulting in database lockout crashes.
- **Dangerous Changes:** Initiating a database hot-swap while database-writing operations are running or when UI windows are open.
- **Precautions:** Swapping profiles should automatically trigger in-place refreshes of settings, trainer cards, and Pokemon PC slots, and all open database connections must be closed atomically.

---

## 4. Case-Sensitivity & Key-Lookup Failures
- **Affected Files:** `functions/encounter_functions.py`, `functions/pokedex_functions.py`, SQLite databases.
- **Why it is risky:** The `pokedex.json` file is case-sensitive, storing Mega/Gmax and special form keys in lowercase (e.g., `mewtwomegay`, `heracrossmega`). If a caught Pokémon's name is capitalized in the SQLite database (e.g., `Mewtwomegay`), lookups in the Pokédex JSON cache will fail, breaking combat stat calculation and causing UI errors.
- **Dangerous Changes:** Saving Pokémon names in the database using `.capitalize()` on the lookup name keys.
- **Precautions:** Ensure new Pokémon names are stored in lowercase inside the SQLite database, and default nicknames map to pretty display strings (e.g., `Mewtwo-Mega-Y`) rather than capitalized database keys.

---

## 5. Disk I/O Caching Violations (Review Card Lag)
- **Affected Files:** `functions/pokedex_functions.py`, `functions/learnset_retrieval.py`.
- **Why it is risky:** The review card hook runs synchronously on the main thread. Invoking raw disk reads (e.g., `json.load`) to check stats, movesets, or level tables on every card reviewed causes massive user interface lag.
- **Dangerous Changes:** Re-introducing on-demand disk operations for `pokedex.json`, `learnsets.json`, or `next_lvl.csv`.
- **Precautions:** Always use the cached, in-memory representations initialized during startup. Static data must never be loaded from disk during a card review session.

---

## 6. Global Singleton Coupling
- **Affected Files:** `singletons.py`, `__init__.py`, almost all UI classes.
- **Why it is risky:** State (`main_pokemon`, `settings_obj`, `logger`, `ankimon_db`) is instantiated in `singletons.py` and heavily relied upon globally.
- **Dangerous Changes:** Removing a singleton, renaming it, or failing to pass the singleton explicitly into a new class constructor.
- **Precautions:** Ensure dependency injection is used when creating new classes, explicitly passing `logger`, `settings_obj`, and the `ankimon_db` database connection.

---

## 7. Thread-Safety Violations in Asynchronous Startup
- **Affected Files:** `startup.py` (`run_startup_background_checks()`), `__init__.py`.
- **Why it is risky:** Background checks are processed on a worker thread using `QueryOp` to avoid main-thread blocking. PyQt6/Qt widgets and hooks **MUST NOT** be created, accessed, or mutated off the main thread. Doing so causes immediate segfault crashes or undefined behaviors.
- **Dangerous Changes:** Triggering GUI dialogs (like migration or downloader views) or mutating active UI singletons directly inside the background thread.
- **Precautions:** Restrict the background thread strictly to read-only DB/IO processes. Return results as dictionaries and perform all UI bindings, updates, and dialog pops inside the `run_startup_ui_callbacks` execution on the main thread.

---

## 8. Windows DWM Compositor Repaint Flickering
- **Affected Files:** `ankimon_items_web/shop.css`, `ankidex/ankidex.css`, `ankimon_items_web/shop_obj.py`.
- **Why it is risky:** When embedding a `QWebEngineView` inside a `QStackedWidget` container with translucent backgrounds or complex styling under Windows Desktop Window Manager (DWM), heavy CSS properties like `backdrop-filter: blur(...)` trigger massive window-level repaint cycles. This results in severe visual flickering or rendering glitches when switching views or recomposing pages.
- **Dangerous Changes:** Adding heavy CSS filters (such as `backdrop-filter` or multiple overlapping blur animations) to pages rendered inside QtWebEngine on Windows.
- **Precautions:** Disable window translucency attributes (`WA_TranslucentBackground`) in python controllers if flickering is observed. Avoid visual blur filters in CSS stylesheets, opting for opaque glassmorphic fallback designs.

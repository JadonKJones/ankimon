# Agent Handoff

This document is a concise, operational summary designed to bring the next coding agent up to speed immediately on the Ankimon fork codebase.

---

## Technical Summary of the Fork Subsystems

### 1. In-Memory Caching (Zero Latency)
- **Status:** Fully Integrated. Pokedex, learnsets, experience formulas, and sprites are cached in memory on boot.
- **Rule:** **Never invoke synchronous file reads (`json.load(open(...))`) during card study reviews.** Always call cached retrieval methods (`search_pokedex_by_id`, `_get_learnset_moves`).

### 2. Defensive Hook Wrapping (Leak Prevention)
- **Status:** Fully Integrated.
- **Rule:** When intercepting Anki Reviewer methods or keyboard shortcuts, **always check global boolean guards (`_ui_hooks_installed`)** to avoid duplicate wrapping layers. Save original method pointers for teardown restoration.

### 3. Database Hot-Swapping (Seamless Swapping)
- **Status:** Fully Integrated.
- **Rule:** Swapping connections between `ankimon.db` and `ankimonDEV.db` requires calling `conn.close()` atomically to prevent multi-threaded database locks. Follow connections swaps immediately with the runtime state refresh cascade.

### 4. Gating & Prerequisite Validation (DAG Verification)
- **Status:** Fully Integrated. Gating logic (`PREREQUISITES` in `encounter_data.py`) prevents evolution jumps recursively.
- **Rule:** **Ensure prerequisite chains form a strict Directed Acyclic Graph (DAG).** Circular prerequisites will trigger infinite recursion locks during card reviews. Run offline simulations to verify behavior.

### 5. Custom Form Base Species checks (Generational Gating)
- **Status:** Fully Integrated. Mega/Gmax variant ID searches (IDs >= 10000) are resolved to base species IDs in `check_id_ok` to ensure generational configuration toggles work correctly.

### 6. Case-Sensitivity (Lowercase Indexing)
- **Status:** Fully Integrated.
- **Rule:** Megas, Gigantamax, and variant name keys must be lowercased before saving to database columns or querying Pokedex caches (e.g. `mewtwomegay`).

### 7. Reward Caps (Cheat-Prevention Threshold)
- **Status:** Fully Integrated.
- **Rule:** Enforce boundaries for card intervals `[5, 250]` and cash `[10, 2000]`. Ensure Cash payouts never exceed the **100:1 cash-to-card reward ratio** (100¥ max payout per reviewed card). Enforce these limits in `validate_and_clamp()` in `settings_schema.py`.

### 8. Pokédex V2 Terminology
- **Rule:** Standardize vocabulary across PC Box, Discovery Map, and Pokédex menus:
  - **"Capture Requirements"** (replaces "Prerequisites" or "Gating")
  - **"Registry Progress"** (replaces "Completion Status" or "Caught Status")
  - **"Unseen Species"** (replaces "Locked" or "Not Seen")

### 9. Unified Web Shell & Bridges (Multi-View UI)
- **Status:** Fully Integrated. Items (Mart & Bag), Ankidex, Settings, Profile, and Team screens all run inside `AnkimonItemsWeb` using QWebEngineView pages.
- **Rule:** Never open separate dialogues for these screens; route them using `_open_shell_at("items" | "ankidex" | "settings" | "profile" | "team")`. Screen data and interactions flow through registered QWebChannel bridges (`bridge`, `nav`, `settings`, `trainer`, `team`). Use `notify_stats_changed()` to broadcast state mutations from background operations to active web views.

### 10. Mobile Reviews Integration (Multi-Companion)
- **Status:** Fully Integrated (Phases 1-8+).
- **Core Architecture:**
  - `functions/mobile_sync.py` handles: watermark-based diff scanning, review queueing (cap: 10 000), team-clone loading, and auto-selection scoring (`select_best_companion` uses `EDO × Speed` scoring with type-effectiveness weighting).
  - `ankimon_items_web/shop_obj.py` (`MobileBridge`) exposes all QWebChannel slots: `getMobileStatus`, `resolveAll`, `resolveNext`, `commitReplayOutcome`, `startBulkResolve`, `getBulkResolveProgress`, `pauseBulkResolve`, `resumeBulkResolve`, `stopBulkResolve`, `toggleMobileCompanion`, `getTeamStatus`.
  - `ankimon_mobile_web/` contains: `mobile.html`/`mobile.js` (3-state review UI + auto-resolve progress with Pause/Stop controls) and `history.html`/`history.js` (battle history log panel).
- **Two Resolution Modes:**
  1. **Auto-Resolve** (`startBulkResolve`): runs in a daemon background thread (`threading.Thread`). Uses `utils.in_bulk_resolve = True` flag to prevent desktop card reviews from writing to SQLite concurrently. A `_bulk_paused` / `_bulk_stopped` flag pair allows Pause/Resume/Stop from JS polling.
  2. **Manual Replay** (`resolveNext`/`commitReplayOutcome`): simulation runs in a `QueryOp` background thread (fire-and-forget). `resolveNext` returns `{"loading": true}` immediately; when the simulation completes `on_sim_success` pushes the result to JS via `page().runJavaScript("window.onResolveNextReady({...})")`. `commit_replay_outcome` pre-computes the return values synchronously, then defers all DB writes and side-effects to a second `QueryOp` background thread. The user may override the companion via `companion_id` argument; the fallback is `select_best_companion()`.
- **Companion Toggles:** `mobile.inactive_companions` setting (list of `individual_id` strings). `toggleMobileCompanion(id)` flips membership. Inactive companions appear darkened in the team grid.
- **Battle History:** `mobile_battle_history` table in SQLite, capped at **500** most-recent records (trimmed on every insert). Queried at `limit=500` by `getMobileHistory`.
- **Critical Rules:**
  - **Do NOT review desktop cards while auto-resolve is running** (race condition on companion stats + SQLite writes). The UI warns users with red text in both the confirmation dialog and progress modal.
  - `utils.in_bulk_resolve` is checked in `encounter_functions.py` and `pokedex_functions.py` to suppress UI callbacks and evolution logic during batch resolution.
  - The `_resolve_internal` method uses `use_transaction = (mode == "all")` to batch-commit all resolved rows; `mode == "next"` commits immediately per encounter.
  - Companion clones are fully healed after each battle (prevents accumulated carry-over damage from causing unexpected early faints).
  - **Encounter sequence is fully deterministic and invariant.** All three paths (`mode="all" commit=False`, `mode="all" commit=True`, `mode="next"`) seed encounters using `_compute_encounter_idx()`, which reads `mobile_resolved_encounters_count` from the `metadata` table in a single query. The same pending queue always produces the same enemy sequence regardless of team composition, active/inactive companions, or resolution mode.
  - `_get_team_max_level()` reads ALL companion levels (active and inactive) via a single batch `IN` query. This `stable_max_level` is used for encounter generation so activating/deactivating companions never shifts the encounter count or species pool.

### 11. Import-Time Decoupling (Headless Harness Safety)
- **Status:** Fully Integrated. Core game simulation modules and state managers are completely decoupled from `aqt` and `PyQt6` GUI imports.
- **Rule:** **Core logic, helper routines, database utilities, and math modules must never import aqt or PyQt6 at the top level.** All GUI widget instantiations, popup dialogues, and layout configurations must be imported lazily inside the methods that require them. This ensures that the headless simulation harness can safely load modules outside of Anki runtime without raising `ImportError` or spawning thread segfaults.
- **Presenter Pattern:** GUI actions (such as dialogue confirmations, warning windows, or HUD status updates) should be wrapped in presenter interfaces routed through the `services` registry (e.g. `services.ui`), allowing the headless runner to override them with silent fakes.

---

## Verification Commands
Before submitting pull requests or ending development iterations:
1. **Run Headless integrity/smoke tests:**
   ```powershell
   $env:QT_QPA_PLATFORM="offscreen"
   python -m pytest tests/ -v
   ```
   Currently: **247 tests** (full mobile sync, auto-resolve, manual replay, and headless import safety suites).
2. **Run offline simulation suites:**
   ```powershell
   python scratch/encounter_weighting_simulations/test_encounter_simulation.py
   ```
   Ensures that all 11 encounter pools, region weights, and prerequisite validations function flawlessly.
3. **Verify headless harness checks:**
   ```powershell
   python harness/check.py
   ```
   Ensures all 9 Tier-1 harness checks (Qt-free / Anki-free simulation) remain green.



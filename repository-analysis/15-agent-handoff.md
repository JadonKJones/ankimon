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

---

## Verification Commands
Before submitting pull requests or ending development iterations:
1. **Run Headless integrity/smoke tests:**
   ```powershell
   $env:QT_QPA_PLATFORM="offscreen"
   python -m pytest tests/ -v
   ```
2. **Run offline simulation suites:**
   ```powershell
   python scratch/encounter_weighting_simulations/test_encounter_simulation.py
   ```
   Ensures that all 11 encounter pools, region weights, and prerequisite validations function flawlessly.

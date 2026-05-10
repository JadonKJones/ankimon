# Ankimon Integration Proposal

## Executive Summary
This proposal outlines the integration of significant architectural improvements, restored features, and developer quality-of-life tools from the current Ankimon fork into the main repository. The fork focuses on **Stability**, **Extensibility**, and **Feature Completeness**, specifically addressing multi-account handling and modernizing the development workflow.

### Key Value Propositions:
- **Rock-Solid Account Management**: Native support for switching between Production and Development databases without data leakage.
- **Modern Dev Workflow**: Instant add-on reloading without restarting Anki, significantly reducing iteration time.
- **Feature Restoration**: Re-integration and stabilization of "Archived" Mega Evolution and Gigantamax (Gmax) logic.
- **Enhanced Player UX**: Team cycling with status clearing and developer-friendly hotkeys.

---

## Feature Deep-Dive

### 1. Multi-Account Switcher
**Function**: Allows developers and players to toggle between `ankimon.db` and `ankimonDEV.db` at runtime.
**Technical Implementation**:
- **Files**: `singletons.py` ([L191-244](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/singletons.py#L191-L244)), `pyobj/database_manager.py` ([L321-328](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/pyobj/database_manager.py#L321-L328)).
- **Logic**: Uses `AnkimonDB.switch_database()` to close the current SQLite connection and open a new one. It then triggers a cascade of in-place updates for settings, the trainer card, and the reviewer HUD.
**Rationale**: Originally built to fix "Multi-account data leakage" (Chat a895d34a). It ensures that switching Anki profiles or DB files doesn't leave stale data in singleton objects.

### 2. Hot-Reload System (Reloader)
**Function**: A "Restart Addon" menu item that re-initializes all Ankimon modules.
**Technical Implementation**:
- **Files**: [reloader.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/reloader.py), [menu_buttons.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/menu_buttons.py#L231-L236).
- **Logic**: Implements a sophisticated teardown of GUI hooks and menu actions, clears `sys.modules`, and performs a clean re-import. Data singletons (DB connection, Settings) are "Reload-Safe" and persist to maintain session state.
**Rationale**: Solves the "Startup Deadlock" problem (Chat 587e0fb3) and allows for rapid feature testing without the 10-second Anki boot penalty.

### 3. Restored Mega & Gigantamax Logic
**Function**: Re-enables the encounter and capture of Mega/Gmax forms.
**Technical Implementation**:
- **Files**: `functions/encounter_functions.py` ([L86-112](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/functions/encounter_functions.py#L86-L112)), `pokedex_functions.py`, `sprite_functions.py`.
- **Logic**: Restores the `Mega` and `Gmax` encounter tiers (gated at Lvl 60/65). Implements specialized sprite resolution logic to handle `actual_id >= 10000` (e.g., Mega Zygarde `10301.png`).
**Rationale**: Restored from cold storage (documented in `_mega_gmax_logic_blueprint.md`) to provide a more feature-complete experience for endgame players.

### 4. Advanced Hotkeys & Team Cycling
**Function**: Hotkey **'9'** for team cycling; Hotkey **'0'** for forced test encounters.
**Technical Implementation**:
- **Files**: `reviewer_ui.py` ([L64-140](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/reviewer_ui.py#L64-L140)).
- **Logic**: `cycle_team_pokemon()` swaps the active `main_pokemon` and calls `reset_bonuses()` to clear stat buffs/debuffs, preventing status leakage between team members.
**Rationale**: Fixed the "Buff Inheritance" bug (Chat be6ec743) and provided better testing tools for encounter rates (Hotkey 0).

---

## Comparison Matrix

| File Path | Nature of Change | Impact |
| :--- | :--- | :--- |
| [startup.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/startup.py) | **Refactor** | Hardened initialization to prevent hook-related crashes. |
| [singletons.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/singletons.py) | **Heavy Modification** | Anchored core state to `mw` for reload safety; added Account Switcher. |
| [reloader.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/reloader.py) | **[NEW]** | Core logic for hot-reloading the add-on. |
| [encounter_functions.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/functions/encounter_functions.py) | **Feature Restoration** | Re-enabled Mega/Gmax; added tier-based fallback logic. |
| [reviewer_ui.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/reviewer_ui.py) | **New Feature** | Implemented Hotkeys '0' and '9' with status reset logic. |
| [database_manager.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/pyobj/database_manager.py) | **Refactor** | Added `switch_database` and schema support for `is_main` flag. |

---

## Merge Recommendations

> [!IMPORTANT]
> **Priority 1: Singletons Migration**
> The `singletons.py` changes are foundational. The main repository must adopt the `getattr(mw, 'attr', None) or Init()` pattern to support the Reloader and Account Switcher.

### Step-by-Step Merge Path:
1. **Infrastructure**: Copy [reloader.py](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/reloader.py) and the `.agents/` directory (for future documentation) to the root.
2. **Core Logic**: Merge `singletons.py` first. This will likely cause conflicts in `__init__.py` which should be resolved by moving global variables to `singletons.py`.
3. **Database**: Update `database_manager.py` to include the `switch_database` method and ensure the `captured_pokemon` schema matches (virtual columns for name/id).
4. **Features**: Bring over the Mega/Gmax blocks in `encounter_functions.py`. 
    * **CAUTION**: Remove the "Testing Overrides" block ([L144-154](file:///c:/Users/hakim/AppData/Roaming/Anki2/addons21/1908235722/functions/encounter_functions.py#L144-L154)) before final merge.
5. **UI**: Add the "Switch Account" and "Restart Ankimon" actions to `menu_buttons.py`.

---

## Stability & Verification

- **Fixed Regressions**: 
    - **Starter Crash**: Fixed `base_stats` dict/list mismatch in `encounter_functions.py`.
    - **PC Sorting**: Resolved the "Date-based sorting" bug while switching main Pokemon.
- **Verification Plan**:
    - **Account Swap**: Verified by toggling between DBs in the Reviewer; HUD updates immediately.
    - **Mega Encounter**: Verified via `pokemon-db-manager` skill injection and Hotkey 0 triggers.
    - **Teardown**: Verified by monitoring `gui_hooks` count after multiple reloads.

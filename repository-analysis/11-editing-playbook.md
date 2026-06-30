# Editing Playbook

This document provides exact, operational playbooks for making safe modifications, additions, and updates to the Ankimon fork codebase.

---

## Playbook 1: Adding a New Regional Form or Variant

Follow these step-by-step developer scripts to register and integrate a new regional form (e.g., Unovan Zorua):

1. **Static Data Verification:**
   - Verify that the target variant exists in `user_files/data_files/pokedex.json`.
   - Ensure the JSON lookup name key is entirely in lowercase and stripped of hyphens (e.g. `"zoruaunova"` instead of `"Zorua-Unova"`).

2. **Register in Lookup Mapping:**
   - Open `functions/encounter_data.py`.
   - Locate the `REGIONAL_FORM_LOOKUP` dictionary.
   - Add the mapping from the base species ID to the new variant's ID:
     ```python
     # Example:zorua (570) -> Zorua-Hisui (10189) and Zorua-Unovan (10271)
     570: [10189, 10271]
     ```

3. **Register in Region Boost Pools:**
   - Locate the `ACTIVE_REGION_BOOSTS` dictionary inside `encounter_data.py`.
   - Add the new variant to the appropriate region list under the target region name (e.g. `"unova"`).

4. **Verify Behavior Offline:**
   - Run the simulation test suite to ensure the new variant resolves correctly in weighted pools:
     ```powershell
     python scratch/encounter_weighting_simulations/test_encounter_simulation.py
     ```

---

## Playbook 2: Defensively Wrapping a Reviewer UI Hook

Follow this playbook to attach new keyboard shortcuts or elements to Anki's reviewer without introducing memory leaks or wrapper hook leakage:

1. **Install Module Guards:**
   - In `reviewer_ui.py`, declare module-level guard flags at the top:
     ```python
     _ui_hooks_installed = False
     _original_shortcutkeys_wrapped = None
     ```

2. **Implement Safe Wrap Functions:**
   - Ensure initialization exits early if hooks are already wrapped:
     ```python
     def setup_reviewer_ui():
         global _ui_hooks_installed, _original_shortcutkeys_wrapped
         if _ui_hooks_installed:
             return

         # Store original reference before monkeypatching
         _original_shortcutkeys_wrapped = Reviewer._shortcutKeys

         # Perform monkeypatch wrapping
         Reviewer._shortcutKeys = custom_shortcutkeys_wrap
         _ui_hooks_installed = True
     ```

3. **Provide Restoration Logic:**
   - Implement a matching cleanup handler that can be called during reload teardowns:
     ```python
     def restore_reviewer_ui():
         global _ui_hooks_installed, _original_shortcutkeys_wrapped
         if not _ui_hooks_installed:
             return

         Reviewer._shortcutKeys = _original_shortcutkeys_wrapped
         _original_shortcutkeys_wrapped = None
         _ui_hooks_installed = False
     ```

---

## Playbook 3: Enforcing Config Validation Caps in the Web Settings GUI

Follow this playbook when adding or modifying reward configurations to maintain fair-play cheat boundaries:

1. **Register Fields in Schema:**
   - Open `ankimon_items_web/settings_schema.py`.
   - Add new settings to the `GROUPS` structure to expose them to the web UI.

2. **Add Validation and Clamping Rules:**
   - Navigate to the `validate_and_clamp(config)` function in `settings_schema.py`.
   - Enforce card intervals bounds `[5, 250]` and cash amount bounds `[10, 2000]`.
   - Enforce the **100:1 cash-to-card cheat-prevention limit**:
     ```python
     if "trainer.cash_reward_amount" in config:
         amt = config["trainer.cash_reward_amount"]
         if isinstance(amt, int):
             new_amt = max(10, min(2000, amt))
             interval = config.get("trainer.cash_reward_interval", 10)
             max_allowed = interval * 100
             if new_amt > max_allowed:
                 new_amt = max_allowed
                 adjustments.append(f"Reward Amount capped at {new_amt}¥ (100:1 ratio limit).")
             config["trainer.cash_reward_amount"] = new_amt
     ```

3. **Save, Commit, and Coalesce UI Refreshes:**
   - Save request triggers the `SettingsBridge.saveSettings()` method in `shop_obj.py`.
   - Clamps are calculated, database values committed, and the `notify_stats_changed()` call instantly refreshes any other open web views.

---

## Common Traps to Avoid

- **The Capitalization Lookup Trap:** JSON lookups fail if database rows capitalize variant keys. Keep variant identifiers in lowercase inside all database schemas.
- **Synchronous Disk I/O Trap:** Do not read or write files directly during card reviews. Use memory loaders.
- **Stale Swapping Connections Trap:** Swapping database paths requires closing the current handle cleanly before opening a new SQLite file.
- **Headless Test Verification:**
  ```powershell
  $env:QT_QPA_PLATFORM="offscreen"
  pytest tests/
  ```

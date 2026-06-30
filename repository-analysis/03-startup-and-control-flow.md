# Startup and Control Flow

This document traces the most important execution and behavior paths in the Ankimon repository.

---

## 1. Add-on Initialization Path (Asynchronous & Thread-Safe)
- **Trigger:** Anki application startup loads installed add-ons.
- **Start File/Symbol:** `__init__.py` -> `start_asynchronous_startup()`.
- **Intermediate Steps:**
  1. Bootstraps basic file paths and directory configurations via `ensure_ankimon_infrastructure()`.
  2. Anchors reload-safe singletons on `mw` (`logger`, `translator`, `settings_obj`, `mw.ankimon_db` SQLite manager).
  3. Spawns an asynchronous background worker thread using `aqt.operations.QueryOp`.
  4. **Background Operations (`run_startup_background_checks()`):**
     - Runs auto-backups (`run_backup()`).
     - Verifies database migration status cleanly.
     - Loads collected Pokémon IDs.
     - Runs config migration, mapping the legacy `battle.automatic_catch_special` to granular chip row auto-catch tiers.
     - Checks if sprites/badges asset directories exist.
     - Generates the initial wild enemy in the background (`generate_random_pokemon()`).
     - Rewrites and aggregates item count metrics (`count_items_and_rewrite()`).
  5. **GUI Thread Callbacks (`run_startup_ui_callbacks()`):**
     - Triggers backup error tracebacks or migration dialog popups if flagged in the background.
     - Displays sprite downloader agreements if folders are missing.
     - Safely loads and synchronizes the background-generated enemy's stats/HP into `enemy_pokemon` on the main GUI thread.
     - Launches starter selection screen if Pokedex count is zero.
     - Wires up menu actions via `create_menu_actions()`.
     - Sets up reviewer hotkeys and registers profile hooks.
     - Sets `mw.ankimon_startup_finished = True` and forces bottom HUD bar redraw.
- **Endpoint/Effect:** The add-on is fully booted, database references re-bound, reviewer shortcuts registered, and battle loop proxy attached, all with zero GUI block lag.
- **State Changes Involved:** Global singletons are initialized; `mw.ankimon_startup_finished` is set to `True`.
- **Persistence Involved:** Thread-safe SQLite read-only operations during background execution; GUI thread commits on callbacks.
- **Integrations Involved:** Sequential wrapping and injection into Anki's reviewer hook system.
- **Why it matters:** Drastically optimizes boot speed, resolving the legacy 10-second blocking startup penalty.
- **Confidence Level:** High

---

## 2. Developer Hot-Reload Path (`reloader.py`)
- **Trigger:** Developer clicks **Ankimon > Restart Ankimon** in the menu bar.
- **Start File/Symbol:** `menu_buttons.py` -> triggers `reloader.restart_ankimon()`.
- **Intermediate Steps:**
  1. Calls `teardown_ankimon()`:
     - Iterates and unregisters all hooks belonging to the addon package from `aqt.gui_hooks`.
     - Closes all active window widgets (`pc_box`, `pokedex_window`, `settings_window`, `evolution_window`).
     - Removes Ankimon menu items from Anki's top-level menu bar.
     - Restores Anki's original Reviewer methods stored in `_shortcutKeys`, `_linkHandler`, and `_bottomHTML` to prevent wrapper accumulation.
  2. Purges modules: Iterates over `sys.modules` and deletes all keys starting with the addon namespace.
  3. Re-imports: Calls `importlib.import_module` on the main entrypoint.
- **Endpoint/Effect:** Code changes are instantly applied to memory without restarting the full Anki application.
- **State Changes Involved:** System modules and GUI hook lists are wiped and re-populated.
- **Persistence Involved:** Reload-safe singletons on `mw` persist their session references to maintain state.
- **Why it matters:** Eliminates Anki's 10-second startup delay, speeding up coding and debugging loops.
- **Confidence Level:** High

---

## 3. Account Switcher / DB Hot-Swap Path
- **Trigger:** User clicks **Switch Account (DEV/Normal)** in the Ankimon menu.
- **Start File/Symbol:** `singletons.py` -> `swap_ankimon_account()`.
- **Intermediate Steps:**
  1. Identifies the active database path (toggles between `ankimon.db` and `ankimonDEV.db`).
  2. Calls `mw.ankimon_db.switch_database(new_path)`:
     - Closes the active sqlite3 connection cleanly using `conn.close()`.
     - Updates the database path string in resources.
     - Re-opens a connection to the new SQLite file and initializes default schemas if the file is new.
  3. Re-reads settings and metadata from the newly opened database.
  4. Triggers in-place updates on active components:
     - Calls `TrainerCard.refresh()` to update trainer Level, XP, and Cash in memory and HUD widgets.
     - If the PC Box grid window is open, calls `reload_pc()` to re-populate slots.
     - Reloads the `main_pokemon` reference from the new team table.
- **Endpoint/Effect:** Active user switches profiles seamlessly inside the reviewer interface at runtime.
- **State Changes Involved:** Global database connection, Settings mappings, and Active Pokemon domains are re-bound in memory.
- **Persistence Involved:** Clean close and switch of the physical `.db` files.
- **Why it matters:** Essential for isolated developer testing without affecting production progress.
- **Confidence Level:** High

---

## 4. Double-Pool Weighted Encounter Path
- **Trigger:** Spawning a new wild Pokémon due to card review progress or hotkey override.
- **Start File/Symbol:** `functions/encounter_functions.py` -> `generate_random_pokemon()`.
- **Intermediate Steps:**
  1. **Tier Roll:** Randomly picks an encounter rarity tier based on review weights (`modify_percentages`).
  2. **Active Region Validation:**
     - If an `active_region` is enabled (e.g. Alola), rolls a weighted chance ( Hisui: 40%, Others: 30%).
     - If successful, builds the **Boosted Pool** collecting regional form variants and introduction generation species for that region.
     - If unsuccessful or the Boosted Pool is empty, builds the **Full Pool** containing all base Pokedex entries.
  3. **Gating Filters:** For each candidate in the selected pool:
     - Verifies starter/legendary/mythical requirements using `_meets_prerequisites` (e.g. must own base form Bulbasaur to spawn Ivysaur).
     - Verifies base generation toggles (`check_id_ok` resolving IDs >= 10000 to base species).
     - Verifies level floors (e.g. Starters min Level 30).
  4. **Post-Selection Resolution:**
     - If a base form is picked, calculates replacement chances: `7 * n %` chance of replacement uniformly among its `n` eligible variants from `REGIONAL_FORM_LOOKUP`.
     - If a regional form was picked directly from the Boosted Pool, it bypasses this step.
- **Endpoint/Effect:** A highly-balanced, gated, and region-aligned wild opponent is generated.
- **State Changes Involved:** `enemy_pokemon` domain object instantiated with generated stats.
- **Why it matters:** Governs the core progression and RPG depth of Ankimon encounters.
- **Confidence Level:** High

---

## 5. Review Card to Battle Turn Path (The Core Loop)
- **Trigger:** Anki's hook framework fires `gui_hooks.reviewer_did_answer_card` when a card is answered.
- **Start File/Symbol:** `__init__.py` -> `on_review_card()` registered callback.
- **Hook Callback Architecture Note:**
  > [!NOTE]
  > Both `card_hooks.py:answerCard_after()` (which tracks card stats and timers) and `__init__.py:on_review_card()` (which handles battle execution) are registered independently to Anki's sequential hook `gui_hooks.reviewer_did_answer_card`. They do not call each other directly; Anki's internal hook framework triggers them in the order they were appended.
- **Intermediate Steps:**
  1. `ankimon_tracker_obj.cards_battle_round` is incremented.
  2. Checks if `cards_battle_round >= settings_obj.get("battle.cards_per_round")`.
  3. If true, a battle turn initiates. Moves are selected for `main_pokemon` and `enemy_pokemon`.
  4. Calls `simulate_battle_with_poke_engine` in `poke_engine/ankimon_hooks_to_poke_engine.py`.
  5. The `poke_engine` processes the turn (`poke_engine/instruction_generator.py`, `poke_engine/damage_calculator.py`).
  6. Results (damage, status changes) are returned.
  7. `main_pokemon` and `enemy_pokemon` HP/status are immediately updated in memory.
  8. `process_battle_data` (`functions/battle_functions.py`) formats the output.
  9. Tooltips and sounds are triggered in the Anki UI.
- **Endpoint/Effect:** HP is reduced, status effects applied, and the user sees the battle result.
- **State Changes Involved:** `main_pokemon.hp`, `enemy_pokemon.hp`, `battle_status`, `cards_battle_round` mutated.
- **Persistence Involved:** Updated in memory singletons.
- **Integrations Involved:** UI tooltips via `aqt.utils.tooltipWithColour`.
- **Why it matters:** This is the primary feature of the add-on. It connects learning to gameplay.
- **Confidence Level:** High

---

## 6. Enemy Pokémon Faint Path (With Auto-Catch)
- **Trigger:** Enemy HP drops below 1 during the `on_review_card` hook.
- **Start File/Symbol:** `__init__.py` -> `on_review_card`.
- **Intermediate Steps:**
  1. Detects `enemy_pokemon.hp < 1`.
  2. Calls `handle_enemy_faint` (`functions/encounter_functions.py`).
  3. XP is calculated and awarded to `main_pokemon`.
  4. **Auto-Catch Gating Check:**
     - Checks if the species is "Special" (Ultra, Legendary, Mythical, Gmax, Mega, or Starter).
     - Checks if `battle.automatic_catch_special` is enabled in settings.
     - If both are true, automatically catches the Pokémon (saving to the SQLite database) even if already owned.
     - Otherwise, standard defeat rules apply.
  5. `mutator_full_reset` is set to 1 to reset the engine state for the next battle.
- **Endpoint/Effect:** Enemy is defeated, rewards (XP/Items/Special captures) are distributed.
- **State Changes Involved:** Enemy state cleared, User XP increased, potential level up.
- **Persistence Involved:** Saving new XP/Level/Capture details to SQLite via `mw.ankimon_db.save_pokemon()`.
- **Why it matters:** Handles progression and reward mechanics.
- **Confidence Level:** High

---

## 7. Profile Open / Sync Path
- **Trigger:** Anki finishes loading a user profile.
- **Start File/Symbol:** `__init__.py` -> `on_profile_did_open`.
- **Intermediate Steps:**
  1. Shows tip of the day.
  2. Checks for monthly rewards (`check_and_award_monthly_pokemon`).
  3. Initializes AnkiWeb sync hooks for SQLite database file (`setup_ankimon_sync_hooks` in `pyobj/ankimon_sync.py`).
  4. Resolves database transaction logs to prevent sync conflicts.
- **Endpoint/Effect:** Daily tasks run, and data is synced across devices.
- **Persistence Involved:** Reads/Writes to the SQLite database.
- **Integrations Involved:** Network access to AnkiWeb/GitHub.
- **Why it matters:** Ensures data consistency and recurring engagement features.
- **Confidence Level:** High

---

## 8. Mobile Reviews Sync & Routing Path
- **Trigger:** Anki sync completes (`gui_hooks.sync_did_finish`).
- **Start File/Symbol:** `pyobj/ankimon_sync.py` -> `on_sync_did_finish()`.
- **Intermediate Steps:**
  1. Detects new review logs synced from mobile devices (using `detect_mobile_reviews`).
  2. If new mobile reviews are found, and the developer database (`ankimonDEV.db`) exists in the profile:
     - Prompts the user/developer with `MobileReviewsRouterDialog` displaying review counts grouped by deck.
     - The user/developer selects a routing target for each deck: **Normal Account (ankimon.db)**, **Developer Account (ankimonDEV.db)**, or **Skip**.
     - Queues the reviews into the respective database files.
     - Advances the mobile watermark in both databases, synchronizing them directly using a lightweight SQLite connection to the inactive database to avoid slow global connection switching.
  3. If the developer database does not exist, queues all reviews directly into the active database and advances its watermark.
- **Endpoint/Effect:** Mobile reviews are successfully routed to their designated accounts, and both databases maintain matching watermarks without redundant global database swaps.
- **State Changes Involved:** Mobile pending review queue counts update; mobile watermarks advanced.
- **Persistence Involved:** Direct writes to SQLite database files.
- **Why it matters:** Allows developers to test features or play in both Normal and DEV modes in parallel while reviewing cards on AnkiMobile.
- **Confidence Level:** High

---

## 9. Mobile Battle Simulation & Resolution Path
- **Trigger:** User initiates battle resolution via Auto-Resolve (`resolveAll`) or Manual Replay (`resolveNext` / `commitReplayOutcome`) in the Mobile Reviews web tab.
- **Start File/Symbol:** `functions/mobile_sync.py` -> `simulate_pending_mobile_battles()`.
- **Intermediate Steps:**
  1. Loads all active team clones using `load_active_team_clones()`. This excludes team members flagged in `mobile.inactive_companions`.
  2. For each pending mobile review battle, simulates the encounter by rolling a random opponent (respecting prerequisites).
  3. In **Auto-Resolve** mode:
     - Automatically selects the optimal companion using `select_best_companion()`, which simulates matchups against the opponent based on move type effectiveness, move power, and speed stats.
     - Simulates combat: calculates damage, faints, catches, and faints. The companion clone is healed back to full HP upon victory.
  4. In **Manual Replay** mode:
     - Prompts the user to preview the opponent, select or override the active companion, and play through the battle.
  5. Computes experience and cash rewards continuously, clamping them using `validate_and_clamp()`.
  6. Writes battle log entries to the `mobile_battle_history` table (and keeps only the 200 most recent records).
- **Endpoint/Effect:** Pending mobile battles are cleared from the queue, companions earn XP/levels, and the trainer receives cash rewards.
- **Persistence Involved:** Pending queue entries updated to resolved; new history logs created; companion data saved.
- **Why it matters:** Offloads mobile study reviews into standard Ankimon gameplay rewards.
- **Confidence Level:** High

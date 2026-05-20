# Editing Playbook

Operational rules for safely modifying the codebase.

## How to Safely Approach a Bug Fix
1.  **Replicate within Anki**: You must understand how the bug manifests in the Anki interface. Is an error dialog appearing, or is it a silent failure?
2.  **Trace the Source**:
    *   If it's a visual issue in the gameloop, inspect `reviewer_iframe.py` and `ankimon_hud_portal.js`.
    *   If numbers (damage/HP) are wrong, inspect `ankimon_hooks_to_poke_engine.py` to ensure the bridge isn't dropping stats, then check `poke_engine/`.
    *   If progression is lost, inspect `database_manager.py` or search for where `db.save_pokemon()` is missing after a mutation.
3.  **Localize the Change**: Ensure your fix operates on the lowest possible subsystem layer. Fix data issues in the database manager, not by hacking the UI to display different numbers.

## How to Safely Approach a Feature Change
1.  **Understand Persistence First**: If the feature requires saving new data (e.g., a new currency type), start by modifying the SQLite schema in `database_manager.py` and adding migration logic to `migration.py`.
2.  **Define Domain Logic**: Add the logic to the appropriate helper file in `functions/` or `pyobj/`.
3.  **Hook into the Event Loop**: Modify `battle_loop.py` or the appropriate PyQt Dialog to trigger the logic.
4.  **Render**: Update the UI templates.

## How to Distinguish Local Change vs System-Wide Change
*   A change within `poke_engine/` is systemic; it affects the math of every battle encounter.
*   A change within `gui_classes/` is local; it only affects that specific window.
*   A change to `singletons.py` or `database_manager.py` is highly systemic and risks breaking the entire application.

## Common Traps Likely to Mislead Future Agents
1.  **"I'll just add an import at the top of the file."** -> *Trap.* Circular dependency crashes will occur due to `singletons.py` cross-linking. Use deferred imports inside functions.
2.  **"I updated `main_pokemon.hp`, the job is done."** -> *Trap.* You merely updated RAM. If you don't call `AnkimonDB.save_main_pokemon()`, the HP reverts on restart.
3.  **"I'll use `isinstance(val, bool)` to check settings."** -> *Trap.* Python booleans subclass integers (`True == 1`). Strict type checking (`type(val) is bool`) is required when parsing `config.json` differences.

## What to Verify Before and After Editing
*   **Startup**: Can Anki open without the Addon crashing it?
*   **Gameloop**: Can you answer a flashcard without the UI freezing?
*   **Persistence**: If you restart Anki, did your changes (HP loss, XP gain) persist?

# Editing Playbook

## How to safely approach a bug fix
1.  Identify if the bug is visual (HUD), mechanical (damage, capture), or persistence-related (lost data).
2.  **Visual**: Inspect `ankimon_hud_portal.js` and `reviewer_iframe.py`.
3.  **Mechanical**: Trace from `battle_loop.py` to `ankimon_hooks_to_poke_engine.py`. Do NOT edit `poke_engine/` unless the core math is wrong.
4.  **Persistence**: Check `database_manager.py` and ensure `.save_pokemon()` is called after mutation.

## Common Traps
*   **Modifying a dict instead of updating the DB**: Changing an attribute on `main_pokemon` does NOT save it to the DB automatically.
*   **Import Errors**: Adding an import at the top of a file might break Anki on startup due to circular references through `singletons.py`.

## What to verify before and after editing
*   Ensure Anki can start without throwing an exception window.
*   Answer one flashcard to ensure `on_review_card` doesn't crash.

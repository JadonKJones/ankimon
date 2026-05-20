# UI Surface to Logic Map

*   **The Gameloop HUD**:
    *   *Surface*: Injected via `ankimon_hud_portal.js` inside Anki's Webview.
    *   *Logic Binder*: `reviewer_iframe.py` generates the HTML strings based on `main_pokemon` and `enemy_pokemon` singletons. Triggered by `battle_loop.py`.
*   **The Settings Menu**:
    *   *Surface*: `gui_classes/` PyQT QDialogs.
    *   *Logic Binder*: `pyobj/settings_window.py` executes validation and updates the Anki configuration.
*   **The Pokedex / Team Menus**:
    *   *Surface*: PyQT QDialogs (`gui_classes/pokemon_team_window.py`).
    *   *Logic Binder*: Direct invocation of `AnkimonDB.get_all_pokemon()` and direct mutation of `singletons.py`.

# Startup and Control Flow

This document traces the 15 most critical execution paths through the Ankimon architecture.

## 1. Application Bootstrap Path
*   **Trigger**: User launches Anki desktop application.
*   **Start file/symbol**: `src/Ankimon/__init__.py`
*   **Intermediate files/symbols**: `singletons.py` -> `database_manager.py:get_db()` -> `startup.py:run_startup_sequence()` -> `startup.py:_check_assets()`.
*   **Endpoint/effect**: Global state is initialized, directories are validated, database migrations are applied, and Anki hooks are registered.
*   **State changes**: Instantiates `main_pokemon`, `enemy_pokemon`, `ankimon_db`, `ankimon_tracker_obj`.
*   **Persistence involved**: Opens SQLite connection to `ankimon.db`. Reads `config.json`.
*   **Why this path matters**: Defines the environment constraints for all subsequent execution.
*   **Confidence level**: High.

## 2. Review Answer Gameloop Path
*   **Trigger**: User answers a flashcard (clicks Again, Hard, Good, or Easy).
*   **Start file/symbol**: `src/Ankimon/card_hooks.py:answerCard_after()`
*   **Intermediate files/symbols**: `ankimon_tracker.py:review()` -> `battle_loop.py:on_review_card()` -> `ankimon_hooks_to_poke_engine.py:simulate_battle_with_poke_engine()` -> `poke_engine/evaluate.py`.
*   **Endpoint/effect**: Health is decremented, status effects applied, and an HTML payload is dispatched to update the reviewer HUD.
*   **State changes**: Mutates `hp`, `stat_stages`, and `volatile_status` on global `main_pokemon` and `enemy_pokemon`. Increments session tracker integers.
*   **Persistence involved**: In-memory only during the immediate loop.
*   **Why this path matters**: The absolute core feature of the application.
*   **Confidence level**: High.

## 3. HUD Rendering Path
*   **Trigger**: Anki transitions to a new review card (`webview_will_set_content` hook).
*   **Start file/symbol**: `src/Ankimon/__init__.py:on_webview_will_set_content()`
*   **Intermediate files/symbols**: `reviewer_ui.py:setup_reviewer_ui()` -> `reviewer_iframe.py:create_iframe_html()`.
*   **Endpoint/effect**: Injects `ankimon_hud_portal.js` which mounts a Shadow DOM containing the battle interface over the flashcard.
*   **State changes**: None (Pure rendering function).
*   **Persistence involved**: Reads sprite assets from disk.
*   **Why this path matters**: The primary visual interface for the user.
*   **Confidence level**: High.

## 4. Wild Pokémon Capture Path
*   **Trigger**: User presses the "Catch" shortcut key (default 'C') when enemy HP is 0.
*   **Start file/symbol**: `src/Ankimon/reviewer_ui.py:catch_shortcut_function()`
*   **Intermediate files/symbols**: `encounter_functions.py:catch_pokemon()` -> `database_manager.py:save_pokemon()`.
*   **Endpoint/effect**: The defeated Pokémon is serialized and inserted into the SQLite database. A new wild encounter is generated.
*   **State changes**: Appends to `_collected_pokemon_ids` set. Regenerates `enemy_pokemon`.
*   **Persistence involved**: Executes SQL `INSERT INTO captured_pokemon`.
*   **Why this path matters**: Core progression mechanic.
*   **Confidence level**: High.

## 5. Pokémon Defeat (Fainting) Path
*   **Trigger**: User presses the "Defeat" shortcut key (default 'D') when enemy HP is 0.
*   **Start file/symbol**: `src/Ankimon/reviewer_ui.py:defeat_shortcut_function()`
*   **Intermediate files/symbols**: `encounter_functions.py:kill_pokemon()` -> `evolution_window.py:check_evolution()` -> `database_manager.py:save_main_pokemon()`.
*   **Endpoint/effect**: Awards XP and EVs to `main_pokemon`, checks for level-ups/evolutions, and saves progress.
*   **State changes**: Mutates `main_pokemon.xp`, `main_pokemon.ev`, `main_pokemon.level`.
*   **Persistence involved**: Executes SQL `UPDATE captured_pokemon SET ... WHERE is_main = 1`.
*   **Why this path matters**: Defines how the user's active entity grows stronger.
*   **Confidence level**: High.

## 6. Main Pokémon Fainting Path
*   **Trigger**: `main_pokemon.hp` drops below 1 during `on_review_card`.
*   **Start file/symbol**: `src/Ankimon/battle_loop.py:handle_main_pokemon_faint()`
*   **Intermediate files/symbols**: `test_window.display_fainted()` -> `pokemon_team_window.py` (if auto-switch is triggered).
*   **Endpoint/effect**: The active Pokémon is rendered unconscious, penalizing the user and forcing a team switch if available.
*   **State changes**: `main_pokemon.hp = 0`.
*   **Why this path matters**: The primary failure state of the application.
*   **Confidence level**: High.

## 7. Configuration Save Path
*   **Trigger**: User clicks "Save" in the Ankimon Settings Window.
*   **Start file/symbol**: `src/Ankimon/pyobj/settings_window.py:save_config()`
*   **Intermediate files/symbols**: `settings.py:set()` -> `anki.config.set()`.
*   **Endpoint/effect**: Validates settings constraints (e.g., preventing all generations from being disabled) and flushes to Anki's configuration manager.
*   **State changes**: Mutates `settings_obj` properties.
*   **Persistence involved**: Writes to Anki's `config.json`.
*   **Why this path matters**: Explains configuration enforcement logic.
*   **Confidence level**: High.

## 8. Data Migration Path
*   **Trigger**: Application startup detects `ankimon_db.is_migrated() == False`.
*   **Start file/symbol**: `src/Ankimon/startup.py`
*   **Intermediate files/symbols**: `migration_dialog.py` -> `migration.py:migrate_all_data()`.
*   **Endpoint/effect**: Parses legacy `mypokemon.json`, normalizes structure, and executes bulk inserts into SQLite.
*   **Persistence involved**: Heavy disk I/O; reads old JSONs, writes to `ankimon.db`.
*   **Why this path matters**: Critical for backwards compatibility.
*   **Confidence level**: High.

## 9. Discord Rich Presence Path
*   **Trigger**: Application startup / Timer tick.
*   **Start file/symbol**: `src/Ankimon/discord_integration.py:setup_discord_hooks()`
*   **Intermediate files/symbols**: `discord_function.py:update_discord_presence()`.
*   **Endpoint/effect**: Connects to local Discord IPC pipe and transmits current gameloop state.
*   **State changes**: None internal.
*   **Integrations involved**: Discord RPC API.
*   **Confidence level**: High.

## 10. Damage Calculation Path
*   **Trigger**: During combat evaluation.
*   **Start file/symbol**: `src/Ankimon/poke_engine/evaluate.py`
*   **Intermediate files/symbols**: `damage_calculator.py:calculate_damage()`.
*   **Endpoint/effect**: Processes base power, STAB, type effectiveness, and RNG variance to return a raw integer damage value.
*   **Why this path matters**: The core physics engine of the gameloop.
*   **Confidence level**: High.

## 11. Asset Generation Path
*   **Trigger**: Missing sprites detected on startup.
*   **Start file/symbol**: `src/Ankimon/startup.py:_check_assets()`
*   **Intermediate files/symbols**: `download_sprites.py:download_and_extract_zip()`.
*   **Endpoint/effect**: Fetches compressed asset payloads from a remote server and unzips them to `user_files/`.
*   **Integrations involved**: External HTTP requests.
*   **Confidence level**: High.

## 12. Pokedex Lookup Path
*   **Trigger**: User opens Pokedex menu.
*   **Start file/symbol**: `src/Ankimon/pokedex/pokedex_obj.py`
*   **Intermediate files/symbols**: `pokedex_functions.py:search_pokedex()`.
*   **Endpoint/effect**: Filters and sorts the entire known Pokémon list against user capture data and renders a UI table.
*   **Confidence level**: Medium.

## 13. Team Switching Path
*   **Trigger**: User opens PC Box or clicks to switch Pokémon.
*   **Start file/symbol**: `src/Ankimon/pyobj/pc_box.py`
*   **Intermediate files/symbols**: `database_manager.py:swap_main_pokemon()`.
*   **Endpoint/effect**: Updates the `is_main` flag in the SQLite database and re-hydrates the global `main_pokemon` instance.
*   **Persistence involved**: SQL updates.
*   **Confidence level**: High.

## 14. Audio Playback Path
*   **Trigger**: Attack occurs or capture succeeds.
*   **Start file/symbol**: `src/Ankimon/utils.py:play_sound()`
*   **Intermediate files/symbols**: `PyQt6.QtMultimedia.QMediaPlayer`.
*   **Endpoint/effect**: Plays `.ogg` audio files asynchronously.
*   **Confidence level**: High.

## 15. Synchronization Path
*   **Trigger**: Anki finishes syncing with AnkiWeb (`sync_did_finish` hook).
*   **Start file/symbol**: `src/Ankimon/hooks.py:sync_on_anki_close`
*   **Intermediate files/symbols**: `database_manager.py:flush()`.
*   **Endpoint/effect**: Guarantees that in-memory cache changes are safely written to disk before Anki exits.
*   **Confidence level**: Medium.

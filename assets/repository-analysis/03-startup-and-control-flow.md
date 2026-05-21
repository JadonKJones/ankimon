# Startup and Control Flow

This document traces the 16 most critical execution paths through the Ankimon architecture, including deep engine evaluation.

## 1. Application Bootstrap Path
*   **Trigger**: User launches Anki desktop application.
*   **Start file/symbol**: `src/Ankimon/__init__.py`
*   **Endpoint/effect**: Global state is initialized, database migrations are applied.
*   **Confidence level**: High.

## 2. Review Answer Gameloop Path (Outer Shell)
*   **Trigger**: User answers a flashcard.
*   **Start file/symbol**: `src/Ankimon/card_hooks.py:answerCard_after()`
*   **Intermediate files/symbols**: `ankimon_tracker.py:review()` -> `battle_loop.py:on_review_card()` -> `ankimon_hooks_to_poke_engine.py:simulate_battle_with_poke_engine()`.
*   **Endpoint/effect**: Dispatches combat intent to the engine, receives the diff, and updates the HUD.
*   **Confidence level**: High.

## 3. Combat Evaluation Path (Inner Engine Physics)
*   **Trigger**: `ankimon_hooks_to_poke_engine.py` calls `evaluate.py`.
*   **Start file/symbol**: `src/Ankimon/poke_engine/evaluate.py`
*   **Intermediate files/symbols**:
    1.  `battle_modifier.py`: Modifies speed/priority based on `special_effects/abilities/` (e.g., Prankster).
    2.  `find_state_instructions.py`: Determines explicit turn ordering.
    3.  `instruction_generator.py`: Translates the selected moves into raw JSON-like instructions.
    4.  `damage_calculator.py`: Applies base power, STAB, type multipliers, and RNG.
*   **Endpoint/effect**: Returns a deterministic list of instructions (e.g., `['damage', 'opponent', 15]`) back to the adapter.
*   **State changes**: Does NOT mutate outer singletons; creates a pure `State` diff.
*   **Why this path matters**: It is the central nervous system of battle mechanics.
*   **Confidence level**: High.

## 4. Special Effects Trigger Path (e.g., End of Turn)
*   **Trigger**: Combat Evaluation reaches the end of an instruction phase.
*   **Start file/symbol**: `src/Ankimon/poke_engine/instruction_generator.py`
*   **Intermediate files/symbols**: `special_effects/items/end_of_turn.py` or `special_effects/abilities/end_of_turn.py`.
*   **Endpoint/effect**: Injects secondary instructions (like Leftovers healing or Poison damage) into the payload.
*   **Confidence level**: High.

## 5. HUD Rendering Path
*   **Trigger**: Anki transitions to a new review card.
*   **Start file/symbol**: `src/Ankimon/__init__.py:on_webview_will_set_content()`
*   **Endpoint/effect**: Injects `ankimon_hud_portal.js` which mounts a Shadow DOM.
*   **Confidence level**: High.

## 6. Wild Pokémon Capture Path
*   **Trigger**: User presses the "Catch" shortcut key (default 'C') when enemy HP is 0.
*   **Start file/symbol**: `src/Ankimon/reviewer_ui.py:catch_shortcut_function()`
*   **Endpoint/effect**: Executes SQL `INSERT INTO captured_pokemon`.
*   **Confidence level**: High.

## 7. Pokémon Defeat (Fainting) Path
*   **Trigger**: User presses the "Defeat" shortcut key.
*   **Start file/symbol**: `src/Ankimon/reviewer_ui.py:defeat_shortcut_function()`
*   **Endpoint/effect**: Awards XP/EVs, checks evolutions, saves progress to SQLite.
*   **Confidence level**: High.

## 8. Main Pokémon Fainting Path
*   **Trigger**: `main_pokemon.hp` drops below 1.
*   **Start file/symbol**: `src/Ankimon/battle_loop.py:handle_main_pokemon_faint()`
*   **Endpoint/effect**: Renders unconscious state, forces team switch.
*   **Confidence level**: High.

## 9. Configuration Save Path
*   **Trigger**: User clicks "Save" in the Ankimon Settings Window.
*   **Start file/symbol**: `src/Ankimon/pyobj/settings_window.py:save_config()`
*   **Endpoint/effect**: Validates and writes to Anki's `config.json`.
*   **Confidence level**: High.

## 10. Data Migration Path
*   **Trigger**: Application startup detects legacy state.
*   **Start file/symbol**: `src/Ankimon/startup.py`
*   **Endpoint/effect**: Parses legacy `mypokemon.json`, writes to `ankimon.db`.
*   **Confidence level**: High.

## 11. Discord Rich Presence Path
*   **Trigger**: Application startup / Timer tick.
*   **Start file/symbol**: `src/Ankimon/discord_integration.py`
*   **Endpoint/effect**: Transmits gameloop state to Discord.
*   **Confidence level**: High.

## 12. Asset Generation Path
*   **Trigger**: Missing sprites detected on startup.
*   **Start file/symbol**: `src/Ankimon/startup.py:_check_assets()`
*   **Endpoint/effect**: Fetches and unzips payload to `user_files/`.
*   **Confidence level**: High.

## 13. Pokedex Lookup Path
*   **Trigger**: User opens Pokedex menu.
*   **Start file/symbol**: `src/Ankimon/pokedex/pokedex_obj.py`
*   **Endpoint/effect**: Filters known Pokémon list against user capture data.
*   **Confidence level**: Medium.

## 14. Team Switching Path
*   **Trigger**: User opens PC Box.
*   **Start file/symbol**: `src/Ankimon/pyobj/pc_box.py`
*   **Endpoint/effect**: Updates the `is_main` flag in SQLite.
*   **Confidence level**: High.

## 15. Audio Playback Path
*   **Trigger**: Attack occurs or capture succeeds.
*   **Start file/symbol**: `src/Ankimon/utils.py:play_sound()`
*   **Endpoint/effect**: Plays `.ogg` audio files.
*   **Confidence level**: High.

## 16. Synchronization Path
*   **Trigger**: Anki finishes syncing with AnkiWeb.
*   **Start file/symbol**: `src/Ankimon/hooks.py:sync_on_anki_close`
*   **Endpoint/effect**: Flushes memory cache to `ankimon.db`.
*   **Confidence level**: Medium.

# Startup and Control Flow

## 1. Startup Path
*   **Trigger**: Anki application launch.
*   **Start file/symbol**: `src/Ankimon/__init__.py`
*   **Intermediate files/symbols**: `src/Ankimon/singletons.py` -> `src/Ankimon/startup.py:run_startup_sequence()` -> `database_manager.py:get_db()`
*   **Endpoint/effect**: Global variables are initialized, database connections are established, migrations run if necessary, and hooks are registered in Anki.
*   **State changes**: Populates `main_pokemon`, `enemy_pokemon`, `settings_obj`.
*   **Persistence**: Connects to `ankimon.db`, reads config.
*   **Why this path matters**: Defines the initial state of the application.
*   **Confidence level**: High.

## 2. Review Action to Battle State Mutation
*   **Trigger**: User clicks "Good", "Hard", "Again", or "Easy" on an Anki flashcard.
*   **Start file/symbol**: `src/Ankimon/card_hooks.py:answerCard_after()`
*   **Intermediate files/symbols**: `src/Ankimon/battle_loop.py:on_review_card()` -> `functions/ankimon_hooks_to_poke_engine.py:simulate_battle_with_poke_engine()` -> `poke_engine/evaluate.py`.
*   **Endpoint/effect**: Damage is calculated, statuses applied, and UI is updated via `tooltipWithColour` and updating the `reviewer_iframe`.
*   **State changes**: `main_pokemon.hp`, `enemy_pokemon.hp`, `ankimon_tracker_obj.cards_battle_round`.
*   **Persistence**: None immediately (cached in memory).
*   **Why this path matters**: This is the core gameplay loop.
*   **Confidence level**: High.

## 3. UI Update Path (HUD Injection)
*   **Trigger**: `webview_will_set_content` hook fires.
*   **Start file/symbol**: `src/Ankimon/__init__.py:on_webview_will_set_content`
*   **Intermediate files/symbols**: `src/Ankimon/reviewer_ui.py`, `src/Ankimon/user_files/web/ankimon_hud_portal.js`.
*   **Endpoint/effect**: The iframe and battle HUD are overlaid onto the Anki flashcard.
*   **Why this path matters**: Explains how visual changes are presented to the user without modifying Anki's core UI.
*   **Confidence level**: High.

# Glossary

*   **`ankimon_db`**: The singleton instance of `AnkimonDB`, a DAO managing the `ankimon.db` SQLite file.
*   **`ankimon_tracker_obj`**: The singleton tracking Anki session stats (cards reviewed, streaks, multipliers).
*   **`battle_loop.py`**: The file containing the core `on_review_card` hook, controlling the flow of gameloop time.
*   **`enemy_pokemon`**: The singleton `PokemonObject` representing the wild encounter or opposing trainer's active combatant.
*   **Gameloop**: The cycle of answering a flashcard, generating combat instructions, applying damage, and updating the UI.
*   **`main_pokemon`**: The singleton `PokemonObject` representing the user's currently active fighting Pokémon.
*   **`mw`**: `aqt.mw`, Anki's Main Window. The root object for accessing Anki's internal state, toolbar, and config.
*   **`poke_engine`**: The isolated, pure Python submodule handling combat physics (damage math, speed calculation, status effects).
*   **`PokemonObject`**: The primary in-memory data container defining a Pokémon's stats, level, and identity.
*   **Shadow DOM**: A web standard used by Ankimon (`ankimon_hud_portal.js`) to inject CSS and HTML into Anki's reviewer window without the styles bleeding into the user's flashcard content.
*   **`singletons.py`**: A file acting as a global namespace registry for instantiated objects.
*   **`State`**: Within the context of the `poke_engine`, an immutable snapshot of the battle board (participants, weather, field conditions).

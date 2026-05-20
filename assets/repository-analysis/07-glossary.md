# Glossary

*   **`main_pokemon`**: The singleton instance representing the user's active Pokémon.
*   **`enemy_pokemon`**: The singleton instance representing the wild Pokémon currently being battled.
*   **`AnkimonDB`**: The SQLite database manager handling all persistence.
*   **`poke_engine`**: The independent submodule handling pure Pokémon battle simulation logic.
*   **`ankimon_tracker_obj`**: The singleton that counts Anki cards reviewed, multipliers, and streak data.
*   **`HUD`**: The Heads-Up Display injected into Anki's reviewer window.
*   **`mw`**: Anki's Main Window object (`aqt.mw`).

# Config Surface Map

*   **Host Location**: Managed by Anki natively inside the addon directory as `config.json` and `meta.json`.
*   **Application Wrapper**: `src/Ankimon/pyobj/settings.py` via the `settings_obj` singleton.
*   **Key Configuration Surface Areas**:
    *   `controls.*`: Keybindings for "Catch" and "Defeat" shortcuts.
    *   `audio.*`: Toggles for sound effects and volume levels.
    *   `battle.cards_per_round`: An integer or range dictating how many Anki cards must be answered before a combat turn executes.
    *   `misc.gen1` through `misc.gen9`: Booleans determining which generations of Pokémon are allowed to spawn.

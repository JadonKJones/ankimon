# Persistence Deep Dive

*   Legacy: `mypokemon.json`, `mainpokemon.json`.
*   Current: `ankimon.db` (SQLite).
*   **Migration**: `startup.py` calls `show_migration_dialog_if_needed` to transition data.

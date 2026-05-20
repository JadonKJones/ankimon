# Persistence Deep Dive

*   **Legacy Implementation**: Historically, Ankimon stored the active party in `mainpokemon.json` and the storage box in `mypokemon.json`. This was fragile and prone to corruption.
*   **Current Implementation**: `ankimon.db` (SQLite3).
*   **The Migration Strategy**: `src/Ankimon/startup.py` calls `AnkimonDB.is_migrated()`. If false, `migration.py` engages. It parses the massive arrays in `mypokemon.json`, serializes the complex nested dictionaries (EVs, IVs, Stats) into strings, and executes bulk `INSERT` statements into the `captured_pokemon` table.
*   **Caching**: To prevent UI lag during flashcard reviews, `database_manager.py` maintains an `_all_pokemon_cache`. This cache is aggressively invalidated upon any write operation (`save_pokemon`, `delete_pokemon`).

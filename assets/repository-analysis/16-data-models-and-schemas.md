# Data Models and Schemas

## 1. PokemonObject
*   **Purpose**: The central in-memory representation of a Pokémon instance.
*   **Key Fields**:
    *   `id` (int): National Dex number.
    *   `name` (str): Species name.
    *   `hp`, `max_hp` (int): Current health tracking.
    *   `stats`, `iv`, `ev` (dict): Spread definitions.
    *   `attacks` (list): Current moveset.
    *   `individual_id` (str): UUID for unique tracking.

## 2. AnkimonDB Schema (SQLite)
*   **Table `captured_pokemon`**:
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    *   `pokemon_id` (INTEGER)
    *   `name` (TEXT)
    *   `nickname` (TEXT)
    *   `level` (INTEGER)
    *   `hp` (INTEGER)
    *   `xp` (INTEGER)
    *   `stats` (TEXT) - JSON serialized dict
    *   `ivs` (TEXT) - JSON serialized dict
    *   `evs` (TEXT) - JSON serialized dict
    *   `attacks` (TEXT) - JSON serialized list
    *   `is_main` (INTEGER) - Boolean flag
    *   `is_favorite` (INTEGER) - Boolean flag
    *   `held_item` (TEXT)

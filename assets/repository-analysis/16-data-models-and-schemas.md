# Data Models and Schemas

## 1. PokemonObject
*   **Purpose**: Represents a Pokémon in memory.
*   **Key Fields**: `id`, `name`, `hp`, `max_hp`, `stats`, `iv`, `ev`, `attacks`.

## 2. AnkimonDB Schema (SQLite)
*   **Tables**: `captured_pokemon`
*   **Key Fields**: `id` (INTEGER PRIMARY KEY), `name` (TEXT), `level` (INTEGER), `hp` (INTEGER), `stats` (TEXT/JSON).

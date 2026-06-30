# Import and Call Hotspots

This document highlights structural centers of gravity in the codebase. Identifying these helps recognize hidden coupling and areas where changes carry disproportionate risk.

---

## High Fan-in Files (Foundation Leaves)
These files act as the foundation of the repository.
1. **`resources.py`**: Almost every file that touches the file system imports paths from here. It is a critical configuration leaf.
2. **`functions/encounter_data.py`**: The absolute source of truth for encounter tiers, prerequisites, and variants. Imported by the simulation suite, PC Box, and gating engines.
3. **`pyobj/settings.py`**: The `settings_obj` is injected into almost every UI component and feature module to check user preferences.
4. **`pyobj/pokemon_obj.py`**: The core domain model. Anything that interacts with Pokémon data imports this.
5. **`pyobj/database_manager.py`**: The database persistence engine (`ankimon_db`). Almost all game mechanics, saving processes, item updates, and box loads depend on this module.
6. **`functions/pokedex_functions.py` & `functions/learnset_retrieval.py`**: The in-memory cache loaders. Imported by UI panels, PC detail cards, and battle simulation bridges.

---

## High Fan-out Files (Orchestrator Hubs)
These files act as orchestrators. Changes in dependencies frequently force updates here.
1. **`__init__.py`**: Imports virtually everything in the add-on to bootstrap the system, register hooks, and wire events.
2. **`singletons.py`**: Imports all the major UI classes (`TestWindow`, `ItemWindow`, `PokemonPC`) to instantiate them globally, and houses the profile switcher.
3. **`reloader.py`**: A developer-mode clean-state orchestrator that teardowns all hooks, widgets, and menu items across Anki's global registry.
4. **`functions/encounter_functions.py`**: Imports tracking, UI updates, saving logic, and Pokémon generation logic to coordinate full encounter cycles.

---

## Technical Chokepoints

### 1. `poke_engine/ankimon_hooks_to_poke_engine.py`
Every battle calculation passes through this file. It translates the Ankimon domain model (`PokemonObject`) into the engine's domain model, and then translates the engine's output back. It is a massive structural chokepoint.

### 2. `pyobj/database_manager.py`
All reads and writes to `ankimon.db` and `ankimonDEV.db` pass through this manager's SQLite connection. The `switch_database()` method acts as the sole transition boundary for account swaps.

### 3. `check_id_ok()` inside `encounter_functions.py`
The absolute chokepoint for generation-based gating of custom forms. It resolves Mega, Gmax, and variant IDs (IDs >= 10000) to base species IDs. If it fails or is bypassed, generation anomalies will occur (e.g., disabled generation forms spawning).

---

## Suspicious Dependency Concentrations & Hidden Coupling
- **Reviewer Hook wrappings:** The connection between `reviewer_ui.py` and Anki's `Reviewer` methods. Bypassing global hook guards leads to wrapper accumulation.
- **Database Schema Serializations:** The PC Box and state managers extract serialized JSON payloads from SQLite text columns. Any schema mutation without migration will crash UI views.

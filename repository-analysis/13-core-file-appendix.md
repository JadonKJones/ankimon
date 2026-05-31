# Core File Appendix

This appendix contains code excerpts and architectural context for the most critical modules in the Ankimon codebase.

---

## 1. `__init__.py`
Observing the core review loop and state synchronization sequence:

```python
# [EXCERPT: Core Review Loop in __init__.py]
def on_review_card(*args):
    try:
        multiplier = ankimon_tracker_obj.multiplier
        # ... [setup omitted] ...

        # Increment the counter when a card is reviewed
        ankimon_tracker_obj.cards_battle_round += 1
        ankimon_tracker_obj.general_card_count_for_battle += 1

        if ankimon_tracker_obj.cards_battle_round >= int(settings_obj.get("battle.cards_per_round")):
            ankimon_tracker_obj.cards_battle_round = 0
            ankimon_tracker_obj.pokemon_encouter += 1

            # ... [move selection logic omitted] ...

            '''
            below is the MOST IMPORTANT function for the battle engine.
            This runs our current Pokemon stats through SirSkaro's Poke-Engine.
            '''
            results = simulate_battle_with_poke_engine(
                main_pokemon,
                enemy_pokemon,
                user_attack,
                enemy_attack,
                mutator_full_reset,
                new_state,
            )

            # Unpack results from the simulation
            battle_info = results[0]
            new_state = copy.deepcopy(results[1])

            # IMMEDIATE STATE SYNCHRONIZATION
            main_pokemon.hp = new_state.user.active.hp
            main_pokemon.current_hp = new_state.user.active.hp
            enemy_pokemon.hp = new_state.opponent.active.hp
            enemy_pokemon.current_hp = new_state.opponent.active.hp

            # Update statuses based on instructions, now that HP is correct.
            enemy_status_changed, main_status_changed = update_pokemon_battle_status(
                battle_info, enemy_pokemon, main_pokemon
            )

            # Persist state directly to SQLite via database manager
            mw.ankimon_db.save_pokemon(main_pokemon.to_dict())
```

---

## 2. `reloader.py`
Tracing modular hot-reload teardowns and module namespace purging:

```python
# [EXCERPT: Developer Reloader in reloader.py]
import sys
import importlib
from aqt import mw

def teardown_ankimon():
    # 1. Unregister hooks from aqt.gui_hooks
    # 2. Close all active GUI dialog widgets
    # 3. Remove custom menu buttons from Anki Menu Bar
    # 4. Restore original Reviewer method references
    
    global _ui_hooks_installed
    from .reviewer_ui import restore_reviewer_ui
    restore_reviewer_ui()

def restart_ankimon():
    try:
        teardown_ankimon()
        
        # Purge all modules in the add-on namespace
        addon_prefix = __name__.split('.')[0]
        to_delete = [m for m in sys.modules if m.startswith(addon_prefix)]
        for mod in to_delete:
            del sys.modules[mod]
            
        # Re-import main entrypoint
        importlib.import_module(addon_prefix)
        mw.progress.timer(100, lambda: mw.reset(), False)
    except Exception as e:
        print(f"Reloader error: {e}")
```

---

## 3. `pyobj/database_manager.py`
Tracing database schema definitions and hot-swaps:

```python
# [EXCERPT: Database Table Setup inside AnkimonDB]
def _setup_database(self):
    conn = self._get_connection()
    cursor = conn.cursor()

    # Table for captured pokemon (replaced legacy mypokemon.json AND mainpokemon.json)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS captured_pokemon (
            individual_id TEXT PRIMARY KEY,
            is_main INTEGER DEFAULT 0,
            data TEXT NOT NULL,
            name TEXT GENERATED ALWAYS AS (json_extract(data, '$.name')) VIRTUAL,
            pokedex_id INTEGER GENERATED ALWAYS AS (json_extract(data, '$.id')) VIRTUAL,
            shiny BOOLEAN GENERATED ALWAYS AS (json_extract(data, '$.shiny')) VIRTUAL,
            level INTEGER GENERATED ALWAYS AS (json_extract(data, '$.level')) VIRTUAL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_name ON captured_pokemon(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_pokedex_id ON captured_pokemon(pokedex_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_shiny ON captured_pokemon(shiny)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_level ON captured_pokemon(level)")

    # Table for team composition
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team (
            slot_position INTEGER PRIMARY KEY,
            individual_id TEXT NOT NULL
        )
    """)

def switch_database(self, new_db_path):
    """Safely closes active connections and binds a new database path at runtime."""
    if self._conn:
        self._conn.close()
        self._conn = None
    self.db_path = new_db_path
    self._setup_database()
```

---

## 4. `functions/encounter_functions.py`
Tracing double-pool random generations and post-selection variant lookups:

```python
# [EXCERPT: Pool generation weighting inside encounter_functions.py]
def generate_random_pokemon():
    # 1. Roll tier probabilities
    tier = select_rarity_tier()
    
    # 2. Check Active Region Pools (Hisui 40%, Others 30%)
    active_reg = settings_obj.get("misc.active_region")
    if active_reg and roll_region_chance(active_reg):
        pool = get_boosted_region_pool(active_reg, tier)
    else:
        pool = get_full_pool(tier)
        
    # Apply gating filters (Prerequisites checking & ID generational validation)
    pool = [p for p in pool if check_id_ok(p) and meets_prereqs(p)]
    
    selected_species = random.choice(pool)
    
    # 3. Post-Selection Variant check
    variant_ids = REGIONAL_FORM_LOOKUP.get(selected_species.id, [])
    if variant_ids and random.random() < (0.07 * len(variant_ids)):
        selected_species = get_regional_substitute(variant_ids)
        
    return build_pokemon_object(selected_species)
```

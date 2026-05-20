# Core File Appendix

## `src/Ankimon/__init__.py` (Excerpt)
**Why selected**: Primary entrypoint showing hook registration.
```python
# --- Card timer and answer hooks ---
from .card_hooks import register_card_hooks
register_card_hooks()

setupHooks(None, ankimon_tracker_obj)

# --- Battle loop ---
from .battle_loop import on_review_card, init_battle_state
init_battle_state(collected_pokemon_ids)
gui_hooks.reviewer_did_answer_card.append(on_review_card)
```

## `src/Ankimon/singletons.py` (Excerpt)
**Why selected**: Shows instantiation of global state.
```python
# Initialize the database (this also runs migrations on first startup)
ankimon_db = get_db(logger)

# Create the Settings object
settings_obj = Settings()

main_pokemon, mainpokemon_empty = update_main_pokemon()
```

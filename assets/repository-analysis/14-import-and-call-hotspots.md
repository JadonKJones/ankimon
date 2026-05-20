# Import and Call Hotspots

## High Fan-in (Many files depend on this)
1.  `src/Ankimon/singletons.py`: imported by almost every UI class and hook to access state.
2.  `src/Ankimon/pyobj/settings.py` (via `settings_obj`): Configuration is read globally.
3.  `src/Ankimon/resources.py`: Contains path definitions used universally for asset loading.

## High Fan-out (This file coordinates many dependencies)
1.  `src/Ankimon/__init__.py`: Pulls in hooks, UI, startup logic, and discord integration.
2.  `src/Ankimon/battle_loop.py`: Calls UI updates, sound utilities, logging, tracking, and the battle engine.

## Chokepoints
*   `src/Ankimon/pyobj/database_manager.py`: All data persistence funnels through `AnkimonDB`.
*   `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`: All battle mechanics funnel through this translation layer.

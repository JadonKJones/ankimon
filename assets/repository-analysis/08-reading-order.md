# Reading Order

Optimized pathways for future agents to comprehend and safely modify the codebase based on specific objectives.

## Path 1: Fast Architectural Orientation
*Goal: Understand the absolute boundaries and data flow in 15 minutes.*
1.  `src/Ankimon/__init__.py`: Understand how Anki triggers Ankimon.
2.  `src/Ankimon/singletons.py`: Map the global namespace.
3.  `src/Ankimon/startup.py`: Understand the bootstrap validation loop.
4.  `src/Ankimon/pyobj/database_manager.py`: Understand the SQLite schema and DAO methods.
5.  `src/Ankimon/battle_loop.py`: Understand the entrypoint for all combat logic.

## Path 2: Deep Architecture Study (The Gameloop)
*Goal: Understand the mathematics, timing, and evaluation of combat.*
1.  `src/Ankimon/battle_loop.py`: Locate the `simulate_battle_with_poke_engine` call.
2.  `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`: Understand how Ankimon's `PokemonObject` is translated into the Engine's `State` object.
3.  `src/Ankimon/poke_engine/evaluate.py`: Read the core evaluation logic for speed ties, turn ordering, and instruction generation.
4.  `src/Ankimon/poke_engine/instruction_generator.py`: Understand how moves are converted into discrete status/damage events.
5.  `src/Ankimon/poke_engine/damage_calculator.py`: Review the raw math governing HP reduction.

## Path 3: Safe Feature Implementation (Adding a Item)
*Goal: Implement a new held item or consumable without breaking persistence.*
1.  `src/Ankimon/addon_files/items.json`: Locate the data store for item definitions.
2.  `src/Ankimon/utils.py`: Find `give_item()` to understand inventory logic.
3.  `src/Ankimon/pyobj/item_window.py`: Understand how the UI parses the JSON and allows the user to trigger an item use.
4.  `src/Ankimon/pyobj/database_manager.py`: Trace how item quantities are decremented and saved.

## Path 4: Debugging Visual Glitches
*Goal: Fix a bug where the HUD overlaps Anki text or fails to update.*
1.  `src/Ankimon/__init__.py`: Locate `on_webview_will_set_content`.
2.  `src/Ankimon/user_files/web/ankimon_hud_portal.js`: Understand the Shadow DOM isolation strategy.
3.  `src/Ankimon/reviewer_ui.py`: See how Anki's bottom HTML is hijacked.
4.  `src/Ankimon/functions/reviewer_iframe.py`: Inspect the string template generation that is ultimately injected into the portal.

## Path 5: High-Risk Refactor Preparation (State Management)
*Goal: Eliminate `singletons.py` in favor of a Dependency Injected architecture.*
1.  `src/Ankimon/singletons.py`: Map every exported variable.
2.  Run an AST grep for `from .singletons import` across the `src/` directory. (Hint: It's massive).
3.  `src/Ankimon/gui_classes/`: Study how PyQT Dialogs currently accept dependencies via `__init__` vs how they fall back to global imports.
4.  `src/Ankimon/pyobj/ankimon_tracker.py`: Study the primary state container that *should* hold references to active entities instead of relying on globals.

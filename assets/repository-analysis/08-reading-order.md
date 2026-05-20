# Reading Order

## Fast Architectural Orientation
1.  `src/Ankimon/__init__.py`: Understand how Ankimon hooks into Anki.
2.  `src/Ankimon/singletons.py`: See what state exists globally.
3.  `src/Ankimon/startup.py`: See how state is initialized.
4.  `src/Ankimon/battle_loop.py`: See the core gameplay loop.

## Deep Architecture Study (Battle Mechanics)
1.  `src/Ankimon/battle_loop.py`: The entrypoint.
2.  `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`: The bridge translating Ankimon objects to Engine objects.
3.  `src/Ankimon/poke_engine/evaluate.py`: The engine's entrypoint.
4.  `src/Ankimon/poke_engine/battle.py`: Core simulator state management.

## Safe Feature Implementation (Adding a new Item)
1.  `src/Ankimon/addon_files/items.json` or equivalent data store: Define the item.
2.  `src/Ankimon/utils.py:give_item()`: Check inventory logic.
3.  `src/Ankimon/pyobj/item_window.py`: Understand how items are used in the UI.
4.  `src/Ankimon/pyobj/database_manager.py`: Ensure item count saves correctly.

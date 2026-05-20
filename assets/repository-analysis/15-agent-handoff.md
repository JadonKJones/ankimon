# Agent Handoff

*   **Well Understood**: The primary gameloop is triggered by Anki's review hooks, processed in `battle_loop.py`, calculated in `poke_engine`, and persisted in `ankimon.db` via `database_manager.py`.
*   **Uncertain**: The exact boundary of what UI components mutate state directly vs what goes through a controller.
*   **Where to start**: If modifying persistence, look at `database_manager.py`. If modifying gameloop behavior, start at `battle_loop.py`. If fixing Anki integration, look at `__init__.py`.
*   **Highest Risk**: Be extremely careful adding global imports due to circular dependency risks involving `singletons.py`.

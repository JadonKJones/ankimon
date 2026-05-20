# Risk Register

## 1. Singleton Mutation Desynchronization
*   **Affected modules**: `singletons.py`, `battle_loop.py`, `database_manager.py`.
*   **Why**: Global instances like `main_pokemon` are modified directly. If `db.save_pokemon()` is not called, data is lost on restart.
*   **Dangerous change**: Modifying properties of `PokemonObject` without ensuring downstream persistence.
*   **Confidence**: High.

## 2. Circular Dependencies
*   **Affected modules**: Entire `src/Ankimon/` tree.
*   **Why**: Heavy reliance on `singletons.py` and deeply nested imports in `functions/` and `gui_classes/`.
*   **Dangerous change**: Adding imports at the top of files instead of inside functions or at the bottom.
*   **Evidence**: `__init__.py` explicitly delays imports or wraps them in functions.
*   **Confidence**: High.

## 3. UI Thread Blocking
*   **Affected modules**: `battle_loop.py`.
*   **Why**: Executing heavy calculations (`poke_engine`) inside Anki's main review hook.
*   **Dangerous change**: Adding synchronous network requests or heavy I/O to `on_review_card`.
*   **Failure mode**: Anki UI freezes.
*   **Confidence**: Medium.

## 4. Iframe / Shadow DOM Conflicts
*   **Affected modules**: `ankimon_hud_portal.js`.
*   **Why**: Manipulates Anki's webview.
*   **Dangerous change**: Changing element IDs or failing to scope CSS rules properly.
*   **Confidence**: Medium.

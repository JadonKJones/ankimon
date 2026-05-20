# Conventions Observed

## 1. Global State Management
*   **Convention**: Instantiate once in `singletons.py`, import globally.
*   **Evidence**: `from .singletons import main_pokemon, settings_obj` is ubiquitous.
*   **Strength**: Strong.

## 2. Error Handling in Hooks
*   **Convention**: Wrap hook logic in `try...except Exception as e: show_warning_with_traceback()`.
*   **Evidence**: Seen in `battle_loop.py` and `startup.py`.
*   **Strength**: Strong.
*   **Guidance**: Never let an exception bubble up to Anki, as it halts the user's review session.

## 3. Import Locality
*   **Convention**: Delayed or function-local imports.
*   **Evidence**: `__init__.py` imports modules immediately before using them, rather than at the top of the file.
*   **Strength**: Moderate.
*   **Guidance**: Used to break circular dependencies.

## 4. UI Layering
*   **Convention**: Complex visual rendering is done via HTML/CSS/JS injected into an iframe/Shadow DOM, rather than native PyQt widgets during review.
*   **Evidence**: `ankimon_hud_portal.js`, `reviewer_iframe.py`.
*   **Strength**: Strong.

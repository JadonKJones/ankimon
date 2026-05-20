# Risk Register

This document identifies fragile or high-impact areas within the repository where structural changes pose severe risks.

## 1. Global Singleton Desynchronization
*   **Affected modules**: `src/Ankimon/singletons.py`, `src/Ankimon/battle_loop.py`, `src/Ankimon/pyobj/database_manager.py`.
*   **Why this area is risky**: The application relies on globally accessible mutable objects (`main_pokemon`).
*   **Dangerous change**: Modifying properties of `main_pokemon` (e.g., `main_pokemon.xp += 10`) inside an arbitrary UI dialog without explicitly calling `ankimon_db.save_main_pokemon(main_pokemon.to_dict())`.
*   **Evidence**: Repeated historical bugs related to lost progression are solved by aggressive database syncing.
*   **Failure modes**: Player state reverts when Anki closes.
*   **Precautions**: Always pair memory mutations with database flushes, or rely exclusively on the `database_manager` to perform the mutation.
*   **Confidence level**: High.

## 2. Circular Import Catastrophe
*   **Affected modules**: Entire `src/Ankimon` tree, specifically files importing from `singletons.py`.
*   **Why this area is risky**: `singletons.py` imports a vast array of UI classes and functions to instantiate them, while those same classes import `singletons.py` to access `main_pokemon` and `settings_obj`.
*   **Dangerous change**: Moving a local import (inside a function body) to the top of a file, or adding a new global import in `singletons.py`.
*   **Evidence**: Observed `ImportError: cannot import name` exceptions bypassed by `def function_name(): from .singletons import ...` constructs throughout the codebase.
*   **Failure modes**: The Anki application crashes entirely upon startup before the addon can load.
*   **Precautions**: Utilize dependency injection where possible. If a global must be accessed, import it inside the function executing the logic.
*   **Confidence level**: High.

## 3. UI Thread Blocking (Gameloop Lag)
*   **Affected modules**: `src/Ankimon/battle_loop.py:on_review_card`, `src/Ankimon/poke_engine/`.
*   **Why this area is risky**: Anki executes `reviewer_did_answer_card` hooks synchronously on the main UI thread.
*   **Dangerous change**: Introducing synchronous I/O, heavy JSON parsing, or deep unoptimized recursion loops inside the battle evaluator.
*   **Evidence**: The engine currently utilizes caching helpers (`@functools.lru_cache`) to prevent disk reads during the gameloop to maintain performance.
*   **Failure modes**: Anki freezes for hundreds of milliseconds after the user answers a flashcard, destroying the spaced-repetition workflow.
*   **Precautions**: Ensure any new logic in the gameloop is strictly CPU-bound and highly optimized O(1) or O(N) operations. Move I/O to async tasks or background threads.
*   **Confidence level**: High.

## 4. Hook Recursion and Event Cascades
*   **Affected modules**: `src/Ankimon/card_hooks.py`.
*   **Why this area is risky**: Anki hooks can trigger other Anki hooks.
*   **Dangerous change**: Artificially triggering card reviews or modifying Anki's state from within a hook callback.
*   **Failure modes**: Infinite recursion crashing Python with a maximum recursion depth error.
*   **Precautions**: Limit hook logic strictly to observing Anki's state and mutating Ankimon's isolated state.
*   **Confidence level**: Medium.

## 5. Webview CSS Bleeding
*   **Affected modules**: `src/Ankimon/user_files/web/ankimon_hud_portal.js`.
*   **Why this area is risky**: Ankimon injects arbitrary HTML/CSS into Anki's primary reviewer window.
*   **Dangerous change**: Removing the Shadow DOM isolation or writing overly broad CSS selectors (e.g., `body { ... }` instead of scoped selectors).
*   **Failure modes**: The user's flashcards become unreadable due to conflicting layout rules or colors.
*   **Precautions**: Maintain strict adherence to the Shadow DOM boundaries established in the portal script.
*   **Confidence level**: High.

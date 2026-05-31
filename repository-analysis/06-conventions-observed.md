# Conventions Observed

This document outlines the coding, UI styling, and architectural conventions actually observed in the Ankimon repository.

---

## 1. Global Singleton Injection
- **Strength:** Strong
- **Evidence:** `singletons.py` instantiates `settings_obj`, `logger`, `main_pokemon`, and `ankimon_db`. These are passed explicitly to the constructors of almost every UI class (e.g., `TestWindow`, `ItemWindow`).
- **Guidance:** Do not rely on importing global variables directly into UI classes. Instead, require them in the `__init__` signature to enforce proper dependency injection and avoid circular imports.

---

## 2. Defensive Hook Wrapping (Wrapper Guards)
- **Strength:** Strong
- **Evidence:** Reviewer hook modifications in `reviewer_ui.py` utilize unique module-level guards like `_ui_hooks_installed = True` and keep original method pointers in `_original_shortcutkeys_wrapped` to prevent duplication during reloads.
- **Guidance:** When wrapping Anki reviewer methods or shortcuts, always guard the monkeypatching block with a boolean flag, and save the original method reference to allow clean restoration.

---

## 3. Active UI Validation & Self-Correction
- **Strength:** Strong
- **Evidence:** The settings GUI in `pyobj/settings_window.py` actively validates user inputs against safety ranges (intervals `[5, 250]`, cash values `[10, 2000]`). If the cash-to-card ratio exceeds the **100:1 cheat limit**, it automatically scales down the cash value and raises a warning dialog.
- **Guidance:** Never fail silently or allow out-of-bound configurations to be saved to SQLite. Implement self-correcting validation logic directly in the GUI save handlers.

---

## 4. UI CSS Palette & Progressive Badging
- **Strength:** Strong
- **Evidence:** Custom components (e.g., Pokedex V2, Discovery Map) use standard, theme-adaptable CSS variables for state badges:
  - Completion/Caught: `var(--accent-green)`
  - Unlocked/Available: `var(--accent-blue)`
  - In Progress: `var(--accent-gold)`
  - Unseen/Locked: `var(--text-muted)`
- **Guidance:** Avoid ad-hoc, hardcoded hex values in styling stylesheets. Utilize Anki's native CSS palette variables to guarantee light and dark mode compatibility.

---

## 5. Nature Glyphs and Stat Indicators
- **Strength:** Strong
- **Evidence:** The PC Box details panel decorates stats based on the Pokémon's Nature using uniform indicators:
  - Boosted Stats (+10%): Green up-arrow glyph (`▲`)
  - Decreased Stats (-10%): Red down-arrow glyph (`▼`)
- **Guidance:** Stat indicators must strictly use these color and glyph standards to match general Pokemon UI expectations.

---

## 6. Case-Sensitivity & Key Lowercasing
- **Strength:** Strong
- **Evidence:** Pokedex caches, JSON datasets (`pokedex.json`), and database queries enforce lowercasing on species names, move names, and form IDs before performing dictionary lookups (e.g., `species.lower().replace("-", "")`).
- **Guidance:** Always apply lowercasing and strip hyphens before running checks against static JSON indexes to prevent lookup failures.

---

## 7. Resource Pathing
- **Strength:** Strong
- **Evidence:** `resources.py` defines `Path` objects for every directory and major file in the project (e.g., `user_path`, `database_path`).
- **Guidance:** Never hardcode file paths string literals. Always import the relevant path variable from `resources.py`.

---

## 8. SQLite Transaction Hygiene
- **Strength:** Strong
- **Evidence:** The `AnkimonDB` class wraps all raw SQLite executions in transactions, committing immediately after mutations (`conn.commit()`).
- **Guidance:** Always perform database modifications using `mw.ankimon_db.execute_query` or specialized high-level save/load helpers. Ensure transactions are committed promptly to prevent thread lockups.

---

## 9. Logging over Printing
- **Strength:** Strong
- **Evidence:** The presence of `mw.logger` (an instance of `ShowInfoLogger`) and explicit rules forbidding `print`.
- **Guidance:** Use `logger.log("info", ...)` or `logger.log_and_showinfo(...)` exclusively for debug/output. Do not use print statements.

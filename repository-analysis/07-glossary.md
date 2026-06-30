# Glossary

This document defines project-specific vocabulary, abbreviations, and architectural labels to maintain complete naming consistency across the Ankimon system.

---

## Standardized Vocabulary

### Capture Requirements
- **Definition:** The explicit list of Pokémon that a user must catch and register in the SQLite database before a target species is unlocked and allowed to spawn in wild encounters.
- **Context:** Formally replaces obsolete terms like "Prerequisites", "Capture Prerequisites", or "Gating Requirements". Used heavily in the Pokédex V2 and Discovery Map interface.

### Registry Progress
- **Definition:** The calculated completion percentage representing a player's registered collection against the total active Pokédex size.
- **Context:** Replaces terms like "Completion Status", "Caught Percentage", or "Caught Status". Displayed visually in the Pokédex sidebar and badge layouts.

### Unseen Species
- **Definition:** An entry in the Pokédex V2 Discovery Map that has not yet been registered or unlocked. Renders as a greyed-out node with custom badges.
- **Context:** Replaces terms like "Locked Pokémon" or "Not Seen".

---

## Architectural & Gameplay Terms

### Full Pool
- **Definition:** The default encounter list containing all base Pokedex species, filtered strictly by generation toggles, level floors, and active `Capture Requirements`.

### Boosted Pool
- **Definition:** A special, isolated pool populated dynamically during regional encounters (e.g. Alola setting is active). It collects regional variants and introduction generation species specific to the selected region.

### Trickle-Down Variant Replacement
- **Definition:** The post-selection replacement algorithm that rolls a `7 * n%` chance to substitute a selected base species with one of its `n` eligible regional variants defined in `REGIONAL_FORM_LOOKUP`.

### Add-on Reloader
- **Definition:** The developer-mode hot-reloader module (`reloader.py`) that teardowns active hooks, closes windows, removes menu items, and re-imports modules via `sys.modules` purging.

### Database Hot-Swap
- **Definition:** Toggling the active database file path (e.g., between `ankimon.db` and `ankimonDEV.db`) at runtime by closing the current sqlite3 connection and re-opening a connection, followed by refreshing in-memory trainer, settings, and PC objects.

### Cheat-Prevention Threshold
- **Definition:** The fair-play settings cap enforcing a maximum **100:1 cash-to-card reward ratio** (100¥ max payout per reviewed card). Enforces interval boundaries `[5, 250]` and cash boundaries `[10, 2000]`.

---

## Core Domain Terms
- **Ankimon:** The name of the add-on, a portmanteau of Anki and Pokémon.
- **Review (Flashcard Review):** The core action in Anki where a user answers a flashcard, driving the progression of the Ankimon battle engine.
- **Encounter:** When a wild Pokémon appears for the user to battle.
- **Main Pokémon / User Pokémon:** The Pokémon currently active and fighting on behalf of the user, denoted with `is_main = 1` in SQLite.
- **Enemy Pokémon / Opponent:** The wild Pokémon currently being battled. Persisted transiently in memory.
- **PC / PC Box:** The UI (`pc_box.py`) where a user views and manages their collection of captured Pokémon.
- **Item Bag:** The UI and data structure managing the user's consumable items stored in SQLite `items`.
- **poke_engine:** The battle simulation engine based on "SirSkaro's Poke-Engine".
- **STAB (Same-Type Attack Bonus):** A damage multiplier applied when a Pokémon uses a move matching its own type.
- **`aqt`:** The Anki Qt GUI module.

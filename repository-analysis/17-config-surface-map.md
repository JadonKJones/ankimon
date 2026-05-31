# Config Surface Map

This document outlines the complete configuration surface of the Ankimon add-on. All settings are persistent across sessions and deck profiles.

---

## 1. Storage and Controller

*   **Physical Config File:** `config.json` situated in the add-on package root directory.
*   **Logical Controller:** `Settings` inside `pyobj/settings.py`.
    *   Exposes a dictionary-based configuration manager.
    *   Provides safe default fallbacks using nested dictionary lookups (e.g., `settings_obj.get("battle.cards_per_round")`).
    *   Maintains safe atomic disk saves through `save_config()` to avoid config loss during system disruptions.

---

## 2. Configuration Key Registry

Below is a detailed map of all configuration parameters active in the system:

| Config Key Path | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| **Battle Mechanics** | | | |
| `battle.cards_per_round` | `int` / `str` | `2` (or range `"2-4"`) | Number of flashcard reviews required to execute one battle turn. If a range string is supplied, the system rolls a random pacing interval between those limits. |
| `battle.automatic_catch_special` | `bool` | `true` | When active, automatically catches and saves any Legendary, Mythical, Ultra, Mega, GMax, or Starter Pokémon upon defeat. |
| `battle.active_region` | `str` | `"Kanto"` | Modifies regional weighted encounters. Determines introduction pools and boosted spawn rates (e.g. `"Alola"`, `"Galar"`, `"Hisui"`). |
| `battle.level_cap` | `int` | `100` | Limits the maximum obtainable level of player and enemy Pokémon during reviews. |
| **Control Hotkeys** | | | |
| `controls.catch_key` | `str` | `"c"` | Keyboard shortcut to trigger an immediate catching attempt on the wild opponent. |
| `controls.defeat_key` | `str` | `"d"` | Keyboard shortcut to bypass battle simulation and immediately defeat the enemy. |
| `controls.key_for_opening_closing_ankimon` | `str` | `"o"` | Global shortcut to toggle the visibility HUD overlays on the reviewer screen. |
| `controls.allow_to_choose_moves` | `bool` | `false` | If active, prompts the user with a selection dialogue to pick active moves instead of selecting a random attack. |
| **Audio Configuration** | | | |
| `audio.sounds` | `bool` | `true` | Enables/Disables sound effects for items and interface interactions. |
| `audio.battle_sounds` | `bool` | `true` | Enables/Disables Pokémon cry sound effects at battle startups and turn transitions. |
| `audio.volume` | `int` | `50` | Operational volume percentage (0 to 100). |
| **Trainer Profile** | | | |
| `trainer.name` | `str` | `"Ash"` | Active username displayed on the trainer card GUI. |
| `trainer.cash` | `int` | `3000` | In-game balance used to buy shop items. |
| `trainer.daily_average` | `int` | `50` | Active review targets. Reaching this yields daily gold awards. |

---

## 3. Configuration Safety Verification

During startup, `singletons.py` reads and verifies the entire configuration dictionary:
1.  **Format Enforcements:** Keys like `volume` are parsed through validation to prevent string-to-integer conversion errors.
2.  **Backup Fallbacks:** In case of missing keys, default values from `pyobj/settings.py` are loaded, and a silent recovery save executes.

> [!TIP]
> Future additions of settings (e.g., custom themes or new regional multipliers) must be declared with appropriate fallback values in `pyobj/settings.py` so that existing users' configuration files migrate cleanly without crashes.

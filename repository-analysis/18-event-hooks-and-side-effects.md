# Event Hooks and Side Effects

This document details the interface boundary between Anki's internal hook framework and the Ankimon game lifecycle. It maps out how card reviews, profile switches, web content injection, and cloud sync actions trigger gameplay mechanics and persistent state changes.

---

## 1. Anki Hook Integration Map

Ankimon integrates tightly with Anki by registering callbacks to `aqt.gui_hooks`. The lifecycle is initialized in `__init__.py`.

```
                  ┌──────────────────────────────────────────┐
                  │          Anki Application Lifecycle      │
                  └────────────────────┬─────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
 ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
 │    Profile Loaded   │    │  Review Answered    │    │ WebView Loading UI  │
 └──────────┬──────────┘    └──────────┬──────────┘    └──────────┬──────────┘
            │                          │                          │
            ▼                          ▼                          ▼
 ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
 │register_profile_    │    │reviewer_did_answer_ │    │webview_will_set_    │
 │hooks()              │    │card                 │    │content              │
 └──────────┬──────────┘    └──────────┬──────────┘    └──────────┬──────────┘
            │                          │                          │
            ▼                          ▼                          ▼
 ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
 │• Load Database      │    │• on_review_card()   │    │• Inject HUD Portal  │
 │• Monthly Rewards    │    │• Battle Turn        │    │  (JS/CSS Asset)     │
 │• Sync Hook Register │    │• XP / Capture       │    │                     │
 └─────────────────────┘    └─────────────────────┘    └─────────────────────────────────┘
```

| `gui_hooks.profile_did_open` | `on_profile_loaded` | `profile_hooks.py` | Executed when a user profile is selected. Initiates database loads, starts the backup manager, awards monthly calendar gifts, initializes mobile review watermarks, restores the mobile menu badge, and clears the desktop session. |
| `gui_hooks.reviewer_did_answer_card` | `on_review_card` | `battle_loop.py` | Appends review counters, evaluates round intervals, processes damage simulations with `poke_engine`, triggers faint/catch actions, and records the desktop `revlog_id` for mobile sync tracking. |
| `gui_hooks.webview_will_set_content` | `on_webview_will_set_content` | `__init__.py` | Injects the Javascript bridge `ankimon_hud_portal.js` and custom CSS overlays directly into the Anki reviewer card iframe. |
| `gui_hooks.sync_did_finish` | `setup_ankimon_sync_hooks` | `pyobj/ankimon_sync.py` | Initiates database index flushing and transaction validation following an AnkiWeb cloud sync, then triggers the mobile review detection and queueing pipeline. If a developer database exists, displays `MobileReviewsRouterDialog` to let the user route reviews per deck to either the normal or developer database, updating watermarks in both databases. |

---

## 2. Independent Reviewer Callback Sequencing

> [!WARNING]
> A common point of confusion is the execution relationship inside Anki's reviewer loop.
> Both `card_hooks.py:answerCard_after()` (which tracks review times) and `__init__.py:on_review_card()` (which handles the RPG battle system) are **completely independent** callbacks registered sequentially to Anki's internal hook list.
> 
> *   They **do not** call each other directly.
> *   If one crashes, the other will still execute, unless the exception propagates and halts the hook runner.
> *   Any share of state between them (e.g. tracking review streaks) must be exchanged explicitly through singletons (`ankimon_tracker_obj`) rather than execution returns.

---

## 3. Gameplay Side Effects

### A. The Evolution / Level-up Chain
When `handle_enemy_faint()` awards experience points to `main_pokemon`:
1.  If XP overflows the requirement, `main_pokemon.level` is incremented.
2.  `evo_window.check_for_evolution()` is fired.
3.  If an evolution is met, a QDialog popup displays, updating the species data inside `captured_pokemon` upon completion.

### B. Daily/Monthly Reward Side Effects
*   **Daily Average Gold:** Reaching the threshold defined by `battle.daily_average` increments `trainer.cash` by 200, which is immediately saved to the active settings profile.
*   **Monthly Pokémon Check:** During startup, the calendar is compared against the database registry to award monthly wild specimens directly to the PC Box.

### C. HUD Updates
Mutations to health status immediately trigger callback bridges using `reviewer_obj.update_life_bar(reviewer, 0, 0)`, pushing the updated HP percentages directly to the Javascript webview overlay using `pycmd` commands.

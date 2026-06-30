# Commits on main since BRRRR_Experimental branched off

### 9dc52cd1 - Merge branch 'main' of https://github.com/h0tp-ftw/ankimon

---

### 3f6523d5 - feat: add Magby monthly challenge for July 2026

```text
assets/challenges/monthly_challenges.json | 60 +++++++++++++++++++++++++++++++
 1 file changed, 60 insertions(+)
```

---

### 7640deba - fix: resolve addon package prefix dynamically & use services registry in leaderboard (#527)

* fix: resolve addon package prefix dynamically & use services registry in leaderboard

* fix: add defensive checks for None services in leaderboard

```text
src/Ankimon/core.py                      |  6 +++++-
 src/Ankimon/pyobj/ankimon_leaderboard.py | 14 +++++++++-----
 2 files changed, 14 insertions(+), 6 deletions(-)
```

---

### 88f7222c - fix: add defensive checks for None services in leaderboard

```text
src/Ankimon/pyobj/ankimon_leaderboard.py | 7 +++++--
 1 file changed, 5 insertions(+), 2 deletions(-)
```

---

### d23734c8 - fix: resolve addon package prefix dynamically & use services registry in leaderboard

```text
src/Ankimon/core.py                      |  6 +++++-
 src/Ankimon/pyobj/ankimon_leaderboard.py | 11 ++++++-----
 2 files changed, 11 insertions(+), 6 deletions(-)
```

---

### 11ef1955 - feat: headless agent harness + aqt-free core refactor (#492)

Makes the Ankimon game core import and run **headless** (no aqt/PyQt6) so an AI agent or a plain test can play it, observe a structured event stream, profile/fuzz it, and validate features — with no Anki and no clicking.

Lands the whole stack (siblings merged into this branch first):
- **aqt-free core refactor** — `core.py` (`build_core`), `services.py` registry, `events.py` bus, `ui_port.py`; ~26 leaf modules now import without aqt.
- **Two-tier harness** (`harness/`, dev-only, never shipped): Tier-1 `Driver` (no Qt) + Tier-2 `RealDriver` (real Qt offscreen).
- **#497** fixtures, **#498** diagnostics, **#499** one-command gate + CI, **#500** settings per-key persistence, **#501** deterministic smoke_play, **#503** agent skill.
- **#506** fuzzers + feature-validation: `mega_fuzz` (do-EVERYTHING: random world × action incl. right-click; crashes + soft-errors + footprint), `feature_check`, `gui_fuzz`/`fuzz`/`move_sweep`, real `QtWebEngine`, extra gate probes, faithful-boot fidelity fixes.
- Unit suite greened; auto_battle / probe_real_play seeded to kill gate flake.

CI green: Tier-1 gate, Tier-2 (real add-on offscreen), run_integrity_tests, ruff. Found bugs (Item Shop random.sample, Pokédex leak, empty-sequence encounter path) are logged for the follow-up fix queue, not fixed here.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

```text
.claude/skills/ankimon-harness/SKILL.md            | 189 +++++++++
 .claude/skills/ankimon-harness/reference.md        | 269 ++++++++++++
 .claude/skills/validate-pr/SKILL.md                |  96 +++++
 .github/workflows/harness.yml                      |  63 +++
 .gitignore                                         |   9 +
 AGENTS.md                                          | 127 +++++-
 Makefile                                           |  19 +
 harness/README.md                                  | 354 ++++++++++++++++
 harness/__init__.py                                |  18 +
 harness/bootstrap.py                               |  80 ++++
 harness/check.py                                   | 102 +++++
 harness/checks/__init__.py                         |   1 +
 harness/checks/probe_contract.py                   | 110 +++++
 harness/checks/probe_core.py                       |  63 +++
 harness/checks/probe_fixtures.py                   |  82 ++++
 harness/checks/probe_foundations.py                |  61 +++
 harness/checks/probe_leaves.py                     |  82 ++++
 harness/checks/probe_migration.py                  | 117 ++++++
 harness/checks/probe_persistence.py                |  90 +++++
 harness/checks/probe_real_boot.py                  |  50 +++
 harness/checks/probe_real_play.py                  |  76 ++++
 harness/clock.py                                   | 100 +++++
 harness/debug.py                                   |  45 +++
 harness/diagnostics.py                             | 238 +++++++++++
 harness/driver.py                                  | 187 +++++++++
 harness/fake_aqt.py                                | 443 ++++++++++++++++++++
 harness/fakes.py                                   | 115 ++++++
 harness/fetch_sprites.py                           |  85 ++++
 harness/fixtures.py                                | 245 +++++++++++
 harness/headless_env.py                            | 147 +++++++
 harness/real_driver.py                             | 125 ++++++
 harness/real_env.py                                | 203 ++++++++++
 harness/requirements-dev.txt                       |  21 +
 harness/scenarios/__init__.py                      |   1 +
 harness/scenarios/auto_battle.py                   |  59 +++
 harness/scenarios/economy.py                       |  48 +++
 harness/scenarios/feature_check.py                 | 154 +++++++
 harness/scenarios/fuzz.py                          | 192 +++++++++
 harness/scenarios/gui_fuzz.py                      | 187 +++++++++
 harness/scenarios/hud_render.py                    | 113 ++++++
 harness/scenarios/longrun.py                       |  48 +++
 harness/scenarios/mega_fuzz.py                     | 450 +++++++++++++++++++++
 harness/scenarios/move_sweep.py                    |  95 +++++
 harness/scenarios/pc_box_moves.py                  |  95 +++++
 harness/scenarios/pokedex_render.py                |  88 ++++
 harness/scenarios/profile_battles.py               |  35 ++
 harness/scenarios/screenshots.py                   |  56 +++
 harness/scenarios/smoke_play.py                    | 106 +++++
 harness/scenarios/soak.py                          |  99 +++++
 harness/screenshot.py                              |  44 ++
 harness/server.py                                  |  94 +++++
 harness/setup_tier2.sh                             |  73 ++++
 harness/setup_webengine.sh                         |  40 ++
 harness/state.py                                   |  61 +++
 src/Ankimon/battle_loop.py                         |  67 +--
 src/Ankimon/const.py                               |  10 +-
 src/Ankimon/core.py                                | 193 +++++++++
 src/Ankimon/events.py                              | 116 ++++++
 .../functions/ankimon_hooks_to_poke_engine.py      |   7 +-
 src/Ankimon/functions/drawing_utils.py             |  39 +-
 src/Ankimon/functions/encounter_functions.py       | 128 ++++--
 src/Ankimon/functions/friendship_evolution.py      |   9 +-
 src/Ankimon/functions/pokedex_functions.py         |  34 +-
 src/Ankimon/functions/pokemon_functions.py         |   5 +-
 src/Ankimon/functions/trainer_functions.py         |   9 +-
 src/Ankimon/functions/update_main_pokemon.py       |   6 +-
 src/Ankimon/gui_presenter.py                       |  48 +++
 src/Ankimon/move_names.py                          |   4 +-
 src/Ankimon/pyobj/InfoLogger.py                    |  63 +--
 src/Ankimon/pyobj/ankimon_tracker.py               |  49 ++-
 src/Ankimon/pyobj/database_manager.py              |  28 ++
 src/Ankimon/pyobj/error_handler.py                 | 101 ++++-
 src/Ankimon/pyobj/pokemon_obj.py                   |  12 +-
 src/Ankimon/pyobj/reviewer_obj.py                  |  21 +
 src/Ankimon/pyobj/settings.py                      |  82 ++--
 src/Ankimon/pyobj/trainer_card.py                  |  31 +-
 src/Ankimon/resources.py                           |  45 ++-
 src/Ankimon/services.py                            |  94 ++++-
 src/Ankimon/singletons.py                          | 187 +++------
 src/Ankimon/ui_port.py                             |  97 +++++
 src/Ankimon/utils.py                               |  79 +++-
 tests/test_encounter_functions.py                  |   8 +
 tests/test_friendship_evolution.py                 |   4 +
 tests/test_headless_harness.py                     | 115 ++++++
 tests/test_settings_init_order.py                  |  45 ++-
 85 files changed, 7467 insertions(+), 419 deletions(-)
```

---

### 2707309c - fix: distinguish bool from int in SettingsWindow save + change detection (#396)

Rebased onto current main (the original #396 conflicted after the cash-reward /
friendship-evo changes shifted these lines).

- on_save: use type(x) is int/float instead of isinstance — bool subclasses int,
  so a boolean setting was being handled by the int branch.
- radio toggles: give the buttons explicit ids and read checkedId() == 1 (also
  avoids AttributeError when nothing is checked) instead of matching button text.
- changed_settings: also flag a change when only the type differs (True vs 1
  compare equal), so e.g. 'Cards per Round = 1' saves correctly.

```text
src/Ankimon/pyobj/settings_window.py | 15 +++++++++------
 1 file changed, 9 insertions(+), 6 deletions(-)
```

---

### afc82416 - fix: start Discord Rich Presence on the first review session (#491)

* fix: start Discord Rich Presence correctly on first review session

The initial Ankimon presence check skipped the first review session because the default object state for `loop` was manually set to `True`, which effectively negated the start routine check when reviewing the first card upon launching Anki.

This fix sets the initial background worker check state `loop` to `False` in the `DiscordPresence` class, and adds proper checking logic with `hasattr` to correctly boot up the Discord rich presence object upon launching the first review. Finally, it cleans up a forgotten hook implementation for `reviewer_will_end` to actually use the corresponding hooked function `on_reviewer_will_end`, fixing the presence reset loop on consecutive review sessions.


* fix: start Discord Rich Presence correctly on first review session

The initial Ankimon presence check skipped the first review session because the default object state for `loop` was manually set to `True`, which effectively negated the start routine check when reviewing the first card upon launching Anki.

This fix sets the initial background worker check state `loop` to `False` in the `DiscordPresence` class, and adds proper checking logic with `hasattr` to correctly boot up the Discord rich presence object upon launching the first review. Finally, it cleans up a forgotten hook implementation for `reviewer_will_end` to actually use the corresponding hooked function `on_reviewer_will_end`, fixing the presence reset loop on consecutive review sessions.


* fix: safely initialize loop state before RPC connection


---------

```text
src/Ankimon/discord_integration.py        | 9 +++------
 src/Ankimon/functions/discord_function.py | 2 +-
 2 files changed, 4 insertions(+), 7 deletions(-)
```

---

### 3901bf31 - fix: run the profile-open connectivity re-check off the GUI thread (#455)

* fix: perform fresh connectivity check when opening profile

Previously, the Ankimon sync system and monthly reward check relied
on a one-shot internet connectivity check evaluated during startup. If
the app launched while offline but the user connected shortly after,
these features remained disabled for the entire session.

This commit modifies `_on_profile_did_open` in `src/Ankimon/profile_hooks.py`
to perform a fresh `test_online_connectivity()` check if the initial
`online_connectivity` state is False, ensuring the sync system and rewards
are initialized if a connection is established before a profile is opened.


* fix: run connectivity check in background task

Refactors the fresh connectivity check on profile open to run
using `mw.taskman.run_in_background`. This prevents the synchronous
`requests.get` call inside `test_online_connectivity` from blocking
Anki's GUI thread and freezing the app on offline machines. The
monthly reward check and sync initialization are moved to the
`on_done` callback.


---------

```text
src/Ankimon/profile_hooks.py | 74 +++++++++++++++++++++++++-------------------
 1 file changed, 43 insertions(+), 31 deletions(-)
```

---

### bacddde5 - feat: detailed local-vs-remote DB comparison in the sync dialog (#490)

* feat: add detailed database comparison to sync dialog

* fix(sync): read trainer info from config table + guarantee DB connection closes

get_db_stats read trainer name/level/cash from user_data, but trainer info lives
in the config table (flat dotted key/value); user_data holds rate_this etc. — so
those fields always showed N/A/1/0. Switch to config. Also wrap the sqlite
connection in a finally so it can't leak on a query error (Gemini high-pri). Same
fix pair as #452.


---------

```text
src/Ankimon/pyobj/ankimon_sync.py | 97 ++++++++++++++++++++++++++++++++++-----
 1 file changed, 86 insertions(+), 11 deletions(-)
```

---

### 5373ca7b - feat: implement minimumDefeated evolution condition for Pawmo/Rellor (#458)

* JULES-INJECTION-OK\n\nFeature: Implement 'minimumDefeated' evolution condition for Pawmo\n\nUpdated `pokedex.json` to change the evolution condition for Pawmot from a Let's Go walking requirement to the `minimumDefeated` condition (100). Implemented logic in `pokedex_functions.py`'s `check_evolution_for_pokemon` to evaluate this condition by reading the `pokemon_defeated` stat from a `PokemonObject` loaded via `ankimon_db`.


* JULES-INJECTION-OK\n\nFeature: Implement 'minimumDefeated' evolution condition for Pawmo\n\nMoved `minimumdefeated` check outside `min_level > 0` condition block. Evaluates `(pokemon_obj.pokemon_defeated or 0) >= evo_defeated` defensively against `TypeError`.


---------

```text
src/Ankimon/data_files/pokedex.json        |  6 ++++--
 src/Ankimon/functions/pokedex_functions.py | 18 +++++++++++++++++-
 2 files changed, 21 insertions(+), 3 deletions(-)
```

---

### 1eede42e - fix: make the in-app updater safe on git clones (ff-only) + PR-install warning + hide pre-v2.0 releases (#440)

* fix: make the in-app updater safe on git clones (ff-only) + PR-install warning + hide pre-v2.0 releases

Git-guard core, split out from the original #440 — the recovery-mode __init__.py
wrapper is deferred to a separate change (it now overlaps #437's __init__ work).

- update_manager: is_git_clone()/_git_repo_root() detection; apply_update() hard-
  refuses on a git clone (the code that does the deleting) and cleans up the
  download; safe git_pull_ff_only() path; 'Holy Ground' user_files/ preserve
  guard; pre-v2.0 release/tag filter (older builds predate the updater).
- menu_buttons: on a clone, swap the destructive updater for a safe
  'Update Ankimon (git pull)' menu item.
- update_dialog: dev-tab clone warning + a PR-install 'unreviewed code' warning.
- en_text: add the missing ankimon_update_button label.
- tests: cover is_git_clone, apply_update refuse-and-cleanup, git_pull_ff_only,
  and the pre-v2.0 version filter.


* test: restore sys.modules after loading update_manager (don't pollute siblings)

The collection-time load rebuilt sys.modules['Ankimon']/['Ankimon.pyobj'] (and
stubbed aqt), which leaked into the session and broke test_addon_integrity's import
walk (tip_of_the_day -> NameError: QDialog). Snapshot + restore the touched keys in
a finally; the returned module object stays valid for the tests.


---------

```text
src/Ankimon/lang/en_text.json       |   1 +
 src/Ankimon/menu_buttons.py         |  50 +++++++--
 src/Ankimon/pyobj/update_dialog.py  |  28 ++++-
 src/Ankimon/pyobj/update_manager.py | 152 ++++++++++++++++++++++++++-
 tests/test_update_manager.py        | 204 ++++++++++++++++++++++++++++++++++++
 5 files changed, 420 insertions(+), 15 deletions(-)
```

---

### dba7bbd3 - fix: backup summary reads the backup's own ankimon.db, not the live DB (#452)

_generate_summary used the live mw.ankimon_db, so every backup's summary showed
*current* stats instead of that backup's historical data. Read backup_dir/ankimon.db
directly instead:
- pokemon/item counts + main pokemon from the backup's own DB
- connection wrapped in contextlib.closing (no leak on query error)
- trainer info read from the config table's flat key/value rows
  (key='trainer.name', ...), guarded on the table existing

Reworked from #452: dropped its read_github_file change (superseded by #489 and
would re-break it) and the per-review battle_loop query (unnecessary); corrected
the config-table read (config is key/value, not a nested data blob).

```text
src/Ankimon/pyobj/backup_manager.py | 70 +++++++++++++++++++++++++++----------
 1 file changed, 52 insertions(+), 18 deletions(-)
```

---

### 226ebaf6 - fix: monthly-challenge shiny-eligibility crash + rate_this/threshold hardening (#483)

* Fix crash and bugs related to Monthly Challenge check

- Added null check in pokemon_trade.py when validating previous monthly challenge status
- Fixed rate_this value checking to support both boolean and legacy string format
- Updated rate_this migration in database_manager.py to properly store a boolean
- Created test suite tests/test_monthly_challenge_fixes.py ensuring regressions don't occur


* fix(monthly): harden migration + threshold check per review

Folds in the two valid Gemini findings:
- migration: only treat rate_this as rated for True/'true' — a legacy string
  'false' is truthy and would wrongly migrate the user to rated.
- shiny check: int-coerce pokemon_defeated and threshold (threshold comes from
  remote JSON and could be a string -> TypeError on >=). None-guard stays first
  so a missing previous-challenge Pokémon still cannot crash.


---------

```text
src/Ankimon/pyobj/database_manager.py |   4 +-
 src/Ankimon/pyobj/pokemon_trade.py    |  13 ++-
 tests/test_monthly_challenge_fixes.py | 194 ++++++++++++++++++++++++++++++++++
 3 files changed, 205 insertions(+), 6 deletions(-)
```

---

### 92b6a272 - feat: add search and sorting to the Pokémon team-selection dialog (#387)

* Add search and sorting to Pokémon team selection

**Problem:** With a large Pokédex, finding the right Pokémon for your team
was tedious as the list had no organization or search functionality.

**Solution:** Enhanced the Pokémon selection dialog with:
- Text search by Pokémon name (real-time filtering)
- Sort options: by Name (A-Z), Level (High-Low), or Pokédex ID
- Live preview of selected Pokémon sprite
- Improved dialog layout with better UX

* Update pokemon_team_window.py

* chore(team-select): remove debug prints from CP calc

Strip the leftover `print(...)` debug statements and the `traceback.print_exc()`
from `_calculate_pokemon_cp`; route the exception to the quiet logger instead of
the console. No behaviour change to the search/sort/CP feature.


---------

```text
src/Ankimon/gui_classes/pokemon_team_window.py | 301 +++++++++++++++++++++----
 1 file changed, 253 insertions(+), 48 deletions(-)
```

---

### 7846dcfc - fix: migrate legacy string items/badges + backfill missing individual_ids (#470)

* fix: resolve migration failures for plain string items and missing individual_ids

- Adds `uuid` generation during JSON-to-SQLite migration for any legacy Pokémon records (in `mypokemon.json`, `mainpokemon.json`, and `team.json`) lacking an `individual_id`.
- Modifies `items.json` migration logic to gracefully handle items stored as plain strings instead of dictionaries by defaulting their quantity to 1.


* fix: Additional defensive fixes if non-dict encountered


* migration: handle legacy string badges + harden individual_id backfill

Absorbs the one unique fix from #471 so #470 is the single complete
migration fix for the legacy JSON -> SQLite path:

- badges loop: accept bare-string badge entries. Previously a string
  badge fell into the dict 'else' branch and crashed on .get(); now
  (int, str) are handled together and any other type is skipped via
  'else: continue'.
- pokemon/main/team: backfill a UUID when individual_id is missing OR
  present-but-empty (not x.get('individual_id') instead of
  'individual_id' not in x), since save_pokemon/save_main_pokemon reject
  records with a falsy individual_id.


---------

```text
src/Ankimon/pyobj/migration_dialog.py | 45 +++++++++++++++++++++++++++--------
 1 file changed, 35 insertions(+), 10 deletions(-)
```

---

### cb4f6fe3 - FIX Issue #398 (Implement Macho Brace & Power Item EV Scaling) (#421)

* Implement Macho Brace & Power Item EV Scaling (#398)

This PR addresses issue #398 by implementing the EV-scaling mechanics for held items (Macho Brace and Power Items)

1. EV Scaling Mechanics (Issue #398)
We updated the EV yield logic when defeating wild Pokémon:

Macho Brace: Doubles all EV gains from the defeated Pokémon.
Power Items (power-weight, power-bracer, etc.): Adds +8 to the corresponding EV stat (HP, Attack, Defense, Special Attack, Special Defense, Speed) of the user's active Pokémon.
Compatibility & Safety: Handled both short stat keys (atk, spa, etc.) and full stat names (attack, special-attack, etc.) dynamically, passing the final yields to limit_ev_yield to enforce standard caps (max 252 per stat, max 510 total).
2. Held Item Memory Sync Bug Fix
During testing, we discovered that equipping a held item via the Bag UI (item_window.py) only updated the SQLite database. The active, in-memory main_pokemon singleton object remained unaffected, meaning its held_item attribute stayed None. When battle results calculated EVs:

It read held_item = main_pokemon.held_item (which was None).
The EV boost was bypassed, awarding only the base EV yield.
The normal EVs were written back to the database, overwriting any expected progress.
Resolved by:

Updating item_window.py to immediately sync self.main_pokemon.held_item in memory when equipping items.
Modifying encounter_functions.py to fetch held_item dynamically from the freshly loaded database record (mainpkmndata.get("held_item")) as a secondary defensive fallback.

* Gemini comments implemented

```text
src/Ankimon/functions/encounter_functions.py | 34 +++++++++++++++++++++++++++-
 src/Ankimon/pyobj/item_window.py             |  5 ++++
 2 files changed, 38 insertions(+), 1 deletion(-)
```

---

### 187a7fe4 - Fix `ValueError` unpacking return value from `read_github_file` (#489)

* Fix `ValueError` by removing tuple unpacking from `read_github_file` return.

The `read_github_file` utility returns a single string or `None`. Unpacking the result as a tuple caused a `ValueError` in `src/Ankimon/pyobj/help_window.py` and `src/Ankimon/gui_entities.py`. This commit corrects the variable assignments to handle the single return value and appropriately uses it as the HTML content.


* fix(help): fall back to cached local copy when GitHub fetch fails

Addresses the Gemini review note: after the unpacking fix, an online help-window
open where read_github_file() returns None (GitHub down / rate-limited) left
html_content blank, ignoring a valid local cache. Add an elif to use local_content
in that case.


---------

```text
src/Ankimon/gui_entities.py      | 9 ++++++---
 src/Ankimon/pyobj/help_window.py | 9 ++++++---
 2 files changed, 12 insertions(+), 6 deletions(-)
```

---

### 454bdd98 - Merge pull request #437 from h0tp-ftw/refactor/service-registry

refactor: aqt-free service registry to decouple addon logic from mw

---

### 25a26723 - Merge branch 'main' of https://github.com/h0tp-ftw/ankimon

---

### 5e5b2ee3 - fix: update softprops/action-gh-release to v3 for fixing "finalize" API call

```text
.github/workflows/main.yml | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### f042c685 - Merge pull request #488 from h0tp-ftw/jules-release-2-03-11149299497305860627

🚀 Release v2.03

---

### 4036cf42 - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 473aa2bf - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 7c01b04d - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 9c7cdbad - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### b28ffdfd - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### c1e76631 - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### dbb158a2 - 🚀 Release v2.03

---

### f6fbbc79 - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 2909d6d0 - 🚀 Release v2.03

```text
assets/changelogs/2.03.md | 251 ++++++++++++++++++++++++++++++++++++++++++++++
 src/Ankimon/manifest.json |   2 +-
 2 files changed, 252 insertions(+), 1 deletion(-)
```

---

### 9d8cd891 - Merge branch 'main' of https://github.com/h0tp-ftw/ankimon

---

### 955ffead - fix: trainer cash reward amount and interval scaled properly

```text
src/Ankimon/config.json       | 2 +-
 src/Ankimon/pyobj/settings.py | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

---

### 1bf04d60 - Merge pull request #487 from h0tp-ftw/jules-fix-migration-fresh-install-11601256179668073970

fix: bypass data migration dialog on fresh installs

---

### 8fddaac3 - fix: bypass data migration dialog on fresh installs

On a fresh installation, the `show_migration_dialog_if_needed` function
would trigger because `db.is_migrated()` returned False, despite there
being no legacy JSON files to migrate.

This patch updates the function to explicitly check for the presence of
legacy JSON data files (`mypokemon_path`, `mainpokemon_path`, etc.).
If no legacy files exist, it marks the database as migrated and silently
bypasses the dialog, preventing unnecessary friction for new users.

```text
src/Ankimon/pyobj/migration_dialog.py | 18 ++++++++++++++++++
 1 file changed, 18 insertions(+)
```

---

### 2a1f4d47 - Merge pull request #468 from h0tp-ftw/dev-setup

feat: add CONTRIBUTING.md and dev setup

---

### 1b1c16b0 - Update setup.py

```text
setup.py | 2 ++
 1 file changed, 2 insertions(+)
```

---

### 374d6379 - Update setup.py

```text
setup.py | 2 --
 1 file changed, 2 deletions(-)
```

---

### deb5e148 - Update setup.py

```text
setup.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### c954d21b - fix: changes to AGENTS.md to prevent repetitive testing and verbose output

```text
AGENTS.md | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)
```

---

### e760c08b - monthly challenge for June 2026

```text
assets/challenges/monthly_challenges.json | 61 +++++++++++++++++++++++++++++++
 1 file changed, 61 insertions(+)
```

---

### 6f91d9ab - Merge branch 'main' of https://github.com/h0tp-ftw/ankimon

---

### 211e9cd0 - fix: fix token and allow manual dispatch for new addon release

```text
.github/workflows/auto-tag-release.yml | 1 +
 .github/workflows/main.yml             | 1 +
 2 files changed, 2 insertions(+)
```

---

### 9bcb0224 - Merge pull request #475 from h0tp-ftw/release/2.02-E-17931330139798208634

🚀 Release v2.02-E

---

### 8a56889b - chore: update release scripts and templates for nicknames

```text
.github/jules/checklist.md      | 2 +-
 .github/jules/release-prompt.md | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

---

### 7643c1e4 - chore: revert readme usernames

```text
.all-contributorsrc | 4 ++--
 README.md           | 4 ++--
 2 files changed, 4 insertions(+), 4 deletions(-)
```

---

### 569d2ee8 - chore: update contributor details

```text
.all-contributorsrc         | 12 ++++++------
 README.md                   |  4 ++--
 assets/changelogs/2.02-E.md |  4 ++--
 3 files changed, 10 insertions(+), 10 deletions(-)
```

---

### e84fd7ac - chore: release v2.02-E

---

### 6ba7a7ee - chore: release v2.02-E

```text
assets/changelogs/2.02-E.md | 31 +++++++++++++++++++++++++++++++
 src/Ankimon/manifest.json   |  2 +-
 2 files changed, 32 insertions(+), 1 deletion(-)
```

---

### f24c8910 - Merge pull request #383 from hakimh2/1.52E_Trainer-Cash

feat: More Configurations for Trainer Cash Earnings with 400¥ Daily Cap

---

### 26b18307 - fix: add zero-division defense and try-except coercion for cash reward config

```text
src/Ankimon/battle_loop.py           | 10 +++++++---
 src/Ankimon/pyobj/settings_window.py | 16 +++++++++++-----
 2 files changed, 18 insertions(+), 8 deletions(-)
```

---

### 45bac145 - docs: clarify daily cap of 400 in cash reward interval description

```text
src/Ankimon/lang/setting_description.json | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### e4f84c15 - feat: enforce 400 daily cash cap and adjust settings bounds to conservative ranges

```text
.gitignore                                |  1 +
 src/Ankimon/battle_loop.py                | 17 +++++++++++++++--
 src/Ankimon/config.json                   |  4 +++-
 src/Ankimon/lang/setting_description.json |  4 ++--
 src/Ankimon/pyobj/settings.py             |  5 +++++
 src/Ankimon/pyobj/settings_window.py      |  8 ++++----
 6 files changed, 30 insertions(+), 9 deletions(-)
```

---

### c1f70f0e - Merge branch 'origin/main' into 1.52E_Trainer-Cash

---

### a945021b - feat: enforce maximum daily economy limit for trainer cash reward amount

```text
src/Ankimon/lang/setting_description.json | 2 +-
 src/Ankimon/pyobj/settings_window.py      | 8 +++++---
 2 files changed, 6 insertions(+), 4 deletions(-)
```

---

### 1056465b - feat: add CONTRIBUTING.md with info

```text
CONTRIBUTING.md | 215 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 215 insertions(+)
```

---

### d7650adb - feat: setup.py for dev setup

```text
setup.py | 336 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 336 insertions(+)
```

---

### ba914100 - fix: requirements.txt updated

```text
requirements.txt | 13 +++----------
 1 file changed, 3 insertions(+), 10 deletions(-)
```

---

### 266b3a4e - chore: add venv/ to gitignore

```text
.gitignore | 1 +
 1 file changed, 1 insertion(+)
```

---

### 8305a59b - Merge pull request #406 from hakimh2/1.52E_PerformanceFix2

perf: implement O(1) in-memory cached CSV lookups and resolve friendship evolution disk I/O conflicts

---

### 6e7b642a - fix: resolve ModuleNotFoundError on friendship_evolution in check_evolution_for_pokemon

```text
src/Ankimon/functions/pokedex_functions.py | 59 +++++++++++++++++++++++++-----
 1 file changed, 50 insertions(+), 9 deletions(-)
```

---

### 15ba477a - perf: align caching with BRRRR_Experimental and restore main comments (#406)

```text
src/Ankimon/business.py                      |  15 -
 src/Ankimon/functions/encounter_functions.py |  12 +-
 src/Ankimon/functions/learnset_retrieval.py  |  57 ++-
 src/Ankimon/functions/pokedex_functions.py   | 715 +++++++++++++++++++--------
 src/Ankimon/functions/pokemon_functions.py   |  57 ++-
 src/Ankimon/pyobj/reviewer_obj.py            |  12 +-
 6 files changed, 609 insertions(+), 259 deletions(-)
```

---

### 2463756f - fix: restore full file integrity and fix JS escaping in reviewer_obj

```text
src/Ankimon/business.py                      |  15 +
 src/Ankimon/functions/encounter_functions.py |  33 +-
 src/Ankimon/functions/learnset_retrieval.py  |  82 ++---
 src/Ankimon/functions/pokedex_functions.py   | 531 ++++++++++++---------------
 src/Ankimon/functions/pokemon_functions.py   |  51 +--
 src/Ankimon/pyobj/reviewer_obj.py            |  12 +-
 6 files changed, 349 insertions(+), 375 deletions(-)
```

---

### 993a0510 - Merge pull request #445 from scotej/feat/friendship-time-evolution

feat: friendship & time-of-day evolution (UI, BFF, sorting, evolve hardening)

---

### dd2339d7 - Update src/Ankimon/functions/pokedex_functions.py

```text
src/Ankimon/functions/pokedex_functions.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### ffc478f3 - Merge pull request #401 from h0tp-ftw/fix-pokemon-generation-hang-7642916372204178686

Fix Pokemon generation infinite loop

---

### e6880ad4 - style: lean docstrings + clearer names in friendship_evolution.py

Applying @h0tp-ftw's review preferences to this PR's own code:
- Rename cryptic locals tod -> time_of_day and pid -> species_id
  ("unintuitive name, easy to typo").
- Trim the remaining verbose docstrings, keeping Args/Returns where they earn
  their place and cutting redundant prose ("holy docstring").

No behaviour change; 53 tests still pass.

```text
src/Ankimon/functions/friendship_evolution.py | 145 ++++++++------------------
 1 file changed, 46 insertions(+), 99 deletions(-)
```

---

### f40596c9 - Merge pull request #405 from h0tp-ftw/fix-pecharunt-tier-14366677515708447049

fix: Update Pecharunt to Mythical tier

---

### b3653c29 - refactor: address PR review — clearer name, leaner docstrings, drop README bullet

Per @h0tp-ftw's inline review on #445:
- Rename the cryptic fevo_id / fevo_name to friendship_evo_id /
  friendship_evo_name in the encounter + XP-share paths ("unintuitive name,
  easy to typo").
- Condense the friendship_evolution.py module docstring and the most verbose
  function docstrings ("holy docstring").
- Drop the README "Friendship & Evolution" feature bullet (suggested change).

```text
README.md                                     |   1 -
 src/Ankimon/functions/encounter_functions.py  |  10 +--
 src/Ankimon/functions/friendship_evolution.py | 104 +++++++++-----------------
 src/Ankimon/functions/trainer_functions.py    |  10 +--
 4 files changed, 44 insertions(+), 81 deletions(-)
```

---

### 9e907a0e - docs: drop 2.02-E changelog; credit @AIbrahimv2 for the evolution fix

Removes the standalone changelog file per the maintainer's request; the
feature stays documented in the README feature list.

The evolution_window.py fix in this PR — replacing the undefined
search_pokeapi_db_by_id() calls with get_growth_rate()/get_base_experience()
— was originally authored by @AIbrahimv2 in h0tp-ftw/ankimon#444. Crediting
him as co-author since this PR supersedes that work.

```text
assets/changelogs/2.02-E.md | 33 ---------------------------------
 1 file changed, 33 deletions(-)
```

---

### 711d38fe - fix: refresh PC on reopen and guard XP-share evolution name lookup

- pc_box.py: showEvent now re-renders the grid so the day/night clock,
  BFF heart, and time-gated evolution badges are current on reopen rather
  than frozen at the last battle's render. Previously showEvent only armed
  the BFF dirty flag and nothing refreshed on .show(), so the time-of-day
  feature could display a stale hour and misreport evolution readiness.
- trainer_functions.py: None-guard return_name_for_id() in the XP-Share
  level-evolution message, matching the other four evolution sites
  (latent AttributeError on a missing-name data gap).

```text
src/Ankimon/functions/trainer_functions.py |  7 ++++++-
 src/Ankimon/pyobj/pc_box.py                | 10 +++++++---
 2 files changed, 13 insertions(+), 4 deletions(-)
```

---

### 29b0af5a - Update src/Ankimon/functions/pokedex_functions.py

```text
src/Ankimon/functions/pokedex_functions.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 76c00b64 - docs: note friendship/evolution feature + add v2.02-E changelog

- README: add a "Friendship & Evolution" feature entry.
- assets/changelogs/2.02-E.md: changelog covering the friendship/time-evolution
  feature and the folded-in bug fixes (#402, #410, #412, #438, #446).

```text
README.md                   |  1 +
 assets/changelogs/2.02-E.md | 33 +++++++++++++++++++++++++++++++++
 2 files changed, 34 insertions(+)
```

---

### 7ea44d73 - fix: fold in assorted evolution & battle bug fixes

Consolidates several in-flight fixes that overlap this PR's evolution/battle
code, so they can be closed as superseded.

- XP-Share no longer crashes when its target is released, traded, or missing
  from the DB: xp_share_gain_exp guards against a None target and clears the
  dangling trainer.xp_share setting; release (PokemonFree) and trade
  (replace_pokemon) clear it proactively. (supersedes #438, #446)
- Leveling no longer raises NameError once the main Pokémon hits level 100 with
  the level cap on — level_cap is now always defined. (supersedes #402)
- Trade-with-held-item evolutions are recognised, and their items surface as
  usable evolution items: Steelix, Scizor, Kingdra, Politoed, Slowking,
  Huntail/Gorebyss, the Porygon line, etc. (supersedes #412)
- Swapping the active Pokémon no longer loses in-memory XP/friendship — the
  outgoing main is persisted from the live object, not the stale DB copy.
  (supersedes #410)

```text
src/Ankimon/functions/encounter_functions.py |  5 +++
 src/Ankimon/functions/pokedex_functions.py   | 53 +++++++++++++++++++++-------
 src/Ankimon/functions/trainer_functions.py   | 11 ++++++
 src/Ankimon/gui_classes/pokemon_details.py   |  8 +++++
 src/Ankimon/pyobj/collection_dialog.py       | 12 ++++---
 src/Ankimon/pyobj/item_window.py             | 14 ++++++--
 src/Ankimon/pyobj/pokemon_trade.py           |  8 +++++
 7 files changed, 93 insertions(+), 18 deletions(-)
```

---

### ebcf74bb - feat: friendship/evolution UI — BFF, badges, sort, Evolve-now, settings

Surface the mechanic in the collection PC and details panel, and add the
settings that control it.

- pyobj/pc_box.py: hot-pink BFF highlight (+ heart) for the highest-friendship
  Pokémon (cached, recomputed only on data changes); a "ready to evolve" badge
  and a "waiting for day/night" badge with tooltips; a day/night header label;
  and a Friendship sort option.
- gui_classes/pokemon_details.py: friendship stat + bar (marked once the
  requirement is met) and a contextual "Evolve into X now" button / requirement
  line.
- pyobj/settings_window.py + lang/setting_name.json + setting_description.json:
  a "Friendship & Time Evolution" master toggle that gates all friendship UI,
  plus "Auto-detect Time Zone" and "Time Zone UTC Offset" for the day/night cycle.

```text
src/Ankimon/gui_classes/pokemon_details.py | 122 +++++++++++++-
 src/Ankimon/lang/setting_description.json  |   4 +
 src/Ankimon/lang/setting_name.json         |   4 +
 src/Ankimon/pyobj/pc_box.py                | 256 +++++++++++++++++++++++++++--
 src/Ankimon/pyobj/settings_window.py       |   3 +
 5 files changed, 364 insertions(+), 25 deletions(-)
```

---

### 3dcbe67b - fix: harden the evolution window and attack dialog

Make the evolve flow safe for the new manual/auto friendship triggers and fix
pre-existing evolution crashes.

- pyobj/evolution_window.py: guard against double-evolution (re-evolving an
  already-evolved Pokémon); recompute CP from the evolved base stats; carry a
  custom nickname across evolution; reset the soft `evolution_rejected` flag on
  a successful evolve and set it (instead of acting like an Everstone) on
  cancel, so a declined Pokémon can still be evolved later; refresh the open
  details panel; add a Close button to the celebration screen; repair the
  error handlers (fixes the #442 evolve crash). Use the existing
  `replaced_attack` translation key for the post-evolution move-replace message
  (the old `replaced_selected_attack` key was absent from every locale, so the
  message surfaced its raw key).
- pyobj/attack_dialog.py: show readable move names (e.g. "Quick Attack") while
  still returning the raw move id to callers.

```text
src/Ankimon/pyobj/attack_dialog.py    | 24 ++++++++++---
 src/Ankimon/pyobj/evolution_window.py | 66 +++++++++++++++++++++++++++++------
 2 files changed, 74 insertions(+), 16 deletions(-)
```

---

### 47250646 - feat: friendship & time-of-day evolution engine

Turn the dormant `friendship` stat into a real mechanic — the core logic,
auto-prompt wiring, and tests. No data files change; the friendship/time data
already lives in pokemon_evolution.csv.

- New functions/friendship_evolution.py: single source of truth
  (evolution_readiness) for both friendship- and level-method evolutions, a
  day/night clock (system time or a configurable fixed UTC offset), per-species
  lookups (lru-cached, immutable NamedTuples), and
  check_friendship_evolution_for_pokemon().
- Read every CSV row per evolved species so multi-method evolutions like
  Eevee -> Sylveon aren't dropped by a first-match read; scope friendship
  evolution to species that evolve purely by friendship (the lone dual-route
  species, Meowth -> Persian, keeps its classic level-up evolution).
- Friendship is uncapped; friendship/level/id values read from the DB are
  coerced None-/type-safely.
- pyobj/pokemon_obj.py: add the soft `evolution_rejected` flag (ctor + to_dict).
- pyobj/settings.py: defaults for the five evolution.* keys.
- functions/pokedex_functions.py: add rows_for_key_in_table; int-coerce
  get_growth_rate/get_base_experience; thread evolution_rejected through
  check_evolution_for_pokemon; repair return_name_for_id's error handler.
- functions/encounter_functions.py, trainer_functions.py: prompt a friendship
  evolution after a defeat / XP-share without double-prompting the level path;
  None-safe evolved-name lookups.
- lang/*_text.json: localized "ready to evolve" message (+ sync missing cp/bp
  labels across locales).
- tests/test_friendship_evolution.py: 118 tests (readiness, day/night + timezone
  math, multi-row CSV, dual-route scoping, coercion, auto-prompt wiring).

```text
src/Ankimon/functions/encounter_functions.py  |  44 +-
 src/Ankimon/functions/friendship_evolution.py | 686 ++++++++++++++++++++++++++
 src/Ankimon/functions/pokedex_functions.py    |  58 ++-
 src/Ankimon/functions/trainer_functions.py    |  33 +-
 src/Ankimon/lang/ch_text.json                 |   7 +-
 src/Ankimon/lang/cz_text.json                 |   7 +-
 src/Ankimon/lang/de_text.json                 |   7 +-
 src/Ankimon/lang/en_text.json                 |   1 +
 src/Ankimon/lang/es_latam_text.json           |   7 +-
 src/Ankimon/lang/fr_text.json                 |   7 +-
 src/Ankimon/lang/it_text.json                 |   7 +-
 src/Ankimon/lang/jp_text.json                 |   7 +-
 src/Ankimon/lang/kr_text.json                 |   7 +-
 src/Ankimon/lang/po_text.json                 |   7 +-
 src/Ankimon/lang/sp_text.json                 |   7 +-
 src/Ankimon/pyobj/pokemon_obj.py              |   3 +
 src/Ankimon/pyobj/settings.py                 |   5 +
 tests/test_friendship_evolution.py            | 654 ++++++++++++++++++++++++
 18 files changed, 1536 insertions(+), 18 deletions(-)
```

---

### d975199d - refactor: migrate migration.py off mw onto services registry

migration.py now reads services.logger instead of mw.logger and no longer
imports aqt at module level. Its only Anki touch (showWarning, 2 calls) is
lazy-imported inside the fix path, so all skip-path logic is testable with
zero Anki. Adds tests/test_migration.py (4 tests). Full suite: 78 passed.

```text
src/Ankimon/functions/migration.py | 24 +++++-----
 tests/test_migration.py            | 98 ++++++++++++++++++++++++++++++++++++++
 2 files changed, 111 insertions(+), 11 deletions(-)
```

---

### 8fdfb9de - refactor: migrate sprite_functions off mw onto services registry

sprite_functions.py now reads services.logger instead of mw.logger and no
longer imports aqt at all (its only Anki dependency was `from aqt import mw`).
Behavior is unchanged -- services.logger is the same logger object singletons
populates. Adds tests/test_sprite_functions.py (3 tests) covering path
resolution, gender fallback, and the substitute fallback, with zero Anki mocking.

Part of the mw-decoupling effort (follows badges_functions). Full suite: 74 passed.

```text
src/Ankimon/functions/sprite_functions.py | 11 +++---
 tests/test_sprite_functions.py            | 59 +++++++++++++++++++++++++++++++
 2 files changed, 64 insertions(+), 6 deletions(-)
```

---

### fd691010 - refactor: add aqt-free service registry; migrate badges_functions off mw

Introduce src/Ankimon/services.py -- a registry that holds the addon's own
services (db, logger, settings, translator) and does NOT import aqt. This is
the seam that lets the addon's logic be tested without an Anki runtime,
replacing the pattern of parking services on Anki's mw global.

- services.py: registry singleton with populate()/reset(); zero aqt/anki imports
- singletons.py: populate the registry once at the composition root; keep the
  mw.X writes as labeled back-compat shims
- __init__.py: drop the duplicate mw.X writes (singletons already sets them);
  keep the mw.translator re-point that compensates for menu_buttons.py:45 so
  mw.translator stays identical to services.translator
- functions/badges_functions.py: read services.db instead of mw.ankimon_db
  (now imports zero aqt)
- tests/test_badges_functions.py: 6 tests exercising it with no Anki mocking

Phase 0 (the seam). Remaining functions/ modules migrate file-by-file with the
same recipe. Full suite: 71 passed.

```text
src/Ankimon/__init__.py                   |  11 ++--
 src/Ankimon/functions/badges_functions.py |   6 +-
 src/Ankimon/services.py                   |  91 ++++++++++++++++++++++++++
 src/Ankimon/singletons.py                 |  19 +++++-
 tests/test_badges_functions.py            | 105 ++++++++++++++++++++++++++++++
 5 files changed, 224 insertions(+), 8 deletions(-)
```

---

### 08d48f2e - Move Pecharunt to Mythical tier in POKEMON_TIERS

- Removed Pecharunt (ID 1025) from the Legendary list.
- Added Pecharunt (ID 1025) to the Mythical list in `src/Ankimon/resources.py`.

```text
src/Ankimon/resources.py | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)
```

---

### f3e16c1b - Fix infinite loop in pokemon generation when all gens are disabled

- Added a 500 loop fallback limit to `generate_random_pokemon` defaulting to Rattata.
- Modified `settings_window.py` to prevent disabling all generations via UI and revert the change to the original configuration if attempted.

```text
src/Ankimon/functions/encounter_functions.py | 12 ++++++++++++
 src/Ankimon/pyobj/settings_window.py         | 18 ++++++++++++++++++
 2 files changed, 30 insertions(+)
```

---

### 1329e475 - Update settings_window.py

While the settings window is open, the config might change dynamically (e.g., trainer cash increases from battles). If you use stale self.config (loaded when window opened), you'd overwrite those dynamic changes. this assures that the earned cash isnt lost

```text
src/Ankimon/pyobj/settings_window.py | 3 +++
 1 file changed, 3 insertions(+)
```

---

### ea926c3a - Update settings_window.py with bounds

```text
src/Ankimon/pyobj/settings_window.py | 44 ++++++++++++++++++++++++++++++++++++
 1 file changed, 44 insertions(+)
```

---

### dc26e851 - Update setting_description.json

```text
src/Ankimon/lang/setting_description.json | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

---

### 4dc477d7 - Update setting_name.json

```text
src/Ankimon/lang/setting_name.json | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
```

---

### d6714aee - Modifying Trainer Cash Earnings

Added two new input possibilities to the settings GUI:
"Cash Reward Per Interval" and "Cards Per Cash Reward"
default values are 100 and 10, meaning for every 10 cards reviewed, the trainer gets 100 cash.

Needless to say, this can be abused to get absurd amounts of cash but setting a lower and upper bound for the options solves this problem. i just havent done it cause im not sure where to put the upper and lower limits for each of the two options :)

```text
src/Ankimon/battle_loop.py                | 6 ++++--
 src/Ankimon/config.json                   | 4 +++-
 src/Ankimon/lang/setting_description.json | 4 +++-
 src/Ankimon/pyobj/settings.py             | 2 ++
 src/Ankimon/pyobj/settings_window.py      | 2 +-
 5 files changed, 13 insertions(+), 5 deletions(-)
```

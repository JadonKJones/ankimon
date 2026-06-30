# Commits on BRRRR_Experimental since conception (ahead of main)

### 91df5fb1 - Merge pull request #486 from jupiterslegacy/fix/team-view-in-deck-overview

fix(ui): migrate deck overview team grid to SQLite and refactor hooks

---

### c62d12c8 - feat(mobile): complete Mobile & Web Reviews integration

Merges the full Mobile & Web Reviews feature into BRRRR_Experimental.

This brings in 38 commits spanning the complete lifecycle of the feature:
initial implementation, three stabilisation rounds, a full regression
fix cycle, encounter-determinism hardening, and a performance pass.

Highlights:
- New mobile_sync.py simulation engine (2 061 lines) with deterministic
  enemy generation seeded exclusively from the review queue
- Full SPA UI in ankimon_mobile_web/ (State 1: queue overview + pokeball
  estimate, State 2: manual replay with companion selector and HP bars)
- MobileBridge @pyqtSlot handlers -- all three resolution modes
  (resolveAll, resolveNext / commitReplayOutcome, startBulkResolve)
  are now non-blocking: every heavy operation runs in a QueryOp
  background thread and pushes results back to JS via runJavaScript
- Encounter sequence invariant enforced across all paths: same pending
  queue always produces the same enemy sequence regardless of team
  composition, mode, or whether previewing or resolving
- 225 tests across test_mobile_sync.py, test_mobile_auto_resolve.py,
  and test_mobile_replay.py -- all passing

Special thanks to @h0tp-ftw for the outstanding collaboration throughout
this project -- from the initial mobile integration architecture through
every round of review, testing, and iteration. This feature would not
exist without that partnership.

---

### e205b25c - perf: refactor resolveNext to use non-blocking asynchronous fire-and-forget pattern

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 47 ++++++++++++++++++-------------
 src/Ankimon/ankimon_mobile_web/mobile.js  | 24 +++++++++++++++-
 2 files changed, 51 insertions(+), 20 deletions(-)
```

---

### 6abc9667 - perf: optimize Mobile & Web Reviews performance and eliminate replay visual lag

```text
src/Ankimon/ankimon_mobile_web/mobile.css    |  1 +
 src/Ankimon/ankimon_mobile_web/mobile.js     | 94 ++++++++++++++++------------
 src/Ankimon/functions/encounter_functions.py | 10 ++-
 src/Ankimon/functions/mobile_sync.py         | 45 ++++++++++---
 4 files changed, 96 insertions(+), 54 deletions(-)
```

---

### 4d5e9527 - perf(mobile): batch hydrated team clone queries and relax replay animations

```text
src/Ankimon/ankimon_mobile_web/mobile.css |  20 ++--
 src/Ankimon/ankimon_mobile_web/mobile.js  |  12 +--
 src/Ankimon/functions/mobile_sync.py      | 160 +++++++++++++++++++-----------
 3 files changed, 120 insertions(+), 72 deletions(-)
```

---

### a4500369 - perf(mobile): defer post-outcome work in commitReplayOutcome

```text
src/Ankimon/ankimon_mobile_web/mobile.css |  20 +--
 src/Ankimon/ankimon_mobile_web/mobile.js  |  10 +-
 src/Ankimon/functions/mobile_sync.py      | 254 +++++++++++++++++-------------
 3 files changed, 161 insertions(+), 123 deletions(-)
```

---

### bf6894e4 - perf(mobile): eliminate synchronous DB work in getMobileStatus

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 80 +++++++++++--------------------
 1 file changed, 27 insertions(+), 53 deletions(-)
```

---

### b7426a39 - perf(mobile): offload resolveNext simulation off the main thread

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 52 +++++++++++++++++++++++++------
 1 file changed, 42 insertions(+), 10 deletions(-)
```

---

### ae5262e1 - fix(mobile-sync): rely exclusively on metadata cache key for encounter index

Avoid using the mobile_battle_history table count for encounter_idx as it is pruned to 500 records. Now we exclusively read the metadata key 'mobile_resolved_encounters_count', falling back to calculating the count via resolved review logs from pending_mobile_battles. Added the commit flag to _compute_encounter_idx to prevent metadata writes during dry-runs/UI polling estimates.

```text
src/Ankimon/functions/mobile_sync.py | 61 +++++++++++++++++-------------------
 1 file changed, 28 insertions(+), 33 deletions(-)
```

---

### 871cbc42 - refactor(mobile-sync): resolve database lockup, UI freeze, memory leak, and seeding issues

- Optimized _compute_encounter_idx in mobile_sync.py to check the metadata cache first and fallback to a fast approximation (resolved_reviews // cards_per_round) rather than executing the slow simulation loop. This resolves UI freezes and thread accumulation (memory leaks) during estimates polling.
- Re-architected database operations inside _compute_encounter_idx to run on the thread-safe connection wrapper db._get_connection() to avoid SQLite transaction locks.
- Fixed seeding alignment between the auto-resolve preview simulation and manual replay turn simulation by healing companions to full HP between simulated battles.
- Fixed the Game menu action name to 'Mobile and Web Reviews' instead of the incorrect 'Mobile & Web Reviews'.
- Added unit tests test_multi_turn_encounter_seeding_alignment and test_enemy_level_uses_active_companions_only_when_inactive_high_level to verify seeding stability and active companion level scaling.
- Updated remaining tests to reflect naming and alignment changes.

```text
src/Ankimon/ankimon_items_web/shop_obj.py    |  66 ++---
 src/Ankimon/functions/encounter_functions.py |  17 +-
 src/Ankimon/functions/mobile_sync.py         | 383 ++++++++++++++++++++-------
 src/Ankimon/menu_buttons.py                  |   8 +-
 src/Ankimon/pyobj/database_manager.py        |  13 +-
 src/Ankimon/singletons.py                    |   8 +
 tests/test_mobile_replay.py                  | 114 ++++++++
 tests/test_mobile_sync.py                    |  77 +++++-
 8 files changed, 545 insertions(+), 141 deletions(-)
```

---

### ffe98a32 - fix(mobile): align mode=next and mode=all encounter generation for full sequence parity

```text
src/Ankimon/functions/mobile_sync.py | 4 ++++
 1 file changed, 4 insertions(+)
```

---

### a70c7ae5 - fix(mobile): make dry-run encounter count independent of team composition

```text
src/Ankimon/functions/mobile_sync.py | 81 +++++++++++++++++++++++-------------
 1 file changed, 52 insertions(+), 29 deletions(-)
```

---

### 04d0bca0 - fix(mobile): unify RNG seeding across mode="next", mode="all" preview, and mode="all" resolve

```text
src/Ankimon/functions/mobile_sync.py | 11 ++++++-----
 1 file changed, 6 insertions(+), 5 deletions(-)
```

---

### 3378c7ff - Merge pull request #505 from h0tp-ftw/fix/mobile-resolve-restore

fix(mobile): restore relative imports + per-encounter heal (4 resolve regressions)

---

### fc8260f3 - fix(mobile): heal the companion to full HP after each resolved encounter

The original dry-run estimator (simulate_pending_mobile_battles) reset the
selected companion's HP to full after every encounter; the #496 unify into
run_mobile_battles dropped that and left only reset_bonuses(), so HP now carried
from one encounter to the next in BOTH the preview and the real auto-resolve.

Consequences:
  * Symptom 2 — the best companion accumulates damage, faints, and weaker
    members cycle in (reviving once all have fainted). Battle lengths then
    depend on how many companions are active and on the odd/even position in
    that fainting-revival cycle, so the extrapolated encounter count swings
    wildly with active-team size. Repro (300 reviews, one strong + two weak
    companions): preview count was 51 / 57 / 75 for 3 / 2 / 1 active members;
    after the fix it is a stable 75 / 75 / 75.
  * Symptom 3 — manual replay reloads the team fresh on every call (so every
    encounter starts at full HP), while preview/auto-resolve carried HP, so the
    three modes drifted apart after the first encounter. Healing each encounter
    in run_mobile_battles makes all three behave identically again.

Restores the per-encounter heal via a shared _heal_to_full() helper, used in
both the enemy-defeated and companion-fainted resolution branches. Tests: 223.

```text
src/Ankimon/functions/mobile_sync.py | 31 +++++++++++++++++++++++++------
 1 file changed, 25 insertions(+), 6 deletions(-)
```

---

### 16403933 - fix(mobile): restore relative imports in _attribute_xp_and_evs_to_companion

The #496 refactor moved _attribute_xp_and_evs_to_companion from
ankimon_items_web/shop_obj.py into functions/mobile_sync.py but converted
three module imports from relative to absolute `from Ankimon...` form:

  - from Ankimon.functions.pokemon_functions import ...
  - from Ankimon.functions.drawing_utils  import tooltipWithColour
  - from Ankimon.pyobj.reviewer_obj       import AttackDialog

At runtime Anki loads the addon under its install-folder package name, not
"Ankimon", so every one of these raised `ModuleNotFoundError: No module named
'Ankimon'`. This crashed:
  - manual replay "Defeat" (commit_replay_outcome -> _attribute_xp_and_evs_to_companion)
  - "Auto-Resolve All" whenever a non-main companion won a battle
    (run_mobile_battles commit path -> _attribute_xp_and_evs_to_companion)

Restored to relative form for the new module location (functions/). The
AttackDialog import is pointed at its real module ..pyobj.attack_dialog
(the canonical path used by every other caller; reviewer_obj never exported
AttackDialog, so the original ..pyobj.reviewer_obj path was itself broken).

The test suite cannot catch this because conftest registers a real "Ankimon"
package stub; the failure only manifests inside Anki. Tests unchanged: 223.

```text
src/Ankimon/functions/mobile_sync.py | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)
```

---

### 05b131c2 - fix: initialize lists for both commit modes (#502)

```text
src/Ankimon/functions/mobile_sync.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

---

### ad54aa0f - fix: resolve auto-resolve preview state drift (#502)

```text
src/Ankimon/functions/mobile_sync.py | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
```

---

### 8e32a48c - fix(mobile): restore missing return in getBulkResolveProgress

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 1 +
 1 file changed, 1 insertion(+)
```

---

### a9f139fb - test(mobile): fix legacy EV test signature to match new _attribute_xp_and_evs_to_companion API

```text
tests/test_mobile_sync.py | 7 ++++++-
 1 file changed, 6 insertions(+), 1 deletion(-)
```

---

### c22b44b2 - test(mobile): restore proper fakes in downgraded mobile tests

```text
tests/test_mobile_auto_resolve.py | 55 +++++++++++++--------------------------
 1 file changed, 18 insertions(+), 37 deletions(-)
```

---

### 26fa44f6 - fix(mobile): fix dry-run estimate drift in run_mobile_battles

```text
src/Ankimon/functions/mobile_sync.py | 7 ++++++-
 1 file changed, 6 insertions(+), 1 deletion(-)
```

---

### e002f0f6 - fix(mobile): harden limit_ev_yield and EV attribution against stale/corrupt companion data

```text
src/Ankimon/functions/mobile_sync.py |  2 ++
 src/Ankimon/utils.py                 | 24 ++++++------------------
 tests/test_mobile_sync.py            | 16 ++++++++++++++++
 3 files changed, 24 insertions(+), 18 deletions(-)
```

---

### 17199863 - fix(mobile): add catch-all error handling to MobileBridge @pyqtSlot wrappers

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 115 +++++++++++++++++++-----------
 1 file changed, 72 insertions(+), 43 deletions(-)
```

---

### f1bb3248 - Merge pull request #502 from h0tp-ftw/fix/496-mobile-resolve-regressions

fix(mobile): repair 4 regressions from the #496 resolve refactor (+ full review)

---

### fbc61db0 - fix(mobile): repair 4 regressions introduced by the #496 resolve refactor

Found via a comprehensive code review of the #496 refactor (steps 1-5). The core
dedup/relocation is faithful (XP/EV/cash math, seeding, catch logic, commit-gating,
SQL all verified equivalent); these are bugs from lines dropped during the move:

1. [HIGH] in_bulk_resolve never reset. _resolve_internal's finally imported `utils`
   but dropped `utils.in_bulk_resolve = False`. After ONE mobile auto-resolve the
   flag stays True for the whole session, silently suppressing level-up tooltips,
   evolution prompts and learn-move dialogs in NORMAL desktop play (encounter_functions
   / pokedex_functions gate those on `not in_bulk_resolve`). Restored the reset.

2. [HIGH] caught_count never incremented in the commit path — auto-resolve always
   reported "0 caught" while the caught list was non-empty (contradictory UI; the
   pokemon were actually caught). Restored `caught_count += 1` in the catch branch.

3. [MED] pokemon_defeated double-counted: commit_replay_outcome called
   _attribute_xp_and_evs_to_companion (which already increments pokemon_defeated on
   the DB row AND the in-memory main) and THEN incremented main_pokemon.pokemon_defeated
   again. Removed the redundant block; the active companion's defeat now counts once.

4. [LOW] removed 4 leftover `print(">>> run_mobile_battles: ...")` debug statements
   that spammed stdout on every resolve/estimate (incl. each bulk-resolve chunk).

Verified: py_compile OK, ruff clean, the WebEngine-free test subset unchanged (no new
failures). The full suite needs QtWebEngine (x86 CI / a desktop) — see PR notes.

```text
src/Ankimon/functions/mobile_sync.py | 24 ++++++++++--------------
 1 file changed, 10 insertions(+), 14 deletions(-)
```

---

### 8bacff1f - fix(mobile): resolve type annotation compatibility with Python 3.9 (#496)

```text
src/Ankimon/functions/mobile_sync.py | 1 +
 1 file changed, 1 insertion(+)
```

---

### 95487dbd - chore(mobile): hoist inline imports, remove double decorator, tidy comments (#496 step 5)

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 22 ++++++++--------------
 src/Ankimon/functions/mobile_sync.py      | 30 +++++++++++++-----------------
 2 files changed, 21 insertions(+), 31 deletions(-)
```

---

### 75e2b101 - refactor(mobile): remove MagicMock guards, replace with real fakes in tests (#496 step 4)

```text
src/Ankimon/functions/mobile_sync.py  | 112 ++++++++-----------------
 src/Ankimon/menu_buttons.py           |  12 ++-
 src/Ankimon/pyobj/database_manager.py |   6 +-
 src/Ankimon/singletons.py             |   9 +++
 tests/test_database_manager.py        |   9 ++-
 tests/test_mobile_auto_resolve.py     | 119 +++++++++++++++------------
 tests/test_mobile_replay.py           |   6 +-
 tests/test_mobile_sync.py             | 148 +++++++++++++++++++++-------------
 8 files changed, 223 insertions(+), 198 deletions(-)
```

---

### d3da1b5b - refactor(mobile): unify dry-run and real resolve into run_mobile_battles (#496 step 3)

```text
src/Ankimon/ankimon_items_web/shop_obj.py |   13 +-
 src/Ankimon/functions/mobile_sync.py      | 1821 ++++++++++++-----------------
 2 files changed, 786 insertions(+), 1048 deletions(-)
```

---

### bafbe396 - refactor(mobile): move resolution engine out of MobileBridge into mobile_sync (#496 step 2)

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 1348 ++---------------------------
 src/Ankimon/functions/mobile_sync.py      | 1150 ++++++++++++++++++++++++
 2 files changed, 1230 insertions(+), 1268 deletions(-)
```

---

### fd1e2488 - refactor(mobile): extract shared simulation helpers into mobile_sync (#496 step 1)

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 192 ++++---------------
 src/Ankimon/functions/mobile_sync.py      | 299 +++++++++++++++++-------------
 2 files changed, 204 insertions(+), 287 deletions(-)
```

---

### 8e5594e0 - Merge pull request #495 from h0tp-ftw/mobile-cleanup/sync-clarity

docs(mobile-sync): fix select_best_companion docstring + remove dead vars

---

### 2c928b07 - Merge pull request #494 from h0tp-ftw/mobile-cleanup/db-history

refactor(mobile-db): drop on-the-fly history table, dedupe history writers

---

### 2803c410 - Merge pull request #493 from h0tp-ftw/mobile-cleanup/db-migration

fix(mobile-db): re-run schema setup on every init so migrations aren't skipped

---

### 22c1897f - docs(mobile-sync): fix select_best_companion docstring + remove dead vars

The docstring described the score as "EDO * Companion Type Matchup * Speed * HP
Fraction", but the code computes score = EDO * Speed: there is no separate
companion type-matchup factor, and HP is deliberately excluded (see the inline
comment) to avoid health-biased selection. Rewrote it to match the real formula
and the Speed/level tie-breakers.

Also removed the now-dead max_hp / hp_fraction locals in the scoring loop —
hp_fraction was computed but never read after HP was dropped from the score.

```text
src/Ankimon/functions/mobile_sync.py | 14 ++++++--------
 1 file changed, 6 insertions(+), 8 deletions(-)
```

---

### 62f6eac5 - refactor(mobile-db): drop on-the-fly history table, dedupe history writers

mobile_battle_history is already created in _setup_database, so the defensive
_ensure_history_table() — which ran a sqlite_master probe on every history
read/write — was redundant. Removed it and all 4 call sites.

add_mobile_history_entry() duplicated the entire INSERT + _clean_val helper +
500-row trim of add_mobile_history_entries_batch(); it now just delegates
([entry] -> batch). Identical behavior, one writer to maintain.

Net: 1 file changed, 2 insertions(+), 75 deletions(-).

```text
src/Ankimon/pyobj/database_manager.py | 77 +----------------------------------
 1 file changed, 2 insertions(+), 75 deletions(-)
```

---

### d2475c07 - fix(mobile-db): re-run schema setup on every init so migrations aren't skipped

_setup_database() short-circuited with an early return whenever a hard-coded set
of table names already existed (and captured_pokemon.is_main was present). The
schema migrations (ALTER TABLE / new indexes / new tables) live *after* that
guard, so any future migration would silently never run on an already-initialized
DB unless the allow-list were also updated by hand — a latent upgrade trap that
stops _setup_database from being the single source of truth for the schema.

Every statement below the guard is idempotent (CREATE TABLE/INDEX IF NOT EXISTS,
guarded ALTER TABLE), so removing the short-circuit is safe; the only cost is a
handful of IF NOT EXISTS checks at startup. Restores _setup_database as the
reliable place migrations run.

```text
src/Ankimon/pyobj/database_manager.py | 23 ++++++-----------------
 1 file changed, 6 insertions(+), 17 deletions(-)
```

---

### b5c80084 - feat(mobile): add settings info indicators to auto-resolve preview

```text
src/Ankimon/ankimon_mobile_web/mobile.css  | 83 ++++++++++++++++++++++++++++++
 src/Ankimon/ankimon_mobile_web/mobile.html | 10 +++-
 2 files changed, 91 insertions(+), 2 deletions(-)
```

---

### 2d3a2059 - remove simulation report and raw JSON data for encounter weighting validation

```text
.gitignore                                         |     2 +
 .../simulation_report.txt                          |   108 -
 .../simulation_results.json                        | 55851 -------------------
 3 files changed, 2 insertions(+), 55959 deletions(-)
```

---

### 92acefcc - feat(mobile): complete Mobile & Web Reviews integration with multi-companion support, async simulation, and sync bugfixes

This commit contains the full implementation and bugfixes for the Mobile & Web Reviews integration, allowing Pokémon battles and reviews from mobile/web to sync seamlessly into Ankimon, including companion selection in replays and multi-companion XP distribution.

Key Changes:

1. Multi-Companion XP & EV Attribution
- Implemented `_attribute_xp_and_evs_to_companion()` in `shop_obj.py` to correctly assign XP, EVs, and handle level-ups for any target companion using `individual_id`, avoiding the active companion lock bug.
- Refactored `commitReplayOutcome` to support manual companion overrides for replays.
- Updated `_resolve_internal_wrapped` to track and distribute XP/EVs/defeat stats dynamically per companion across multiple cards using `companion_xp`, `companion_evs`, and `companion_battle_count` mappings.

2. Async Mobile Review Simulation & Unbounded Query Fix
- Moved the review estimation logic in `getMobileStatus` to run asynchronously on a background thread (`QueryOp`). The UI immediately displays loading status, and results are pushed dynamically to the front-end.
- Added `window.updateMobileEstimates(estimates)` callback in `mobile.js` to process the async payload.
- Optimized `getMobileStatus` database lookup by replacing an unbounded table scan with 2 targeted, bounded queries.
- Ensured a synchronous fallback path exists when executing under pytest environment.

3. Database Synchronization & Watermarking Fixes
- Fixed a watermark desync bug in `ankimon_sync.py` by ensuring each database connection reads its own watermark status prior to sync instead of using a global shared state.
- Implemented `make_safe_clone` in `mobile_sync.py` with a deep-copy of the stats dictionary and attribute recovery fallback.

4. UI/UX Refinements
- Integrated a nav switcher notification dot for pending mobile reviews via `notify_stats_changed`.
- Added the `getPendingReviewsCount` JS bridge slot.
- Renamed "Mobile Reviews" to "Mobile & Web Reviews" in sidebar navigation, html templates, and descriptions.
- Capped history retrieval limit to 500 records instead of 200.

5. Test Suite Extensions
- Added three new integration tests in `test_mobile_auto_resolve.py` validating XP attribution under multi-companion setups, replay outcome overrides, and database-specific sync boundaries.
- Added seed generation validation test for dynamic review counts in `test_mobile_sync.py`.

6. Documentation & Infrastructure
- Updated Section 10 in `repository-analysis/15-agent-handoff.md` to document the new mobile sync architecture.
- Logged all new experimental entry points in `_BRRR_EXPERIMENTAL_FEATURE_LIST.md`.

```text
.gitignore                                         |    2 +
 repository-analysis/00-executive-overview.md       |   19 +-
 repository-analysis/02-file-cards.md               |   16 +-
 repository-analysis/03-startup-and-control-flow.md |   40 +
 repository-analysis/15-agent-handoff.md            |   20 +
 repository-analysis/16-data-models-and-schemas.md  |   61 +
 repository-analysis/17-config-surface-map.md       |    6 +
 .../18-event-hooks-and-side-effects.md             |    8 +-
 repository-analysis/19-ui-surface-to-logic-map.md  |    5 +
 repository-analysis/20-persistence-deep-dive.md    |   20 +
 src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md     |   22 +-
 src/Ankimon/ankidex/ankidex.html                   |    7 +
 src/Ankimon/ankidex/ankidex.js                     |   21 +
 src/Ankimon/ankimon_items_web/nav-switcher.css     |   37 +
 src/Ankimon/ankimon_items_web/nav-switcher.js      |   27 +
 src/Ankimon/ankimon_items_web/settings.html        |    7 +
 src/Ankimon/ankimon_items_web/settings.js          |    2 +-
 src/Ankimon/ankimon_items_web/settings_schema.py   |   25 +
 src/Ankimon/ankimon_items_web/shop.html            |    7 +
 src/Ankimon/ankimon_items_web/shop_obj.py          | 2037 +++++++++++++++++++-
 src/Ankimon/ankimon_mobile_web/history.html        |  126 ++
 src/Ankimon/ankimon_mobile_web/history.js          |  236 +++
 src/Ankimon/ankimon_mobile_web/mobile.css          | 1395 ++++++++++++++
 src/Ankimon/ankimon_mobile_web/mobile.html         |  372 ++++
 src/Ankimon/ankimon_mobile_web/mobile.js           |  985 ++++++++++
 src/Ankimon/ankimon_profile_web/profile.css        |   31 +
 src/Ankimon/ankimon_profile_web/profile.html       |    7 +
 src/Ankimon/ankimon_profile_web/profile_data.py    |   17 +-
 src/Ankimon/ankimon_profile_web/team.html          |   16 +
 src/Ankimon/ankimon_profile_web/team.js            |   76 +-
 src/Ankimon/battle_loop.py                         |   14 +
 .../functions/ankimon_hooks_to_poke_engine.py      |   40 +-
 src/Ankimon/functions/encounter_functions.py       |  100 +-
 src/Ankimon/functions/mobile_sync.py               |  845 ++++++++
 src/Ankimon/functions/pokedex_functions.py         |   34 +-
 src/Ankimon/functions/sprite_functions.py          |   17 +
 src/Ankimon/gui_classes/overview_team.py           |    3 +-
 src/Ankimon/menu_buttons.py                        |   63 +-
 src/Ankimon/profile_hooks.py                       |   44 +-
 src/Ankimon/pyobj/ankimon_sync.py                  |  101 +-
 src/Ankimon/pyobj/database_manager.py              |  456 ++++-
 src/Ankimon/pyobj/pokemon_obj.py                   |   10 +-
 src/Ankimon/pyobj/settings.py                      |    4 +
 src/Ankimon/singletons.py                          |    5 +-
 src/Ankimon/utils.py                               |    9 +
 tests/conftest.py                                  |   37 +-
 tests/test_encounter_functions.py                  |    9 +-
 tests/test_learnset_retrieval.py                   |   17 +
 tests/test_learnset_robustness.py                  |   22 +
 tests/test_mobile_auto_resolve.py                  |  736 +++++++
 tests/test_mobile_replay.py                        |  461 +++++
 tests/test_mobile_sync.py                          | 1648 ++++++++++++++++
 tests/test_profile_hooks.py                        |  161 ++
 tests/test_reviewer_ownership_cache.py             |   18 +-
 54 files changed, 10347 insertions(+), 157 deletions(-)
```

---

### cc32606d - fix(team-overview): use logger.log instead of non-existent logger.exception

The except-guard in __init__.py called logger.exception(...), but Ankimon's
ShowInfoLogger only implements .log()/.log_and_showinfo() — so if hook
registration ever failed, the handler itself would raise AttributeError and
propagate out of startup, defeating the try/except it sits in. Use
logger.log('error', ...) and include the exception text.

```text
src/Ankimon/__init__.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 9de533a0 - test encounter sim small update

```text
.../simulation_report.txt                          |   108 +
 .../simulation_results.json                        | 55851 +++++++++++++++++++
 .../test_encounter_simulation.py                   |    12 +-
 3 files changed, 55965 insertions(+), 6 deletions(-)
```

---

### c7e9a814 - fix(encounter): resolve regional forms spawn bug & isolate tests

- Fix incorrect pokedex.json lookup path in _build_regional_lookup (changed from user_files/data_files/pokedex.json to data_files/pokedex.json).
- Fix active region mismatch by normalising ctive_region configuration to lowercase and stripping whitespace.
- Restructure base species substitution logic in generate_random_pokemon to strictly gate eligible variants to the active region if set. This ensures only variants belonging to the selected region (e.g., Alolan forms when active region is Alola) can substitute base forms (0% appearance for non-matching regions), while falling back to all regional variants if no active region is configured.
- Resolve test pollution and mock leakage across the pytest suite:
  - In 	est_encounter_functions.py, force-load the real encounter_data and pokedex_functions to ensure correct prerequisite checking.
  - In 	est_evolution_item_consumption.py, dynamically subclass the freshly loaded EvoWindow inside each test block and invoke setup_mocks to isolate namespaces.
  - In 	est_held_items.py, unconditionally mock the Ankimon.business module and reload stubs before each test in the 	emp_env fixture.

```text
src/Ankimon/functions/encounter_functions.py       | 25 +++++---
 tests/conftest.py                                  | 44 ++++++++++++++
 .../test_encounter_simulation.py                   | 67 +++++++++++++++++++---
 tests/test_encounter_functions.py                  | 25 +++++++-
 tests/test_evolution_item_consumption.py           | 56 ++++++++++++------
 tests/test_friendship_evolution.py                 | 17 ++++++
 tests/test_held_items.py                           | 42 ++++++++------
 tests/test_profile_pokedex_completion.py           | 12 +++-
 8 files changed, 236 insertions(+), 52 deletions(-)
```

---

### 9e160360 - docs: update experimental feature list summary and highlights

```text
src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md | 92 +++++++++++++++++++++++---
 1 file changed, 82 insertions(+), 10 deletions(-)
```

---

### 95ca7623 - unimportant

```text
src/Ankimon/functions/encounter_data.py | 22 +++++++++++-----------
 1 file changed, 11 insertions(+), 11 deletions(-)
```

---

### 8c795df9 - feat: redistribute special forms to legendary/mythical tiers, enforce prerequisites, and fix learnset issues

- Move all stat-redistribution (0 or negative BST boost) special forms out of the Mega list to their respective Legendary or Mythical lists:
  - Moved to LEGENDARY: Dialga Origin (10245), Palkia Origin (10246), Giratina Origin (10007), Zygarde 10% (10181), Urshifu Rapid Strike (10191), Tornadus Therian (10019), Thundurus Therian (10020), Landorus Therian (10021), Enamorus Therian (10249)
  - Moved to MYTHICAL: Deoxys Attack (10001), Deoxys Defense (10002), Deoxys Speed (10003), Shaymin Sky (10006), Meloetta Pirouette (10018), Keldeo Resolute (10024)
- Retained/added in MEGA_AND_SPECIAL (MEGA): Kyogre Primal (10077), Groudon Primal (10078), Eternatus Eternamax (10190), Zygarde Complete (10120), Necrozma Dusk Mane (10155), Necrozma Dawn Wings (10156), Necrozma Ultra (10157), Kyurem Black (10022), Kyurem White (10023), Zacian Crowned (10188), Zamazenta Crowned (10189), Calyrex Ice (10193), Calyrex Shadow (10194), Terapagos Terastal (10276), Terapagos Stellar (10277), Hoopa Unbound (10086), Magearna Original (10147)
- Enforce base species ownership prerequisites for all relocated special forms (e.g., Dialga owned required to encounter Dialga Origin).
- Fix learnset retrieval logic to support Relearn ('R') and Special/Event ('S') moves, enabling signature moves like Behemoth Blade/Bash, Sunsteel Strike, and Moongeistbeam to show in the Learn Moves window.
- Implement programmatic move exclusions (DEOXYS_EXCLUSIONS) to prevent Deoxys forms from cross-learning each other's form-exclusive moves via level-up.
- Add test coverage and fix unit test package stubs in `conftest.py` to prevent test pollution.

```text
src/Ankimon/functions/encounter_data.py            | 110 ++++++++++++++++-----
 src/Ankimon/functions/encounter_functions.py       |  11 ++-
 src/Ankimon/functions/learnset_retrieval.py        |  71 ++++++++++---
 src/Ankimon/pyobj/pc_box.py                        |   1 +
 src/Ankimon/resources.py                           |   8 ++
 tests/conftest.py                                  |   2 +-
 .../test_overhaul_simulation.py                    |  11 +++
 tests/test_encounter_functions.py                  |  27 +++++
 tests/test_learnset_retrieval.py                   |  70 ++++++++++++-
 tests/test_wishlist_serialization.py               |   1 -
 10 files changed, 267 insertions(+), 45 deletions(-)
```

---

### 2325900a - implement Eternamax encounter

```text
src/Ankimon/functions/encounter_data.py    | 7 ++++---
 src/Ankimon/functions/pokedex_functions.py | 3 +++
 2 files changed, 7 insertions(+), 3 deletions(-)
```

---

### 77c8cf2d - feat: implement learnset retrieval logic for eternamax

```text
src/Ankimon/functions/learnset_retrieval.py |   2 +-
 tests/test_learnset_retrieval.py            |  60 ++++++++++--
 tests/test_pc_box_evolution_button.py       | 139 ++++++++++++++++++++++++++++
 3 files changed, 194 insertions(+), 7 deletions(-)
```

---

### a8c2047c - fix: add defensive error handling for legacy JSON fallbacks

- Wrapped legacy JSON loading in local try/except blocks to prevent corrupted files from bypassing the final fallback.
- Added type validation (isinstance checks) for JSON data to handle malformed lists or dictionaries.
- Ensured that a failure in reading `team.json` does not prevent the function from attempting to load from `mypokemon.json`.

```text
src/Ankimon/gui_classes/overview_team.py | 22 ++++++++++++++++------
 1 file changed, 16 insertions(+), 6 deletions(-)
```

---

### 4cd66709 - fix: restore broken team overview grid using AnkimonDB

- Updated `load_pokemon_team` to query the new SQLite database (`ankimon_db`) instead of relying on legacy JSON files, which caused the grid to fail silently for new users.
- Added fallback logic for legacy JSON data to ensure backward compatibility.
- Moved hook registrations into `__init__.py` to prevent import side-effects and improve error handling during the startup sequence.

```text
src/Ankimon/__init__.py                  |  18 +++++-
 src/Ankimon/gui_classes/overview_team.py | 103 ++++++++++++++-----------------
 2 files changed, 65 insertions(+), 56 deletions(-)
```

---

### 78033e50 - fix: KeyError: 'Legendary' in modify_percentages when reviews are low

```text
src/Ankimon/functions/encounter_functions.py | 22 ++++++++++++++--------
 tests/test_encounter_functions.py            | 17 +++++++++++++++++
 2 files changed, 31 insertions(+), 8 deletions(-)
```

---

### 03ed045f - docs(AGENTS.md): add ankimon_context.md sync to Documentation Maintenance table

```text
AGENTS.md | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)
```

---

### 69bbd59b - docs(AGENTS.md): add Documentation Maintenance section + stub .agents/ copies for token savings

Add a 'Documentation Maintenance' subsection under 'Making Changes' that tells agents
which repository-analysis/ documents to update when their code changes affect architecture,
data models, settings, hooks, or UI surfaces. Includes a change-type-to-document lookup
table and explicit exclusions for trivial changes (bug fixes, CSS-only, tests, comments).

Also replace the 3 identical .agents/ copies (AGENTS.md, CLAUDE.md, GEMINI.md) with
one-line stubs pointing to root AGENTS.md. Since all 4 files were loaded as user rules
on every turn, the duplication cost ~13,500 tokens/turn of pure overhead. The .agents/
directory is gitignored so the stubs are local-only.

```text
AGENTS.md | 20 ++++++++++++++++++++
 1 file changed, 20 insertions(+)
```

---

### 3ec387cf - TEMP: modify encounter rates; trainer LVL boost  adjustments

```text
src/Ankimon/functions/encounter_functions.py | 32 +++++++++++++++++-----------
 1 file changed, 20 insertions(+), 12 deletions(-)
```

---

### eadeed1a - docs: unify and rewrite AGENTS.md with real repository intelligence

- Unifies the previously disparate root AGENTS.md and .agents/AGENTS.md templates into a single high-fidelity, project-specific instruction manual.
- Eliminates generic agent boilerplate (e.g., phantom directories, unused command lines, unconfigured tools/credentials).
- Inlines critical agent handoff guidelines, coding conventions, singletons map, and data flow architecture from the \
epository-analysis/\ documents.
- Restructures the file mapping section to reference the 30+ actual core modules instead of an arbitrary list.
- Registers the specialized agent skills inventory (e.g. trade-generator, db-manager, frontend-design) with their triggers.
- Injects a Risk Register Quick Reference highlighting the 8 key operational hazards (such as circular prerequisites and database hot-swap cascade lockouts).
- Indexes all 21 repository intelligence files (\
epository-analysis/\ 00-20) for easy agent lookups.
- Clarifies the testing framework instructions, clearly distinguishing between standard \pytest\ coverage and the specialized, non-routine encounter weighting simulations.

```text
AGENTS.md | 352 +++++++++++++++++++++++++++++++++++++++++++++++++++-----------
 1 file changed, 290 insertions(+), 62 deletions(-)
```

---

### 54df8c3e - fix: implement dynamic global square root scaling for PC Box stat bars

```text
src/Ankimon/gui_classes/pokemon_details.py | 21 +++++++++++++++++++--
 1 file changed, 19 insertions(+), 2 deletions(-)
```

---

### 91f63c29 - feat: display equipped items in modern Web Bag and fix grid card layouts

- Web bag displays equipped items in fully vibrant colors with border/badge highlights
- Grouped equipped items in the grid, listing equipping Pokémon in the Side Detail Inspector
- Implemented 'Unequip' action inside Side Detail Inspector to unequip items from the Web Bag UI
- Set a stable card height of 200px and compacted margins to ensure uniform heights regardless of in-stock price pills
- Structured top-left tags (STOCK/TM) and top-right badges with safety max-widths and text-overflow/flex-wrapping to prevent overlap
- Added test suite coverage verifying serialization and slot trigger logic

```text
src/Ankimon/ankimon_items_web/shop.css    |  89 +++++++-
 src/Ankimon/ankimon_items_web/shop.html   |   5 +
 src/Ankimon/ankimon_items_web/shop.js     |  74 +++++--
 src/Ankimon/ankimon_items_web/shop_obj.py |  90 +++++++-
 src/Ankimon/pyobj/item_window.py          |   5 +
 src/Ankimon/pyobj/pc_box.py               |  12 ++
 src/Ankimon/pyobj/pokemon_obj.py          |   8 +
 tests/test_held_items.py                  | 335 ++++++++++++++++++++++++++++++
 8 files changed, 592 insertions(+), 26 deletions(-)
```

---

### 95db8922 - docs: Add startup update notification system porting guide

```text
docs/updater_porting_guide.md | 474 ++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 474 insertions(+)
```

---

### b80b42eb - Merge pull request #482 from AIbrahimv2/fix/ankidex-sprite-aspect-ratio

fix: preserve sprite aspect ratio in Ankidex

---

### 1c2e0434 - fix: preserve sprite aspect ratio in Ankidex

Add object-fit: contain to the detail (#det-sprite), evolution (.evo-sprite), form-chip (.form-chip img), and capture-requirement (.prereq-item img) sprites so non-square sprites are letterboxed instead of stretched into their fixed boxes. Most visible on animated GIFs such as Kyogre's 234x55 canvas, which was being stretched vertically into the 180x180 hero box. Mirrors the item-bag fix. Also add a ?v=20260531 cache-buster to the ankidex.css <link> (it previously had none) so QWebEngineView reloads the updated stylesheet.

```text
src/Ankimon/ankidex/ankidex.css  | 7 +++++++
 src/Ankimon/ankidex/ankidex.html | 2 +-
 2 files changed, 8 insertions(+), 1 deletion(-)
```

---

### 1ae5be32 - Hotkey 9 fix

```text
src/Ankimon/pyobj/settings.py | 1 +
 src/Ankimon/reviewer_ui.py    | 4 ++--
 2 files changed, 3 insertions(+), 2 deletions(-)
```

---

### 4a5d14b1 - TEMP: modify encounter rates

```text
src/Ankimon/functions/encounter_functions.py | 28 +++++++++++++++-------------
 1 file changed, 15 insertions(+), 13 deletions(-)
```

---

### db78d826 - fix: backup manager trainer name N/A and 0 cash display issue

In backup_manager.py, _generate_summary was attempting to read trainer.name, trainer.cash, and trainer.level using db.get_user_data which queries the user_data table. Since these keys are stored in the config table, this resulted in returning fallback/default values. Replaced the queries with db.get_config_value to correctly fetch trainer info from the config table. Added a new unit test suite in test_backup_manager.py to verify.

```text
src/Ankimon/pyobj/backup_manager.py |   8 +--
 tests/test_backup_manager.py        | 131 ++++++++++++++++++++++++++++++++++++
 2 files changed, 135 insertions(+), 4 deletions(-)
```

---

### 6e8a231c - docs: relocate and update repository-analysis to project root

Moved '.agents/repository-analysis' to the root directory 'repository-analysis' to track it in git.

Updated all documents to reflect the new unified HTML5 web shell window (AnkimonItemsWeb), zero-lag asynchronous startup (QueryOp), and parsed in-memory O(1) caches.

Documented 'shop_obj.py' and 'profile_data.py' as core UI/data bridges and detailed settings schema validation in 'settings_schema.py'.

Updated '05-risk-register.md' with thread-safety and Windows DWM compositor paint risks, and revised Playbook 3 in '11-editing-playbook.md'.

```text
repository-analysis/00-executive-overview.md       |  78 ++++++++++
 repository-analysis/01-architecture-map.md         | 152 ++++++++++++++++++
 repository-analysis/02-file-cards.md               | 138 +++++++++++++++++
 repository-analysis/03-startup-and-control-flow.md | 161 +++++++++++++++++++
 repository-analysis/04-source-of-truth.md          | 146 ++++++++++++++++++
 repository-analysis/05-risk-register.md            |  67 ++++++++
 repository-analysis/06-conventions-observed.md     |  72 +++++++++
 repository-analysis/07-glossary.md                 |  55 +++++++
 repository-analysis/08-reading-order.md            |  60 ++++++++
 repository-analysis/09-module-boundaries.md        |  53 +++++++
 repository-analysis/10-test-intelligence.md        |  62 ++++++++
 repository-analysis/11-editing-playbook.md         | 118 ++++++++++++++
 repository-analysis/12-unknowns-and-questions.md   |  31 ++++
 repository-analysis/13-core-file-appendix.md       | 171 +++++++++++++++++++++
 repository-analysis/14-import-and-call-hotspots.md |  42 +++++
 repository-analysis/15-agent-handoff.md            |  59 +++++++
 repository-analysis/16-data-models-and-schemas.md  | 133 ++++++++++++++++
 repository-analysis/17-config-surface-map.md       |  51 ++++++
 .../18-event-hooks-and-side-effects.md             |  70 +++++++++
 repository-analysis/19-ui-surface-to-logic-map.md  | 125 +++++++++++++++
 repository-analysis/20-persistence-deep-dive.md    |  92 +++++++++++
 21 files changed, 1936 insertions(+)
```

---

### 3c4c3e9a - feat: support customizable team rotation cycle limits in team selection window

- Added controls.team_cycle_count default configuration set to 3.
- Exposed a saveCycleCount(count) PyQt slot on the TeamBridge to sync user selection instantly to the database.
- Retrieved the cycle count setting dynamically in the profile data payload to populate the UI.
- Upgraded the study hotkey '9' team cycling logic in reviewer_ui.py to dynamically bound cycling range based on the user's limit.
- Handled rotation disabled state (limit <= 1) with an informative tooltip warning.
- Structured and styled a custom 'Team Rotation' dropdown select within the Team Builder sidebar.
- Implemented real-time dynamic rotation badges (↻) over active slot cards in the team grid to provide visual feedback.
- All 167 Python unit tests passed successfully.

```text
src/Ankimon/ankimon_items_web/shop_obj.py       |  4 +++
 src/Ankimon/ankimon_profile_web/profile.css     | 35 +++++++++++++++++++++++++
 src/Ankimon/ankimon_profile_web/profile_data.py |  3 +++
 src/Ankimon/ankimon_profile_web/team.html       | 11 ++++++++
 src/Ankimon/ankimon_profile_web/team.js         | 24 ++++++++++++++++-
 src/Ankimon/pyobj/settings.py                   |  1 +
 src/Ankimon/reviewer_ui.py                      | 16 ++++++++---
 7 files changed, 89 insertions(+), 5 deletions(-)
```

---

### 464c767d - feat: add animated sprites to team selection window with toggle synced with Ankidex

```text
src/Ankimon/ankimon_items_web/shop_obj.py       |  4 ++
 src/Ankimon/ankimon_profile_web/profile.css     | 18 ++++++++
 src/Ankimon/ankimon_profile_web/profile_data.py |  6 +++
 src/Ankimon/ankimon_profile_web/team.html       | 11 ++++-
 src/Ankimon/ankimon_profile_web/team.js         | 56 ++++++++++++++++++++-----
 5 files changed, 83 insertions(+), 12 deletions(-)
```

---

### abcfddf3 - Merge pull request #477 from AIbrahimv2/feat/profile-team-web into BRRRR_Experimental

feat(profile+team): modernize UI with unified HTML5 Profile & Team screens, fix Pokédex completion alignment, and resolve merge conflicts

This merge integrates the comprehensive transition of Ankimon's Trainer Card, 
Team Builder, Choose-Sprite dialog, and Achievements Case from legacy Qt/Python 
widgets to an elegant, high-performance HTML5/JS unified web shell. It also 
resolves the Pokédex completion mismatch bug and integrates base-branch settings.

Core Features Integrated:
-------------------------
- **New HTML5 Profile Tab:** A premium dark-mode profile interface leveraging the 
  Outfit font and sleek glassmorphic aesthetics. Features real-time Trainer level/XP 
  progress bars, league rank badges, and showcases for "Favorite Pokémon", 
  "Highest Level", "Best Friend", and a "Recently Caught" card grid with entrance pops.
- **Interactive Trainer Rename & Sprite Picker:** Adds double-click inline renaming on 
  the Trainer Card (reverting on bridge errors) and an inline modal picker lazy-loading 
  ~1,400 trainer sprites filterable by Generation, Category, and Sex.
- **Unified Navigation switcher:** Consolidates navigation CSS and JS dropdown switcher 
  rules across all 5 web tabs (Items, Ankidex, Team, Profile, Settings) into a single 
  shared, asset-backed module.
- **New HTML5 Team Builder Tab:** A responsive 6-slot visual team manager with dynamic 
  CP calculations, simple slot-swapping roster pickers, interactive XP Share target 
  selection (marked with a gold star badge), and a comprehensive Type coverage 
  matchup widget displaying team defensive weaknesses and offensive strengths.
- **Deprecated Qt Teardown:** Fully deletes unreferenced legacy files:
  - `pyobj/trainer_card_window.py`
  - `gui_classes/pokemon_team_window.py`
  - `gui_classes/choose_trainer_sprite_graphical.py`
  - `pyobj/achievements_dialog.py`

Key Alignment Fixes & Hardening (Antigravity modifications):
-----------------------------------------------------------
- **Pokédex completion count alignment:** Corrects the mismatch between the Profile 
  and the main Ankidex by querying all caught IDs (aggregating box, history, and 
  evolution registers) and deduplicating form IDs >= 10000 (Megas, Gmax, Alolan/Galarian 
  forms) to their base species_id using the central memory index.
- **Scalar-casting Fix:** Resolved a TypeError where wrapping the returned set of 
  `get_all_pokemon_ids()` in the `_q` integer-casting helper threw a silent exception.
- **Dialog Teardown Guard:** Protected the web channel deferred `_run_live_refresh` hook 
  with try/except RuntimeError guards, preventing app crashes if the web dialog is 
  closed before the timer fires.
- **Validation Hardening:** Added explicit type checks in `TeamBridge.saveTeam` to enforce 
  strictly formatted lists, and wrapped the friendship level parsing in defensive guards.
- **Automated Coverage:** Added a dedicated unit test suite in `tests/test_profile_pokedex_completion.py` 
  asserting form deduplication, historical aggregation, and explicit Evolution marks.

Conflict Resolutions:
--------------------
- **.gitignore:** Resolved conflicts by preserving local skips like `__pycache__/` 
  and developer utilities.
- **shop_obj.py:** Merged import sections cleanly, preserving both the Web profile 
  payload bridges and the experimental wishlist serialization methods.
- **encounter_functions.py:** Integrated granular automatic-catch checkboxes 
  (`auto_catch_legendary`, `auto_catch_mythical`, etc.) from BRRRR_Experimental, 
  fully phasing out the deprecated single catch-all checkbox logic.

---

### 302c3761 - revert: undo auto ruff formatting on the branch [skip ci]

```text
src/Ankimon/ankimon_items_web/settings_schema.py |   12 +-
 src/Ankimon/ankimon_items_web/shop_obj.py        |   99 +-
 src/Ankimon/ankimon_profile_web/profile_data.py  |  403 +----
 src/Ankimon/battle_loop.py                       |   47 +-
 src/Ankimon/functions/encounter_data.py          | 1751 ++++++----------------
 src/Ankimon/functions/pokedex_functions.py       |  304 +---
 src/Ankimon/menu_buttons.py                      |   17 +-
 src/Ankimon/pyobj/pc_box.py                      |  706 ++++-----
 src/Ankimon/pyobj/settings.py                    |   55 +-
 src/Ankimon/pyobj/settings_window.py             |   64 +-
 src/Ankimon/pyobj/trainer_card.py                |   34 +-
 src/Ankimon/reloader.py                          |   39 +-
 src/Ankimon/startup.py                           |   96 +-
 tests/test_encounter_functions.py                |   89 +-
 tests/test_friendship_evolution.py               |    3 +
 tests/test_profile_pokedex_completion.py         |  139 +-
 tests/test_wishlist_serialization.py             |   15 +-
 17 files changed, 1109 insertions(+), 2764 deletions(-)
```

---

### c97246fa - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/settings_schema.py |   12 +-
 src/Ankimon/ankimon_items_web/shop_obj.py        |   83 +-
 src/Ankimon/ankimon_profile_web/profile_data.py  |    9 +-
 src/Ankimon/functions/encounter_data.py          | 1751 ++++++++++++++++------
 src/Ankimon/functions/encounter_functions.py     |   41 +-
 src/Ankimon/functions/pokedex_functions.py       |  304 +++-
 src/Ankimon/pyobj/pc_box.py                      |  706 +++++----
 src/Ankimon/pyobj/settings.py                    |   55 +-
 src/Ankimon/pyobj/settings_window.py             |   64 +-
 src/Ankimon/startup.py                           |   96 +-
 tests/test_encounter_functions.py                |   89 +-
 tests/test_friendship_evolution.py               |    3 -
 tests/test_profile_pokedex_completion.py         |  139 +-
 tests/test_wishlist_serialization.py             |   15 +-
 14 files changed, 2355 insertions(+), 1012 deletions(-)
```

---

### 6fde473d - merge: resolve conflicts between pr-477 and BRRRR_Experimental

---

### 3658c5e2 - fix: align profile pokedex completion count with ankidex count

```text
src/Ankimon/ankimon_profile_web/profile_data.py |  29 +++-
 tests/test_profile_pokedex_completion.py        | 182 ++++++++++++++++++++++++
 2 files changed, 205 insertions(+), 6 deletions(-)
```

---

### 21aadfab - TEMP: modify encounter rates

```text
src/Ankimon/functions/encounter_functions.py | 65 +++++++++++++++-------------
 1 file changed, 34 insertions(+), 31 deletions(-)
```

---

### 06904eaa - feat(Dev): hardcode ID

```text
src/Ankimon/functions/encounter_functions.py | 4 ++++
 1 file changed, 4 insertions(+)
```

---

### 0f4f0cc4 - fix: resolve auto-catch wishlist pretty name rendering bug after restart

On restart, the wishlist setting's chips rendered only numeric IDs instead of pretty names. Fixes this by:

- Serializing pretty names under the 'names' dictionary for the battle.auto_catch_wishlist setting in the shop_obj.py backend.

- Seeding the state._wishlistNames frontend cache inside buildWishlistControl using the setting.names dictionary on settings initialization.

- Adding a comprehensive unit test suite in test_wishlist_serialization.py to guarantee robust name serialization.

```text
src/Ankimon/ankimon_items_web/settings.js |  7 +++
 src/Ankimon/ankimon_items_web/shop_obj.py | 10 +++++
 tests/test_wishlist_serialization.py      | 74 +++++++++++++++++++++++++++++++
 3 files changed, 91 insertions(+)
```

---

### 11067b28 - merge: fix(pc-box): sort by CP and stats with stats fallback (#476)

Resolves the issue where sorting the PC Box by CP or individual stats ordered legacy captured Pokémon incorrectly by near-minimum values.

- Root Cause: Legacy databases store base stats under the "stats" key and do not carry the modern "base_stats" key. The lightweight stub query selected only "base_stats_json", resulting in empty data and CP/stat recalculation using minimum clamp defaults.
- Fix: Modified fetch_filtered_pokemon to select "stats_json" as part of the lightweight query and implemented fallback checks in both CP-sorting and individual-stat-sorting blocks.
- Cleans up and untracks the .claude/ preview configuration directory.
- Preserves full author attribution for the original changes by @AIbrahimv2 while keeping the diff clean of IDE auto-formatting.

Reviewed-by: Hakimh2
Approved-by: Hakimh2
Closes #476

---

### 311de82e - chore: stop tracking .claude/ and add it to .gitignore

```text
.gitignore | 1 +
 1 file changed, 1 insertion(+)
```

---

### 7452b168 - fix(pc-box): fall back to $.stats for individual-stat sorting too

```text
src/Ankimon/pyobj/pc_box.py | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)
```

---

### 04ff5449 - fix(pc-box): sort by CP using base stats with a stats fallback

```text
src/Ankimon/pyobj/pc_box.py | 16 +++++++++++-----
 1 file changed, 11 insertions(+), 5 deletions(-)
```

---

### 73230066 - feat(config): add Pikachu (25) and Eevee (133) to the default auto-catch wishlist

- Updated 'battle.auto_catch_wishlist' default value to [25, 133] inside both pyobj/settings.py and config.json.
- This ensures newly created profiles start with Pikachu and Eevee pre-populated in their Always-Catch Wishlist out of the box.

```text
src/Ankimon/config.json       | 2 +-
 src/Ankimon/pyobj/settings.py | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

---

### 6b90a4b4 - style(settings): relocate Auto-Battle Rules subgroup to the top of Battle settings

- Restructured the 'Battle' settings schema in settings_schema.py.
- Grouped the general display settings under a new 'HUD & Mechanics' subgroup.
- Positioned the 'Auto-Battle Rules' subgroup at the very top of subgroups, ensuring it is rendered first in the Battle settings panel.
- Verified that all 165 automated tests continue to pass successfully.

```text
src/Ankimon/ankimon_items_web/settings_schema.py | 28 ++++++++++++++----------
 1 file changed, 16 insertions(+), 12 deletions(-)
```

---

### cfcb1bee - feat(settings): implement per-tier auto-catch toggles, regional forms toggle, and premium always-catch wishlist suggestions modal

- Split legacy global toggle into 7 per-tier toggles (Legendary, Mythical, Ultra Beast, Starter, Mega, Gigantamax, Regional Form).
- Added 'battle.auto_catch_wishlist' config and implemented startup migrations for legacy preferences.
- Created 'Auto-Battle Rules' web settings subgroup housing per-tier chips, modes, and the custom wishlist control.
- Fixed input debounce race condition for wishlist 'Add' button and 'Enter' key via an instant search lookup fallback.
- Added a full-width 'Choose from Caught...' action button opening a centered, glassmorphic modal suggestions grid.
- Implemented asynchronous caught Pokémon retrieval with Gen 3 front sprites, offline fallbacks, and real-time active state toggling/syncing.
- Applied PC Box pretty name formatting (e.g. Alolan Raichu) to search dropdown results.
- Excluded unspawnable/unavailable Pikachu Cosplay forms and 10099 (Alolan Pikachu) from active pools and search.
- Filtered out redundant plate, drive, and memory sub-forms of Arceus, Silvally, and Genesect to prevent search clutter.
- Restructured CSS layouts to prevent side clipping, and replaced modal backdrop blurs to avoid GPU-compositing flickering in QWebEngineView.
- Integrated legacy settings tree parity and verified full compliance with all 165 automated unit tests.

```text
src/Ankimon/ankimon_items_web/settings.css       | 293 +++++++++++++++++++++
 src/Ankimon/ankimon_items_web/settings.js        | 307 +++++++++++++++++++++++
 src/Ankimon/ankimon_items_web/settings_schema.py |  26 +-
 src/Ankimon/ankimon_items_web/shop_obj.py        |  89 ++++++-
 src/Ankimon/config.json                          |   9 +-
 src/Ankimon/functions/encounter_data.py          |   4 +-
 src/Ankimon/functions/encounter_functions.py     |  37 ++-
 src/Ankimon/lang/setting_description.json        |   9 +-
 src/Ankimon/lang/setting_name.json               | 127 +++++-----
 src/Ankimon/pyobj/settings.py                    |   9 +-
 src/Ankimon/pyobj/settings_window.py             |   9 +-
 src/Ankimon/startup.py                           |  17 ++
 tests/test_encounter_functions.py                | 174 +++++++++++++
 13 files changed, 1029 insertions(+), 81 deletions(-)
```

---

### 0ac01d6a - feat: remove Friendship & Time Evolution setting and always enable it

- Modified Settings.get() to force-return True for 'evolution.friendship_time_enabled', always enabling friendship and time-based evolutions for all trainers.
- Removed the setting option from both the PyQt Settings dialog ('settings_window.py') and the dynamic Web Settings interface ('settings_schema.py').
- Removed setting translation assets from 'setting_name.json' and 'setting_description.json' to keep all settings fully consistent and pass static tests.
- Fixed a reverse ID Pokedex index mapping bug in 'pokedex_functions.py' where the form variant 'pichuspikyeared' overrode the base form 'pichu' under ID 172. Added a baseSpecies check to prioritize true base forms and resolve the Pichu manual evolution lockout.
- Updated mock Settings stubs and test cases in 'test_friendship_evolution.py' to confirm evolutions trigger successfully even when overridden to False. Added a Pichu evolution readiness test case.

```text
src/Ankimon/ankimon_items_web/settings_schema.py |  1 -
 src/Ankimon/functions/pokedex_functions.py       |  4 +++-
 src/Ankimon/lang/setting_description.json        |  1 -
 src/Ankimon/lang/setting_name.json               |  1 -
 src/Ankimon/pyobj/settings.py                    |  2 ++
 src/Ankimon/pyobj/settings_window.py             |  1 -
 tests/test_friendship_evolution.py               | 19 ++++++++++++++++---
 7 files changed, 21 insertions(+), 8 deletions(-)
```

---

### e7a73c71 - tier fallback hierarchy fix

```text
src/Ankimon/functions/encounter_functions.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 3c7b6776 - chore: remove Qt screens superseded by the web shell

These dialogs were replaced by the web Profile/Team screens earlier in
this PR (their menu entries now route to the shell) and are now fully
unreferenced — delete the dead code:
- pyobj/trainer_card_window.py (TrainerCardGUI -> web Profile)
- gui_classes/pokemon_team_window.py (PokemonTeamDialog -> web Team)
- gui_classes/choose_trainer_sprite_graphical.py (TrainerSpriteGraphicalDialog
  -> web sprite picker)
- pyobj/achievements_dialog.py (AchievementsDialog -> Profile badge case)

AchievementWindow is intentionally left for now — it's still imported and
instantiated in singletons.py, so it needs a separate small unwiring.

```text
.../gui_classes/choose_trainer_sprite_graphical.py |  82 ---
 src/Ankimon/gui_classes/pokemon_team_window.py     | 570 ---------------------
 src/Ankimon/pyobj/achievements_dialog.py           |  63 ---
 src/Ankimon/pyobj/trainer_card_window.py           | 137 -----
 4 files changed, 852 deletions(-)
```

---

### 877fe760 - fix(profile+team): harden against review-flagged edge cases

Address gemini-code-assist review on the PR:
- _run_live_refresh: guard the isVisible() check with try/except RuntimeError
  — the deferred QTimer can fire after the dialog's C++ object is deleted
  (window closed), which would otherwise crash.
- TeamBridge.saveTeam: reject a parsed payload that isn't a list, so a
  non-list JSON (e.g. a bare number) can't TypeError downstream.
- _friendship_stub: wrap the friendship int() conversion so corrupted data
  can't crash the whole profile page load.

```text
src/Ankimon/ankimon_items_web/shop_obj.py       | 9 ++++++++-
 src/Ankimon/ankimon_profile_web/profile_data.py | 6 +++++-
 2 files changed, 13 insertions(+), 2 deletions(-)
```

---

### 26b5727d - refactor(nav): unify the dropdown CSS into one shared stylesheet

The nav-switcher/dropdown styles were duplicated across three stylesheets
(profile.css, shop.css, and ankidex/nav-switcher.css). Extract them into a
single ankimon_items_web/nav-switcher.css (a superset — includes shop's
:disabled / .nav-menu-status / .app-logo.icon-gear extras and the
navMenuPop keyframe the filter dropdowns also use) and load it on all five
screens. Removed the inlined copies from profile.css and shop.css and
deleted ankidex/nav-switcher.css. Each page still defines the theme custom
properties the shared rules consume, so nothing else changes.

```text
src/Ankimon/ankidex/ankidex.html                   |   2 +-
 .../nav-switcher.css                               |  43 ++++-
 src/Ankimon/ankimon_items_web/settings.html        |   3 +-
 src/Ankimon/ankimon_items_web/shop.css             | 194 ---------------------
 src/Ankimon/ankimon_items_web/shop.html            |   3 +-
 src/Ankimon/ankimon_profile_web/profile.css        |  76 --------
 src/Ankimon/ankimon_profile_web/profile.html       |   3 +-
 src/Ankimon/ankimon_profile_web/team.html          |   3 +-
 8 files changed, 45 insertions(+), 282 deletions(-)
```

---

### 00a0530e - refactor(nav): consolidate the dropdown switcher into one shared module

The dropdown nav wiring (open/close, click-outside, Escape, route to
nav.open<Screen>()) was duplicated four times — profile-nav.js,
ankidex/nav-switcher.js, and inline in shop.js and settings.js — so adding
a screen meant editing all four.

Replace them with a single ankimon_items_web/nav-switcher.js exposing
wireNavSwitcher(nav) (pages that build their own QWebChannel pass nav from
it) and initNavSwitcher() (for Ankidex, which has no channel of its own and
lets the module build the single channel). All five screens now load it;
the two old copies are deleted and the shop/settings inline copies removed.
Routing is generic (open + Capitalized screen name) and the current screen's
active menu item is a no-op, so no screen-specific branches remain.

```text
src/Ankimon/ankidex/ankidex.html                   |  5 +-
 src/Ankimon/ankidex/nav-switcher.js                | 70 ----------------------
 .../nav-switcher.js}                               | 35 +++++++----
 src/Ankimon/ankimon_items_web/settings.html        |  3 +-
 src/Ankimon/ankimon_items_web/settings.js          | 39 ++----------
 src/Ankimon/ankimon_items_web/shop.html            |  3 +-
 src/Ankimon/ankimon_items_web/shop.js              | 49 ++-------------
 src/Ankimon/ankimon_profile_web/profile.html       |  2 +-
 src/Ankimon/ankimon_profile_web/profile.js         |  2 +-
 src/Ankimon/ankimon_profile_web/team.html          |  2 +-
 src/Ankimon/ankimon_profile_web/team.js            |  2 +-
 11 files changed, 47 insertions(+), 165 deletions(-)
```

---

### aaccc174 - fix(profile+team): address code-review findings

- team.js: carry the resolved forme/mega sprite into a team slot when it's
  assigned via the roster picker (previously dropped, so a mega 404'd to
  0.png until reload); don't overwrite the shown CP with a missing refined
  value.
- profile.js: roll the avatar back (sprite_url + re-render) when setSprite
  is rejected; inline rename now cancels on blur — only Enter saves — so
  clicking away never silently saves a half-typed name.
- profile_data.py: _calc_cp recomputes on a stored cp of 0 (not just None);
  format_pokemon_name resolves the plain species name through the shared
  utils.POKEMON_NAME_LOOKUP instead of a parallel capitalizer, so the web
  screens match the rest of the app's display names.
- menu_buttons.py: only set the one-shot profile action when actually
  opening the Profile screen, so opening another screen can't clobber or
  strand it.
- team.js: comment clarifying TYPE_FX is intentionally independent of the
  battle engine's eff_chart.json (older/simplified values).

```text
src/Ankimon/ankimon_profile_web/profile.html    |  2 +-
 src/Ankimon/ankimon_profile_web/profile.js      | 11 +++++--
 src/Ankimon/ankimon_profile_web/profile_data.py | 39 ++++++++++++++++---------
 src/Ankimon/ankimon_profile_web/team.html       |  2 +-
 src/Ankimon/ankimon_profile_web/team.js         |  9 ++++--
 src/Ankimon/menu_buttons.py                     |  7 +++--
 6 files changed, 47 insertions(+), 23 deletions(-)
```

---

### 0bf39dbf - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/shop_obj.py       |  16 +-
 src/Ankimon/ankimon_profile_web/profile_data.py | 394 +++++++++++++++++++----
 src/Ankimon/battle_loop.py                      |  47 ++-
 src/Ankimon/functions/encounter_functions.py    | 402 +++++++++++++++---------
 src/Ankimon/menu_buttons.py                     |  17 +-
 src/Ankimon/pyobj/trainer_card.py               |  34 +-
 src/Ankimon/reloader.py                         |  39 ++-
 7 files changed, 694 insertions(+), 255 deletions(-)
```

---

### a433c401 - feat(profile+team): web Profile & Team screens in the unified shell

Move the Trainer Card, Team, Choose-Sprite and Achievements flows out of
their old Qt dialogs and into the AnkimonItemsWeb shell as two new web
screens, alongside Items / Ankidex / Settings.

- ankimon_profile_web/: Profile (trainer card, stat tiles, team showcase,
  recently caught, badge case, sprite picker, inline trainer-name rename)
  and Team (roster picker with CP sort + type filters, XP Share, and
  Strengths/Weaknesses/Resistances type analysis).
- Shell hosting in shop_obj.py (TrainerBridge / TeamBridge, screen
  loading, payloads); menu routing in menu_buttons.py; shell teardown on
  reload in reloader.py so web-asset changes take effect.
- Live stat updates: singletons.notify_stats_changed() fans gameplay
  events (catch, XP/level, cash) to whichever shell screen is open with no
  manual reload — hooked at the catch / XP / cash chokepoints. Best-effort
  and screen-agnostic. See ankimon_items_web/LIVE_UPDATES.md.
- Navigator polish across all five screens: item-sprite icons, de-carded
  larger icons, consistent header sizing, and Team-above-Profile order.

Mega/forme sprites resolve via the addon's get_sprite_path (base-species
fallback); CP reads the stored value so it matches the picker. Also
gitignore local tooling (.claude/, __pycache__/).

```text
.gitignore                                      |    2 +
 src/Ankimon/ankidex/ankidex.html                |   20 +-
 src/Ankimon/ankidex/nav-switcher.css            |   19 +-
 src/Ankimon/ankidex/nav-switcher.js             |    2 +
 src/Ankimon/ankimon_items_web/LIVE_UPDATES.md   |  171 ++++
 src/Ankimon/ankimon_items_web/settings.html     |   25 +-
 src/Ankimon/ankimon_items_web/settings.js       |    2 +
 src/Ankimon/ankimon_items_web/shop.css          |   19 +-
 src/Ankimon/ankimon_items_web/shop.html         |   24 +-
 src/Ankimon/ankimon_items_web/shop.js           |   23 +-
 src/Ankimon/ankimon_items_web/shop_obj.py       |  270 +++++-
 src/Ankimon/ankimon_profile_web/__init__.py     |    0
 src/Ankimon/ankimon_profile_web/profile-nav.js  |   62 ++
 src/Ankimon/ankimon_profile_web/profile.css     | 1050 +++++++++++++++++++++++
 src/Ankimon/ankimon_profile_web/profile.html    |  152 ++++
 src/Ankimon/ankimon_profile_web/profile.js      |  614 +++++++++++++
 src/Ankimon/ankimon_profile_web/profile_data.py |  809 +++++++++++++++++
 src/Ankimon/ankimon_profile_web/team.html       |  146 ++++
 src/Ankimon/ankimon_profile_web/team.js         |  641 ++++++++++++++
 src/Ankimon/battle_loop.py                      |    8 +
 src/Ankimon/functions/encounter_functions.py    |    9 +
 src/Ankimon/menu_buttons.py                     |   53 +-
 src/Ankimon/pyobj/trainer_card.py               |    9 +
 src/Ankimon/reloader.py                         |    6 +-
 src/Ankimon/singletons.py                       |   26 +-
 25 files changed, 4056 insertions(+), 106 deletions(-)
```

---

### a2e65e54 - feat: enhance Shop/Bag Pokémon picker with evolution eligibility, CP display, and high-performance caching

This update overhaul the Pokémon selection window used for evolution and held items, providing a smoother, more informative, and highly optimized experience for players with large collections.

Key Improvements:
- Evolution Eligibility & Smart Filtering:
  - Dynamically filters the picker to show ONLY compatible targets when an evolution item is selected.
  - Adds green border/glow highlighting and priority sorting for eligible Pokémon.
  - Optimized O(1) backend checking using the pre-built pokedex index, eliminating redundant file I/O and CSV parsing.

- Enhanced UI/UX:
  - Added visibility for CP and Level on every Pokémon card in the picker grid.
  - Implemented a two-stage sprite fallback system (Specific Form -> Base Species -> Placeholder) to ensure all Pokémon (Mega, Regional, etc.) have visual representation.
  - Eliminated visual flicker by pre-rendering cached lists before displaying the modal.

- Advanced State & Cache Management:
  - Introduced 'choicesContext' to ensure accurate list refreshing when switching between different evolution stones.
  - Implemented high-performance instance caching for the base team list to maintain near-instant open times for regular item usage.
  - Fixed various edge cases where stale eligibility data could leak into non-evolution contexts.

Technical Details:
- Modified shop_obj.py to handle optimized data enrichment (CP, Base ID, Eligibility) in a single pass.
- Updated shop.js to manage modal state and keyed DOM reconciliation for flicker-free transitions.
- Added specialized styling in shop.css for new badges and eligibility indicators.

```text
src/Ankimon/ankimon_items_web/shop.css    |  27 +++++++-
 src/Ankimon/ankimon_items_web/shop.js     |  60 +++++++++++++---
 src/Ankimon/ankimon_items_web/shop_obj.py | 110 +++++++++++++++++++++++-------
 3 files changed, 161 insertions(+), 36 deletions(-)
```

---

### e89a25b8 - fix: add defensive NoneType checks for mw and reviewer before HUD update

- Added guard check in new_pokemon() to prevent any possible NoneType errors.
- Resolved local scoping gotcha in Python by utilizing the globally imported mw directly instead of a local import statement.

```text
src/Ankimon/functions/encounter_functions.py | 11 ++++++-----
 1 file changed, 6 insertions(+), 5 deletions(-)
```

---

### 24da44fb - fix: add update_hud parameter to new_pokemon to resolve manual mode HUD refreshes

- Added optional parameter update_hud: bool = False to new_pokemon() in encounter_functions.py to trigger immediate HUD updates on demand.
- Passed update_hud=True to new_pokemon() calls inside manual catch, defeat, and dev hotkey triggers in reviewer_ui.py to immediately refresh the WebView screen on manual transitions.
- Kept automatic battle transitions fully optimized (update_hud=False) to avoid redundant renders and maintain zero study lag.
- Added test_new_pokemon_with_update_hud and adjusted test_hotkey_0_updates_life_bar assertions in test_reviewer_ownership_cache.py.

```text
src/Ankimon/functions/encounter_functions.py | 14 ++++---
 src/Ankimon/reviewer_ui.py                   |  6 +--
 tests/test_reviewer_ownership_cache.py       | 61 ++++++++++++++++++++++++++--
 3 files changed, 70 insertions(+), 11 deletions(-)
```

---

### 428489ec - revert: restore global HUD updates in new_pokemon to prevent manual mode lag

- Reverted the optimization that removed the update_life_bar call inside new_pokemon().
- This ensures that manual catch/defeat shortcut triggers and HUD buttons immediately refresh the screen without requiring a card flip.
- Removed explicit update_life_bar calling from test_encounter_shortcut_function to avoid duplication.
- Updated unit test test_hotkey_0_triggers_new_encounter to match.

```text
src/Ankimon/functions/encounter_functions.py | 6 +++++-
 src/Ankimon/reviewer_ui.py                   | 6 ------
 tests/test_reviewer_ownership_cache.py       | 8 +-------
 3 files changed, 6 insertions(+), 14 deletions(-)
```

---

### b299e113 - Merge pull request #473 from AIbrahimv2/shop-reroll-skip-confirm

feat(shop): daily skip-confirm option + slimmer reroll modal

---

### 22d440e9 - perf: optimize defeat transitions, remove redundant commits, and restore hotkey 0 refresh

- Implemented an in-memory database cache (self._all_pokemon_ids_cache) in AnkimonDB to avoid synchronous SQLite JSON scanning during every random encounter generation.
- Handled cache invalidation inside database mutators (save_pokemon, delete_pokemon, replace_pokemon, save_main_pokemon, add_to_history, mark_as_caught, switch_database).
- Removed redundant save_pokemon call when saving main pokemon progress, eliminating duplicate serialization and slow consecutive SQLite commits.
- Stripped redundant WebView rendering (update_life_bar) from new_pokemon() to prevent double-rendering and visual lag during gameplay transitions.
- Restored explicit HUD rendering in test_encounter_shortcut_function so hotkey 0 manually updates the WebView correctly.
- Added comprehensive unit tests in test_reviewer_ownership_cache.py validating cache behavior, invalidation, and hotkey 0 refresh.

```text
src/Ankimon/functions/encounter_functions.py |   8 +-
 src/Ankimon/pyobj/database_manager.py        |  20 ++
 src/Ankimon/reviewer_ui.py                   |   6 +
 tests/test_reviewer_ownership_cache.py       | 371 +++++++++++++++++++++++++++
 4 files changed, 399 insertions(+), 6 deletions(-)
```

---

### a08232db - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 18 ++++++++++++++----
 1 file changed, 14 insertions(+), 4 deletions(-)
```

---

### efe2f5af - feat(shop): add daily skip-confirm option, simplify reroll modal

Adds a "Don't ask again today" checkbox to the reroll confirmation
modal that suppresses the confirmation for the rest of the day. The
preference is stored in user_data with a date stamp and treated as
False whenever the date no longer matches today's, giving the
"reset every day" behavior without a cleanup pass — same pattern as
get_daily_items.

Also tightens the modal itself: drops the verbose body paragraph,
shrinks the icon, and replaces the boxy "Balance after" panel with
an inline "cost -> balance left" summary.

```text
src/Ankimon/ankimon_items_web/shop.css    | 120 ++++++++++++++++++++----------
 src/Ankimon/ankimon_items_web/shop.html   |  14 ++--
 src/Ankimon/ankimon_items_web/shop.js     |  19 +++++
 src/Ankimon/ankimon_items_web/shop_obj.py |  29 ++++++++
 4 files changed, 136 insertions(+), 46 deletions(-)
```

---

### 729fa96f - fix: resolve PC Box flashing blank white window popups

Root cause: widget.setParent(None) in clear_layout() turned animating widgets into temporary top-level windows.

Fixed by keeping widgets parented during deleteLater(), explicitly parenting grid elements, and deferring QMovie starts to showEvent/hideEvent.

```text
src/Ankimon/pyobj/pc_box.py | 28 +++++++++++++++++-----------
 1 file changed, 17 insertions(+), 11 deletions(-)
```

---

### ed58fde5 - feat: add move-based manual evolutions & correct evolution form distinction

This commit fully implements move-based level-up manual evolutions in the PC Box, resolves key normalization lookup discrepancies, prevents regional form evolution leaks, and robustly handles evolved nickname updates.

Key changes:
- Move-based Level-Up Evolutions: Enabled 'levelMove' type evolutions by defaulting 'min_level = 1' when omitted in 'pokedex.json'. Taught attack checks in '_level_readiness' verify if the required move (e.g. 'Mimic' for Mime Jr.) is learned, showing appropriate warnings/badges and the Evolve button.
- Punctuation-Insensitive Key Matching: Strips dots ('.') and colons (':') in key normalizers inside 'pokedex_functions.py' and 'friendship_evolution.py', correcting lookups for 'Mr. Mime' ('mrmime') and 'Type: Null' ('typenull').
- Form-Aware Evolution Fallback Guard: Prevents Kantonian Mr. Mime from incorrectly showing as evolvable into Mr. Rime by treating 'pokedex.json' as the absolute source of truth when a species is present, bypassing legacy CSV search fallbacks.
- Default Nickname Evolution Update: Resolves a bug where default nicknames (like 'Mime Jr.') were retained as custom nicknames upon evolution due to raw prevo identifier mismatch ('mime-jr'). Normalizes strings before comparison and updates to the pretty evolved form pretty name.
- Details Panel & Grid Cache Sync: Included attacks in 'pkmn_data_stub' inside 'pokemon_details.py' and direct JSON extraction of attacks in 'fetch_filtered_pokemon()' inside 'pc_box.py'.
- Evolve Window C++ Lifecycle Guard: Gracefully recreates the 'EvoWindow' if the underlying C++ Qt widget has been closed or garbage-collected.
- CSS and JS layout improvements in Ankidex for better compound requirement presentation.
- Automated Tests: Added tests validating mime jr readiness, Mr. Mime form distinction, and evolution nickname updates. All 153 tests pass perfectly.

```text
src/Ankimon/ankidex/ankidex.css               |  2 +-
 src/Ankimon/ankidex/ankidex.js                | 36 +++++++----
 src/Ankimon/ankidex/ankidex_obj.py            |  2 +-
 src/Ankimon/functions/encounter_functions.py  | 12 ++++
 src/Ankimon/functions/friendship_evolution.py | 60 +++++++++++++++---
 src/Ankimon/functions/pokedex_functions.py    | 15 +++--
 src/Ankimon/gui_classes/pokemon_details.py    |  1 +
 src/Ankimon/pyobj/evolution_window.py         | 21 ++++++-
 src/Ankimon/pyobj/item_window.py              |  3 +
 src/Ankimon/pyobj/pc_box.py                   |  4 +-
 src/Ankimon/pyobj/pokemon_obj.py              |  2 +-
 tests/test_evolution_item_consumption.py      | 88 +++++++++++++++++++++++++++
 tests/test_location_evolutions.py             | 57 +++++++++++++++++
 13 files changed, 272 insertions(+), 31 deletions(-)
```

---

### 51b5d8ba - fix: add active_region default to settings config

```text
src/Ankimon/pyobj/settings.py | 1 +
 1 file changed, 1 insertion(+)
```

---

### d02465f6 - feat(shell): implement QStackedWidget multi-view in AnkimonItemsWeb to eliminate load delays

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 84 +++++++++++++++++++++----------
 1 file changed, 57 insertions(+), 27 deletions(-)
```

---

### 8bb2715d - merge: port Settings into unified shell (#465) by AIbrahimv2 (Discord Krow)

Port all Ankimon settings into the unified shell window with geometry persistence.

---

### 2a2e9beb - style: auto ruff format

```text
src/Ankimon/pyobj/item_window.py | 9 ++++++---
 1 file changed, 6 insertions(+), 3 deletions(-)
```

---

### e39c6cf0 - feat(evolution): region-aware level evolution — prefer Galarian/Alolan target when active_region is set

check_evolution_for_pokemon() and _level_readiness() now read the misc.active_region setting and filter evolution candidates accordingly:
- If a candidate has an evoRegion matching active_region (case-insensitive), it is preferred and selected.
- If a candidate has an evoRegion that doesn't match active_region, it is excluded.
- If a candidate has no evoRegion, but a sibling has one matching active_region, the base target is suppressed in favor of the regional target.
- Also adds support for evoType=='levelMove' (e.g., Wyrdeer, Mr. Mime-Galar) by checking the Pokémon's current move list before approving the evolution.
- Removes the now-redundant legacy CSV fallback (species CSV was superseded by pokedex.json in the priority check path).

Region comparisons are fully case-insensitive with null guards throughout both friendship_evolution.py and pokedex_functions.py.

Tests (test_location_evolutions.py):
- 7 comprehensive tests covering Pikachu->Raichu (no region), Exeggcute->Alolan Exeggutor (Alola region), Koffing->Galarian Weezing, Hisuian item evolutions, move-based evolutions (Stantler->Wyrdeer), and friendship/time filtering.

```text
src/Ankimon/functions/friendship_evolution.py |  43 +++++
 src/Ankimon/functions/pokedex_functions.py    | 244 ++++++++++++++++++--------
 tests/test_location_evolutions.py             | 187 ++++++++++++++++++++
 3 files changed, 399 insertions(+), 75 deletions(-)
```

---

### 1376e062 - feat(evolution): stone item consumption on confirm — deduct quantity and refresh item windows

When a player uses an evolution stone (Fire Stone, Ice Stone, etc.) and confirms the evolution, the item's quantity is now decremented by 1 in the database. Both the legacy ItemWindow (PyQt) and the new web-based AnkimonItemsWeb are refreshed if open.

Implementation details:
- item_name is propagated from ItemWindow.Check_Evo_Item() -> ask_pokemon_evo() -> _ask_pokemon_evo_layout() -> evolve_pokemon() via a new optional parameter.
- after saving the evolved Pokemon to the DB, evolve_pokemon() calls db.update_item_quantity(item_name, -1) and invokes renewWidgets()/update_ui_data() on open widgets/dialogs to refresh them in real-time.

Tests:
- test_evolution_item_consumption.py stubs aqt and PyQt widgets, and verifies that db.update_item_quantity('fire-stone', -1) is called exactly once when evolve_pokemon() is called with Eevee and Fire Stone.

```text
src/Ankimon/pyobj/evolution_window.py    |  27 +++++--
 tests/test_evolution_item_consumption.py | 135 +++++++++++++++++++++++++++++++
 2 files changed, 157 insertions(+), 5 deletions(-)
```

---

### 67978406 - fix(learnset): add PokéAPI suffix-cleaning and 3-tier fallback to resolve Galarian Darmanitan 'no learnset' error

Root cause: PokéAPI uses suffixed identifiers like 'darmanitan-galar-standard', 'giratina-altered', 'meowstic-female' that don't match the Smogon learnset keys 'darmanitangalar', 'giratina', 'meowsticf'. A scan of the learnset data confirmed 62 Pokémon affected by this mismatch.

Fix (learnset_retrieval.py):
- Adds clean_pokeapi_name() which strips known cosmetic PokéAPI suffixes (-standard, -normal, -altered, -land, -red-striped, -male, -ordinary, -aria, -average, -disguised, -amped, -ice, -single-strike, -zero, -curly, -two-segment, -green-plumage, -plant, -mask) and maps '-female' -> 'f'.
- Resolution tier 1: direct key normalization (existing behaviour)
- Resolution tier 2: apply clean_pokeapi_name() + normalize the cleaned result
- Resolution tier 3: reverse-lookup canonical key via pokedex ID index
- Existing Mega/Gmax/Primal base-form fallback now correctly uses the normalized (not raw) name as the species search key.

Tests (test_learnset_retrieval.py):
- TestLearnsetMismatches.test_clean_pokeapi_name_suffixes — verifies all major suffix-stripping cases including -standard, -female, -altered, -mask
- TestLearnsetMismatches.test_get_learnset_moves_with_mismatched_pokeapi_names — verifies full retrieval pipeline with suffixed input names

```text
src/Ankimon/functions/learnset_retrieval.py | 48 ++++++++++++++++++++++++++---
 tests/test_learnset_retrieval.py            | 24 +++++++++++++++
 2 files changed, 67 insertions(+), 5 deletions(-)
```

---

### 9482e6bf - merge: in-shell Pokémon picker for evolution and held items (#466) by AIbrahimv2 (Discord Krow)

This merges PR #466 by AIbrahimv2 (Discord Krow), implementing a performance-optimized inline card grid modal for choosing targets of evolution stones and held items. It avoids QInputDialog popups, renders up to 60 cards with debounced search, uses a compact JSON payload for big databases, and includes a fallback sprite loader to gracefully display greyed-out placeholders at reduced opacity for missing assets.

---

### d5d3f82b - merge: port Settings into unified shell (#465) by AIbrahimv2 (Discord Krow)

This merges PR #465 by AIbrahimv2 (Discord Krow), porting all Ankimon settings into the unified QDialog shell window. It adds the Settings screen as the third sidebar option (alongside Items and Ankidex), implements declarative group parsing, validation/clamping, and integrates base64 window geometry persistence alongside de-minimization logic.

---

### fd08c678 - fix(shop): graceful sprite fallback for missing item images and navigation polish

```text
src/Ankimon/ankimon_items_web/shop.js | 28 ++++++++++++++++++++++++----
 1 file changed, 24 insertions(+), 4 deletions(-)
```

---

### 575a02da - fix(shop,ankidex): remove backdrop-filter blur to fix Windows DWM render flicker

```text
src/Ankimon/ankidex/ankidex.css        |  1 -
 src/Ankimon/ankimon_items_web/shop.css | 24 ++++++++++++++++++++----
 2 files changed, 20 insertions(+), 5 deletions(-)
```

---

### 97e90402 - fix(items): pass item_name to evolution dialog and load evolution items from pokedex.json

```text
src/Ankimon/pyobj/item_window.py | 33 ++++++++++++++-------------------
 1 file changed, 14 insertions(+), 19 deletions(-)
```

---

### 76d53aa1 - feat(shop): persist and restore window geometry; de-minimize on menu open

Adds two geometry helpers to AnkimonItemsWeb:
  - _restore_geometry(): reads base64 Qt geometry blob from mw.pm.profile on init
  - _save_geometry(): encodes and persists current geometry to profile on close/hide
    (skips save when minimized to avoid persisting an offscreen state)

Overrides show() so that clicking any menu item (Items, Settings, Mart, Ankidex)
on a minimized window calls showNormal() then raise_() + activateWindow(), instead
of silently failing. Uses the same storage pattern as pc_box.py.

Also hoists _open_shell_at() in menu_buttons.py to function scope (outside the
database_complete branch) so the Mart action can route through it, ensuring the
Mart button also de-minimizes and restores the window correctly.

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 32 +++++++++++++++++++++++++++++++
 src/Ankimon/menu_buttons.py               | 19 ++++++++++--------
 2 files changed, 43 insertions(+), 8 deletions(-)
```

---

### c1a3721b - fix(shop): resolve AttributeError on Qt 6.6.2 — setContextMenuPolicy belongs to QWidget not QWebEnginePage

In Anki 25.02.5 / Qt 6.6.2, constructing AnkimonItemsWeb raised:
  AttributeError: 'QWebEnginePage' object has no attribute 'setContextMenuPolicy'

setContextMenuPolicy() is defined on QWidget (and its subclass QWebEngineView),
not on QWebEnginePage. Moved the call from self.webview.page() to self.webview
directly. Fixes startup crash in all Qt 6.x environments.

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 0ed6fda3 - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 4 +---
 1 file changed, 1 insertion(+), 3 deletions(-)
```

---

### 0ab9938c - feat(items): in-shell Pokémon picker for evolution + held items

Replaces the QInputDialog popup that Use opened for evolution items and
held items with a card-grid modal that lives inside the Items window —
same Ankidex card styling, search, and active/shiny/held marks.

Performance notes:
- Choices are lazy-fetched on first picker open (not shipped with the
  inventory payload — for players with 10k+ captures the payload would
  be multiple MB on every push). Cached on both sides for the lifetime
  of the window; invalidated after team-mutating actions.
- Render is capped at 60 cards with a "+ X more — type to refine"
  footer past the cap, so even very large teams don't blow out the DOM
  or the sprite-decode queue.
- Compact field names on the wire (id/p/n/l/s/m/h/nk), sprite URL
  reconstructed JS-side from pokedex_id.
- Explicit img width/height + min-height on the card lock the grid
  layout before sprites decode, no more collapsing rows.

Routing:
- bridge.useItemOnPokemon(item, individual_id) calls Check_Evo_Item
  directly for evolution items, _give_held_item_by_id for held items —
  no QInputDialog. dispatch_use still handles heal/fossil/pokeball
  paths that don't need a target picker.

```text
src/Ankimon/ankimon_items_web/shop.css    | 290 ++++++++++++++++++++++++++++++
 src/Ankimon/ankimon_items_web/shop.html   |  25 +++
 src/Ankimon/ankimon_items_web/shop.js     | 285 ++++++++++++++++++++++++++++-
 src/Ankimon/ankimon_items_web/shop_obj.py | 146 ++++++++++++++-
 4 files changed, 744 insertions(+), 2 deletions(-)
```

---

### 75ccad0d - fix(items+settings): UX polish (save bug, scroll-spy, icons, flash, loading)

Settings save:
- Settings.save_config(config) needs the dict; previous call was nullary
  and silently failed (kept the bug hidden because settings_obj.set had
  already mutated the in-memory config, so subsequent clicks reported
  success without actually persisting anything to disk).

Scroll-spy and section nav:
- Replaced fragile offsetTop/scrollTop math (then IntersectionObserver,
  which also missed short bottom sections) with: click-wins suppress-spy
  for 1.5s + reading-line check on scroll + nearest-below fallback at
  max scroll. Every section is now reachable, including Study/Generations
  on short pages.
- scrollToGroup now computes the scroll target via rect math
  (elRect.top - scrollerRect.top + scrollerScrollTop) so the section
  header lands consistently, with 32px breathing room below the top bar.
- Strengthened sidebar active state: brighter blue tint + 3px left
  accent bar via inset box-shadow + count badge picks up the accent.

Section design:
- Dropped the card chrome from .settings-subgroup so subgroups render
  the same way as top-level groups (bold header with bottom border, no
  card background) — visually unified.
- Flash highlight on nav jump now uses a ::before pseudo with
  asymmetric inset (negative top, positive bottom) so the tinted area
  is ~14px on all four sides instead of doubled at the bottom from the
  row's internal padding. isolation: isolate on the section establishes
  a stacking context so z-index: -1 on the pseudo stays scoped.

Loading state and visual polish:
- Set the QWebEngineView page background to #0d1117 and add an inline
  <style>html { background: #0d1117 }</style> in each HTML's head, so
  the first paint is dark instead of white.
- Skeleton placeholders (pulsing dim cards/rows) in items grid, settings
  content, and Ankidex pokemon grid; cleared by the existing first
  render of each screen.
- Save button no longer red; now uses neutral blue idle and green when
  dirty. Red was inherited from .nav-action which the Mart's reroll
  needs (destructive action); Save isn't destructive.

Icons:
- Replaced the ⚙ Unicode glyph with an inline SVG gear (Feather style)
  in all three nav dropdowns + sized to 32x32 as the Settings sidebar
  logo. Glyph wasn't filling the icon box.
- Items entry now uses the hyper-potion sprite from user_files for both
  the dropdown icon and the shop.html sidebar logo. Differentiates from
  Ankidex (which keeps the pokeball as its unique identity).

PR #465 review:
- _coerce_incoming raises ValueError on non-coercible numeric input
  instead of silently writing garbage to config (range strings for
  battle.cards_per_round still pass through).
- handle_save_settings wraps the coercion loop in try/except and only
  calls settings_obj.set for keys that actually changed.
- handle_reroll clamps random.sample sizes to min(requested, pool size).
- ItemWindow.Evolve_Fossil returns True/False; dispatch_use checks it
  so the web Items toast reflects the actual outcome.

Save bridge:
- SettingsBridge.saveSettings now takes a JSON string instead of
  QVariant; PyQt's QVariant -> dict auto-unwrap isn't reliable on the
  first invocation (varies by Qt/PyQt version), which made the first
  save click error out.

Section design unification mirrored from PR #464: Items entry uses the
same hyper-potion sprite as the dropdown; Ankidex dropdown entry uses
the pokeball; gen toggles collapse to a chip row; dropped redundant
config keys outside of dev mode.

```text
src/Ankimon/ankidex/ankidex.html            |  13 ++--
 src/Ankimon/ankidex/nav-switcher.css        |  10 ++-
 src/Ankimon/ankimon_items_web/settings.css  | 109 ++++++++++++++++++++++------
 src/Ankimon/ankimon_items_web/settings.html |  49 ++++++++++++-
 src/Ankimon/ankimon_items_web/settings.js   | 103 +++++++++++++++++++++-----
 src/Ankimon/ankimon_items_web/shop.css      |  23 +++++-
 src/Ankimon/ankimon_items_web/shop.html     |  13 ++--
 src/Ankimon/ankimon_items_web/shop_obj.py   |   4 +-
 8 files changed, 264 insertions(+), 60 deletions(-)
```

---

### 6267a602 - fix(items): forward-port PR #464 fixes to #465 (icon, right-click, flicker)

PR #465 branched off #464 before its review-feedback fixes landed, so
those changes weren't visible when running this branch in Anki. Apply
them here too so users on #465 see the same polish without waiting for

- Replace the ✦ Unicode star with the pokeball image for the Ankidex
  entry in all three dropdowns (shop.html, ankidex.html, settings.html).
- Disable the QtWebEngine browser-style right-click menu via
  setContextMenuPolicy(NoContextMenu) on the shell's webview.
- Apply the DocumentFragment + replaceChildren atomic-swap pattern to
  the Items grid render (shop.js) so buy/use/reroll no longer flashes
  an empty grid mid-refresh. Add contain: layout style on .shop-grid
  to scope reflow.
- Same flicker fix applied to the Settings page renderers (settings.js
  renderGroupJumps + renderContent). The save → re-fetch cycle rebuilds
  ~60 setting rows; without the atomic swap, that flashed the entire
  form area on every save.

```text
src/Ankimon/ankimon_items_web/settings.html |  2 +-
 src/Ankimon/ankimon_items_web/settings.js   | 15 +++++++++++----
 src/Ankimon/ankimon_items_web/shop.js       |  1 -
 src/Ankimon/ankimon_items_web/shop_obj.py   |  2 +-
 4 files changed, 13 insertions(+), 7 deletions(-)
```

---

### 1f5f7a3f - fix(settings): address PR #465 review — nav scroll + first-save error

- Section jump-links in the sidebar didn't reliably scroll the content
  pane. scrollIntoView in QtWebEngine sometimes targets the document
  rather than the .content-scroll container. Compute the section's
  offset relative to the scroller and call scroller.scrollTo() directly.
- First click on Save threw "Invalid payload" while the second click
  worked. Root cause: SettingsBridge.saveSettings declared a "QVariant"
  parameter, and PyQt's QVariant → dict auto-unwrap doesn't always
  succeed on the first invocation (varies by Qt/PyQt version). Round-
  trip the payload as a JSON-encoded str instead — JS does
  JSON.stringify(state.edits), Python json.loads on receipt. Removes
  the type-conversion ambiguity entirely, so saves work on the first
  click every time.

```text
src/Ankimon/ankimon_items_web/settings.js | 14 ++++++++++++--
 src/Ankimon/ankimon_items_web/shop_obj.py | 13 +++++++++++--
 2 files changed, 23 insertions(+), 4 deletions(-)
```

---

### 784c59e4 - style: auto ruff format

```text
src/Ankimon/pyobj/item_window.py | 9 +++++++--
 1 file changed, 7 insertions(+), 2 deletions(-)
```

---

### 922c68f0 - fix(settings): address PR #465 review — validation, save-skip, clamps, fossil status

- _coerce_incoming now raises ValueError when a numeric field receives a
  non-coercible string instead of silently writing the raw string to
  config. Range strings (e.g. "1-3" for battle.cards_per_round) still pass
  through, where validate_and_clamp normalizes them.
- handle_save_settings wraps the coercion loop in a try/except and surfaces
  validation errors to the JS toast. Also snapshots the original config and
  only calls settings_obj.set for keys that actually changed, avoiding
  spurious observer notifications when the payload is mostly unchanged.
  Skip save_config entirely if nothing changed after clamping.
- handle_reroll clamps random.sample sizes to min(requested, pool size).
  Prevents a ValueError crash if either daily pool drops below
  number_of_daily_items.
- ItemWindow.Evolve_Fossil returns True on success and False otherwise.
  dispatch_use checks the return so the web Items toast accurately
  reflects whether the fossil revived (existing ItemLabel button callers
  ignore the new return value — backwards-compatible).

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 47 ++++++++++++++++++++++---------
 src/Ankimon/pyobj/item_window.py          | 14 ++++++---
 2 files changed, 44 insertions(+), 17 deletions(-)
```

---

### 3ec41e61 - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 19 ++++++++++++-------
 1 file changed, 12 insertions(+), 7 deletions(-)
```

---

### 38300ae4 - fix(settings): UX polish + collapse gen toggles into a chip row

- Fix #settings-search input styling — shop.css's pokemon-search / shop-search
  ID rules don't apply here, so the input was rendering with default browser
  chrome. Mirror the same transparent-bg / no-border treatment.
- Trim the sidebar status card from three lines to two: drop the verbose
  "Changes auto-validate on save" subtitle. The "All saved" / "N unsaved"
  state line is the meaningful signal.
- Hide the monospace config-key text (trainer.name, misc.show_tip_on_startup,
  etc.) by default. End users don't need internal identifiers. Surface them
  only when is_dev_mode() returns true — the dev_mode flag rides along in
  the settings payload and JS conditionally renders .setting-key.
- Collapse the 9 per-generation Enabled/Disabled toggles into a single chip
  row. settings_schema.py grows a "chip_group" concept; shop_obj.py emits
  one composite "Enabled Generations" setting with type "chips" listing all
  9 keys + current values; settings.js renders chips styled like the
  Ankidex's type-filter pills. Each chip still maps back to its own
  misc.gen* config key, so the existing save / dirty / dev-key flows all
  work unchanged. Pattern is reusable for any future N-boolean group.

```text
src/Ankimon/ankimon_items_web/settings.css       | 63 ++++++++++++++++++++++++
 src/Ankimon/ankimon_items_web/settings.html      |  1 -
 src/Ankimon/ankimon_items_web/settings.js        | 51 +++++++++++++++++--
 src/Ankimon/ankimon_items_web/settings_schema.py | 30 +++++++----
 src/Ankimon/ankimon_items_web/shop_obj.py        | 38 ++++++++++----
 5 files changed, 160 insertions(+), 23 deletions(-)
```

---

### 66a39dcf - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/settings_schema.py | 18 +++++-----
 src/Ankimon/ankimon_items_web/shop_obj.py        | 45 ++++++++++++++++--------
 src/Ankimon/menu_buttons.py                      |  2 +-
 3 files changed, 41 insertions(+), 24 deletions(-)
```

---

### 5296243e - feat(settings): port Ankimon settings into the unified shell window

Adds Settings as the third screen in the shell, joining Items and Ankidex.
Replaces the legacy QMainWindow-based settings_window.py launch for the
common case — the old class stays alive as a backing service in case
anything still calls it directly.

New module ankimon_items_web/settings_schema.py defines the two-level
group structure (mirroring the legacy window) plus the validation/
clamping rules (cards_per_round int-or-range, cash_reward_interval
5..250, cash_reward_amount 10..2000 with 100:1 ratio cap).

shop_obj.py gains:
- SCREEN_SETTINGS constant + load_screen routing
- SettingsBridge with getSettings() and saveSettings() pyqtSlots
- get_settings_data() — builds the schema payload from the hard-coded
  group structure + cached lang/setting_name.json + cached
  lang/setting_description.json + current settings_obj values
- handle_save_settings() — coerces incoming values back to the type of
  the existing config entry, runs the schema's clamping pass, persists
  via settings_obj.save_config, and refreshes reviewer hotkeys

The web UI (settings.html / settings.css / settings.js) renders each
group as a labelled section with a "Sections" jump-list in the sidebar,
shows per-row dirty markers, and disables Save until something changes.
Search filters by both label and description; collapsed groups auto-hide
when their visible row count drops to zero.

Form primitives: text input, numeric input, dropdown, and a segmented
Enabled/Disabled toggle for booleans. All styled with the existing
Ankidex tokens (dark only — light theme remains a separate effort).

The nav switcher in all three pages (Items, Ankidex, Settings) gains a
Settings option. Menu wiring updated so the Tools → Settings entry
opens the shell at the Settings screen instead of the legacy window.

```text
src/Ankimon/ankidex/ankidex.html                 |   7 +
 src/Ankimon/ankidex/nav-switcher.js              |   3 +-
 src/Ankimon/ankimon_items_web/settings.css       | 332 ++++++++++++++++
 src/Ankimon/ankimon_items_web/settings.html      | 110 ++++++
 src/Ankimon/ankimon_items_web/settings.js        | 466 +++++++++++++++++++++++
 src/Ankimon/ankimon_items_web/settings_schema.py | 199 ++++++++++
 src/Ankimon/ankimon_items_web/shop.html          |   7 +
 src/Ankimon/ankimon_items_web/shop.js            |   9 +-
 src/Ankimon/ankimon_items_web/shop_obj.py        | 199 +++++++++-
 src/Ankimon/menu_buttons.py                      |   5 +-
 10 files changed, 1332 insertions(+), 5 deletions(-)
```

---

### be6f8ff8 - fix(pc): prevent AttributeError when refreshing grid before PC Box is initialized

```text
src/Ankimon/pyobj/item_window.py    | 3 ++-
 src/Ankimon/pyobj/pokemon_trade.py  | 4 +++-
 src/Ankimon/pyobj/starter_window.py | 4 +++-
 3 files changed, 8 insertions(+), 3 deletions(-)
```

---

### 90481102 - merge: merge PR #464 by AIbrahimv2 (Krow on Discord)

- Unifies Mart, Item Bag, and Ankidex inside a single web-based QDialog shell window (AnkimonItemsWeb)
- Introduces state-aware cards showing stock, owned counts, category pills, price tags, and custom TM type-glows
- Adds smooth in-place dropdown navigation transitions between screens to eliminate close/reopen window flickering
- Improves performance via O(1) CSV dictionary lookups, learning pool caching, and live profile-switching refreshes
- Resolves Windows DWM/repaint flickering using Keyed DOM Reconciliation (DOM Diffing/Re-use) and backdrop-filter optimizations

---

### 16bed550 - style: auto ruff format

```text
src/Ankimon/ankidex/ankidex_obj.py        | 147 ++++++++++++++++++++++--------
 src/Ankimon/ankimon_items_web/shop_obj.py |   4 +-
 2 files changed, 110 insertions(+), 41 deletions(-)
```

---

### 225b76ed - fix(shop): resolve Windows DWM flickering, implement Keyed DOM Reconciliation, and fix TM accuracy display

```text
src/Ankimon/ankidex/ankidex_obj.py        |   6 +-
 src/Ankimon/ankimon_items_web/shop.css    |   2 -
 src/Ankimon/ankimon_items_web/shop.js     | 180 +++++++++++++++++++++++++++---
 src/Ankimon/ankimon_items_web/shop_obj.py |   9 +-
 src/Ankimon/singletons.py                 |   3 +
 5 files changed, 176 insertions(+), 24 deletions(-)
```

---

### 590300ec - Merge pull request #463 from AIbrahimv2/feature/restart-shortcut (Dev feature)

feat(menu): add Ctrl+Shift+R shortcut for Restart Ankimon

---

### af44b58c - Merge pull request #462 from AIbrahimv2/fix/ankidex-empty-state-centering

style(ankidex): center empty-state in viewport with balanced vertical rhythm

---

### 04adddd9 - fix: infinite cash rewards on card review by correcting day_cutoff subtraction

- Refactored get_total_reviews to use direct SQLite queries against Anki's revlog table, ensuring language-agnostic and robust review count retrieval.

- Corrected the time filter by subtracting 24 hours (86400 seconds) from tomorrow's day_cutoff, shifting the timestamp to today's rollover cutoff rather than tomorrow's future boundary.

- Added thorough unit tests in tests/test_ankimon_tracker.py with isolated DynamicMockModule stubs to ensure full coverage and pristine test environment isolation.

```text
src/Ankimon/pyobj/ankimon_tracker.py |  23 +++++--
 tests/test_ankimon_tracker.py        | 113 +++++++++++++++++++++++++++++++++++
 2 files changed, 130 insertions(+), 6 deletions(-)
```

---

### a6e8709c - fix(items): kill white flash, add skeletons, swap Items icon to hyper-potion

Visual loading polish:
- Set QWebEngineView page background to #0d1117 and add inline
  <style>html { background: #0d1117 }</style> in shop.html and
  ankidex.html. The first paint is now dark instead of the white default
  that flashed between window-show and full CSS application.
- Skeleton placeholders (pulsing dim cards) in the items grid and the
  ankidex pokemon-grid so the main content area shows structure during
  the load window. Each page's first render replaces the skeletons with
  real cards (renderGrid uses replaceChildren; ankidex.js does
  innerHTML='').

Identity icons:
- Replaced the Items pokeball with the hyper-potion sprite in both the
  shop.html sidebar logo and the Items dropdown entries (shop.html +
  ankidex.html). Ankidex keeps the pokeball as its own unique identity.
  Sizing comes from existing .app-logo and .nav-menu-icon img rules;
  added .icon-item-sprite for image-rendering: pixelated at small sizes.

```text
src/Ankimon/ankidex/ankidex.html          | 36 +++++++++++++++++++++++++++++--
 src/Ankimon/ankidex/nav-switcher.css      |  6 ++++++
 src/Ankimon/ankimon_items_web/shop.css    |  8 +++++++
 src/Ankimon/ankimon_items_web/shop.html   | 33 +++++++++++++++++++++++++---
 src/Ankimon/ankimon_items_web/shop_obj.py |  4 ++++
 5 files changed, 82 insertions(+), 5 deletions(-)
```

---

### ecb03017 - fix(items): address PR #464 review — flicker, right-click, dropdown icon

- Replace the ✦ Unicode star with the pokeball image for the Ankidex
  entry in both nav dropdowns. Matches the existing Items entry's icon
  and gives the dropdown a consistent visual language.
- Disable the QtWebEngine browser-style right-click menu (Inspect,
  Reload, Back/Forward, etc.) via setContextMenuPolicy(NoContextMenu)
  at webview creation. Irrelevant noise in a game UI.
- Reduce grid refresh flicker. The old render did
  grid.innerHTML='' followed by sequential appendChild calls — the
  empty intermediate state plus per-append reflow showed as a visible
  flash on every buy/use/reroll. Now builds the new content into a
  DocumentFragment off-DOM and swaps it in atomically with
  replaceChildren — single reflow, no empty-grid state. Also adds
  contain: layout style on .shop-grid so any remaining repaint stays
  scoped to the grid (sidebar/topbar don't get touched).

```text
src/Ankimon/ankidex/ankidex.html          |  2 +-
 src/Ankimon/ankimon_items_web/shop.css    |  3 +++
 src/Ankimon/ankimon_items_web/shop.html   |  2 +-
 src/Ankimon/ankimon_items_web/shop.js     | 20 ++++++++++++++------
 src/Ankimon/ankimon_items_web/shop_obj.py |  3 +++
 5 files changed, 22 insertions(+), 8 deletions(-)
```

---

### 12efa99d - docs: document Encounter Rate Simulator and Pity Simulator in experimental feature list

- Add comprehensive summary of the hidden Developer-mode Encounter Rate Simulator dashboard to the experimental feature list.
- Detail the dynamic variable sliders, EP progress gauge, interactive Y-axis auto-scaling curves, and comparison matrix.
- Document the new independent Pity & Dry Spell Simulator addition, highlighting the custom-styled, crash-proof select dropdown workaround for PyQt6 WebEngine and dynamic HSL color-themed multiplier charts.

```text
src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md | 11 +++++++++++
 1 file changed, 11 insertions(+)
```

---

### 969e5208 - feat: implement Ankimon Encounter Overhaul and web-based simulator

- Implement the Encounter Systems Overhaul in 'encounter_functions.py', transitioning from inflated wild spawns to a highly structured progression-driven economy.
- Re-architect rare encounter formulas using a unified 100-point Mastery Index (EP) based on scaled Trainer Level, true Pokedex completion (with regional-to-base ID resolution), session review progress, and Core Team CP.
- Implement an Exponential Rarity Scaling ('Soft Landing') curve to limit endgame aggregate rare spawn rates to a healthy 12.3% cap, alongside strict player level locks (Starters, Megas, Legendaries, Ultra Beasts).
- Implement an Independent Pity System tracking dry reviews globally inside the SQLite database, applying quadratic scaling, and resetting the won tier while incrementing others.
- Centralize and parameterize all coefficients, weights, caps, and boundaries at the top of the overhaul section for effortless developer configuration.
- Implement the web-based visual Encounter Rate Simulator dashboard utilizing HTML5/JS slider inputs, integrated into a PyQt6 QWebEngineView window under Developer Mode.
- Create 'docs/encounter_overhaul_spec.md' detailing the full design, Mermaid diagrams, mathematical models, and legacy vs overhaul rate comparisons.
- Add 'src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md' entries documenting the overhaul as an inactive-by-default experimental branch feature (USE_OVERHAUL_ENCOUNTER_SYSTEM = False).

```text
docs/encounter_overhaul_spec.md                 | 217 ++++++
 src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md  |  23 +-
 src/Ankimon/encounter_simulator/simulator.html  | 792 ++++++++++++++++++++++
 src/Ankimon/encounter_simulator/simulator.js    | 834 ++++++++++++++++++++++++
 src/Ankimon/functions/encounter_functions.py    | 202 +++++-
 src/Ankimon/menu_buttons.py                     |   8 +
 src/Ankimon/pyobj/encounter_simulator_dialog.py | 301 +++++++++
 7 files changed, 2373 insertions(+), 4 deletions(-)
```

---

### 2bde3abe - test: add encounter overhaul unit tests and comprehensive scenario simulations

- Add 'tests/test_encounter_overhaul.py' to verify the new Mastery Index (EP), Soft-Landing curve scaling, level locks, and independent pity tracking behaviors.
- Add 'tests/test_encounter_simulator.py' to test rate-calculation lookups and Webapp specifications.
- Add 'tests/encounter_weighting_simulations/test_overhaul_simulation.py' verifying 4 realistic player progression scenarios (Beginner locks, Mid-game Ultra Beast unlocks, Endgame Master soft-landing cap, and Legendary pity multiplier boosts with SQLite reset/increment updates).
- Correct legacy paths to 'pokedex.json' and 'encounter_functions.py' inside 'test_encounter_simulation.py'.
- Modernize module mocking in simulation files to treat package directories ('Ankimon', 'Ankimon.functions', and 'Ankimon.pyobj') as package namespaces on disk, preventing namespace pollution and allowing the full 136-test suite to run green.
- Register 'encounter_simulator_dialog' in the test addon integrity check.

```text
.../test_encounter_simulation.py                   | 898 +++++++++++++++++++++
 .../test_overhaul_simulation.py                    | 420 ++++++++++
 tests/test_addon_integrity.py                      |   1 +
 tests/test_encounter_overhaul.py                   | 159 ++++
 tests/test_encounter_simulator.py                  | 119 +++
 5 files changed, 1597 insertions(+)
```

---

### 08660549 - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 14 +++++++++-----
 1 file changed, 9 insertions(+), 5 deletions(-)
```

---

### 452f8ae8 - style(items): tighten placeholder copy and suppress redundant TM OWNED badge

- "Mart Counter" implied shop-only when the detail panel handles both
  Mart and Bag items. Renamed to "Item Inspector" with neutral copy.
- The green OWNED badge on TM cards is redundant in the Bag view (every
  visible card is owned). Suppress it there; keep it in the Shop view
  where it carries real info ("already bought this TM").

```text
src/Ankimon/ankimon_items_web/shop.html |  4 ++--
 src/Ankimon/ankimon_items_web/shop.js   | 15 ++++++++++-----
 2 files changed, 12 insertions(+), 7 deletions(-)
```

---

### 95b1ca8f - fix(items): address PR #464 review — duplicate method, race, fund loss

- Remove the duplicate update_ui_data definition that overrode the
  shell-aware version and would have silently broken Ankidex updates
  after buy/use/reroll actions.
- Defer load_screen's URL change until _save_ankidex_prefs's async
  getAnkidexState() callback fires. Previously the JS context tore
  down before prefs were read, dropping any in-page state the user
  toggled (view mode, sort, sprite mode).
- Reorder handle_reroll so the new stock is written to the DB before
  the trainer cash is deducted. A DB write failure no longer charges
  the player 100¥ for no new stock.

```text
src/Ankimon/ankimon_items_web/shop_obj.py | 75 +++++++++++++++----------------
 1 file changed, 36 insertions(+), 39 deletions(-)
```

---

### 0f4e2a11 - style: auto ruff format

```text
src/Ankimon/ankimon_items_web/shop_obj.py |  67 +++---
 src/Ankimon/menu_buttons.py               | 127 ++++++++---
 src/Ankimon/pyobj/ankimon_shop.py         |  12 +-
 src/Ankimon/pyobj/item_window.py          | 335 +++++++++++++++++++-----------
 src/Ankimon/singletons.py                 | 168 ++++++++++++---
 5 files changed, 507 insertions(+), 202 deletions(-)
```

---

### 159d2497 - feat(items): unify Mart and Item Bag into a web-based shell window

Replaces the standalone Item Shop (PyQt) and Item Bag (PyQt) windows
with a single QWebEngineView-based screen that shows today's stock and
the player's inventory in one grid. Each card is state-aware (in shop,
owned, both), filters by view (In Shop Today / In Your Bag) and category,
with a detail panel offering Buy and Use actions per item.

Adds a shared in-page dropdown switcher so users can navigate between
Items and Ankidex inside the same window — same QDialog, same
QWebEngineView, only the loaded HTML changes. Ankidex stays standalone-
compatible: the new nav-switcher CSS hides the dropdown affordance
unless body.shell-mode is set (which only happens when the shell window
successfully connects QWebChannel).

Performance: PokemonShopManager.get_tm_pool() now caches the flattened
TM pool on first call. AnkimonItemsWeb indexes items.csv and
item_flavor_text.csv into dicts on first use; per-item lookups become
O(1) instead of full CSV scans (was ~200 file opens per window load on
a heavy bag).

ItemWindow.dispatch_use(item_name, item_type) extracts the use-item
branching (heal / fossil / pokeball / evolution-item / held-item) into
a public method that the web shell invokes without showing the old
PyQt bag. The old bag's render code is untouched; cleanup is left to
a follow-up.

```text
src/Ankimon/ankidex/ankidex.html          |   28 +-
 src/Ankimon/ankidex/nav-switcher.css      |  167 ++
 src/Ankimon/ankidex/nav-switcher.js       |   67 +
 src/Ankimon/ankimon_items_web/__init__.py |    0
 src/Ankimon/ankimon_items_web/shop.css    | 3451 +++++++++++++++++++++++++++++
 src/Ankimon/ankimon_items_web/shop.html   |  194 ++
 src/Ankimon/ankimon_items_web/shop.js     |  617 ++++++
 src/Ankimon/ankimon_items_web/shop_obj.py |  451 ++++
 src/Ankimon/menu_buttons.py               |   22 +-
 src/Ankimon/pyobj/ankimon_shop.py         |    7 +
 src/Ankimon/pyobj/item_window.py          |   36 +
 src/Ankimon/singletons.py                 |   15 +
 12 files changed, 5046 insertions(+), 9 deletions(-)
```

---

### 93a0be06 - style: auto ruff format

```text
src/Ankimon/menu_buttons.py | 124 +++++++++++++++++++++++++++++++++-----------
 1 file changed, 95 insertions(+), 29 deletions(-)
```

---

### 8f1961c9 - feat(menu): add Ctrl+Shift+R keyboard shortcut for Restart Ankimon

```text
src/Ankimon/menu_buttons.py | 1 +
 1 file changed, 1 insertion(+)
```

---

### b4890568 - style(ankidex): center empty-state in viewport with balanced vertical rhythm

The "No Pokémon found" empty state was a sibling of .content-scroll, so it
got pushed to the bottom of the main area instead of centering. Moved it
inside .content-scroll, made the scroll container a flex column, and gave
.empty-state flex: 1 so it fills and centers. Replaced uniform gap with
explicit margins on the icon/h2/p for clearer vertical hierarchy
(28 / 16 / 32 px).

```text
src/Ankimon/ankidex/ankidex.css  | 21 +++++++++++++++++++--
 src/Ankimon/ankidex/ankidex.html | 15 +++++++--------
 2 files changed, 26 insertions(+), 10 deletions(-)
```

---

### 908a818c - style(ankidex): remove card caught-indicator dot and flatten window corners

```text
src/Ankimon/ankidex/ankidex.css  | 24 +-----------------------
 src/Ankimon/ankidex/ankidex.html |  1 -
 2 files changed, 1 insertion(+), 24 deletions(-)
```

---

### 0f88f628 - fixing comments

```text
src/Ankimon/functions/encounter_functions.py | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)
```

---

### b7af15d1 - style: replace misleading PC box manual evolution indicator with a golden double chevron PNG asset and adjust slot color contrast

```text
src/Ankimon/addon_sprites/evolution_indicator.png | Bin 0 -> 5041 bytes
 src/Ankimon/lang/ch_text.json                     |   6 +--
 src/Ankimon/lang/cz_text.json                     |   6 +--
 src/Ankimon/lang/de_text.json                     |   6 +--
 src/Ankimon/lang/en_text.json                     |   6 +--
 src/Ankimon/lang/es_latam_text.json               |   6 +--
 src/Ankimon/lang/fr_text.json                     |   6 +--
 src/Ankimon/lang/it_text.json                     |   6 +--
 src/Ankimon/lang/jp_text.json                     |   6 +--
 src/Ankimon/lang/kr_text.json                     |   6 +--
 src/Ankimon/lang/po_text.json                     |   6 +--
 src/Ankimon/lang/sp_text.json                     |   6 +--
 src/Ankimon/pyobj/pc_box.py                       |  56 ++++++++++++++++++----
 13 files changed, 80 insertions(+), 42 deletions(-)
```

---

### 67552f00 - fix(battle): reset caught state and synchronize comprehensive caught IDs

Key Improvements:
1. State Reset: Added 'ankimon_tracker.caught = 0' inside 'new_pokemon' to explicitly clear the wild capture tracking state at the beginning of an encounter. Corrected the duplicate return guard indentation in 'catch_pokemon' so duplicate catches are blocked regardless of the 'Pop-Up on Defeat' setting.
2. Comprehensive Pokedex Caught Retrieval: Updated 'get_all_pokemon_ids' in AnkimonDB to union currently owned, released (history), and explicitly caught (PC evolution tracking) pokedex IDs, casting all to integers to completely prevent already-caught/collected Pokemon from being auto-caught.
3. Battle Loop State Synchronization: Integrated 'init_battle_state' inside 'swap_ankimon_account' to ensure the active battle state in-memory collection cache is synchronized when switching profiles/databases.

```text
src/Ankimon/functions/encounter_functions.py |  9 +++++----
 src/Ankimon/pyobj/database_manager.py        | 22 ++++++++++++++++++++--
 src/Ankimon/singletons.py                    |  2 ++
 3 files changed, 27 insertions(+), 6 deletions(-)
```

---

### 0c438f9d - fix: add day/night conditions to Cosmoem branching evolutions

```text
src/Ankimon/data_files/pokedex.json          | 2 ++
 src/Ankimon/data_files/pokemon_evolution.csv | 4 ++--
 2 files changed, 4 insertions(+), 2 deletions(-)
```

---

### 4feb127b - fix(pokedex): persistently retain pre-evolved caught states during manual PC evolutions

Resolved a bug where evolving a Pokémon in-place causes its pre-evolved states to disappear from the Pokédex caught list because they are no longer in captured_pokemon and were never released to pokemon_history.

Key Improvements:
1. Database Manager: Added 'mark_as_caught' and 'get_caught_ids' helper methods storing species IDs persistently under 'pokedex_caught' in user_data. Integrated into 'save_pokemon' and 'save_main_pokemon' persistence choke points.
2. Evolution Window: Intercepted 'evolve_pokemon' to explicitly save the pre-evolved species ID ('prevo_id') to the caught list prior to database mutation.
3. Pokédex: Updated 'get_ankidex_data' to union the persistent caught list with currently owned and released historical database sets, preserving all past data with full backward compatibility.
4. Testing: Created 'tests/test_pokedex_evolution_bug.py' to verify that Bulbasaur, Ivysaur, and Venusaur remain fully caught/seen post-evolution.

```text
src/Ankimon/ankidex/ankidex_obj.py    |   7 ++
 src/Ankimon/pyobj/database_manager.py |  33 +++++++
 src/Ankimon/pyobj/evolution_window.py |   7 ++
 tests/test_pokedex_evolution_bug.py   | 161 ++++++++++++++++++++++++++++++++++
 4 files changed, 208 insertions(+)
```

---

### bc4f2b81 - docs: document trainer cash earnings difference in experimental feature list

```text
src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

### 14f42873 - perf(startup): implement zero-lag asynchronous & thread-safe startup sequence

Move heavy IO and CPU-intensive boot tasks (SQLite validation, sprite existence checking, backup generation, first enemy randomization) to a background thread using Anki's QueryOp.

Highlights:
- Avoid blocking Anki UI thread during startup.
- Enable 'check_same_thread=False' on SQLite database connection.
- Guard battle loops, HUD, hotkeys, and menu button creation to fall back gracefully until background startup completes.
- Fix UnboundLocalError in reviewer hotkeys by removing local duplicate tooltip imports.
- Ensure proper link suppression by returning True from reviewer PyCmd route wrapper.
- Clean up duplicate Settings import in singletons.py.
- Fully document these changes in _BRRR_EXPERIMENTAL_FEATURE_LIST.md.

```text
src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md |   9 +
 src/Ankimon/__init__.py                        | 205 ++++++++-------
 src/Ankimon/battle_loop.py                     |   3 +
 src/Ankimon/functions/rate_addon_functions.py  |   5 +-
 src/Ankimon/gui_entities.py                    |  40 ++-
 src/Ankimon/menu_buttons.py                    |  37 ++-
 src/Ankimon/profile_hooks.py                   |  84 ++++--
 src/Ankimon/pyobj/database_manager.py          |   2 +-
 src/Ankimon/reviewer_ui.py                     |  27 +-
 src/Ankimon/singletons.py                      | 253 ++++++++++++------
 src/Ankimon/startup.py                         | 183 ++++++++-----
 tests/test_addon_integrity.py                  | 341 ++++++++++++++++---------
 12 files changed, 785 insertions(+), 404 deletions(-)
```

---

### f7dc3a4e - chore: deactivate starters

```text
src/Ankimon/functions/encounter_functions.py | 15 +++++++++------
 1 file changed, 9 insertions(+), 6 deletions(-)
```

---

### 988d71dc - feat: Implement background update notifications, weekly snooze, and premium 3-Tab update dialog

Implemented a robust branch update checker and asynchronous installer for the experimental branch, featuring user data protection, locked-file safety, and a premium 3-tab update interface.

Key Components:
- Asynchronous Startup Check: Queries GitHub API for the latest commit on the 'BRRRR_Experimental' branch in a silent background thread to prevent UI thread freezing.
- Resilient Connectivity Bypasses: Skips fragile pre-checks to allow update checks even in restricted test sandboxes (like AnkiTEST) or transient offline states.
- Guaranteed Data Protection: Protects user progress by completely safeguarding all database files ('ankimon.db', '-shm', '-wal' in 'user_files/'), custom downloaded sprites, local backups, and critical root files ('HelpInfos.html', 'updateinfos.md', 'meta.json') from being overwritten during updates.
- Premium 3-Tab Update Dialog:
  - Tab 1: BRRRR_Experimental Branch: Displays active branch name, installed commit SHA, commit author/date, weekly snooze status, and a scrollable, light/dark-themed commit logs feed from GitHub. Includes one-click update button.
  - Tab 2: Releases: Dropdown selector and installer for official experimental releases.
  - Tab 3: Developer: Lazy-loads and installs directly from custom remote branches, tags, or Pull Requests.
- Weekly Snooze System: Adds checkbox to snooze update prompts for 7 days, persisting the state inside 'update_state.json'.
- File-Lock Safety: Safely bypasses Windows permission locks on static assets (e.g., loaded '.ttf' fonts) by logging non-fatal warnings and proceeding with code replacement.
- Menu Integration: Renamed menu item to "Check for Updates" under 'Ankimon => Help' for a standard UX experience.

```text
.gitignore                                     |   1 +
 src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md |  46 +-
 src/Ankimon/__init__.py                        |   3 +-
 src/Ankimon/changelog.py                       |  61 +++
 src/Ankimon/menu_buttons.py                    |   2 +-
 src/Ankimon/pyobj/update_dialog.py             | 619 ++++++++++++++++++++++++-
 src/Ankimon/pyobj/update_manager.py            | 118 ++++-
 tests/test_branch_updates.py                   | 226 +++++++++
 8 files changed, 1041 insertions(+), 35 deletions(-)
```

---

### 180bcf29 - feat: Overhaul PC Box, Battle Logic, port manual evolution, and implement Trade V2

Delivered a major upgrade to the PC Box UI/UX, overhauled the battle and evolution systems, added level-gated progression, and modernized the trade system with V2 protocol.

Key Features & Overhauls:
1. PC Box (mini) Rework:
   - Persistent details panel with widget reuse to eliminate UI flickering during navigation.
   - Beautiful visual polishing: Added HSL colors, smooth fade-in animations for headers, sliding bar animations for stats, and hover lift effects on grid slots.
   - Friendship bar relocated directly below the XP bar in the Stats tab for a clean, unified presentation.
   - Integrated scotej's manual evolution button directly into the PC details panel, enabling immediate evolution when readiness criteria are met.
   - Maximized window stability: Migrated the details panel to a persistent QStackedWidget, fixing a legacy Qt layout bug that forced maximized windows to restore/un-maximize when selecting a Pokémon.
   - Nature indicators (▲/▼) added to stat labels to visually highlight 10% Nature boosts/reductions.
   - Added advanced sorting by all individual stats, CP, IV Total, and EV Total.
   - Integrated the 'MoveManagerWidget' into the PC Box to manage Pokémon moves.

2. Advanced Battle & Collection Logic:
   - Form-Aware Evolution: Prioritized 'pokedex.json' metadata over legacy CSVs in auto-evolution and manual evolution to fully support regional form evolutionary paths (e.g., Alolan Geodude -> Alolan Graveler).
   - Time-of-Day Evolution Constraints: Enforced day/night conditions for evolution. The PC Box displays status warnings (e.g., "waiting for Night") if level criteria are met but time constraints are not.
   - Rare & Level-Gated Encounters: Mega and Gigantamax forms now require encountering the base form first. Starters are rare level-gated encounters with prerequisite chains (e.g., Charmander caught first). Legendaries (Gen I-IX) use prerequisite chains from 'encounters.txt'.
   - Region Selection: Added a region selection setting that boosts generation appearance odds dynamically.
   - Auto-Catch Setting: Option to automatically catch rare Pokémon regardless of manual/auto-battle settings.
   - EV-Yield Items: Implemented Macho Brace (doubles EV yield) and Power Items (Anklet, Band, etc., adding flat +8 EVs to specific stats).

3. Trade V2 System:
   - Versioning Protocol: Added version 'v02' (sentinel '-200') to verify compatibility and prevent version mismatches.
   - Nature Transmission: Transmitted Natures in trade codes (legacy codes default to Serious).
   - Legacy Mode: Option to generate old format codes for backward compatibility.
   - Normalization & Canonicalization: Cleansed code inputs to minimize manual entry errors.

4. Developer & Power-User Tools:
   - Hidden Developer Mode: Activated by profile/trainer name strings. Enables Account & Database Switcher, Add-on Reloader menu option, and immediate encounter hotkey '0'.
   - Hotkey '9': Team cycling during battle while clearing status effects.

5. Architectural & Data Improvements:
   - Generational Fallback: Fallback chain (Gen 9 -> Gen 1) to resolve incomplete move data.
   - Sprite Fallbacks: Improved naming and back-sprite lookups to prevent MissingNo errors.
   - Reward Balancing: Configurable cash reward amounts and payout intervals.

```text
.gitignore                                     |    6 +
 src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md |  144 +++
 src/Ankimon/__init__.py                        |   16 +-
 src/Ankimon/addon_files/nature_chart.html      |   38 +
 src/Ankimon/ankidex/ankidex.js                 |   38 +-
 src/Ankimon/battle_loop.py                     |   36 +-
 src/Ankimon/business.py                        |    4 +-
 src/Ankimon/card_hooks.py                      |    7 +
 src/Ankimon/config.json                        |    7 +-
 src/Ankimon/data_files/pokedex.json            | 1231 +++++++++++++++++++----
 src/Ankimon/data_files/pokemon.csv             |   30 +-
 src/Ankimon/functions/battle_functions.py      |   18 +-
 src/Ankimon/functions/encounter.txt            |  110 ++-
 src/Ankimon/functions/encounter_data.py        |  477 ++++++++-
 src/Ankimon/functions/encounter_functions.py   |  616 ++++++++++--
 src/Ankimon/functions/friendship_evolution.py  |  755 ++++++++++++++
 src/Ankimon/functions/pokedex_functions.py     |  146 ++-
 src/Ankimon/functions/pokemon_functions.py     |   47 +-
 src/Ankimon/functions/sprite_functions.py      |  100 +-
 src/Ankimon/functions/trainer_functions.py     |   25 +-
 src/Ankimon/functions/update_main_pokemon.py   |    6 +-
 src/Ankimon/gui_classes/overview_team.py       |    1 +
 src/Ankimon/gui_classes/pokemon_details.py     |  527 ++++++----
 src/Ankimon/gui_classes/pokemon_team_window.py |  347 ++++++-
 src/Ankimon/gui_entities.py                    |  115 ++-
 src/Ankimon/lang/ch_text.json                  |   14 +-
 src/Ankimon/lang/cz_text.json                  |   14 +-
 src/Ankimon/lang/de_text.json                  |   14 +-
 src/Ankimon/lang/en_text.json                  |   11 +-
 src/Ankimon/lang/es_latam_text.json            |   14 +-
 src/Ankimon/lang/fr_text.json                  |   14 +-
 src/Ankimon/lang/it_text.json                  |   14 +-
 src/Ankimon/lang/jp_text.json                  |   14 +-
 src/Ankimon/lang/kr_text.json                  |   14 +-
 src/Ankimon/lang/po_text.json                  |   14 +-
 src/Ankimon/lang/setting_description.json      |   10 +-
 src/Ankimon/lang/setting_name.json             |   12 +-
 src/Ankimon/lang/sp_text.json                  |   14 +-
 src/Ankimon/menu_buttons.py                    |   56 +-
 src/Ankimon/profile_hooks.py                   |   12 +
 src/Ankimon/pyobj/ankimon_tracker.py           |    1 +
 src/Ankimon/pyobj/database_manager.py          |   43 +-
 src/Ankimon/pyobj/download_sprites.py          |    2 +-
 src/Ankimon/pyobj/evolution_window.py          |   51 +-
 src/Ankimon/pyobj/item_window.py               |   11 +-
 src/Ankimon/pyobj/move_picker.py               |  328 ++++++
 src/Ankimon/pyobj/pc_box.py                    | 1260 +++++++++++++++++++++---
 src/Ankimon/pyobj/pokemon_obj.py               |   98 +-
 src/Ankimon/pyobj/pokemon_trade.py             |  232 ++++-
 src/Ankimon/pyobj/reviewer_obj.py              |  667 +++++++------
 src/Ankimon/pyobj/settings.py                  |   74 +-
 src/Ankimon/pyobj/settings_window.py           |  180 +++-
 src/Ankimon/pyobj/starter_window.py            |    2 +-
 src/Ankimon/pyobj/test_window.py               |  199 ++--
 src/Ankimon/pyobj/trainer_card.py              |   22 +
 src/Ankimon/pyobj/translator.py                |   10 +
 src/Ankimon/reloader.py                        |  117 +++
 src/Ankimon/resources.py                       |   14 +-
 src/Ankimon/reviewer_ui.py                     |  204 +++-
 src/Ankimon/singletons.py                      |    1 +
 src/Ankimon/utils.py                           |   43 +-
 tests/test_addon_integrity.py                  |    2 +-
 tests/test_cp_formula.py                       |    2 +-
 tests/test_friendship_evolution.py             |  654 ++++++++++++
 64 files changed, 7870 insertions(+), 1435 deletions(-)
```

---

### 617686e6 - perf: implement in-memory caching for high-latency file I/O and DB queries

Transitioned high-latency file I/O and redundant SQLite database queries to a comprehensive, aggressive in-memory caching system, drastically reducing review-to-battle latency to nearly zero.

Key Optimizations:
- File I/O Elimination: Cached heavy game metadata files in memory at startup, including 'learnsets.json', 'pokedex.json', and 'next_lvl.csv' (experience tables). This completely avoids slow disk reads during card answer processing, move selection, and level-ups.
- CSV Memory Mapping: Parsed and cached heavy CSV data files ('pokemon.csv', 'stats.csv', 'pokemon_species.csv', 'evolution.csv') into memory-resident dictionary structures for instantaneous O(1) lookups.
- HUD Sprite Caching: Implemented sprite caching in the reviewer UI to eliminate redundant file checks and disk reads, ensuring fluid animations and instant HUD rendering during battle loops.
- Reverse Species Indexing: Built an species ID to name reverse index ('species_id' -> 'pokemon_name') during boot for O(1) identification.
- PC Box Cache Layer: Optimized PC Box queries by caching the results of the last filtered database query. Navigating between boxes, paging, or selecting different Pokémon no longer triggers a new SQLite query unless the filter state actually changes.
- Smart Cache Invalidation: Balanced performance with data accuracy by tracking filter states and invalidating caches only when mutations (captures, team updates, or edits) occur.
- Updated Singletons: Modified 'singletons.py', 'functions/learnset_retrieval.py', and 'startup.py' to wire and manage the lifetime of the new global memory caches.

```text
src/Ankimon/functions/learnset_retrieval.py |  90 +++++---
 src/Ankimon/singletons.py                   | 334 ++++++++++++++++------------
 src/Ankimon/startup.py                      |   4 +-
 3 files changed, 256 insertions(+), 172 deletions(-)
```

---

### ab76d768 - feat: implement Ankidex (Pokédex V2) with HTML5/QtWebEngine

Replaced the legacy, resource-heavy Pokédex system with Ankidex, a high-performance web-based implementation powered by QtWebEngine, HTML5, CSS3, and Vanilla JavaScript.

Key Changes:
- Modernized Tech Stack: Rewrote the entire Pokédex interface using modern web standards (HTML5/CSS3) with a beautiful Glassmorphism styling and seamless Vanilla JavaScript interactions, embedded inside a QtWebEngineView for a premium native feel.
- Enhanced Performance: Optimized asset load times and transitions, resulting in faster Pokédex open times and zero-latency scrolling or tab switching.
- Advanced Search & Filtering: Rebuilt the search engine to enable real-time keyword filtering, sorting, and instantaneous responsiveness.
- Multi-Form & Regional Support: Added full support for regional forms (Alolan, Galarian, Hisuian, etc.) and special Pokémon variants, rendering correct sprites and stats dynamically.
- Refactored Codebase Structure:
  - Added new web files: ankidex.html, ankidex.css, ankidex.js, and abilities.json.
  - Introduced 'ankidex_obj.py' to manage QtWebEngine integration and Python-JS bridge communication.
  - Extensively refactored 'functions/pokedex_functions.py' to integrate with the new schema and index.
  - Completely cleaned up and deleted legacy files: 'pokedex/pokedex.html', 'pokedex/pokedex_obj.py', and 'pokedex/pokemon_names.json'.

```text
src/Ankimon/ankidex/abilities.json         |  266 ++++
 src/Ankimon/ankidex/ankidex.css            | 2360 ++++++++++++++++++++++++++++
 src/Ankimon/ankidex/ankidex.html           |  382 +++++
 src/Ankimon/ankidex/ankidex.js             | 2231 ++++++++++++++++++++++++++
 src/Ankimon/ankidex/ankidex_obj.py         |  193 +++
 src/Ankimon/ankidex/pokedex_flavor.json    |    1 +
 src/Ankimon/functions/pokedex_functions.py |  630 +++++---
 src/Ankimon/pokedex/pokedex.html           |  624 --------
 src/Ankimon/pokedex/pokedex_obj.py         |   98 --
 src/Ankimon/pokedex/pokemon_names.json     | 1027 ------------
 10 files changed, 5836 insertions(+), 1976 deletions(-)
```

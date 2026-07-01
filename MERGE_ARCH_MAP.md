# MERGE_ARCH_MAP.md — old→new organization map & re-fit key

How Stage B re-fits each BRRRR_Experimental feature onto **main's** architecture (the target). Read
this with `MERGE_FEATURE_INVENTORY.md` (what to port) and `MERGE_NEEDS_REVIEW.md` (open questions).

Target architecture = **main's**: keep the service seam (`core/services/events/ui_port/gui_presenter`
+ `hooks`) and the `harness/` test infra; re-express exp's behavior through the seam; never revert to
direct `aqt.mw.*`; never delete the harness/seam.

---

## 1. Recorded verified facts (Stage B inherits these)

### 1.1 Commit identity (NR-13)
Configured git identity is **`h0tp-ftw <h0tp-ftw@users.noreply.github.com>`** — a GitHub **noreply**
address, so the repo Privacy Check passes with **no "I consent…" line**. Do NOT change it; do NOT
commit a personal email. (The brief's guessed `141889580+…` address is not what the machine uses;
git is ground truth.)

### 1.2 Environment / gate discipline (see MERGE_BASELINE.md, NR-10)
- **Two environments, mirroring CI's two jobs.** Tier-1 / ruff / logic tests run **Qt-free**
  (`pip install requests ruff pytest`). Tier-2 real-boot/play + the scaffolding smoke tests run in a
  **full-Qt** venv (`… pytest-qt orjson PyQt6 aqt anki`). Running Tier-1 with PyQt6 importable
  **segfaults at teardown** (no `QCoreApplication`) — reproduced on the pristine base.
- Python here **3.14.6**; CI uses **3.12** — re-baseline if Stage B runs on 3.12.
- **QtWebEngine headless env** (export before any Qt/QWebEngineView check):
  ```bash
  export QT_QPA_PLATFORM=offscreen
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-software-rasterizer"
  export QTWEBENGINE_DISABLE_SANDBOX=1
  ```
  `xvfb-run` is absent here; **offscreen alone sufficed** (QApplication, QWebEngineView, both Tier-2
  probes all ran). CI wraps Tier-2 in `xvfb-run -a … QT_QPA_PLATFORM=offscreen`; if a future check
  needs a display, install `xvfb`.

### 1.3 SQLite WAL / threading contract (stdlib; NR-05)
`sqlite3.connect(path, check_same_thread=False)` + one connection per thread via `threading.local()`.
WAL (`PRAGMA journal_mode=WAL`) splits committed data across `db` + `db-wal`; a single-file copy
(as `probe_persistence` and `BackupManager` do) then loses the `-wal` frames. **WAL is opt-in**
(`AnkimonDB(wal=False)` default) in the base. A concurrent-writer leaf enabling `wal=True` MUST also
add a checkpoint-before-copy (`PRAGMA wal_checkpoint(TRUNCATE)`) or copy all three files.

### 1.4 Verified API signatures (Context7 / repo; §17)
- **QWebChannel (PyQt6):** `QWebChannel(page)`; `channel.registerObject(name, qobject)` publishes the
  object's `pyqtSignal`s / `pyqtSlot`s / properties to JS; `page.setWebChannel(channel)` installs it
  (one per page, no ownership transfer). Transport in JS = `qt.webChannelTransport` via
  `qwebchannel.js`. Imports: `from PyQt6.QtWebChannel import QWebChannel`,
  `from PyQt6.QtWebEngineWidgets import QWebEngineView`.
- **QueryOp (aqt):** `QueryOp(parent=mw, op=lambda col: ..., success=on_done).with_progress().run_in_background()`
  — `op(col)` runs off the GUI thread; `success(result)` runs on the GUI thread. The harness
  `fake_aqt` provides a synchronous QueryOp with the same contract for tests.

---

## 2. Seam API surface (main; the re-fit target)

`src/Ankimon/services.py` — `services` singleton registry (aqt-free). Attributes:
`db, logger, settings, translator, tracker, main_pokemon, enemy_pokemon, trainer_card, achievements,
ui (presenter), test_window, evo_window, pokemon_pc, reviewer, col`. Methods: `populate(**kw)`
(skip-if-None), `reset()`.
`src/Ankimon/events.py` — `events` (`_EventBus`): `enable(sink)/disable()/is_enabled()/emit(type, **fields)/
drain()/peek()/clear()/reset()`.
`src/Ankimon/ui_port.py` — `HeadlessPresenter`: `choose_move(attacks)`, `choose_attack_to_replace(attacks,
new)`, `notify(level, msg)`, `warn(msg)`, `report_error(exc, msg="")`.
`src/Ankimon/gui_presenter.py` — `QtPresenter`: the real-Qt implementation of that presenter interface
(swapped into `services.ui` by the production root).
`src/Ankimon/core.py` — `build_core()` (constructs logger/db/settings/translator/state, populates
`services`), `bind_runtime_globals()` (binds bare module globals in the core logic modules to live
registry objects), `_build_placeholder_enemy()`.
`src/Ankimon/hooks.py` — `setupHooks(check_data, ankimon_tracker_obj)`.

### 2.1 direct-`mw.*` → seam translation dictionary (apply to every ported feature)
| exp direct access | main seam entrypoint |
|---|---|
| `from aqt import mw` / `aqt.mw` state | (do not import mw for state) |
| `mw.ankimon_db` | `services.db` |
| `mw.settings_obj` | `services.settings` |
| `mw.main_pokemon` / `mw.enemy_pokemon` | `services.main_pokemon` / `services.enemy_pokemon` |
| `mw.trainer_card`, `mw.ankimon_tracker` | `services.trainer_card`, `services.tracker` |
| tooltips / info / errors | `services.ui.notify(level,msg)` / `.warn(msg)` / `.report_error(exc,msg)` |
| sound / state-change signalling | `events.emit(type, **fields)` |
| `mw.test_window/evo_window/pokemon_pc/reviewer_obj` | `services.test_window/evo_window/pokemon_pc/reviewer` |
| web-shell screen windows | `host.mount(screen_id, view, bridges=...)` on the base `WebShellHost` |
| genuine Anki APIs (`mw.col`, `mw.taskman`, `gui_hooks`, `mw.form`, `mw.progress`) | still via `aqt` (these ARE Anki, not addon state) |

Bare-name globals (`main_pokemon`, `settings_obj`, `ankimon_db`, …) in `battle_loop.py`,
`functions/encounter_functions.py`, `functions/ankimon_hooks_to_poke_engine.py` are bound by
`core.bind_runtime_globals()` (see `core._RUNTIME_GLOBALS`); a feature that adds a new such module or
global extends that map rather than importing from `singletons`.

## 3. The ~13 shared modules — old→new (seam-vs-direct-mw reversion set)

For all of these, **base each ported change on main's seam version**; re-express wanted exp behavior via
§2.1. Stage A did **not** edit these (except the scaffolding in §5); their exp leaf-logic lands per
feature in Stage B.
```
exp direct-mw (OLD)                                  -> main seam (NEW)
battle_loop.py                       reviewer/state via mw   -> services.*/events.emit; globals via bind_runtime_globals
functions/encounter_functions.py     mw.* + no #402 guard    -> services.*; KEEP #402 level-cap NameError guard
functions/pokedex_functions.py       drops services registry -> services.settings/db (active_region etc.)
functions/pokemon_functions.py       mw.*                    -> services.*
functions/sprite_functions.py        mw.*                    -> services.*
functions/trainer_functions.py       mw.* + strips XP guards  -> services.*; KEEP XP-share None-checks
functions/update_main_pokemon.py     mw.*                    -> services.* (already seam on main)
pyobj/ankimon_tracker.py             mw.*                    -> services.tracker/state
pyobj/pokemon_obj.py                 mw.* + strips XP guards  -> services.*; KEEP XP-share None-checks
pyobj/settings.py                    lazy singletons import  -> services.settings; single-key set() (perf) preserved
pyobj/trainer_card.py                mw.*                    -> services.trainer_card
utils.py                             mw.*                    -> services.* (is_main_thread/is_alive DONE in base)
singletons.py                        mw-anchored reload      -> keep main's; populate services.* + core.bind_runtime_globals()
```
Plus two non-strict seam collisions: `functions/friendship_evolution.py` (main uses `services.settings`,
exp `mw.settings_obj`) and `functions/ankimon_hooks_to_poke_engine.py` (main via `services`, exp inline mw);
and `__init__.py` (composition root — main delegates to singletons/services/hooks while still using `mw`
for real Anki APIs; exp boots everything onto `mw`).

## 4. WEB-SHELL: base (in-base) vs screens (Stage-B leaves)

**In the base** (`src/Ankimon/webshell/`, F10, DONE-IN-BASE):
- `host.py::WebShellHost(QDialog)` — the FRAME: `QStackedWidget` + nav `QComboBox` +
  `mount(screen_id, view, *, label, bridges)` / `show_screen(id)` / `screen_ids()` / `notify_stats_changed()`.
- `live_update.py::LiveUpdateBridge(QObject)` — `stats_changed = pyqtSignal(str)`,
  `notify_stats_changed(payload)`, `@pyqtSlot request_refresh()`. Registered on every mounted web
  screen's QWebChannel as `"live"`.
- `__init__.py` — thin re-export.

**Leaf SCREENS (Stage B; each mounts via `host.mount(...)`):** Items/Shop (`ankimon_items_web/shop*`,
`shop_obj.py` screen classes, `pyobj/ankimon_shop.py`, `pyobj/item_window.py`), Web Settings
(`ankimon_items_web/settings*`, `settings_schema.py`), Ankidex SPA (`ankidex/*`), Profile+Team
(`ankimon_profile_web/*`, `gui_classes/overview_team.py`), Mobile (`ankimon_mobile_web/*`,
`functions/mobile_sync.py`), Encounter simulator (`encounter_simulator/*`,
`pyobj/encounter_simulator_dialog.py`). Their screen-specific bridges (Items/Nav/Settings/Trainer/
Team/Mobile) are leaf; pass them to `mount(..., bridges={...})`. `notify_stats_changed` producers
(cash/xp/level/caught changers) call `host.live_bridge.notify_stats_changed(...)` — do NOT put this in
`singletons.py` (NR-04).

## 5. Scaffolding synthesised in Stage A (new/changed base files)

| Concern | Base location | Commit | Notes |
|---|---|---|---|
| Thread helpers | `utils.is_main_thread`, `utils.is_alive` | cafa3788 | sys.modules-guarded; aqt-free |
| Thread-safe DB | `pyobj/database_manager.py` (`ConnectionWrapper`, per-thread conns, `check_same_thread=False`, `switch_database`, mobile tables) | 57aaba99 | WAL opt-in (NR-05); registered as `services.db` via `core.get_db` |
| Web-shell host+bridge | `webshell/host.py`, `webshell/live_update.py`, `webshell/__init__.py` | c2b16b44 | new package, zero screens |
| Async boot primitive | `boot_async.run_startup_boot` | e1ea7a0b | wraps `aqt.operations.QueryOp`; injectable for tests |
| Scaffolding smoke gate | `tests/test_scaffolding_smoke.py` | 38d39d8e/b2619fe4 | §16 (a)-(d); run standalone in Qt env |

**DB-layer routing:** `core.build_core()` → `get_db(logger)` → `services.db` (unchanged wiring). The
thread-safe layer is transparent to existing callers (GUI thread still gets one shared connection, now
via `ConnectionWrapper`). New tables ship empty and idempotent.
**Singletons / QueryOp boot:** main's synchronous boot is intact (probe_real_boot green); the
`boot_async` primitive is available but not yet wired into `__init__`/`startup` (deferred — reload-safe
singletons + async rewiring is F31/F32, Stage B).
**Harness retention:** `harness/` and the seam are kept in full (exp deleted them). Do not remove.
**requirements.txt / manifest / changelog (NR-11):** `requirements.txt` UNCHANGED (main's list; `markdown`
kept — changelog uses it; QtWebEngine+QWebChannel come via `aqt`/`PyQt6`; DB uses stdlib `json`). Keep
main's manifest `version: 2.03` and `assets/changelogs/{2.02-E,2.03}.md`; treat exp's `2.01-E` string as a
synthesis item to reconcile in a Stage-B version bump — do NOT regress to 2.01-E. Keep main's June/July
2026 monthly challenges (Comfey, Magby).

## 6. AUTHORIZATIONS (keyed by inventory ID) — deletes/edits a Stage-B unit MAY make
Absent an explicit authorization here, Stage B must **escalate** (append to `MERGE_NEEDS_REVIEW.md`)
rather than delete or edit an otherwise-immutable file.
- **F16 (Ankidex SPA):** MAY delete `src/Ankimon/pokedex/{pokedex.html,pokedex_obj.py,pokemon_names.json}`
  (superseded by `ankidex/`). MAY edit `functions/pokedex_functions.py` (re-fit region-aware lookup onto
  `services`; KEEP main's seam).
- **F50 (native trainer/team windows removal):** MAY delete
  `gui_classes/{pokemon_team_window.py,choose_trainer_sprite_graphical.py}` and
  `pyobj/trainer_card_window.py` — **edit-vs-delete** with main (main edited `pokemon_team_window.py`);
  authorized only once the web Team/Profile screens (F18) are mounted and cover their function.
- **AchievementsDialog removal (D5 row):** MAY delete `pyobj/achievements_dialog.py` once the web Profile
  screen shows achievements.
- **Web-shell screen leaves (F11/F12/F13/F18/…):** MAY edit `menu_buttons.py` to add their nav entry and
  `singletons.py` lazy getters (thin), and MAY add screen-specific bridges — all **purely additive**;
  MUST NOT reshape existing seam signatures.
- **DB-touching leaves (mobile-sync F29, pokedex-completion, PC-box caching):** MAY add their own methods
  to `pyobj/database_manager.py` (shared-file hotspot; scaffolding already in base) — additive only; the
  mobile-sync leaf that turns on WAL MUST land the checkpoint-before-copy fix (NR-05).
- **Seam entrypoints:** a leaf MAY add a **purely-additive** new `services`/`events`/`ui_port`/`hooks`
  function when the arch map shows none exists (flag in the PR). **Editing/reshaping any existing seam
  signature/behavior is forbidden** and is escalated.

## 7. Shared-file hotspots (feed Stage-B wave ordering)
Files touched by multiple deferred leaves (land in owner-gated waves, not in parallel):
`menu_buttons.py` (every menu-adding leaf), `singletons.py` (lazy getters), `pyobj/database_manager.py`
(mobile-sync, pokedex-completion, PC-box), `pyobj/settings.py` + `config.json` + `lang/*` (every
settings-key leaf — insert keys surgically onto main's files, NR ledger notes the whitespace-reindent
trap on `setting_name.json`), `functions/encounter_functions.py` (encounter overhaul + auto-catch),
`functions/pokedex_functions.py` (Ankidex + evolution), `battle_loop.py` (reviewer HUD + cash + mobile).

## 8. Cross-check (§14 / §21)
- **Partition:** the 52 inventory rows' Source location(s) are set-equal to the 165-file exp-only change
  set (`git diff --name-only a8abbd66..origin/BRRRR_Experimental`) — verified programmatically (0 leaks,
  0 double-assignments) and re-verified by an independent subagent.
- **Arch-map completeness:** for every inventory row a concrete NEW-organization target path + the seam
  entrypoint(s) for each direct-mw call are resolved (§2.1 dictionary + per-domain targets above).
- Subagent verdict + any deltas are recorded below.

### Independent subagent cross-check — VERDICT (Stage A)
An independent read-only verifier re-enumerated from git and reconciled against the artifacts:
- **PARTITION: CLEAN-PARTITION.** Git change set = 165; inventory distinct Source paths = 165; set-equal
  both directions (0 leaks, 0 phantom paths); 0 double-assignments; all 52 rows carry a Source field.
- **ARCH-MAP COMPLETENESS: PASS.** All 52 rows have a concrete NEW-org target (none blank/TBD); every
  `mw.*` access in the rows resolves — via the §2.1 dictionary, kept-as-Anki-API (`mw.col/pm/app/
  addonManager/reviewer`), or an inline row-specific seam target. No unresolved entrypoint.
- **SPOT-CHECKS: 6/6 OK** (F09/F25/F33 DONE-IN-BASE; F14/F16/F50 DEFERRED) — git name-status matched
  each feature's description.
- **DELTAS:** none affecting partition/completeness. One owner-awareness note: the three meta-docs
  **F03** (`repository-analysis/`), **F04** (`AGENTS.md` edit-vs-edit), **F07**
  (`_BRRR_EXPERIMENTAL_FEATURE_LIST.md`) need a disposition decision (drop vs keep/reconcile) — see
  `MERGE_NEEDS_REVIEW.md` **NR-14**; they are flagged in-row, not completeness gaps.

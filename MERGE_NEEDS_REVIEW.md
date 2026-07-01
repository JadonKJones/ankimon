# MERGE_NEEDS_REVIEW.md — escalation ledger (append-only)

The escalation / open-question log for the BRRRR_Experimental → main integration.

**Contract.** Append-only; **both stages append, never overwrite.** One entry per open
question / deferral-with-doubt / significantly-inappropriate candidate / doc-vs-diff conflict /
owner escalation. Nothing is dropped from the integration without an entry here **plus** an
owner ping. Stage A (this session) owns the branch and appends directly. Stage B never pushes
to the integration branch directly — it appends via PRs the owner merges (one consolidated
escalations PR per wave, plus each feature PR carrying its own append).

Status legend: **OPEN** (needs owner) · **RESOLVED** (owner decided) · **INFO** (recorded, no action).

---

## NR-01 — Base branch excludes local `main` commit `6d37cae9` ("im a ghost")  ·  RESOLVED
- **What:** local `main` was +1 ahead of `origin/main` via `6d37cae9`, which added only
  `main_vs_BRRRR_Experimental_diff_report.md` (a diff-report doc; no shipped code).
- **Risk:** baking a scratch analysis doc into the integration base.
- **Recommendation:** branch off `origin/main`; preserve the doc outside the repo.
- **Resolution (owner, Stage A):** "delete it, it was a joke, never meant to be committed."
  The file was moved to `~/Downloads/main_vs_BRRRR_Experimental_diff_report.md` and the
  integration branch was based on `origin/main` (`9dc52cd1`) so the ghost commit is excluded.
  Note: per Stage-A hard rules the local `main` branch itself was **not** rewritten (main is
  read-only); the ghost commit remains only on the local `main` ref, harmless and excluded from
  all integration work. Owner may reset it themselves with `git branch -f main origin/main`.

## NR-02 — Web-shell HOST requires a new architectural home  ·  RESOLVED
- **What:** Definition A puts the QWebEngine host + QWebChannel bridge in the base, but exp's
  host is the monolithic `ankimon_items_web/shop_obj.py::AnkimonItemsWeb` that hard-wires all 7
  screens + their bridges. A zero-screen host needs a **new** module home.
- **Risk:** inventing a materially new cross-cutting home (§20a trigger).
- **Resolution (owner, Stage A):** "extract host+bridge to new home now." Created
  `src/Ankimon/webshell/` (`host.py` `WebShellHost` + `live_update.py` `LiveUpdateBridge`),
  zero concrete screens, stub-mountable. Leaf screens mount via `host.mount(...)` in Stage B.

## NR-03 — Ambiguous scaffolding items deferred to Stage B  ·  RESOLVED
- **What:** caching layer (learnsets/pokedex/CSV/TM-pool/reverse-id index), `MovePickerDialog`,
  `settings_schema.py`, `translator.change_language()` are scaffolding-shaped but each is either
  woven into leaf modules, a user-facing widget, or single-consumer.
- **Resolution (owner, Stage A):** owner delegated the call; **all four DEFERRED to Stage B**
  (§9: a smaller clean scaffolding set beats a larger broken one). None is a seam entrypoint
  needed by 2+ leaves, so each can be added purely-additively in its owning Stage-B unit.

## NR-04 — `notify_stats_changed` relocated out of `singletons.py`  ·  RESOLVED (INFO)
- **What:** exp put the live-update push (`notify_stats_changed`) in `singletons.py`, but repo
  rules require `singletons.py` to stay logic-free.
- **Resolution:** the push logic lives in `webshell/live_update.py::LiveUpdateBridge`
  (`notify_stats_changed` + `stats_changed` signal). `singletons.py` is untouched. Stage B wires
  producers (cash/xp/level/caught changes) to call `host.live_bridge.notify_stats_changed(...)`.

## NR-05 — WAL is opt-in; live WAL enablement deferred (persistence guard)  ·  OPEN (Stage B)
- **What:** exp runs the SQLite DB in WAL for concurrent background access. But the harness
  `probe_persistence` and `BackupManager` simulate/perform a restart by copying **only**
  `ankimon.db` — WAL buffers committed writes in the `-wal` sidecar, so a single-file copy loses
  them ("DATA LOST ON RESTART"). WAL is thus **incompatible with main's single-file persistence
  guard** (§12) unless a checkpoint precedes every copy.
- **Decision (Stage A):** `AnkimonDB(wal=False)` by default — the thread-safe connection layer
  (`check_same_thread=False` + per-thread connections) ships **without** forcing WAL, preserving
  main's persistence/backup behavior (probe_persistence stays green). The `wal=True` capability
  is proven by the scaffolding smoke test on a scratch DB.
- **Stage-B requirement:** the concurrent-writer leaf (mobile-sync) that needs WAL must enable
  it (`wal=True`) **together with** a checkpoint-before-copy fix in `BackupManager`/any db-file
  copy path (`PRAGMA wal_checkpoint(TRUNCATE)`), or copy all of `.db`/`.db-wal`/`.db-shm`.
  **Do not enable WAL live without that fix** or restart-persistence regresses.

## NR-06 — `reloader.py` deferred (mw-coupled dev tool)  ·  OPEN (Stage B)
- **What:** exp's `reloader.py` hot-reload is listed as scaffolding (§9) but is inherently
  `mw`-coupled (tears down `gui_hooks`, `mw.pokemenu`, `mw.form.menubar`) and references leaf
  windows that don't exist on main (`item_window`, `ankidex`, the web shell). It is also
  Developer-Mode-gated (a leaf) and no §16 smoke test needs it.
- **Recommendation:** DEFER to Stage B, landing with the Developer-Mode + web-shell leaves so its
  teardown list matches the then-present windows. Re-express its `mw.*` teardown through the seam
  where possible; full seam re-expression of a runtime-teardown dev tool may be disproportionate
  (a NEEDS-REVIEW for Stage B, not a license to keep direct-mw in shipped feature code).

## NR-07 — Pre-existing whole-tree ruff debt on the base (baseline red)  ·  INFO
- **What:** `ruff check --config ci_ruff_check.toml src/Ankimon` = **10 errors** (all `UP018`,
  all in the stray file `src/Ankimon/gui_classes/AnkimonWindow copy.py`); `ruff format --check`
  = **78 files would reformat**. Present on pristine `origin/main`.
- **Why not fixed:** CI lints/formats **changed files only**, so it never trips these; the
  Stage-A/B gate lints the whole tree and surfaces the debt. Mass-reformatting untouched files
  would balloon diffs and risk churn.
- **Standard:** Stage A/B add **zero new** ruff-check errors, and every added/modified file is
  `ruff format`-clean (verified: counts stayed 10 / 78). Owner may separately want a one-off
  `ruff format` sweep and deletion of the stray `AnkimonWindow copy.py`.

## NR-08 — `pytest tests/test_addon_integrity.py` blocks under real-aqt + offscreen  ·  INFO
- **What:** the integrity smoke test hangs on a modal `AgreementDialog.exec()` reached at import
  (`singletons`→`ankimon_shop`→`utils.daily_item_list`→`download_sprites`) when the sprites/items
  dir is absent. It is authored for a **mocked-aqt** context (dialogs become inert MagicMocks);
  installing real `aqt`/`PyQt6` makes the dialog real, and there is no user to accept it (xvfb
  would not help).
- **Why not a base defect:** the real-boot signal it approximates is covered GREEN by Tier-2
  `probe_real_boot` (which provisions the env). Not run by CI (`harness.yml` runs Tier-1+Tier-2).
- **Standard:** treated as an environment/test-harness limitation, unchanged from baseline.

## NR-09 — Scaffolding smoke tests run standalone (non-hermetic base suite)  ·  INFO
- **What:** several base test files mock `PyQt6`/`aqt` in `sys.modules` and rebind
  `sys.modules['Ankimon']` to a bare module. Bundled with them, the Qt-dependent smoke tests
  cannot construct real widgets (host becomes a MagicMock; signals do not fire).
- **Resolution:** `tests/test_scaffolding_smoke.py` runs **standalone** in the gate
  (`pytest tests/test_scaffolding_smoke.py` → 4 passed); an autouse guard makes it **skip**
  gracefully (not fail) if bundled with the mocking suite. Un-mocking a compiled Qt extension
  mid-process is unreliable, so standalone is the contract.

## NR-10 — Two-environment gate discipline (Qt-free Tier-1 vs Qt Tier-2)  ·  INFO
- **What:** running Tier-1 (`make check`/economy/longrun) with PyQt6 importable **segfaults at
  teardown** (no `QCoreApplication`) — reproduced on the pristine base (7/9 go red). Mirrors CI's
  separate `tier1` (installs only `requests`) and `tier2` (full Qt) jobs.
- **Resolution:** Stage A ran Tier-1/lint/logic in a Qt-free venv and Tier-2/smoke in a Qt venv.
  Stage B must do the same (see `MERGE_BASELINE.md` §2/§5). Also note Python here is 3.14.6 vs
  CI's 3.12 — re-baseline if Stage B runs on 3.12.

## NR-11 — `requirements.txt` intentionally left unchanged in Stage A  ·  INFO
- **What:** main = `aqt, pytest, pytest-qt, requests, PyQt6, markdown`; exp = `pytest, pytest-qt,
  anki, aqt, PyQt6, orjson, requests` (−markdown, +anki, +orjson).
- **Decision (Stage A):** unchanged. The minimal scaffolding needs nothing new — QtWebEngine +
  QWebChannel come transitively via `aqt`/`PyQt6`; the DB layer uses stdlib `json` (not `orjson`);
  `markdown` is still used by main's changelog rendering and must NOT be dropped.
- **Stage-B requirement:** a leaf that genuinely imports `orjson` (or needs `anki` listed
  explicitly) adds it in that leaf's PR by import-graph evidence; do not blanket-adopt exp's list.

## NR-12 — Divergence/commit counts differ slightly from the brief  ·  INFO
- Git ground truth: `main…origin/BRRRR_Experimental` = **88 / 163** (brief said 88/161);
  **145** non-merge exp-only commits (brief ~143); exp-only change set = **165 files**
  (`git diff --stat a8abbd66..origin/BRRRR_Experimental`). Git wins; recorded for Stage B.

## NR-14 — Meta-docs disposition (repository-analysis / AGENTS.md / feature-list)  ·  OPEN
- **What:** three exp meta-docs are DEFERRED leaves but need an explicit keep-vs-drop-vs-reconcile call
  (surfaced by the independent cross-check):
  - **F03** `repository-analysis/` (21 files) — an agent-oriented architecture audit that describes exp's
    web-shell + direct-`mw` world, which **contradicts main's seam**. As-is it would document a codebase
    that does not exist on main.
  - **F04** `AGENTS.md` — edit-vs-edit with main (main +126 lines seam-oriented; exp +373 lines pointing at
    direct-mw + `repository-analysis/`). Must be reconciled onto main's seam guidance, not overwritten.
  - **F07** `src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md` — a transient planning/changelog doc.
- **Recommendation:** F04 → reconcile (keep main's seam guidance, graft any still-true exp notes).
  F03 → keep only if rewritten to main's architecture, else drop (or move under `docs/` clearly labelled
  "describes the pre-integration exp branch"). F07 → drop from the shipped tree (its content is preserved
  in this ledger + the diff report).
- **Owner decision needed** before Stage B ports F03/F04/F07.

## NR-13 — Commit identity differs from the brief (both are noreply)  ·  INFO
- Brief expected `141889580+h0tp-ftw@users.noreply.github.com`; the machine's configured git
  identity is `h0tp-ftw <h0tp-ftw@users.noreply.github.com>` (a valid GitHub **noreply**, so the
  Privacy Check passes with no consent line). Not changed (§4). Stage B inherits this identity.

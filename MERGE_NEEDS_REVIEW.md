# MERGE_NEEDS_REVIEW.md — escalation ledger (append-only)

The escalation / open-question log for the BRRRR_Experimental → main integration.

**Contract.** Append-only; **both stages append, never overwrite.** One entry per open
question / deferral-with-doubt / significantly-inappropriate candidate / doc-vs-diff conflict /
owner escalation. Nothing is dropped from the integration without an entry here **plus** an
owner ping. Stage A (this session) owns the branch and appends directly. Stage B never pushes
to the integration branch directly — it appends via PRs the owner merges (one consolidated
escalations PR per wave, plus each feature PR carrying its own append).

Status legend: **OPEN** (needs owner) · **RECOMMENDED** (Stage A suggests a path; not decided) ·
**RESOLVED** (owner decided) · **INFO** (recorded, no action).

> **On recommendations.** Any "Recommended path" written below is **non-binding guidance from Stage A**,
> not a mandate. Stage B and the owner are free to pursue a different approach — the recommendation
> is a default to save a round-trip, not a decision. Whoever acts should append their **actual**
> choice + rationale (git stays ground truth); a different, well-reasoned path is entirely welcome.

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

## NR-05 — WAL is opt-in; live WAL enablement deferred (persistence guard)  ·  RECOMMENDED (Stage B's call)
- **What:** exp runs the SQLite DB in WAL for concurrent background access. But the harness
  `probe_persistence` and `BackupManager` simulate/perform a restart by copying **only**
  `ankimon.db` — WAL buffers committed writes in the `-wal` sidecar, so a single-file copy loses
  them ("DATA LOST ON RESTART"). WAL is thus **incompatible with main's single-file persistence
  guard** (§12) unless a checkpoint precedes every copy.
- **Decision (Stage A):** `AnkimonDB(wal=False)` by default — the thread-safe connection layer
  (`check_same_thread=False` + per-thread connections) ships **without** forcing WAL, preserving
  main's persistence/backup behavior (probe_persistence stays green). The `wal=True` capability
  is proven by the scaffolding smoke test on a scratch DB.
- **Hard invariant (not negotiable):** if the live DB is ever put into WAL, restart-persistence
  regresses (probe_persistence goes red, real user saves can be lost) **unless** the WAL is flushed
  into `ankimon.db` before any single-file copy. Don't ship live WAL without solving that.
- **Recommended path (non-binding — Stage B may choose otherwise):** keep `wal=False` until a leaf
  genuinely needs concurrent read-during-write (only the mobile-sync engine, F14/F29, plausibly does);
  when it does, enable `wal=True` **and** add `PRAGMA wal_checkpoint(TRUNCATE)` before every db-file
  copy in `BackupManager`/`switch_database`/any backup path, then re-green probe_persistence.
  - Equally acceptable alternatives if Stage B prefers: copy all three files (`.db`/`.db-wal`/`.db-shm`)
    in the backup path; or keep WAL off entirely and rely on per-thread connections + short
    transactions (the base already works this way and passes the gate); or a different concurrency
    model altogether. Any of these is fine — just don't violate the hard invariant above, and append
    the chosen approach here.

## NR-06 — `reloader.py` deferred (mw-coupled dev tool)  ·  RECOMMENDED (Stage B's call)
- **What:** exp's `reloader.py` hot-reload is listed as scaffolding (§9) but is inherently
  `mw`-coupled (tears down `gui_hooks`, `mw.pokemenu`, `mw.form.menubar`) and references leaf
  windows that don't exist on main (`item_window`, `ankidex`, the web shell). It is also
  Developer-Mode-gated (a leaf) and no §16 smoke test needs it.
- **Recommended path (non-binding — Stage B may choose otherwise):** land it in Stage B alongside the
  Developer-Mode + web-shell leaves, so its window-teardown list matches the then-present windows;
  re-express `mw.*` teardown through the seam where reasonable. A runtime-teardown dev tool that
  operates on Anki's own `gui_hooks`/menubar is a legitimate place where full seam re-expression may be
  disproportionate — if so, escalate it as its own item rather than treating it as license to keep
  direct-`mw` in shipped feature code.
  - Stage B is free to instead bring `reloader.py` earlier (as a standalone dev primitive that no-ops
    on missing windows), rewrite it differently, or drop it — its call, appended here with rationale.

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

## NR-14 — Meta-docs disposition (repository-analysis / AGENTS.md / feature-list)  ·  RECOMMENDED (owner/Stage B call)
- **What:** three exp meta-docs are DEFERRED leaves but need an explicit keep-vs-drop-vs-reconcile call
  (surfaced by the independent cross-check):
  - **F03** `repository-analysis/` (21 files) — an agent-oriented architecture audit that describes exp's
    web-shell + direct-`mw` world, which **contradicts main's seam**. As-is it would document a codebase
    that does not exist on main.
  - **F04** `AGENTS.md` — edit-vs-edit with main (main +126 lines seam-oriented; exp +373 lines pointing at
    direct-mw + `repository-analysis/`). Must be reconciled onto main's seam guidance, not overwritten.
  - **F07** `src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md` — a transient planning/changelog doc.
- **Recommended path (non-binding — owner/Stage B may choose otherwise):**
  - **F04 `AGENTS.md`** → reconcile: keep main's seam-oriented guidance as the base, graft any still-true
    exp notes; do NOT adopt exp's direct-`mw`/`repository-analysis` framing.
  - **F03 `repository-analysis/`** → keep only if rewritten to describe main's (seam) architecture; else
    drop, or move under `docs/` clearly labelled "describes the pre-integration exp branch."
  - **F07 `_BRRR_EXPERIMENTAL_FEATURE_LIST.md`** → drop from the shipped tree (its content is preserved in
    this ledger + the diff report in `~/Downloads`).
  - These are docs only — no runtime/gate impact — so any choice (keep all, drop all, reconcile) is safe.
    Owner/Stage B: pick freely and append the decision; the above is just a sensible default.

## NR-13 — Commit identity differs from the brief (both are noreply)  ·  INFO
- Brief expected `141889580+h0tp-ftw@users.noreply.github.com`; the machine's configured git
  identity is `h0tp-ftw <h0tp-ftw@users.noreply.github.com>` (a valid GitHub **noreply**, so the
  Privacy Check passes with no consent line). Not changed (§4). Stage B inherits this identity.

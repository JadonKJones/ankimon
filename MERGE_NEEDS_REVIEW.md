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

## NR-15 — origin/BRRRR_Experimental advanced 8 commits past Stage A's snapshot (uncovered work)  ·  OPEN (owner decided: escalate)
- **What (git ground truth, Stage B):** at Stage B start `origin/BRRRR_Experimental` = `11b5292e`, i.e. **8 non-merge commits ahead** of the tip Stage A enumerated from (`aad0d6b4`). The exp-only change set is now **170 files, not 165** (NR-12). Per invariant 1a (git > docs) Stage B reconciled the delta.
- **The 8 commits (`aad0d6b4..11b5292e`):** `dfca1848` two bugs from PR #532 pre-merge audit · `8712866b` isolate mocks in test_monthly_challenge_fixes.py · `28bbbf9f` manual port of settings_window bool/int + friendship-evolution fallback · `e62cfd34` migrate legacy string items/badges + backfill individual_ids (#470) · `bf53e341` monthly-challenge shiny-eligibility crash + rate_this/threshold hardening (#483) · `0113b61d` start Discord Rich Presence on first review (#491) · `5ff1a54b` fix ValueError unpacking read_github_file (#489) · `e174af63` bypass data-migration dialog on fresh installs.
- **5 files OUTSIDE Stage A's 165-file partition (no inventory row covers them):**
  1. `src/Ankimon/discord_integration.py` + `src/Ankimon/functions/discord_function.py` — Discord Rich Presence first-review start (#491).
  2. `src/Ankimon/pyobj/help_window.py` — read_github_file ValueError-unpack fix (#489) (paired with `gui_entities.py`, covered by **F43**).
  3. `src/Ankimon/pyobj/migration_dialog.py` — fresh-install migration bypass + legacy string item/badge migration + individual_id backfill (#470) + #532 audit fix.
  4. `tests/test_monthly_challenge_fixes.py` — test for #483 monthly-challenge hardening (production hunks land in `database_manager.py`/`pokemon_trade.py`).
- **Plus extra hunks on 5 ALREADY-COVERED files** (auto-included by those rows' live two-dot manifests at port time → not lost): `pokedex_functions.py`→F17, `settings_window.py`→F28, `database_manager.py`→F14/F25, `pokemon_trade.py`→F48, `gui_entities.py`→F43. Each porting unit is instructed to verify the post-snapshot hunks vs base and call them out in its PR. (F28 PR #544 already carries the settings_window bool/int hunks.)
- **Owner decision (Stage B, control point #2):** **escalate all uncovered work to NEEDS-REVIEW only** — do NOT auto-open PRs for the 5 uncovered files. Rationale: late upstream bug-fixes (citing merged PRs #470/#483/#489/#491/#532), never in Stage A's contract, possibly already on `main`/base (→ superseded no-ops); owner triages manually.
- **Recommended next step:** for each uncovered item, `git diff a8abbd663896b05da592ba7f5402ab6923248974..origin/BRRRR_Experimental -- <path>` then diff vs `origin/main` to check if the upstream PR already merged into main; port only the genuinely-absent ones as a small follow-up, or cherry-pick the upstream commits directly. Reconstruct with `git show 0113b61d 5ff1a54b e174af63 e62cfd34 bf53e341 dfca1848 28bbbf9f 8712866b`.
- **Update (Wave-1 fix pass, 2026-07-02):** exp advanced AGAIN during Wave 1: `11b5292e` → `b04e4bec` (**8 more non-merge commits**, plus merge `41d007d6` = PR #533): `a6204235` in-app updater git-clone (ff-only) safety + PR-install warning + hide pre-v2.0 releases · `64c4c4c2` minimumDefeated evolution condition (Pawmo/Rellor) · `cde90654` trainer cash reward amount/interval scaling · `42066340` circular-import fix in pokedex_functions.py · `4a1cd0cd` Pawmo/Rellor manual evolution check + PC-Box button · `0553e18f` auto-prompt Pawmo evolution on victory reviews · `98dffe9b` gitignore database files globally · `b04e4bec` docs refresh of the DROPPED F03/F07 files (NR-16/17 stand; F07 is 298 lines at this tip). Exp-only change set is now **171 files**. Exactly ONE file is net-new and uncovered by any inventory row: `tests/test_update_manager.py` (pairs with **F26** `update_manager.py` — add it to the manual triage list above). Every other touched file already sits in an existing row's manifest, so its post-snapshot hunks ride along at port time: `update_manager.py`/`update_dialog.py`→F26, `encounter_functions.py`→F22, `friendship_evolution.py`+`tests/test_friendship_evolution.py`→F40, `pokedex_functions.py`/`data_files/pokedex.json`→F17, `gui_classes/pokemon_details.py`→F43, `menu_buttons.py`→F36, `pyobj/pc_box.py`→F42, `pyobj/settings.py`/`config.json`→F28, `lang/en_text.json`→F01, `.gitignore`→F08. Owner decision above applies unchanged (NEEDS-REVIEW only, no auto-PRs). Wave-2+ units and the final triage MUST recompute the delta from git (`git log --oneline --no-merges aad0d6b4..origin/BRRRR_Experimental`) rather than trusting the counts frozen here.

## NR-16 — F03 repository-analysis/ (21 docs) — DROPPED per owner (NR-14 resolution)  ·  RESOLVED
- **What:** F03 (DEFERRED-TO-STAGE-B leaf) = 21 agent-oriented architecture-audit docs under `repository-analysis/` describing exp's web-shell + **direct-`mw`** world, which contradicts main's service seam (would document a codebase that does not exist on main).
- **Owner decision (Stage B, control point #2):** **drop** from the shipped tree. Content preserved in this ledger + the diff report at `~/Downloads/main_vs_BRRRR_Experimental_diff_report.md`; reconstructable via `git show origin/BRRRR_Experimental:repository-analysis/<file>`.
- **Outcome:** no PR; recorded as intentionally dropped (zero-feature-loss satisfied by this entry). Completes F03's set-diff obligation.

## NR-17 — F07 _BRRR_EXPERIMENTAL_FEATURE_LIST.md — DROPPED per owner (NR-14 resolution)  ·  RESOLVED
- **What:** F07 (DEFERRED-TO-STAGE-B leaf) = `src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md`, a 295-line transient exp planning/changelog index inside the shipped addon dir.
- **Owner decision (Stage B, control point #2):** **drop** from the shipped tree (content preserved in this ledger + the diff report). Reconstructable via `git show origin/BRRRR_Experimental:src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md`.
- **Outcome:** no PR; recorded as intentionally dropped. Completes F07's set-diff obligation.
- **Note:** F04 (`AGENTS.md`) is NOT dropped — owner chose *reconcile onto main's seam guidance*; ships as a docs unit in a later wave.

## NR-18 — F30↔F22 atomic-pair partition refinement (CPM formula + its test)  ·  RESOLVED (Stage B)
- **What:** exp shipped `business.calculate_cpm()` rescale and its paired assertion `tests/test_cp_formula.py::test_level_100_near_cap` (`0.84`→`2.45`) as ONE atomic change (commit `180bcf29`). Stage A's clean partition split them: `business.py`→**F30**, `test_cp_formula.py`→**F22**. F30 therefore could not ship green in isolation (base test still pinned the old 0.84 cap → 1 new pytest failure).
- **Resolution (Stage B orchestrator, Wave 1):** authorized **F30 (PR #546)** to carry the single `test_level_100_near_cap` assertion line alongside `business.py`. It is byte-identical to what F22 will also carry, so it **auto-merges** with F22's later PR (no conflict, no semantic double-port). `calculate_cpm(100) = 2.4207… ∈ (2.4, 2.45]`.
- **Action for the Wave-2 F22 unit:** when porting `test_cp_formula.py`, expect the `test_level_100_near_cap` line already at `2.4 < cpm <= 2.45` (landed by F30); apply the rest of F22's test changes onto it. Do NOT treat the pre-applied line as a conflict.

## NR-19 — Wave-1 PR fix-up pass: cross-PR findings for later rows  ·  OPEN (informational)
Context: after Gemini's automated review of PRs #534–#547, a fix-up pass (2026-07-02) added review/polish commits to the Wave-1 branches (13 of 14 PRs updated; F37 #540 needed nothing). Three findings landed outside the fixing unit's partition and are recorded here for the rows that own them:
- **F38 → F22 (encounter overhaul, Wave 2):** base `functions/encounter_data.py` still lists Pecharunt (1025) under `LEGENDARY` and lacks all 15 F38 alternate-form IDs; exp's `encounter_data.py` fixes both. F22 owns that file and MUST land exp's tier lists. A self-arming guard now ships in PR #537 — `tests/test_encounter_tier_data.py::test_encounter_data_agrees_with_pokemon_tiers_on_f38_ids` stays green until any F38 form ID appears in `encounter_data.py`, then fails a partial/unfaithful port. Secondary for F22 review: in exp, 10191 (urshifu-rapid-strike) appears in BOTH `LEGENDARY` and `UNAVAILABLE`, and all F38 form IDs are `PREREQUISITES` keys — the guard deliberately treats those as F22 semantics, but the `LEGENDARY`∩`UNAVAILABLE` overlap for 10191 deserves a look at port time.
- **F28 → owner of `database_manager.py` (F25/DONE-IN-BASE row):** AnkimonDB's config scalar encoding (`str_value = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)` in `save_all_config`/`set_config_value`) cannot round-trip Python `None` (stored as the string `"None"`) and int-ifies digit strings on read (`controls.catch_key "6"` comes back as int `6` via `json.loads` — base's `setup_reviewer_ui` receives ints after a reload today, pre-existing on main). PR #544 patched only the None case at the settings layer (load_config normalization restricted to None-default keys); the principled fix — encode `None` as JSON null, consider storing all values as JSON — belongs in `database_manager.py`. Also: `database_manager.py` defines `set_config_value` twice in the same class (~lines 861 and 914); the first is dead code shadowed by the second (the perf single-row upsert) and should be deleted by the same owner.
- **F39 parity-oracle warning (all rows):** exp's own `tests/test_addon_integrity.py` skip filter is vacuous at the exp tip — a bare `'Ankimon'` in `SKIP_MODULES` prefix-matches every module, so exp's integrity test is a no-op pass that validates nothing. Fixed on the F39 branch (PR #545, commit `3888002f`). Any row or verifier citing exp's integrity test as parity evidence should re-verify against the fixed version.

## NR-20 — Attribution policy: credit BRRRR_Experimental authors on ported commits  ·  POLICY (owner, 2026-07-02)
- **Owner request:** the original BRRRR_Experimental author(s) must receive contributor credit for ported code ("this was originally BRRR's code").
- **Ground truth** (`git shortlog -sne a8abbd66..origin/BRRRR_Experimental`): **Hakimh2** `<74561421+hakimh2@users.noreply.github.com>` authored 131 of the exp-only commits (same account also commits as **BrAk909**; two commits with a broken `Your Name <you@example.com>` author have Hakimh2 as committer → map them to Hakimh2). **AIbrahimv2** `<66210743+AIbrahimv2@users.noreply.github.com>` authored 34, Jupytrr 2, h0tp-ftw 12.
- **Wave-1 retrofit (done):** pushed commits are immutable (no force-push), so each feature PR #534–#546 received one empty attribution commit carrying `Co-authored-by:` trailers for the exp authors of that feature's files (Hakimh2 everywhere; + AIbrahimv2 on F08/#534), plus an "Attribution" section in the PR body. GitHub counts co-authored commits toward the Contributors graph once they reach the default branch (i.e. after integration → main).
- **Wave-2+ MANDATE:** every ported feature commit MUST carry `Co-authored-by:` trailers for the exp authors of its ported hunks, computed per feature via `git log --format='%an <%ae>' a8abbd66..origin/BRRRR_Experimental -- <feature paths>` (exclude h0tp-ftw self-credit; map `Your Name <you@example.com>` → Hakimh2). Trailer form: `Co-authored-by: Hakimh2 <74561421+hakimh2@users.noreply.github.com>`.
- **Merge-style note (owner):** both merge styles preserve the credit — squash-merge aggregates co-author trailers into the squash commit automatically; a regular merge preserves the co-authored commits themselves.

## NR-21 — Wave-2 escalations: cross-PR findings + fuzz-found pre-existing bugs  ·  OPEN (informational)
Context: Wave 2 (PRs #548 F26, #549 F31, #550 F43, #551 F22 — ported 2026-07-02, all gate-green with Gemini review fix-up rounds) surfaced findings outside the fixing unit's partition, plus a fuzzing sweep of the integration tip. Recorded here for the rows that own them.

**Cross-PR findings (from the Wave-2 fix-up passes):**
- **F31 → F32 (`src/Ankimon/__init__.py`, Wave 3):** `__init__.py` (line 114 at `fd9010f4`) registers `gui_hooks.reviewer_did_answer_card.append(on_review_card)` with NO idempotency guard — the same reload-unsafety class Gemini flagged and F31 fixed in `card_hooks.py` (PR #549, commit `2987c17f`: registry-anchored `(hook, handler)` record with remove-before-append). F32 owns `__init__.py` and MUST apply the same guard pattern; `probe_real_boot`'s double-boot hook count is the ground truth.
- **F43 → owner of `functions/pokemon_functions.py` (no active row; likely Wave-5 NR-15 triage):** `find_experience_for_level` raises `UnboundLocalError` for `level > 99` with an unrecognized growth-rate string — the >99 branch never assigns `experience` before `return experience` (the <100 path already defaults to 0). Callers sharing the exposure: `trainer_functions.py`, `encounter_functions.py`, `reviewer_iframe.py`. F43's call-site `max(1, ...)` clamp (PR #550) cannot catch an exception raised inside the function. Fix: final default in the >99 branch + regression test.
- **F26 → F20 (profile hooks, Wave 4):** PR #548 gates the branch-update poll on boot-time connectivity captured in the `schedule_branch_update_check` closure (mirrors how base gates `check_and_show_changelog`); exp re-evaluated connectivity per profile-open in `profile_hooks.py`. F20 can restore per-open checking when it lands.

**Fuzz-found pre-existing bugs (2026-07-02, `mega_fuzz` 12-seed Tier-2 sweep + `fuzz.py` 400-iteration Tier-1 on tip `fd9010f4`; every crash site byte-identical to `main` — NOT wave regressions; owner decision: defer, fix later as a standalone hardening PR or in whichever row next touches the file):**
- **Profile-load hard crash:** `pyobj/starter_window.py:302 resize_pixmap_img` divides by a null QPixmap's width (0) when a starter sprite PNG is missing/corrupt → `ZeroDivisionError` inside `run_startup_sequence()` → addon fails to boot. Repro: `python harness/scenarios/mega_fuzz.py --replay 0 80 corrupt`.
- **Item Shop hard crash (SIGABRT):** with sprites declined, `utils.daily_item_list()` returns `[]` → `DAILY_ITEMS_POOL = []` → Game→Item Shop runs `random.sample([], 3)` (`pyobj/ankimon_shop.py:455`); the ValueError escapes the Qt menu slot and aborts Anki. The empty-list guard in `daily_item_list` (commented "to prevent the crash") only moved the crash from import time to the menu click. Repro: `python harness/scenarios/mega_fuzz.py --replay 4 80 blank`.
- **`functions/pokedex_functions.py:469 get_growth_rate` raises `ValueError(species_id)` for 10xxx alternate-form IDs** (~5% of Tier-1 fuzz iterations). Callers use `get_growth_rate(sid) or "medium"`, expecting a falsy return — the fallback is unreachable dead code. Increasingly user-reachable now that F38 (tiers) and F22 (encounter overhaul) make form encounters real.
- Non-deterministic one-offs (observed once in the sweep, clean on isolated replay; kept for pattern-matching): enemy HP `13/12` invariant violation; one caught "Error simulating battle" error event; one `int('')` ValueError.

## NR-22 — Wave-3 escalations: cross-row findings from PRs #553–#559  ·  OPEN (informational)
Context: Wave 3 (PRs #553 F32, #554 F17, #555 F34, #556 F40, #557 F42, #558 F23, #559 F51 — ported 2026-07-02 on Opus 4.8, all gate-green through porter → adversarial verifier → Gemini fix-up rounds). Findings that land outside the fixing unit's partition, recorded for their owners.

- **F32 → owner of `utils.py` (F33 rows / Wave-5 triage):** `count_items_and_rewrite()` (utils.py:508) now runs on F32's QueryOp background thread, and its own `except` handler calls `show_warning_with_traceback` → constructs a `QDialog` OFF the GUI thread when a DB failure occurs mid-boot (low probability: requires `get_all_items()` to fail after the same thread already used the DB; headless-safe; matches exp verbatim). Fix: make the function raise (letting startup.py's outer log-only handler catch) or route through `services.ui`.
- **F32 (parity note):** the vestigial `get_main_pokemon_data()` call in `_generate_first_enemy_background` is a no-op DB read (result discarded; `main_pokemon` is populated eagerly at import) — kept for exp parity; safe to drop in a later polish row.
- **F17 → owner of `data_files/items.csv`:** data gap — no identifier for **'Metal Alloy'**, so the `useItem` evolution Duraludon → Archaludon (evoItem 'Metal Alloy') cannot match under any name normalization. Add the item row (data fix, any wave).
- **F40 (parity note):** Cosmoem day/night level-evolution branching is INERT — `pokemon_evolution.csv` rows 429/430 tag Solgaleo=day / Lunala=night at Lv53, but `get_level_evolutions` does not consult time-of-day for level evolutions. Matches exp exactly (not a port defect); wiring it is a deliberate behavior change for a future polish row.
- **F51 (parity note):** `_get_display_name` substring-matches 'mega'/'gmax' in the species name, so ordinary species containing those substrings (Meganium, Yanmega) display English pretty names instead of localized names in non-English locales. Byte-for-byte exp behavior; a future polish row could tighten to real form-suffix checks.
- **F23 → merged F22 (`functions/encounter_functions.py`, Wave-5 polish):** line ~433 — `_modify_percentages_legacy`'s fallback (`main_pokemon.level if main_pokemon is not None else 1`) is less robust than the overhaul guard its comment claims to mirror (no guard against a None/absent `.level` attribute). Pre-existing merged F22 code; out of F23's scope; align the guard (or the comment) in the Wave-5 pass.

## NR-23 — Wave-4 escalations: web-shell/mobile/menu cross-cutting findings  ·  OPEN (informational)
Context: Wave 4 (mobile F14/F15/F29 + ankidex F16 merged @106eea16; menu F36/F21 in Wave-4c; the web-shell HOST providing `AnkimonItemsWeb`/`WebShellHost`). Non-blocking findings surfaced by the adversarial verifiers + Fable final checks that land outside the fixing unit's partition — all polish/cleanup-grade (none blocked merge). Recorded here for the rows that own them; substantive ones are Wave-5 candidates.

- **Mobile → XP-Share design divergence (substantive, Wave-5):** mobile replay XP is awarded via `save_main_pokemon_progress` in `functions/mobile_sync.py` and never routes through `kill_pokemon`'s `xp_share_gain_exp` (the `pyobj/ankimon_sync.py` sync hook only triggers the replay), so an XP-Share designee gains NO XP from mobile-synced battles. Not a dropped guard (None-checks intact) — a behavioral gap vs desktop. Follow-up: decide whether mobile battles should credit the XP-Share target.
- **Mobile → production test-double sniff (cleanup):** `pyobj/ankimon_sync.py` `on_sync_did_finish` special-cases test mocks with `if type(max_revlog_id).__name__ in ("MagicMock","Mock")` — production code branching on a test double. Harmless at runtime (real sqlite never returns a Mock). Follow-up: move the isolation into the tests and drop the sniff.
- **Menu → `is_dev_mode()` helper missing (substantive, Wave-5):** there is no real `is_dev_mode()` on the tip — only local `def is_dev_mode(): return False` fallbacks in `reviewer_ui.py:28`, `ankimon_items_web/shop_obj.py:30`, and `menu_buttons.py:44` (the same fallback). So the dev submenu (Switch Account, Encounter Rate Simulator) is wired but INERT (always hidden). The real helper belongs to F33 (marked DONE-IN-BASE, but `is_dev_mode` didn't land). Follow-up: add `is_dev_mode()` to `utils.py` reading the developer-mode setting and replace the scattered local fallbacks.
- **Menu → deferred entries (Wave-5):** the nature-chart menu entry is not wired (needs a `get_nature_chart` factory); the `restart_ankimon` dev action is not wired (`reloader.py` absent on the tip — F31/NR-06). `create_menu_actions` kept its now-unused `pokedex_window` param to avoid an out-of-scope `__init__.py` signature change. Follow-up: wire both once the factory/reloader land, and drop the vestigial param.
- **Ankidex → payload-shape duplication + dual settings namespace (cleanup/migration):** `get_ankidex_data`'s db-None empty payload hand-duplicates the full SPA contract shape (`ankidex/ankidex_obj.py`) — schema drift would need editing in two places. Separately, prefs read still falls back to legacy `pokedex_v2.*` keys alongside `ankidex.*`, leaving a dual namespace. Follow-up: derive the empty payload from one source of truth; retire `pokedex_v2.*` in a migration unit.
- **F12 → skipped web-serialization test now un-skippable (cleanup):** `test_equipped_items_web_serialization_and_unequip` is an unconditional `pytest.skip`; now that the HOST is merged (`AnkimonItemsWeb` exists) it can be un-skipped for live coverage. Follow-up: un-skip in the Wave-5 test pass.

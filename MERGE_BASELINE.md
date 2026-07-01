# MERGE_BASELINE.md — Pristine gate baseline for `integration/brrr-into-main`

**Purpose.** This file records the exact pass/fail state of every gate check on the
**untouched** integration base, so both Stage A and Stage B share one definition of
"green": **green = no NEW failures versus this recorded baseline.** If a check is already
red or unrunnable here, that is the baseline — do not treat matching it as a regression,
and do not weaken/skip/delete any check to move it.

Stage A was authored/verified by Claude (Opus 4.8). Report reality, not optimism.

---

## 1. Base identity

- Integration branch: `integration/brrr-into-main`
- Branched from: **`origin/main` @ `9dc52cd1`** (`9dc52cd100117d9e807d190af68b23f43d8c3786`)
  — the local `main` scratch commit `6d37cae9` ("im a ghost", which only added
  `main_vs_BRRRR_Experimental_diff_report.md`) was **excluded** per owner decision; that doc
  was moved out to `~/Downloads/`.
- Submodule: `src/Ankimon/poke_engine` @ `f3092b03` (initialized; `poke_engine` is pure-Python,
  needs only `requests`).
- Baseline measured on the pristine tree **before** any scaffolding synthesis.

## 2. Environment (record verbatim; reused by Stage B)

- Host OS: Linux (CachyOS); shell `/bin/fish`. System Python: **3.14.6**.
  ⚠️ **The repo's own CI (`.github/workflows/harness.yml`) uses Python 3.12** (Tier-1) / 3.12
  (Tier-2). This baseline was taken on **3.14.6**. Record as a known env delta; if Stage B runs
  on 3.12 it should re-baseline. Everything below passed on 3.14.6.
- **No system Python packages and no `pip` were preinstalled**; `xvfb`/`xvfb-run` are **absent**.
  Isolated venvs were created in the session scratchpad (NOT in the repo, NOT committed).

  ⚠️ **TWO environments are required — do not use one venv for everything** (this mirrors
  CI's two separate jobs, `harness.yml` `tier1` vs `tier2`). Tier-1 / lint / logic tests MUST
  run **Qt-free**: if PyQt6 is importable, the Tier-1 harness (and even pytest logic that boots
  the addon) loads real Qt with no `QCoreApplication` and **segfaults at teardown** — this
  happens on the *pristine* base too (7/9 Tier-1 checks go red purely from PyQt6 being present,
  though each probe's own logic still prints OK). So:

  ```bash
  # venv_t1 — Qt-FREE: compileall, ruff, make check, economy, longrun, pytest logic tests
  python3 -m venv <venv_t1>                       # ensurepip → pip 26.1.2
  <venv_t1>/bin/pip install requests ruff pytest

  # venv_qt — FULL Qt: Tier-2 probe_real_boot/play, and the scaffolding smoke tests
  python3 -m venv <venv_qt>
  <venv_qt>/bin/pip install requests ruff pytest pytest-qt orjson PyQt6 aqt anki
  ```

  Exact versions used for this baseline:

  | Package | Version |
  |---|---|
  | requests | 2.34.2 |
  | ruff | 0.15.20 |
  | pytest | 9.1.1 |
  | pytest-qt | 4.5.0 |
  | PyQt6 | 6.11.0 (Qt runtime 6.11.1) |
  | aqt | 26.5 |
  | anki | 26.5 |
  | orjson | 3.11.9 |

- **QtWebEngine / headless env** (export before any check that boots Qt / QWebEngineView):

  ```bash
  export PYTHONPATH="$PWD/src"
  export QT_QPA_PLATFORM=offscreen
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-software-rasterizer"
  export QTWEBENGINE_DISABLE_SANDBOX=1
  ```

  `xvfb-run` is unavailable in this environment. The repo's CI wraps Tier-2 in
  `xvfb-run -a … QT_QPA_PLATFORM=offscreen`. Here, **`QT_QPA_PLATFORM=offscreen` alone was
  sufficient** — `QApplication`, `QWebEngineView` instantiation, and both Tier-2 probes all
  ran clean without an X server. If a future check truly needs a display, install `xvfb` and
  run under `xvfb-run -a` (CI's form).

## 3. Gate results on the pristine base

Legend: ✅ pass · 🟡 pre-existing red / limitation (this IS the baseline) · ❌ fail.

### (a) Compile — incl. poke_engine
```bash
python -m compileall -q src/Ankimon
```
✅ **PASS** (exit 0). Whole package incl. `poke_engine` byte-compiles; submodule pointer valid.

### (b) Lint & format (ruff) — whole `src/Ankimon` (poke_engine & pypresence excluded by config)
Config: **`ci_ruff_check.toml`** is used for BOTH check and format
(confirmed from `.github/workflows/ruff_format.yml` lines 44/51 and `ruff_check.yml` line 45).
`ci_ruff_check.toml`: `extend-exclude = ["poke_engine","pypresence"]`, `select = ["PLE","UP018"]`.

```bash
ruff check  --config ci_ruff_check.toml src/Ankimon
ruff format --check --config ci_ruff_check.toml src/Ankimon
```
🟡 **`ruff check`: 10 errors (baseline red)** — all rule `UP018` (native-literals), **all 10 in
one stray file `src/Ankimon/gui_classes/AnkimonWindow copy.py`**. Pre-existing on `origin/main`.
🟡 **`ruff format --check`: 78 files would be reformatted** (15 already formatted). Pre-existing
whole-tree formatting debt.
> Why red on a "clean" base: the repo's CI runs ruff **only on changed files** (`xargs` over
> changed-files), so it never sees this whole-tree debt. The Stage-A/B gate runs ruff on the
> whole `src/Ankimon`, which surfaces it. **Standard for Stage A/B: add ZERO new ruff-check
> errors, and every file you add/modify must be `ruff format`-clean** (so the 10 / 78 counts do
> not increase for files you touch). Do not mass-reformat untouched files.

### (c) Tests — pytest (headless)
> ⚠️ `pytest tests/` is **NOT part of the repo's CI** (`harness.yml` runs Tier-1 + Tier-2 only;
> `main.yml` is release-only). Per the "trust the repo" rule it is auxiliary, but recorded here.

```bash
# smoke (as the gate names it):
python -m pytest tests/test_addon_integrity.py -v
# full, minus the smoke:
python -m pytest tests/ --ignore=tests/test_addon_integrity.py -q
```
✅ **Full suite minus integrity smoke: 149 passed** (~1.3s). All pure-logic tests
(they use `tests/conftest.py` stubs; only `test_addon_integrity.py` uses real-Qt `qapp`).
🟡 **`test_addon_integrity.py`: BLOCKS (does not complete) under real-`aqt` + offscreen.**
Diagnosis (faulthandler): during its `pkgutil.walk_packages` import sweep,
`card_hooks.py` → `singletons.py:30` → `ankimon_shop.py:32` (module-level
`DAILY_ITEMS_POOL = daily_item_list()`) → `utils.daily_item_list()` → (when the sprites/items
dir does not exist) `download_sprites.show_agreement_and_download_dialog()` → a **modal
`QDialog.exec()`** with no user to accept it. The test is authored for a **mocked-`aqt`** context
(its `except ImportError` path makes dialogs inert MagicMocks); installing **real** `aqt`/`PyQt6`
here makes the dialog real. `xvfb` would NOT help (still no clicker). **The real-boot signal this
smoke approximates is covered GREEN by Tier-2 `probe_real_boot` (below), which provisions the env
properly.** Treat as an environment/test-harness limitation, not a base defect. Stage B inherits it.

### (d) Local harness gate — THE authoritative gate (what CI enforces)
```bash
make check                              # = python3 harness/check.py  (Tier-1, no Qt)
python3 harness/scenarios/economy.py
python3 harness/scenarios/longrun.py 3000
python3 -m harness.checks.probe_real_boot   # Tier-2 (real add-on, offscreen Qt)
python3 -m harness.checks.probe_real_play   # Tier-2
```
✅ **`make check` (Tier-1): all 9 checks green** — `probe_contract` (~65 seams intact),
`probe_core`, `probe_fixtures`, `probe_foundations`, `probe_leaves` (26 modules imported aqt-free),
`probe_migration`, `probe_persistence`, `smoke_play`, `test_headless_harness`.
✅ **`economy.py`: OK** (buy funded/insufficient-funds paths).
✅ **`longrun.py 3000`: OK** (3000 answers, ~2,833 turns/sec; event totals emitted).
✅ **`probe_real_boot`: OK** — real add-on boots under offscreen Qt (`FakeMW`, `QtPresenter`,
real windows `TestWindow`/`EvoWindow`/`PokemonPC`/`Reviewer_Manager`, 3 review hooks registered).
✅ **`probe_real_play`: OK** — real play-through (answers ~29, resolutions 3, caught 2, defeated 1).
(Benign non-failing stderr: `qt.multimedia.ffmpeg`, `propagateSizeHints()`, `QPixmap::scaled null
pixmap` from missing sprite assets headless.)

`make doctor` → ✅ ready (python ≥3.10 OK, poke_engine present).

### (e) Scaffolding smoke tests (§16)
Not applicable to the pristine base (no scaffolding present yet). These will be **added** with the
scaffolding in Phase 3 and must be green in the Phase-4 re-run:
host+stub-screen mount, WAL 2-thread open/close, one QWebChannel `notify_stats_changed` push,
one QueryOp boot to completion.

## 4. Summary — pristine base

| Check | Result |
|---|---|
| compileall (incl poke_engine) | ✅ PASS |
| ruff check (`ci_ruff_check.toml`, whole `src/Ankimon`) | 🟡 10 UP018 errors, all in `gui_classes/AnkimonWindow copy.py` (baseline) |
| ruff format --check (`ci_ruff_check.toml`) | 🟡 78 files would reformat (baseline debt) |
| pytest (full, minus integrity smoke) | ✅ 149 passed |
| pytest `test_addon_integrity.py` (smoke) | 🟡 blocks: real-aqt modal dialog; covered by `probe_real_boot` |
| make check (Tier-1, 9 checks) | ✅ PASS |
| economy.py | ✅ PASS |
| longrun.py 3000 | ✅ PASS |
| probe_real_boot (Tier-2) | ✅ PASS |
| probe_real_play (Tier-2) | ✅ PASS |

**Authoritative CI gate (Tier-1 + Tier-2) is fully GREEN on the pristine base.** The only reds are
the pre-existing whole-tree ruff debt (not CI-gated) and the auxiliary integrity-smoke modal-dialog
limitation. Both are flagged in `MERGE_NEEDS_REVIEW.md`.

## 5. Re-verify command (copy/paste) — TWO environments

```bash
cd "$HOME/PycharmProjects/ankimon"
git submodule update --init --recursive
export PYTHONPATH="$PWD/src"

# ---- (A) Qt-FREE env (venv_t1): compile, lint, Tier-1, logic tests ----
python -m compileall -q src/Ankimon
ruff check  --config ci_ruff_check.toml src/Ankimon                 # baseline: 10 errors
ruff format --check --config ci_ruff_check.toml src/Ankimon         # baseline: 78 reformat
make check                                                          # Tier-1: 9/9
python3 harness/scenarios/economy.py
python3 harness/scenarios/longrun.py 3000
python -m pytest tests/ --ignore=tests/test_addon_integrity.py \
                        --ignore=tests/test_scaffolding_smoke.py -q  # 149 passed

# ---- (B) Qt env (venv_qt): Tier-2 + scaffolding smoke ----
export QT_QPA_PLATFORM=offscreen
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-software-rasterizer"
export QTWEBENGINE_DISABLE_SANDBOX=1
python -m pytest tests/test_scaffolding_smoke.py -q   # scaffolding smoke, STANDALONE: 4 passed
python3 -m harness.checks.probe_real_boot
python3 -m harness.checks.probe_real_play
```

> The scaffolding smoke tests (added with the scaffolding) run **standalone** in the Qt env;
> bundled with the base suite they skip gracefully because several base test files mock
> PyQt6/aqt in `sys.modules`. The base logic suite (149) runs in EITHER env.

# Ankimon agent harness

Play Ankimon **headlessly** — no Anki, no Qt, no display — so an AI agent (or a
plain test) can drive the real game logic, observe a structured event stream, and
validate features/PRs without a human clicking through Anki.

This is dev-only tooling. It is **not** shipped with the add-on.

## Why this exists

Anki add-ons are painful to test: every module historically imported `aqt`, so
importing anything dragged in the whole GUI runtime, and there was no
machine-readable record of what the game *did*. This harness is the payoff of the
"headless-core" refactor:

- The game **core** (DB, settings, battle loop, encounters, catching, leveling,
  evolution checks, the poke-engine bridge) now imports with **no `aqt`/`PyQt6`**.
- Every observable action emits a structured **event** (`encounter`, `battle`,
  `faint`, `catch`, `defeat`, `levelup`, `evolution_offered`, `tooltip`, `sound`,
  `hud`, `log`, `notify`, `error`, …) via `src/Ankimon/events.py`.
- GUI side-effects are reached through a small **UI presenter port**
  (`services.ui`) and the window objects in `services` — real Qt in Anki,
  recording fakes here.

## Requirements

- Plain `python3` (3.10+). **No** `aqt`, `PyQt6`, `pytest`, or a display needed.
- The `poke_engine` git submodule must be present (battle simulation):
  `git submodule update --init --recursive`.
- `requests` is used by a couple of helpers but not by the core loop.

## Run it

```bash
# Import-safety + smoke probes
python3 harness/checks/probe_foundations.py
python3 harness/checks/probe_leaves.py      # 26 core modules import aqt-free
python3 harness/checks/probe_core.py        # build_core() boots the whole game state

# Scripted play sessions
python3 harness/scenarios/smoke_play.py     # answer cards, catch + defeat
python3 harness/scenarios/auto_battle.py    # automatic_battle modes 1/2/3
python3 harness/scenarios/economy.py        # cash + buying items

# Interactive REPL — one JSON request per line in, one JSON response per line out
python3 -m harness.server
printf '{"action":"answer","ease":"good"}\n{"action":"get_state"}\n{"action":"quit"}\n' \
  | python3 harness/server.py
```

## Tier 2 — run the REAL add-on (offscreen Qt)

Tier 1 (above) is fast and runs anywhere, but it swaps Ankimon's real Qt windows
for recording fakes — so it can't reproduce real-Qt behaviour (widget memory,
crashes, glitches) or run logic that lives *inside* the window classes (e.g. the
PC box).

**Tier 2 boots the genuine add-on** — real `import Ankimon` → real `__init__.py`
→ `singletons.py` → every real Qt window — with only the *Anki host* faked
(`harness/fake_aqt.py`: `mw`, `gui_hooks`, `aqt.*`) and **real PyQt6 in offscreen
mode**. Nothing is drawn, but the real widgets/memory/PC box are all live, which
is what makes real-Qt glitches and "crash after N encounters" reproducible.

It needs PyQt6 + native Qt libs. The setup is **sudo-free** (a venv with pip
bootstrapped via get-pip.py, and the Qt `.deb`s *downloaded and extracted* into a
local dir — nothing installed system-wide; `rm -rf .tier2` undoes it):

```bash
bash harness/setup_tier2.sh        # one-time: builds .tier2/ (venv + local Qt libs)
source .tier2/env.sh               # LD_LIBRARY_PATH + QT_QPA_PLATFORM=offscreen + venv
python -m harness.checks.probe_real_boot   # real add-on boots; objects are the REAL classes
python -m harness.checks.probe_real_play   # plays via real hooks: real windows, real battles
```

Drive it from Python (same action surface as Tier 1, via real hooks/windows):

```python
from harness.real_driver import RealDriver
d = RealDriver(settings_overrides={"battle.cards_per_round": 1})
d.answer("good")     # fires the real reviewer_did_answer_card hook chain
d.catch()            # the real reviewer catch shortcut
d.get_state()
```

Tier-2 scenarios (drive + see the real windows):

```bash
python -m harness.scenarios.pc_box_moves   # open the real PC box, change a caught
                                           # Pokemon's moves (persists to DB) + screenshot
python -m harness.scenarios.screenshots    # PNGs of the real battle window + PC box
```

`harness/screenshot.py` (`grab(widget, path)`) renders any real widget to a PNG via
`widget.grab()` — offscreen Qt still paints to a buffer, so you get the genuine UI
(real sprites + layout) with no display.

### Real sprites (pixel-accurate)

By default a fresh profile has no sprites, so `real_env` seeds one placeholder
`substitute.png` — the real window code runs, just with placeholder pixels. To
run with the genuine Pokémon art, fetch the real sprite set (same `sprites.zip`,
~600 MB, the add-on uses; stdlib-only, sudo-free):

```bash
python3 harness/fetch_sprites.py          # -> .tier2/sprites-cache (one-time)
```

After that, each Tier-2 session symlinks its `sprites/` dir to that cache, so the
real windows load the real sprites (verified: e.g. `rhyhorn #111` ->
`front_default/111.png`). Set `ANKIMON_SPRITE_CACHE` to point elsewhere.

Note: the 3 WebEngine windows (pokedex/achievements/help) use lightweight stubs
so the boot doesn't need the Chromium-based `PyQt6-WebEngine`.

## Drive it from Python

```python
from harness.driver import Driver

d = Driver(settings_overrides={"battle.cards_per_round": 1})
events = d.answer("good")     # answer a card -> the real battle loop runs
d.get_state()                 # JSON-able snapshot: main/enemy/tracker/collection/trainer
# when the wild Pokemon faints:
d.defeat()                    # or d.catch()  -> spawns the next encounter
```

### Actions (Driver methods, also the REPL `action` names)

| action | what it does |
|---|---|
| `answer(ease)` | answer a card (`1-4` or `again/hard/good/easy`) → runs the battle loop |
| `catch()` / `defeat()` | resolve a fainted wild Pokemon, then spawn the next |
| `encounter()` | force a brand-new wild encounter |
| `set_setting(key, value)` | change a settings key (e.g. `battle.automatic_battle`) |
| `set_move(move)` | script the move chosen next turn (needs `controls.allow_to_choose_moves`) |
| `add_cash(n)` / `buy_item(name)` | drive the shop economy |
| `get_state()` | snapshot of the world |
| `drain_events()` | events since the last drain |

Each action returns the events it produced; `get_state()` returns the snapshot.

## How it boots (architecture)

```
bootstrap()         install a stub `Ankimon` package + ANKIMON_USER_PATH (temp dir)
   │                so the aqt-free core imports without running Ankimon/__init__.py
core.build_core()   construct logger/DB/settings/translator/Pokemon/trainer/tracker,
   │                register them in services  (SAME code production uses)
fakes.install_fakes recording stand-ins for test_window/evo_window/pokemon_pc/reviewer
core.bind_runtime_globals()   point the battle-loop modules' globals at the registry
Driver              high-level actions over that session
```

The production composition root (`src/Ankimon/singletons.py`) calls the *same*
`build_core()` and then builds the real Qt windows + `QtPresenter` on top — so the
harness and Anki share one source of truth and can't drift.

## Scope & caveats

- **Two fidelity tiers.** *Tier 1* (fake windows) validates game logic/state/PR
  behaviour and runs anywhere with no deps — but can't reproduce real-Qt
  behaviour or window-internal logic. *Tier 2* (real add-on, offscreen Qt)
  reproduces real widgets/memory/glitches and runs the real window code; it needs
  the `.tier2` env. Neither renders to a screen, so pure visual/CSS bugs still
  need a human or real Anki — though Tier 2 *can* `widget.grab().save("x.png")` to
  capture how a widget looks offscreen.
- **One session per process.** Sessions reset the DB singleton + registry, but the
  writable `user_path` is fixed at first import; for full isolation run each
  session in a fresh interpreter (the scenarios/tests do).
- **Errors surface as events,** not crashes: the battle loop reports exceptions
  through the `error` event (check for `type == "error"`), mirroring how Anki shows
  the error dialog.
- The bundled `poke_engine` prints battle debug to stdout; the Driver suppresses it
  so it never pollutes the REPL's JSON channel.
```

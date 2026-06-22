# Ankimon harness — complete reference

The exhaustive API/functionality surface. `SKILL.md` is the quick playbook; read
this when you need an exact signature, the full event/setting catalog, or a module
you haven't used. Everything here lives in `harness/` (dev-only, never shipped).
Prose/architecture depth: `harness/README.md`; contributor rules: `AGENTS.md`.

## Module map (`harness/`)
| file | what it is |
|---|---|
| `driver.py` | **Driver** — the Tier-1 agent API (drives the aqt-free core directly) |
| `headless_env.py` | `start_session(...)` — boots a Tier-1 session (what `Driver` wraps) |
| `real_driver.py` | **RealDriver** — Tier-2 API (drives the real add-on via real Anki hooks) |
| `real_env.py` | `start_real_session(...)` — boots the genuine add-on offscreen |
| `fixtures.py` | build/seed Pokémon + `set_enemy` (load saves, construct state) |
| `diagnostics.py` | `profile(...)` — DB-query/cProfile/memory profiler + `Report` |
| `debug.py` | `wait_for_client()` — attach pdb/debugpy |
| `check.py` | the one-command Tier-1 gate (`--doctor` too) |
| `clock.py` | controllable calendar (install/advance) |
| `screenshot.py` | `grab(widget, path)` — offscreen widget → PNG (Tier 2) |
| `state.py` | `snapshot()`, `grade_for()`, `normalize_ease()` |
| `server.py` | JSON-line REPL over the Driver |
| `bootstrap.py` | `bootstrap()` (import stub + env) + `quiet()` |
| `fakes.py` | recording fake windows (Tier 1) |
| `fake_aqt.py` | fake Anki host: `mw`, `gui_hooks`, `aqt.*` (Tier 2) |
| `checks/` | `probe_*` import/boot probes | 
| `scenarios/` | scripted play sessions |

## Tier 1 — `Driver`
```python
from harness.driver import Driver
d = Driver(**kwargs)        # kwargs flow to start_session()
```
`start_session` / `Driver(...)` keyword args:
| arg | default | meaning |
|---|---|---|
| `settings_overrides` | `None` | dict of settings keys set before the first encounter, e.g. `{"battle.cards_per_round": 1}` |
| `seed` | `None` | construct a starting state (see Fixtures) — main/team/box/items |
| `db` | `None` | path to an existing `ankimon.db`; **copied** into a throwaway profile, source never mutated |
| `clock_start` | `None` | a `datetime`; turns on the controllable calendar |
| `first_encounter` | `None` | open on a real wild encounter. `None` → True for a blank session, False when `db=` is given |
| `evolution_policy` | `"decline"` | how the fake evo window answers: `"decline"` or `"ignore"` |
| `event_sink` | `None` | `callable(event_dict)` tee'd every event (e.g. a JSONL writer) |
| `user_path` | temp dir | profile dir (a fresh temp dir if None) |

**Actions** (each returns the list of events it produced, except where noted):
| method | returns | notes |
|---|---|---|
| `answer(ease=3)` | events | `ease` = `1-4` or `again/hard/good/easy`; runs the real battle turn |
| `catch()` | events | catch the **fainted** wild mon, then spawn the next |
| `defeat()` | events | defeat the fainted wild mon for XP, then spawn the next |
| `encounter()` | events | force a brand-new **random** wild encounter |
| `set_enemy(spec=None, **kw)` | events | force a **specific** wild encounter (Fixtures spec); emits `encounter` |
| `set_move(move)` | `{ok,next_move}` | script the move chosen next turn (needs `controls.allow_to_choose_moves=True`) |
| `set_setting(key, value)` | `{ok,key,value}` | change a settings key live (**returns a dict, not events**) |
| `add_cash(amount)` | `{ok,cash}` | add trainer cash |
| `buy_item(name, item_type=None)` | events | drive the shop economy (check cash, deduct price, add item); emits `buy` |
| `advance_time(days=0,hours=0,minutes=0,seconds=0)` | `{ok,now}` | fast-forward the clock (needs `clock_start=`) |
| `time_of_day()` | str | Ankimon's day/night reading at the current clock |
| `get_state()` | snapshot dict | JSON-able world snapshot (see below) |
| `drain_events()` | events | events since the last drain |
| `act(action, **kwargs)` | varies | dispatch a named action (used by the REPL) |

## Tier 2 — `RealDriver`
```python
from harness.real_driver import RealDriver           # needs the .tier2 env
d = RealDriver(settings_overrides={...}, first_encounter=True)
```
Boots the genuine add-on (`start_real_session(user_path=None, settings_overrides=None,
neuter_network=True)`) with real Qt windows offscreen; actions fire the **real**
`gui_hooks` / reviewer shortcuts. Action surface (subset of Tier 1):
`answer / catch / defeat / encounter / set_setting / advance_time / time_of_day /
get_state / drain_events / act`. (No `set_enemy`/`set_move`/`add_cash`/`buy_item` on
Tier 2 yet — use Tier 1 for those, or `d.services` / the real window objects directly.)
Requires `bash harness/setup_tier2.sh` once (see Tier-2 setup below).

## Fixtures — construct state (`harness/fixtures.py`)
Used via `Driver(seed=...)`, `Driver(db=...)`, and `Driver.set_enemy(...)`. Pokémon are
built from the game's **own pokedex data**; only the spec fields you pin are overridden.

**Pokémon spec** (a dict; one species id required):
| field | notes |
|---|---|
| `species` or `id` | name (e.g. `"Gengar"`) or pokedex id |
| `level` | default 50 |
| `ability` | any string — **not** legality-checked (feature: test illegal combos) |
| `moves` / `attacks` | list; default = up to 4 from the level-legal learnset. Auto-normalized (`"Shadow Ball"`→`shadowball`) |
| `ivs`/`iv`, `evs`/`ev` | dict or scalar; default IV 31, EV 0 |
| `nature` | default `"serious"` |
| `shiny` | default False |
| `gender` | **`"M"`/`"F"`/`"N"`** (not `"female"`) |
| `held_item` | internal name, e.g. `"lucky-egg"` (not `"Lucky Egg"`) |
| `hp` | pin a current HP (e.g. to reproduce a low-HP bug) |

**`seed=` dict** (all optional): `main` (a spec → becomes is_main + team slot 1),
`team` (list of specs), `box` (list — caught, off-team), `items` (`{name: qty}`).

Functions (if you need them directly): `build_pokemon(spec) -> PokemonObject`,
`seed_db(seed, db)`, `set_enemy(services, events, spec)`.

> Defaults are **clean/canonical** (IV 31, first ability, first learnset moves), not a
> random wild roll — deliberately reproducible. For a true random wild mon use
> `d.encounter()` (you don't pick the species/level there).

## Diagnostics — profile (`harness/diagnostics.py`)
```python
from harness.diagnostics import profile
with profile(driver, label="run", memory=False, backend="cprofile", top=15) as report:
    ...workload...
report.print()        # human-readable
report.as_dict()      # JSON-able (for assertions / diffing branches)
```
- `backend`: `"cprofile"` (stdlib, default) · `"pyinstrument"` (pip; falls back to
  cprofile with a note if absent) · `"none"`.
- `memory=True`: adds `tracemalloc` top-allocators (heavier; great for leak hunting).
- **`Report` fields**: `label`, `backend`, `wall_seconds`, `query_total`, `queries`
  (`{normalized_sql: count}` — N+1 detector), `rss_start`, `rss_end`,
  `tracemalloc_top` (`[(loc, kb, count)]`), `cprofile_top` (`[(func, ncalls, tot, cum)]`),
  `profile_text` (pyinstrument tree).
- **Read it right:** query counts + profiler *shape* are hardware-independent (the
  *where*/*how-it-scales*); wall/RSS are indicative on this box only.
- Optional tools (into a **venv**, never add-on deps): `harness/requirements-dev.txt`
  (pyinstrument, scalene, memray, py-spy, line_profiler, objgraph, debugpy).

## The world snapshot (`get_state()`)
```python
{
  "main":  {name, id, level, hp, max_hp, xp, status, attacks, shiny, tier},
  "enemy": {name, id, level, hp, max_hp, xp, status, attacks, shiny, tier},
  "tracker": {encounter, cards_round, multiplier, caught, card_streak},
  "collection": {count, ids},                          # caught pokedex ids
  "trainer": {name, level, xp, cash},
}
```

## Event catalog (returned by actions / `drain_events()` / the REPL)
Each event is `{"type": <name>, ...fields}`. To investigate: scan for `type=="error"`,
and assert invariants from `get_state()`.
| type | when | key fields |
|---|---|---|
| `encounter` | a wild mon appears | pokemon, id, level, tier, shiny, hp, max_hp |
| `battle` | a battle turn resolves | user, enemy, user_move, enemy_move, dmg_to_enemy, dmg_to_user, user_hp, enemy_hp, multiplier |
| `faint` | a mon faints | who (`enemy`/`main`), pokemon, id |
| `catch` | caught | pokemon, id, shiny, tier, nickname |
| `defeat` | defeated | pokemon, id, tier |
| `levelup` | main levels up | pokemon, level |
| `evolution_offered` | evo eligible | pokemon, trigger (`level`/`friendship`), evo_id |
| `tooltip` | on-screen battle/level text | message, color |
| `sound` | a cry/effect would play | kind (`cry`/`effect`), pokemon_id / sound |
| `hud` | HUD repaint | action |
| `log` / `notify` | log line / would-be popup | level, message |
| `dialog` | a move/attack/evo choice point | dialog, options, chosen |
| `buy` | shop purchase | item, ok, price/reason |
| `error` | an exception in the game loop (= Anki's error dialog) | message, exception, traceback |

## Scenarios (`harness/scenarios/`, run as scripts or `from harness.scenarios import X; X.run(...)`)
| scenario | signature | purpose | tier |
|---|---|---|---|
| `smoke_play` | `run(max_answers=120, target_resolutions=4, verbose=True, seed=7)` | answer cards, catch+defeat, assert invariants (the gate's core) | 1 |
| `auto_battle` | `run(mode=2, answers=40, verbose=True)` | `battle.automatic_battle` modes 1/2/3 | 1 |
| `economy` | `run(item="potion", verbose=True)` | earn/grant cash + buy an item | 1 |
| `longrun` | `run(n=1000, verbose=True)` | thousands of turns; aggregates events | 1 |
| `soak` | `run(n=10000, tier="real", sample=1000, verbose=True)` | memory soak; watch RSS for leaks | 1/2 |
| `profile_battles` | `main(n=2000)` | N battles under the profiler (DB/cProfile/memory) | 1 |
| `pc_box_moves` | `run(verbose=True, shots_dir=None)` | open the **real** PC box, change a mon's moves (persists) + screenshot | 2 |
| `screenshots` | `run(shots_dir=None, verbose=True)` | PNGs of the real battle window + PC box | 2 |

## Probes (`harness/checks/`) — import/boot safety
`probe_foundations`, `probe_leaves` (all core modules import aqt-free), `probe_core`
(`build_core()` boots the whole state), `probe_fixtures` (load/seed/set_enemy + a real
bug repro) — Tier 1. `probe_real_boot`, `probe_real_play` — Tier 2 (need `.tier2`).
New `probe_*.py` auto-join the gate.

## The gate (`harness/check.py`)
`python3 harness/check.py` runs every Tier-1 probe + smoke + the regression test,
isolated, → single PASS/FAIL, **exit 0 = green**. `--doctor` checks python≥3.10 +
the `poke_engine` submodule. CI runs it on every PR (`.github/workflows/harness.yml`).
`make check / setup / doctor / tier2` are sugar.

## REPL (`python3 -m harness.server`)
One JSON request per line in, one JSON response per line out.
- Request: `{"action": "<name>", ...kwargs}` · Response: `{"ok": true, "result": ...}` or `{"ok": false, "error": "..."}`.
- Actions: `answer, catch, defeat, encounter, set_setting, set_move, buy_item, add_cash, get_state, drain_events, ping, quit`.
```bash
printf '{"action":"answer","ease":"good"}\n{"action":"get_state"}\n{"action":"quit"}\n' | python3 harness/server.py
```

## Controllable clock
`Driver(clock_start=datetime(2026,6,1,12,0))` then `d.advance_time(days=, hours=, …)`
and `d.time_of_day()`. Drives day/night evolutions, daily cash reset, streaks, capture
stamps. (Real-time *delays* — animations/timers — are skipped entirely; only the
calendar is simulated.) Underlying: `harness/clock.py` (`install_clock/advance/now`).

## Debugging
```bash
python3 -m pdb harness/scenarios/smoke_play.py        # stdlib; or breakpoint() in src/
python3 -m debugpy --listen 5678 --wait-for-client harness/scenarios/smoke_play.py
# or, inside a script:  from harness.debug import wait_for_client; wait_for_client(port=5678)
```
Set breakpoints in `src/Ankimon`; inspect variables while a *simulated* review runs.

## Tier-2 setup (offscreen Qt)
```bash
bash harness/setup_tier2.sh        # one-time, sudo-free: venv + locally-extracted Qt libs under .tier2/
source .tier2/env.sh               # LD_LIBRARY_PATH + QT_QPA_PLATFORM=offscreen + venv
python3 harness/fetch_sprites.py   # optional: real ~600MB sprite set (pixel-accurate)
```
`harness/screenshot.py:grab(widget, path, size=None)` renders any real widget to PNG.
Note: the 3 WebEngine windows (pokedex/achievements/help) use lightweight stubs so the
boot doesn't need Chromium-based `PyQt6-WebEngine`.

## Settings keys (for `set_setting` / `settings_overrides` / fuzzing)
Full set + defaults live in `DEFAULT_CONFIG` (`src/Ankimon/pyobj/settings.py`). Groups:
- `battle.*` — `automatic_battle` (0=manual,1/2/3), `cards_per_round`, `daily_average`, `card_max_time`, `review_based_damage`
- `evolution.*` — `friendship_time_enabled`, `day_start_hour`, `night_start_hour`, `timezone_auto`, `timezone_offset`
- `controls.*` — `allow_to_choose_moves`, `pokemon_buttons`, `defeat_key`, `catch_key`, `key_for_opening_closing_ankimon`
- `gui.*` — `animate_time`, `gif_in_collection`, `styling_in_reviewer`, `hp_bar_config`, `pop_up_dialog_message_on_defeat`, `reviewer_image_gif`, `reviewer_text_message_box[_time]`, `show_mainpkmn_in_reviewer`, `team_deck_view`, `view_main_front`, `xp_bar_config`, `xp_bar_location`, …
- `audio.*` — `sound_effects`, `sounds`, `battle_sounds`, `volume`
- `misc.*` — `gen1..gen9`, `remove_level_cap`, `language`, `ssh`, `leaderboard`, `ankiweb_sync`, `show_tip_on_startup`, `discord_rich_presence[_text]`, `developer_mode`
- `trainer.*` — `name`, `sprite`, `id`, `cash`, `cash_reward_amount`, `cash_reward_interval`, `cash_earned_today`, `last_cash_reward_date`, `level`, `xp`

## Caveats / honest limits
- **Two tiers.** Tier 1 = fast, anywhere, fake windows (logic/state/data). Tier 2 =
  real Qt windows offscreen (real widget memory/glitches), needs `.tier2`.
- **Logic/state/data → yes; pixels & felt-latency → a human.** The harness finds the
  *cause* of lag (N+1 queries, deepcopy churn), not the milliseconds a user feels.
- **One session per process.** Sessions reset the DB singleton + registry, but
  `user_path` is fixed at first import; for full isolation run each session in a fresh
  interpreter (the scenarios/probes/`check.py` do).
- **Errors surface as `error` events**, not raised exceptions (mirrors Anki's error dialog).
- **Never put any of this in `src/`**; generated saves are throwaway (temp dirs), never committed.

# Ankimon — Agent & Contributor Guide

A Pokémon game addon for [Anki](https://apps.ankiweb.net/) — the spaced repetition flashcard app. Every card review triggers a Pokémon battle. You catch, evolve, and collect Pokémon while studying.

The addon runs inside Anki's Python/Qt environment. `aqt` is Anki's module, `mw` is the main window singleton.

> This file is the single source of agent instructions. It is mirrored to `AGENTS.md` (root), `.agents/AGENTS.md`, `.agents/CLAUDE.md`, and `.agents/GEMINI.md`.

---

## Before You Code: Read the Repository Intelligence

> [!IMPORTANT]
> This repository contains **21 detailed analysis documents** in [`repository-analysis/`](repository-analysis/) covering architecture, data models, startup flow, risk register, editing playbooks, and more.
>
> Before making any code changes, read (in order):
> 1. [`00-executive-overview.md`](repository-analysis/00-executive-overview.md) — startup sequencing & architecture
> 2. [`15-agent-handoff.md`](repository-analysis/15-agent-handoff.md) — the 9 operational rules below (expanded)
> 3. [`11-editing-playbook.md`](repository-analysis/11-editing-playbook.md) — step-by-step recipes for common changes
>
> For deep dives, consult the [reading order](repository-analysis/08-reading-order.md).

---

## Repository Structure

```
src/Ankimon/                  # The Anki addon (symlinked to addons21/ for dev)
  __init__.py                 # Entry point — imports, wiring, hook registration
  startup.py                  # Boot sequence: backup, migration, assets, first enemy
  singletons.py               # All singleton objects (settings, pokemon, tracker, etc.)
  battle_loop.py              # Core battle loop (on_review_card), BattleState dataclass
  card_hooks.py               # Card timer + answer quality tracking hooks
  reviewer_ui.py              # Reviewer shortcut keys + bottom bar buttons
  profile_hooks.py            # Profile lifecycle: tip of the day, monthly pokemon, sync
  hook_registry.py            # Catch/defeat hook system for external integrations
  resources.py                # File paths, constants, version detection
  business.py                 # CP calculation, experience formulas
  reloader.py                 # Dev-mode hot-reload: teardown + module purge + restart
  utils.py                    # Shared utility functions
  const.py                    # Global constants
  gui_entities.py             # UI entity definitions
  menu_buttons.py             # Anki menu item wiring
  texts.py                    # User-facing text strings
  changelog.py                # GitHub changelog fetch + update notification
  discord_integration.py      # Discord Rich Presence hooks
  hooks.py                    # Additional hook utilities

  functions/                  # Game logic (encounters, battles, badges, evolution)
  pyobj/                      # Qt dialog classes (settings, shop, PC box, evolution)
    database_manager.py       #   ← THE chokepoint for all DB reads/writes
    pokemon_obj.py            #   ← PokemonObject model
    reviewer_obj.py           #   ← HUD updates via JavaScript injection
    settings.py               #   ← Settings singleton with live get()/set()
  gui_classes/                # More UI classes (pokemon details, team view)
  classes/                    # Additional domain classes
  poke_engine/                # Battle simulation engine (from ArdentRoe/poke-engine)

  web/                        # Shared web assets (HTML/CSS/JS for QWebEngine views)
  ankimon_items_web/          # Items/Ankidex/Settings/Profile/Team web shell
  ankimon_profile_web/        # Profile web view
  ankidex/                    # Pokédex web UI
  achievements/               # Achievement system
  data_files/                 # Static data (pokedex.json, learnsets.json, etc.)
  pokedex/                    # Pokédex data files
  lang/                       # Localization files
  encounter_simulator/        # Encounter simulation tools

  user_files/                 # User data directory (gitignored)
    sprites/                  #   Pokemon sprites (downloaded on first run)
    ankimon.db                #   SQLite database (all user data)
    ankimonDEV.db             #   Dev/test database (hot-swappable)

repository-analysis/          # 21 detailed architecture & analysis documents
tests/                        # Test suite
scripts/                      # Release/build scripts
.agents/skills/               # Agent skills (trade generator, DB manager, etc.)
```

> For per-file details, see [02-file-cards.md](repository-analysis/02-file-cards.md).

---

## Architecture

### Data Flow (Core Battle Loop)

1. User reviews a card in Anki
2. `card_hooks.py` tracks timing and answer quality
3. `battle_loop.py` runs the battle → calls poke-engine via the bridge
4. `encounter_functions.py` handles catch/defeat/level-up
5. `reviewer_obj.py` updates the HUD via JavaScript injection into the webview

### Key Singletons (singletons.py)

All singletons are anchored to `mw` for reload safety. Pass via constructor injection — never import directly.

| Singleton | Source | Purpose |
|---|---|---|
| `settings_obj` | `pyobj/settings.py` | User preferences, live `get()`/`set()` |
| `main_pokemon` | `pyobj/pokemon_obj.py` | Active player Pokémon |
| `enemy_pokemon` | `pyobj/pokemon_obj.py` | Current wild opponent |
| `ankimon_tracker_obj` | `pyobj/ankimon_tracker.py` | Review counts, battle round counter |
| `ankimon_db` | `pyobj/database_manager.py` | SQLite connection manager |
| `trainer_card` | `pyobj/trainer_card.py` | Player profile (level, cash, badges) |
| `logger` | `ShowInfoLogger` | Logging (use this, never `print()`) |

### Data Storage

All user data is in SQLite (`user_files/ankimon.db`). Only `database_manager.py` should touch the DB directly.

Key tables: `captured_pokemon`, `items`, `badges`, `team`, `pokemon_history`, `metadata`

Legacy JSON files are migrated on first run via `migration_dialog.py`.

---

## Critical Rules for Agents

These are the **non-negotiable constraints** that prevent the most common agent mistakes. Violating any of these will introduce bugs.

> [!CAUTION]
> These rules are extracted from [15-agent-handoff.md](repository-analysis/15-agent-handoff.md) and [06-conventions-observed.md](repository-analysis/06-conventions-observed.md). Read both for full context.

### 1. Never Do Synchronous Disk I/O During Card Reviews

Static data (pokedex.json, learnsets.json, sprites) is parsed once at startup and cached in memory. During card reviews, always use cached methods (`search_pokedex_by_id`, `_get_learnset_moves`). Never call `json.load(open(...))` in the review path.

### 2. Defensive Hook Wrapping

All reviewer hooks (`_shortcutKeys`, `_linkHandler`, `_bottomHTML`) are monkeypatched with boolean guards. Always:
- Check `if _ui_hooks_installed: return` before wrapping
- Save original method pointers for teardown restoration
- Restore originals in `restore_reviewer_ui()`

Failure causes wrapper accumulation → massive review lag.

### 3. Database Hot-Swap Protocol

When toggling between `ankimon.db` and `ankimonDEV.db`:
1. Close connection atomically (no open cursors/transactions)
2. Switch path
3. Open new connection
4. Run state refresh cascade: Settings → TrainerCard → PC Box → MainPokemon

### 4. Case-Insensitive Key Lowercasing

**Always `.lower()` all name keys before DB saves or cache lookups.** JSON lookups fail silently on capitalized names. Strip hyphens too where applicable.

### 5. Reward Cap Enforcement

All reward values have enforced bounds via `validate_and_clamp()`:
- Intervals: `[5, 250]`
- Cash: `[10, 2000]`
- Max ratio: `100:1` (cash-to-card cheat prevention)

### 6. poke_engine Isolation

`poke_engine/` is a standalone battle simulation engine with **zero Ankimon imports**. The only bridge is `functions/ankimon_hooks_to_poke_engine.py`. Never import from `poke_engine/` directly anywhere else.

### 7. Thread Safety

- Background threads (`QueryOp` workers) must **never** access or mutate Qt GUI objects
- Background threads return data as dicts; all UI work happens in the main-thread callback
- Qt widgets can only be created/accessed on the main thread

### 8. Pokédex V2 Terminology

Use the standardized terms — agents and UI text must be consistent:
- **Capture Requirements** (not "Prerequisites")
- **Registry Progress** (not "Completion Status")
- **Unseen Species** (not "Locked")

### 9. Unified Web Shell Routing

All web-based screens route through `AnkimonItemsWeb` with `_open_shell_at("items"|"ankidex"|"settings"|"profile"|"team")`. Use QWebChannel bridges (`bridge`, `nav`, `settings`, `trainer`, `team`) for Python↔JS communication. Broadcast updates via `notify_stats_changed()`.

---

## Conventions

| Convention | Detail |
|---|---|
| **Logging** | Use `logger.log()`, never `print()` |
| **Resource paths** | Always use `resources.py` — never hardcode file paths |
| **CSS theming** | Use palette variables: `--accent-green`, `--accent-blue`, `--accent-gold`, `--text-muted` |
| **Nature display** | Green ▲ (boosted stat) / Red ▼ (decreased stat) |
| **SQLite transactions** | Use `with conn:` blocks for immediate commits |
| **Singleton access** | Pass via constructor `__init__` — never import globals directly |
| **Virtual columns** | Never write to virtual columns — write to the `data` JSON field via `save_pokemon()` |
| **CSS blur filters** | Avoid `backdrop-filter: blur()` — causes Windows DWM compositor flickering in QWebEngine |

---

## Making Changes

### General Rules

- Run `pytest tests/` after **every** change. All tests must pass.
- Run the Anki smoke test for anything touching startup, imports, or singletons.
- Never modify user data files (anything gitignored).
- `__init__.py` is a thin orchestrator — add new logic to the appropriate extracted module.
- `singletons.py` instantiates objects — don't add logic there.

### Documentation Maintenance

When your change **adds, removes, or significantly restructures** a module, singleton, data model, setting key, UI surface, or hook — update the relevant `repository-analysis/` document to match.

| Change type | Documents to update |
|---|---|
| New/removed module or file | [02-file-cards.md](repository-analysis/02-file-cards.md), [14-import-hotspots.md](repository-analysis/14-import-and-call-hotspots.md) |
| New/changed singleton | [02-file-cards.md](repository-analysis/02-file-cards.md), [03-startup-and-control-flow.md](repository-analysis/03-startup-and-control-flow.md) |
| New/changed data model or table | [16-data-models-and-schemas.md](repository-analysis/16-data-models-and-schemas.md), [20-persistence-deep-dive.md](repository-analysis/20-persistence-deep-dive.md) |
| New/changed setting key | [17-config-surface-map.md](repository-analysis/17-config-surface-map.md) |
| New/changed Anki hook or side effect | [18-event-hooks-and-side-effects.md](repository-analysis/18-event-hooks-and-side-effects.md) |
| New/changed UI surface or dialog | [19-ui-surface-to-logic-map.md](repository-analysis/19-ui-surface-to-logic-map.md) |
| New risk identified | [05-risk-register.md](repository-analysis/05-risk-register.md) |
| New convention established | [06-conventions-observed.md](repository-analysis/06-conventions-observed.md) |
| Architecture change (layers, boundaries) | [01-architecture-map.md](repository-analysis/01-architecture-map.md), [09-module-boundaries.md](repository-analysis/09-module-boundaries.md) |
| AGENTS.md itself updated | `.agents/skills/openrouter-agent/references/ankimon_context.md` |

**Do NOT update repo-analysis docs for**: bug fixes, CSS-only changes, test-only changes, comment/docstring edits, or changes that don't affect the documented architecture.

If the AGENTS.md itself needs updating (new rule, new skill, etc.), update all 4 mirrored copies: `AGENTS.md`, `.agents/AGENTS.md`, `.agents/CLAUDE.md`, `.agents/GEMINI.md`. Also update `.agents/skills/openrouter-agent/references/ankimon_context.md` to keep the OpenRouter context in sync.

### Editing Playbooks

For step-by-step recipes, see [11-editing-playbook.md](repository-analysis/11-editing-playbook.md):

- **Adding a new regional form**: Update `REGIONAL_FORM_LOOKUP` → add to `ACTIVE_REGION_BOOSTS` → run encounter simulation tests
- **Wrapping a reviewer hook**: Declare guards → check before wrapping → save originals → implement cleanup
- **Adding a new setting**: Add default in `database_manager.py` → add UI in `settings_window.py` → access via `settings_obj.get("key")`
- **Adding a new module**: Create file → wire in `__init__.py` → add to integrity ignore list if it needs Anki runtime

### PR Workflow

- Every change goes through a PR, even small fixes. No direct pushes to main.
- PRs from external contributors: push adapted code to their branch if `maintainerCanModify` is true, then merge their PR so they get credit.
- Reference the original issue/PR number in commit messages: `fix: nickname bug (#361)`

---

## Running Tests

```bash
# Install dependencies (once)
pip install pytest pytest-qt PyQt6 markdown

# Run all tests (headless Qt)
$env:QT_QPA_PLATFORM="offscreen"
python -m pytest tests/ -v

# Run just the integrity test (imports every module)
python -m pytest tests/test_addon_integrity.py -v
```

All tests should pass. The integrity test dynamically imports every module to catch ImportError/AttributeError at load time.

### Encounter Simulation Suite (Specialized)

> [!NOTE]
> This is **not** a routine test. Only run it when changing encounter logic — pool weights, regional forms, variant substitution rates, prerequisite gating, or gen toggles.

```bash
python scratch/encounter_weighting_simulations/test_encounter_simulation.py
```

Runs 10k+ mock generations to verify encounter rate integrity (pool percentages, active region spawn rates, starter gating, prerequisite DAGs, post-selection variant substitution).

### Test Integrity Ignore List

The integrity test skips these modules (they require full Anki runtime):
- `Ankimon.singletons` (StopIteration from mock Qt widgets)
- `Ankimon.pyobj.tip_of_the_day` (uses `from aqt.qt import *` at class level)
- `Ankimon.poke_engine.tests.*` / `Ankimon.poke_engine.setup` (upstream test files)

If you add a new module that crashes during import without Anki, add it to `ignore_modules` in `test_addon_integrity.py` AND explain why.

## Running Anki for Manual Testing

```bash
# Using the anki-vscode dev setup:
<PATH_TO_ANKI_EXECUTABLE> -b "<PATH_TO_ANKI_PROFILE>"

# Quick 20-second smoke test:
timeout 20 <PATH_TO_ANKI_EXECUTABLE> -b "<PATH_TO_ANKI_PROFILE>" 2>&1 || true
```

Clean startup should show: `AnkimonDB: Database schema initialized.` and `Ankimon Startup.` with no tracebacks.

---

## Common Pitfalls

| Pitfall | Why it matters |
|---|---|
| `aqt` and `anki` modules only exist inside Anki runtime | Tests must mock them |
| Qt widgets can only be created/accessed on the main thread | Segfaults otherwise |
| `settings_obj.get()` is called live everywhere | Values are not cached at startup — changes take effect immediately |
| Sprites are gitignored and downloaded on first run | Source of truth: `h0tp-ftw/ankimon-sprites` repo |
| `user_files/` is for runtime data | Never commit files there |
| Circular prerequisite chains | Cause infinite recursion → Anki hang. Prerequisites must form a strict DAG |
| Mega/Gmax IDs ≥ 10000 | Must be resolved to base species via `check_id_ok()` for gen toggle checks |
| `card_hooks.py:answerCard_after()` and `__init__.py:on_review_card()` | These are INDEPENDENT Anki callbacks — they don't call each other |

---

## Agent Skills

Specialized skills are available in `.agents/skills/`. Agents should check for relevant skills before implementing from scratch.

| Skill | Trigger |
|---|---|
| **ankimon-trade-generator** | Generating trade codes, computing trade passwords, gifting Pokémon |
| **pokemon-db-manager** | Adding/removing Pokémon to/from a `.db` file by name or Pokédex ID |
| **frontend-design** | Creating web components, UI layouts, or polishing web views |
| **improve-codebase-architecture** | Finding refactoring opportunities, improving testability |
| **openrouter-agent** | Delegating heavy token-expensive tasks to cheaper LLMs |
| **skill-creator** | Creating, modifying, or benchmarking agent skills |
| **ankimon-harness** | Testing, profiling, fuzzing, reproducing bugs in the game with no Anki and no clicking |
| **validate-pr** | Validating, reviewing, testing, or signing off on a PR or branch |

---

## Risk Register (Quick Reference)

| Risk | Precaution |
|---|---|
| Circular prerequisite chains | Verify DAG structure; all chains must lead to a zero-prereq base |
| Reviewer hook wrapper accumulation | Use `_ui_hooks_installed` guards; restore originals on teardown |
| Database hot-swap lockout | Close connections atomically; run full state refresh cascade |
| Case-sensitivity lookup failures | Always lowercase + strip hyphens before lookups |
| Disk I/O during card reviews | Always use in-memory caches |
| Global singleton coupling | Use dependency injection, pass explicitly via constructors |
| Thread-safety violations in async startup | Background thread = read-only; all GUI on main thread |
| Windows DWM compositor flickering | Avoid `backdrop-filter: blur()`; disable `WA_TranslucentBackground` |

> Full risk analysis: [05-risk-register.md](repository-analysis/05-risk-register.md)

---

## External Repos

- [`h0tp-ftw/ankimon-sprites`](https://github.com/h0tp-ftw/ankimon-sprites) — Sprite assets. GitHub Action auto-builds ZIP + syncs to HuggingFace.
- [`ArdentRoe/poke-engine`](https://github.com/ArdentRoe/poke-engine) — Battle simulation engine used as a submodule.
- [`h0tp-ftw/anki-vscode`](https://github.com/h0tp-ftw/anki-vscode) — Dev environment setup for running Anki with debugger.

---

## Repository Intelligence Index

For deeper dives into any subsystem, consult these documents in `repository-analysis/`:

| # | Document | What it covers |
|---|---|---|
| 00 | [Executive Overview](repository-analysis/00-executive-overview.md) | Startup sequencing, architecture overview |
| 01 | [Architecture Map](repository-analysis/01-architecture-map.md) | 5-layer architecture, module relationships |
| 02 | [File Cards](repository-analysis/02-file-cards.md) | Per-file summaries with dependencies |
| 03 | [Startup & Control Flow](repository-analysis/03-startup-and-control-flow.md) | Boot order, battle loop, settings loading |
| 04 | [Source of Truth](repository-analysis/04-source-of-truth.md) | SQLite authority, encounter pools |
| 05 | [Risk Register](repository-analysis/05-risk-register.md) | 8 identified risks with mitigations |
| 06 | [Conventions](repository-analysis/06-conventions-observed.md) | 9 coding conventions |
| 07 | [Glossary](repository-analysis/07-glossary.md) | Pokédex V2 terminology |
| 08 | [Reading Order](repository-analysis/08-reading-order.md) | 5 curated trails for different goals |
| 09 | [Module Boundaries](repository-analysis/09-module-boundaries.md) | 4-layer boundary map |
| 10 | [Test Intelligence](repository-analysis/10-test-intelligence.md) | Test strategy, mocking, coverage |
| 11 | [Editing Playbook](repository-analysis/11-editing-playbook.md) | Step-by-step recipes for common changes |
| 12 | [Unknowns](repository-analysis/12-unknowns-and-questions.md) | Resolved uncertainties |
| 13 | [Core File Appendix](repository-analysis/13-core-file-appendix.md) | Key code excerpts |
| 14 | [Import Hotspots](repository-analysis/14-import-and-call-hotspots.md) | Most-imported files, chokepoints |
| 15 | [Agent Handoff](repository-analysis/15-agent-handoff.md) | 9 operational rules for agents |
| 16 | [Data Models](repository-analysis/16-data-models-and-schemas.md) | PokemonObject fields, SQLite schemas |
| 17 | [Config Surface](repository-analysis/17-config-surface-map.md) | All settings keys with defaults |
| 18 | [Event Hooks](repository-analysis/18-event-hooks-and-side-effects.md) | Anki hooks, custom hooks, side effects |
| 19 | [UI Surface Map](repository-analysis/19-ui-surface-to-logic-map.md) | UI elements → backing logic files |
| 20 | [Persistence](repository-analysis/20-persistence-deep-dive.md) | SQLite WAL, backups, hot-swap |

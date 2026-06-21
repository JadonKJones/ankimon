"""
harness/headless_env.py — boot a fresh, isolated Ankimon session headless.

Wires together everything needed to *play* without Anki/Qt:
  1. bootstrap() — env + sys.path + the import stub (before any Ankimon import).
  2. build_core() — the real aqt-free game state (DB/settings/Pokemon/...).
  3. install_fakes() — recording stand-ins for the GUI windows.
  4. settings overrides + battle state + a first wild encounter.

Returns a SimpleNamespace of the live objects and the callables the Driver
invokes. Everything runs against a throwaway temp profile so sessions never
touch a real Anki install.
"""

from __future__ import annotations

import tempfile
from types import SimpleNamespace

from .bootstrap import bootstrap, quiet


def start_session(
    user_path=None,
    settings_overrides=None,
    evolution_policy: str = "decline",
    event_sink=None,
    first_encounter: bool = True,
) -> SimpleNamespace:
    """Boot a headless session and return a namespace of handles for the Driver.

    user_path: profile dir (a fresh temp dir if None).
    settings_overrides: dict of settings keys to set (e.g. {"battle.cards_per_round": 1}).
    evolution_policy: "decline" | "ignore" — how FakeEvoWindow answers evolutions.
    event_sink: optional callable(dict) tee'd every event (e.g. JSONL writer).
    first_encounter: generate a real wild Pokemon up front (vs the placeholder).
    """
    if user_path is None:
        user_path = tempfile.mkdtemp(prefix="ankimon_session_")

    bootstrap(user_path=user_path)

    # Safe to import the aqt-free core now that the stub + env are in place.
    from Ankimon.events import events
    from Ankimon.services import services
    from Ankimon.core import build_core, bind_runtime_globals
    from . import fakes

    # Per-session isolation: point the DB at THIS session's profile dir and drop
    # any cached singleton, so sessions are independent even within one process.
    # (resources.user_path is computed once at import from the env var, so for a
    # 2nd+ session we must update it — and database_manager's bound copy — here.)
    import Ankimon.resources as _resources
    import Ankimon.pyobj.database_manager as _dbm
    from pathlib import Path as _Path
    _resources.user_path = _Path(user_path)
    _dbm.user_path = _Path(user_path)
    _dbm.reset_db()
    services.reset()

    # Build core game state and install GUI fakes with events OFF, so none of the
    # setup noise (config save, etc.) lands in the buffer the agent reads.
    events.disable()
    events.reset()
    with quiet():
        build_core()
    fakes.install_fakes(evolution_policy=evolution_policy)

    if settings_overrides:
        with quiet():
            for key, value in settings_overrides.items():
                services.settings.set(key, value)

    # Now that core + GUI fakes are all registered, bind the core logic modules'
    # bare globals (main_pokemon, settings_obj, test_window, …) to them.
    bind_runtime_globals()

    # Battle state: the set of already-collected pokedex ids + reset counters.
    from Ankimon.battle_loop import init_battle_state, on_review_card
    from Ankimon.functions.encounter_functions import (
        new_pokemon,
        catch_pokemon,
        kill_pokemon,
    )
    from Ankimon.utils import load_collected_pokemon_ids

    collected_ids = load_collected_pokemon_ids()
    init_battle_state(collected_ids)

    # From here on, capture events for the agent.
    events.enable(sink=event_sink)
    events.reset()

    if first_encounter:
        # Replace the placeholder Rattata with a real, level-scaled wild Pokemon
        # so the session opens on a genuine encounter (emits an "encounter" event).
        with quiet():
            new_pokemon(
                services.enemy_pokemon,
                services.test_window,
                services.tracker,
                services.reviewer,
            )

    return SimpleNamespace(
        user_path=user_path,
        services=services,
        events=events,
        on_review_card=on_review_card,
        new_pokemon=new_pokemon,
        catch_pokemon=catch_pokemon,
        kill_pokemon=kill_pokemon,
        collected_ids=collected_ids,
    )

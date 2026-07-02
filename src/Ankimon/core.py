"""
core.py — the aqt-free composition root for Ankimon's game state.

Builds the addon's core objects — logger, database, settings, translator, the
main and (placeholder) enemy Pokemon, trainer card, tracker, achievements — and
registers them in the service registry (:mod:`Ankimon.services`). It imports
NOTHING from aqt/PyQt6, so the exact same construction runs in two places:

* **Production** — ``singletons.py`` calls :func:`build_core` and then builds the
  Qt windows on top, wiring the real :class:`QtPresenter` into ``services.ui``.
* **Headless** — the agent harness calls :func:`build_core` and wires recording
  fakes + the default :class:`HeadlessPresenter` instead.

Sharing this code (rather than duplicating it in the harness) is what keeps the
two roots from drifting, and it means the headless tests exercise the very same
construction production uses.

Ordering note: ``services.db`` and ``services.logger`` are registered BEFORE
``Settings()`` is constructed, because ``Settings.load_config`` reads
``services.db`` on the first call. Registering them late would make the very
first config load fall through to defaults.
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace

from .services import services
from .pyobj.InfoLogger import ShowInfoLogger
from .pyobj.database_manager import get_db
from .pyobj.settings import Settings
from .pyobj.translator import Translator
from .pyobj.pokemon_obj import PokemonObject
from .pyobj.trainer_card import TrainerCard
from .pyobj.ankimon_tracker import AnkimonTracker
from .functions.update_main_pokemon import update_main_pokemon
from .functions.badges_functions import populate_achievements_from_badges


def _build_placeholder_enemy() -> PokemonObject:
    """The initial enemy Pokemon shown before the first real encounter.

    Mirrors the historical default from singletons.py verbatim. It is a
    placeholder: ``new_pokemon()`` overwrites it (via ``update_stats``) the first
    time an encounter is generated.
    """
    return PokemonObject(
        name="Rattata",
        shiny=False,
        id=19,
        level=5,
        ability="Run Away",
        type=["Normal"],
        stats={
            "hp": 39, "atk": 52, "def": 43, "spa": 60, "spd": 50, "spe": 65, "xp": 101,
        },
        attacks=["Quick Attack", "Tackle", "Tail Whip"],
        base_experience=58,
        growth_rate="medium-slow",
        hp=30,
        ev={"hp": 3, "atk": 5, "def": 4, "spa": 1, "spd": 2, "spe": 3},
        iv={"hp": 27, "atk": 24, "def": 3, "spa": 24, "spd": 16, "spe": 21},
        gender="M",
        battle_status="Fighting",
        xp=0,
        position=(5, 5),
        tier="Normal",
        captured_date=None,
        individual_id=str(uuid.uuid4()),
    )


def build_core(
    logger=None,
    db=None,
    settings=None,
    translator=None,
    main_pokemon=None,
    enemy_pokemon=None,
    trainer_card=None,
    tracker=None,
    achievements=None,
) -> SimpleNamespace:
    """Construct the core game objects and register them in ``services``.

    Returns a ``SimpleNamespace`` of the constructed objects so a caller
    (singletons / the harness) can also expose them as module globals for
    back-compat.
    """
    # Logger + DB first, and registered immediately: Settings() reads services.db.
    if logger is None:
        logger = ShowInfoLogger()
    services.populate(logger=logger)

    if db is None:
        db = get_db(logger)
    services.populate(db=db)

    if settings is None:
        settings = Settings()
    services.populate(settings=settings)

    if translator is None:
        translator = Translator(language=int(settings.get("misc.language")))
    services.populate(translator=translator)

    # Game state.
    mainpokemon_empty = False
    if main_pokemon is None:
        main_pokemon, mainpokemon_empty = update_main_pokemon()

    if enemy_pokemon is None:
        enemy_pokemon = _build_placeholder_enemy()

    if trainer_card is None:
        trainer_card = TrainerCard(
            logger,
            main_pokemon,
            settings,
            trainer_name=settings.get("trainer.name"),
            trainer_id="".join(filter(str.isdigit, str(uuid.uuid4()).replace("-", ""))),
            team="Pikachu (Level 25), Charizard (Level 50), Bulbasaur (Level 15)",
            league="Unranked",
        )

    if tracker is None:
        tracker = AnkimonTracker(trainer_card=trainer_card)
        tracker.set_main_pokemon(main_pokemon)
        tracker.set_enemy_pokemon(enemy_pokemon)

    if achievements is None:
        achievements = populate_achievements_from_badges(
            {str(i): False for i in range(1, 69)}
        )

    # Load in-memory caches to eliminate disk I/O during reviews/gameplay
    from .functions.pokedex_functions import (
        _load_pokedex_cache,
        _load_pokedex_id_index,
        _load_poke_species_cache,
        _load_pokemon_csv_cache,
        _load_stats_csv_cache,
        _load_poke_evo_cache,
        _load_moves_cache,
        _load_pokemon_names_csv,
        _load_pokemon_descriptions_csv,
    )
    from .functions.pokemon_functions import _load_next_lvl_cache

    caches = {
        "pokedex": _load_pokedex_cache(),
        "pokedex_id_index": _load_pokedex_id_index(),
        "poke_species": _load_poke_species_cache(),
        "pokemon_csv": _load_pokemon_csv_cache(),
        "stats_csv": _load_stats_csv_cache(),
        "poke_evo": _load_poke_evo_cache(),
        "moves": _load_moves_cache(),
        "pokemon_names": _load_pokemon_names_csv(),
        "pokemon_descriptions": _load_pokemon_descriptions_csv(),
        "next_lvl": _load_next_lvl_cache(),
    }

    services.populate(
        tracker=tracker,
        main_pokemon=main_pokemon,
        enemy_pokemon=enemy_pokemon,
        trainer_card=trainer_card,
        achievements=achievements,
        caches=caches,
    )

    return SimpleNamespace(
        logger=logger,
        ankimon_db=db,
        settings_obj=settings,
        translator=translator,
        main_pokemon=main_pokemon,
        mainpokemon_empty=mainpokemon_empty,
        enemy_pokemon=enemy_pokemon,
        trainer_card=trainer_card,
        ankimon_tracker_obj=tracker,
        achievements=achievements,
        caches=caches,
    )


# --- Runtime global binding -------------------------------------------------
#
# The core logic modules (battle_loop / encounter_functions / the poke-engine
# bridge) refer to shared singletons by bare name (``main_pokemon``,
# ``settings_obj`` …) — exactly as they did when they imported those names from
# ``singletons``. Python resolves such bare names against the *module's own
# globals* at call time; a module-level ``__getattr__`` does NOT intercept them
# (it only fires for ``module.attr`` access from outside). So we bind them as
# real module globals here, pointing at the live registry objects. This both
# preserves the original behaviour (those imports were snapshots of stable
# objects) and keeps function parameters of the same name shadowing correctly.
#
# Each entry: module path -> {bare global name: services attribute name}.
_RUNTIME_GLOBALS = {
    "Ankimon.functions.encounter_functions": {
        "main_pokemon": "main_pokemon",
        "ankimon_tracker_obj": "tracker",
        "trainer_card": "trainer_card",
        "settings_obj": "settings",
        "translator": "translator",
        "ankimon_db": "db",
        "pokemon_pc": "pokemon_pc",
    },
    "Ankimon.battle_loop": {
        "main_pokemon": "main_pokemon",
        "enemy_pokemon": "enemy_pokemon",
        "settings_obj": "settings",
        "reviewer_obj": "reviewer",
        "ankimon_tracker_obj": "tracker",
        "test_window": "test_window",
        "evo_window": "evo_window",
        "logger": "logger",
        "achievements": "achievements",
        "trainer_card": "trainer_card",
        "translator": "translator",
    },
    "Ankimon.functions.ankimon_hooks_to_poke_engine": {
        "ankimon_tracker_obj": "tracker",
        "settings_obj": "settings",
    },
}


def bind_runtime_globals() -> None:
    """Point the core logic modules' bare globals at the live registry objects.

    Call this from the composition root AFTER every service (core *and* the GUI
    windows / fakes) has been registered, since some bound names (test_window,
    evo_window, pokemon_pc, reviewer) are populated only after build_core().
    """
    import importlib

    root_pkg = __package__ or "Ankimon"
    for module_path, mapping in _RUNTIME_GLOBALS.items():
        real_module_path = module_path
        if module_path.startswith("Ankimon."):
            real_module_path = root_pkg + module_path[len("Ankimon"):]
        module = importlib.import_module(real_module_path)
        for global_name, attr in mapping.items():
            current_val = getattr(module, global_name, None)
            if current_val is not None and type(current_val).__name__ == "ServiceProxy":
                continue
            setattr(module, global_name, getattr(services, attr))

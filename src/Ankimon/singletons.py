"""
singletons.py — the production composition root (Anki / Qt).

Originally this module both *built* every Ankimon object and *held* it as a
module global. It has since been split:

* The aqt-free core (logger, DB, settings, translator, the Pokemon, trainer
  card, tracker, achievements) is built by :func:`Ankimon.core.build_core`.
* This module builds the Qt **windows** on top of that core and registers
  everything — core objects, GUI windows, and the Qt UI presenter — in the
  service registry (:mod:`Ankimon.services`).

It also keeps the historical module-level names (``settings_obj``, ``logger``,
``test_window``, …) and the ``mw.<service>`` shims so the not-yet-migrated
importers and ``__init__.py`` keep working unchanged.

The agent harness is the *other* root: it calls the same ``build_core()`` but
wires recording fakes + the headless presenter instead of the Qt windows below.

Author: Axil (original); split into core/gui 2026-06.
"""

from aqt import mw

# GUI window/widget classes (all import Qt).
from .pyobj.settings_window import SettingsWindow
from .pyobj.test_window import TestWindow
from .pyobj.achievement_window import AchievementWindow
from .pyobj.ankimon_tracker_window import AnkimonTrackerWindow
from .pyobj.ankimon_shop import PokemonShopManager
from .ankidex.ankidex_obj import Ankidex
from .pyobj.reviewer_obj import Reviewer_Manager
from .pyobj.evolution_window import EvoWindow
from .pyobj.starter_window import StarterWindow
from .pyobj.item_window import ItemWindow
from .pyobj.pc_box import PokemonPC
from .gui_entities import (
    License,
    Credits,
    TableWidget,
    IDTableWidget,
    NatureTableWidget,
    Version_Dialog,
)
from .resources import addon_dir
from .services import services
from .core import build_core, bind_runtime_globals
from .gui_presenter import QtPresenter

# --- Core (aqt-free) composition. Populates services.{db,logger,settings,
#     translator,tracker,main_pokemon,enemy_pokemon,trainer_card,achievements}. ---
_core = build_core()
logger = _core.logger
ankimon_db = _core.ankimon_db
settings_obj = _core.settings_obj
translator = _core.translator
main_pokemon = _core.main_pokemon
mainpokemon_empty = _core.mainpokemon_empty
enemy_pokemon = _core.enemy_pokemon
trainer_card = _core.trainer_card
ankimon_tracker_obj = _core.ankimon_tracker_obj
achievements = _core.achievements

# Back-compat shims: modules not yet migrated still read mw.<service>. These
# mirror the registry and are removed file-by-file as call sites move to
# `services`. (NOTE: menu_buttons.py re-creates mw.translator at its own import
# time; __init__.py re-points mw.translator back afterwards. Both go away when
# menu_buttons is migrated.)
mw.ankimon_db = ankimon_db
mw.logger = logger
mw.translator = translator
mw.settings_obj = settings_obj

# --- GUI windows (Qt), built on top of the core objects above. ---
settings_window = SettingsWindow(
    config=settings_obj.config,  # Use settings_obj.config instead of settings_obj.settings.config
    set_config_callback=settings_obj.set,
    save_config_callback=settings_obj.save_config,
    load_config_callback=settings_obj.load_config,
)
mw.settings_ankimon = settings_window

item_window = getattr(mw, "item_window", None) or ItemWindow(
    logger=logger, settings_obj=settings_obj, main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon, achievements=achievements,
    starter_window=starter_window,
    evo_window=evo_window,
)
mw.item_window = item_window

# Pokemon PC
pokemon_pc = getattr(mw, "pokemon_pc", None)
def get_pokemon_pc():
    global pokemon_pc
    if not is_alive(pokemon_pc):
        pokemon_pc = PokemonPC(
            logger=logger, translator=translator, reviewer_obj=reviewer_obj,
            test_window=test_window, settings=settings_obj, main_pokemon=main_pokemon,
        )
        mw.pokemon_pc = pokemon_pc
    return pokemon_pc

# Initialize initially
get_pokemon_pc()

# UI Utilities
eff_chart = TableWidget()
gen_id_chart = IDTableWidget()
nature_chart = NatureTableWidget()
license = License()
credits = Credits()
version_dialog = Version_Dialog()

evo_window = EvoWindow(
    logger,
    settings_obj,
    main_pokemon,
    translator,
    reviewer_obj,
    test_window,
    achievements,
)
starter_window = StarterWindow(logger, settings_obj)
item_window = ItemWindow(  # Create an instance of the MainWindow
    logger=logger,
    settings_obj=settings_obj,
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    achievements=achievements,
    starter_window=starter_window,
    evo_window=evo_window,
)

pokemon_pc = PokemonPC(
    logger=logger,
    translator=translator,
    reviewer_obj=reviewer_obj,
    test_window=test_window,
    settings=settings_obj,
    main_pokemon=main_pokemon,
)

# --- Register the GUI windows + the Qt UI presenter in the registry, so the
#     core logic (battle_loop / encounter_functions) reaches them via services. ---
services.populate(
    ui=QtPresenter(),
    test_window=test_window,
    evo_window=evo_window,
    pokemon_pc=pokemon_pc,
    reviewer=reviewer_obj,
)

# Bind the core logic modules' bare globals (main_pokemon, settings_obj,
# test_window, …) to the now-fully-populated registry. Must run after the
# services.populate above so the GUI window bindings are non-None.
bind_runtime_globals()

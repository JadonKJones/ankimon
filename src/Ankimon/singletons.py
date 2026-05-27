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
from .pokedex.pokedex_obj import Pokedex
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
    Pokedex_Widget,
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

# Create an instance of the MainWindow
test_window = TestWindow(
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    settings_obj=settings_obj,
    ankimon_tracker_obj=ankimon_tracker_obj,
    translator=translator,
    parent=mw,
    logger=logger,
)

achievement_bag = AchievementWindow()

# Initialize the Pokémon Shop Manager
shop_manager = PokemonShopManager(
    logger=logger,
    settings_obj=settings_obj,
    set_callback=settings_obj.set,
    get_callback=settings_obj.get,
)

ankimon_tracker_window = AnkimonTrackerWindow(tracker=ankimon_tracker_obj)
pokedex_window = Pokedex(addon_dir, ankimon_tracker=ankimon_tracker_obj)
reviewer_obj = Reviewer_Manager(
    settings_obj=settings_obj,
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    ankimon_tracker=ankimon_tracker_obj,
)

eff_chart = TableWidget()
pokedex = Pokedex_Widget()
gen_id_chart = IDTableWidget()
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


def get_evo_window():
    """Return the live EvoWindow, recreating it if its C++ part was destroyed.

    The EvoWindow can be closed/garbage-collected (especially from the PC box /
    item flows); calling into a dead Qt widget raises ``RuntimeError``. This
    getter rebuilds it transparently so callers always get a usable window.
    """
    global evo_window
    from .utils import is_alive
    if not is_alive(evo_window):
        evo_window = EvoWindow(
            logger,
            settings_obj,
            main_pokemon,
            translator,
            reviewer_obj,
            test_window,
            achievements,
        )
    return evo_window


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


def get_item_window():
    """Return the live ItemWindow, recreating it if its C++ part was destroyed.

    Used by the evolution flow to refresh item quantities after an evolution
    stone is consumed.
    """
    global item_window
    from .utils import is_alive
    if not is_alive(item_window):
        item_window = ItemWindow(
            logger=logger,
            settings_obj=settings_obj,
            main_pokemon=main_pokemon,
            enemy_pokemon=enemy_pokemon,
            achievements=achievements,
            starter_window=starter_window,
            evo_window=evo_window,
        )
    return item_window


def get_items_window():
    """Return the web-based items window if present.

    The QtWebEngine items window (``ankimon_items_web``) is not part of this
    build, so there is nothing to refresh; return ``None`` so callers treat the
    web-items refresh as a safe no-op.
    """
    return None


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

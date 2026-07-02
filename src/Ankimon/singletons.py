"""
singletons.py — the production composition root (Anki / Qt), reload-safe.

Originally this module both *built* every Ankimon object and *held* it as a
module global. It has since been split:

* The aqt-free core (logger, DB, settings, translator, the Pokemon, trainer
  card, tracker, achievements) is built by :func:`Ankimon.core.build_core`.
* This module builds the Qt **windows** on top of that core and registers
  everything — core objects, GUI windows, and the Qt UI presenter — in the
  service registry (:mod:`Ankimon.services`).

Reload safety (F31): construction is idempotent and lazy.

* The **core** is get-or-create through the services registry: when a previous
  composition root already populated ``services`` (an add-on reload, a double
  boot, or the harness), the live registry objects are reused instead of being
  rebuilt — so a second boot cannot duplicate the DB connection, the tracker,
  or the ``Reviewer_Manager`` (whose constructor registers ``gui_hooks``).
* The **windows** are no longer constructed at import time. Each window is
  built on first access — via its ``get_*_window()`` factory or via plain
  ``from .singletons import <name>`` (which lands in the module-level
  ``__getattr__`` below) — and cached, with :func:`Ankimon.utils.is_alive`
  liveness checks so a window whose underlying C++ object was deleted is
  transparently re-created instead of handed out dead.

The historical module-level names (``settings_obj``, ``logger``,
``test_window``, …) and the ``mw.<service>`` shims are kept, so the
not-yet-migrated importers and ``__init__.py`` keep working unchanged: the
window names now resolve through ``__getattr__`` to the same live instances.

The agent harness is the *other* root: it calls the same ``build_core()`` but
wires recording fakes + the headless presenter instead of the Qt windows below.

Author: Axil (original); split into core/gui 2026-06; reload-safe 2026-07.
"""

from types import SimpleNamespace

from aqt import mw

from .pyobj.ankimon_shop import PokemonShopManager
from .pyobj.reviewer_obj import Reviewer_Manager
from .resources import addon_dir
from .services import services
from .core import build_core, bind_runtime_globals
from .gui_presenter import QtPresenter
from .utils import is_alive

# --- Core (aqt-free) composition: get-or-create (reload-safe). ---------------
# First boot: build_core() constructs everything and populates services.
# Reload / double boot (the services module survived): reuse the live registry
# objects instead of constructing duplicates.


def _core_is_populated() -> bool:
    """True when a previous composition root already built the core."""
    return (
        services.db is not None
        and services.logger is not None
        and services.settings is not None
    )


def _core_from_registry() -> SimpleNamespace:
    """Mirror the live registry objects into the shape build_core() returns."""
    return SimpleNamespace(
        logger=services.logger,
        ankimon_db=services.db,
        settings_obj=services.settings,
        translator=services.translator,
        main_pokemon=services.main_pokemon,
        # Only known at first construction (update_main_pokemon() reports it);
        # nothing imports it, so a reused root does not recompute it.
        mainpokemon_empty=None,
        enemy_pokemon=services.enemy_pokemon,
        trainer_card=services.trainer_card,
        ankimon_tracker_obj=services.tracker,
        achievements=services.achievements,
    )


_core = _core_from_registry() if _core_is_populated() else build_core()
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

# --- Window-less managers (eager, get-or-create where the registry knows them). ---

# The Pokémon Shop Manager. Not registry-backed (yet): cheap, side-effect-free
# construction, so rebuilding it on a reload is harmless.
shop_manager = PokemonShopManager(
    logger=logger,
    settings_obj=settings_obj,
    set_callback=settings_obj.set,
    get_callback=settings_obj.get,
)

# Reviewer manager. Get-or-create: its constructor appends to gui_hooks, so a
# reload that re-ran it unconditionally would double-register those hooks.
reviewer_obj = services.reviewer
if reviewer_obj is None:
    reviewer_obj = Reviewer_Manager(
        settings_obj=settings_obj,
        main_pokemon=main_pokemon,
        enemy_pokemon=enemy_pokemon,
        ankimon_tracker=ankimon_tracker_obj,
    )
    services.populate(reviewer=reviewer_obj)

# --- GUI windows: lazy, idempotent factories (F31). ---------------------------
#
# No window is constructed at import time. The seam-registered windows
# (test_window / evo_window / pokemon_pc) are cached in the services registry
# itself; every other window lives in _WINDOW_CACHE. After registering a seam
# window its factory re-runs core.bind_runtime_globals() so the core logic
# modules' bare globals (battle_loop.test_window, …) pick up the live instance.

_WINDOW_CACHE = {}


def _cached(name, factory):
    """Get-or-create a non-registry window: reuse while alive, else rebuild."""
    win = _WINDOW_CACHE.get(name)
    if is_alive(win):
        return win
    win = factory()
    _WINDOW_CACHE[name] = win
    return win


def get_settings_window():
    def _build():
        from .pyobj.settings_window import SettingsWindow

        win = SettingsWindow(
            config=settings_obj.config,  # Use settings_obj.config instead of settings_obj.settings.config
            set_config_callback=settings_obj.set,
            save_config_callback=settings_obj.save_config,
            load_config_callback=settings_obj.load_config,
        )
        # Back-compat shim (pre-F31 this was written at import time).
        mw.settings_ankimon = win
        return win

    return _cached("settings_window", _build)


def get_test_window():
    win = services.test_window
    if is_alive(win):
        return win
    from .pyobj.test_window import TestWindow

    win = TestWindow(
        main_pokemon=main_pokemon,
        enemy_pokemon=enemy_pokemon,
        settings_obj=settings_obj,
        ankimon_tracker_obj=ankimon_tracker_obj,
        translator=translator,
        parent=mw,
        logger=logger,
    )
    services.populate(test_window=win)
    bind_runtime_globals()
    return win


def get_achievement_bag():
    def _build():
        from .pyobj.achievement_window import AchievementWindow

        return AchievementWindow()

    return _cached("achievement_bag", _build)


def get_ankimon_tracker_window():
    def _build():
        from .pyobj.ankimon_tracker_window import AnkimonTrackerWindow

        return AnkimonTrackerWindow(tracker=ankimon_tracker_obj)

    return _cached("ankimon_tracker_window", _build)


def get_pokedex_window():
    def _build():
        from .pokedex.pokedex_obj import Pokedex

        return Pokedex(addon_dir, ankimon_tracker=ankimon_tracker_obj)

    return _cached("pokedex_window", _build)


def get_eff_chart():
    def _build():
        from .gui_entities import TableWidget

        return TableWidget()

    return _cached("eff_chart", _build)


def get_pokedex_widget():
    def _build():
        from .gui_entities import Pokedex_Widget

        return Pokedex_Widget()

    return _cached("pokedex", _build)


def get_gen_id_chart():
    def _build():
        from .gui_entities import IDTableWidget

        return IDTableWidget()

    return _cached("gen_id_chart", _build)


def get_license():
    def _build():
        from .gui_entities import License

        return License()

    return _cached("license", _build)


def get_credits():
    def _build():
        from .gui_entities import Credits

        return Credits()

    return _cached("credits", _build)


def get_version_dialog():
    def _build():
        from .gui_entities import Version_Dialog

        return Version_Dialog()

    return _cached("version_dialog", _build)


def get_evo_window():
    win = services.evo_window
    if is_alive(win):
        return win
    from .pyobj.evolution_window import EvoWindow

    win = EvoWindow(
        logger,
        settings_obj,
        main_pokemon,
        translator,
        reviewer_obj,
        get_test_window(),
        achievements,
    )
    services.populate(evo_window=win)
    bind_runtime_globals()
    return win


def get_starter_window():
    def _build():
        from .pyobj.starter_window import StarterWindow

        return StarterWindow(logger, settings_obj)

    return _cached("starter_window", _build)


def get_item_window():
    def _build():
        from .pyobj.item_window import ItemWindow

        return ItemWindow(  # Create an instance of the MainWindow
            logger=logger,
            settings_obj=settings_obj,
            main_pokemon=main_pokemon,
            enemy_pokemon=enemy_pokemon,
            achievements=achievements,
            starter_window=get_starter_window(),
            evo_window=get_evo_window(),
        )

    return _cached("item_window", _build)


def get_pokemon_pc():
    win = services.pokemon_pc
    if is_alive(win):
        return win
    from .pyobj.pc_box import PokemonPC

    win = PokemonPC(
        logger=logger,
        translator=translator,
        reviewer_obj=reviewer_obj,
        test_window=get_test_window(),
        settings=settings_obj,
        main_pokemon=main_pokemon,
    )
    services.populate(pokemon_pc=win)
    bind_runtime_globals()
    return win


# The unified Ankimon web shell (F11/F13/F18): Items/Shop, Settings, Profile and
# Team all live in this one QDialog (one window, one dropdown navigator). Lazy +
# reload-safe like the other window factories, but not registry-backed — it is a
# pure GUI window, so it lives in its own module-level cache with an is_alive()
# liveness check (a shell whose C++ object was deleted is rebuilt, not handed out
# dead). Seam-correct: constructed from the services-resolved core objects above,
# never from mw.* (F31 keeps mw coupling out of this module, NR-04).
_items_web_window = None


def get_items_window():
    global _items_web_window
    if is_alive(_items_web_window):
        return _items_web_window
    from .ankimon_items_web.shop_obj import AnkimonItemsWeb

    _items_web_window = AnkimonItemsWeb(
        addon_dir,
        shop_manager=shop_manager,
        item_window=get_item_window(),
        ankimon_tracker=ankimon_tracker_obj,
        trainer_card=trainer_card,
        settings_obj=settings_obj,
        logger=logger,
    )
    return _items_web_window


# The standalone Ankidex (Pokédex V2) SPA window (F16): its own QDialog +
# QWebEngineView, opened via this factory (and reused by the web shell's inline
# Ankidex screen through get_ankidex_window().get_ankidex_data()). Lazy +
# reload-safe like the other window factories, and — like the web shell above —
# not registry-backed (a pure GUI window), so it lives in its own module-level
# cache with an is_alive() liveness check (a dialog whose C++ object was deleted
# is rebuilt, not handed out dead). Seam-correct: constructed from the
# services-resolved tracker, never from mw.* (its data getter reads
# services.db / services.settings), keeping mw coupling out of this module (NR-04).
_ankidex_window = None


def get_ankidex_window():
    global _ankidex_window
    if is_alive(_ankidex_window):
        return _ankidex_window
    from .ankidex.ankidex_obj import Ankidex

    _ankidex_window = Ankidex(addon_dir, ankimon_tracker=ankimon_tracker_obj)
    return _ankidex_window


# DEFERRED seam points (do NOT add here in F31):
# * get_nature_chart() -> gui_entities.NatureTableWidget lands with F36 (the
#   widget does not exist on this base yet).
# * notify_stats_changed() (QWebChannel live-update push) belongs to the
#   webshell host / F10+F49, not to this module (NR-04).
# * swap_ankimon_account() (dev DB switch) belongs to F36/F27 wiring and must
#   call services.db.switch_database when it lands.

# Per-name lazy proxies: `from .singletons import test_window` (and plain
# module attribute access) constructs ONLY the requested window, on first
# access. None of these names is a real module global, so this __getattr__ is
# their only resolution path.
_LAZY_WINDOWS = {
    "settings_window": get_settings_window,
    "test_window": get_test_window,
    "achievement_bag": get_achievement_bag,
    "ankimon_tracker_window": get_ankimon_tracker_window,
    "pokedex_window": get_pokedex_window,
    "eff_chart": get_eff_chart,
    "pokedex": get_pokedex_widget,
    "gen_id_chart": get_gen_id_chart,
    "license": get_license,
    "credits": get_credits,
    "version_dialog": get_version_dialog,
    "evo_window": get_evo_window,
    "starter_window": get_starter_window,
    "item_window": get_item_window,
    "pokemon_pc": get_pokemon_pc,
}


def __getattr__(name):
    factory = _LAZY_WINDOWS.get(name)
    if factory is not None:
        return factory()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# --- Qt UI presenter + runtime-global binding. --------------------------------
# Idempotent: only swap in a QtPresenter when the registry does not already
# hold one, so a reload keeps the existing presenter instance.
if not isinstance(services.ui, QtPresenter):
    services.populate(ui=QtPresenter())

# Bind the core logic modules' bare globals (main_pokemon, settings_obj,
# test_window, …) to the now-populated registry. The window bindings
# (test_window / evo_window / pokemon_pc) may still be None here — each lazy
# factory re-runs bind_runtime_globals() after registering its window, so the
# bindings are live before any gameplay code can run.
bind_runtime_globals()

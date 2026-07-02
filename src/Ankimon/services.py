"""
services.py — the addon's own service registry.

Historically Ankimon hung its own objects (database, logger, translator,
settings) on Anki's global ``mw`` (the main window). That coupled every module
to Anki: importing anything pulled in ``aqt``, and the only way to substitute a
fake in a test was to monkeypatch a global. This module is the replacement — a
small registry that holds those services and, deliberately, does **not** import
``aqt`` or ``anki``.

This is a *registry* pattern, not full dependency injection. It is still a
global, but one the tests own and one that does not drag in Anki. Constructor
injection can be layered on top later, module by module; until then this is the
seam that makes the addon's own logic testable without an Anki runtime.

Usage
-----
Populate it **once** at the composition root (see ``singletons.py``)::

    from .services import services
    services.populate(db=ankimon_db, logger=logger,
                      settings=settings_obj, translator=translator)

Read it anywhere instead of reaching into ``mw``::

    from .services import services
    services.db.get_pokemon(...)

In a test, assign fakes — no Anki, no ``sys.modules`` surgery::

    from Ankimon.services import services
    services.db = FakeDB()

Author: Ankimon contributors
Created: 2026-05-21
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    # Type-checker-only imports. Guarded by TYPE_CHECKING so they never execute
    # at runtime — that is what keeps this module free of any aqt/anki import.
    from .pyobj.database_manager import AnkimonDB
    from .pyobj.InfoLogger import ShowInfoLogger
    from .pyobj.settings import Settings
    from .pyobj.translator import Translator
    from .pyobj.ankimon_tracker import AnkimonTracker
    from .pyobj.pokemon_obj import PokemonObject
    from .pyobj.trainer_card import TrainerCard


class Services:
    """Holds the addon's own services and shared game state. No Anki dependency.

    The registry holds three kinds of thing:

    * **Core services** (``db``/``logger``/``settings``/``translator``) — already
      aqt-free helper objects.
    * **Core game state** (``tracker``/``main_pokemon``/``enemy_pokemon``/
      ``trainer_card``/``achievements``) — the live objects the battle loop
      mutates. Code reads them from here (often via :func:`module_getattr`)
      instead of importing them from ``singletons``, which is what lets that
      code import without pulling in Anki.
    * **UI ports** (``ui`` presenter, and the window objects ``test_window`` /
      ``evo_window`` / ``pokemon_pc`` / ``reviewer``) — swapped between the real
      Qt implementations (production) and recording fakes (the agent harness).
    """

    def __init__(self) -> None:
        # Core, aqt-free services.
        self._db = None
        self._logger = None
        self._settings = None
        self._translator = None

        # Core game state (also aqt-free objects).
        self._tracker = None
        self._main_pokemon = None
        self._enemy_pokemon = None
        self._trainer_card = None
        self._achievements = None
        self._caches = None

        # UI port. Defaults to a GUI-less presenter so core logic can always
        # call ``services.ui.*`` safely; the production root swaps in a Qt one.
        from .ui_port import HeadlessPresenter
        self.ui = HeadlessPresenter()

        # GUI window objects, injected by the composition root: real Qt windows
        # in production, recording fakes in the harness. Core logic reaches them
        # through ``services`` so either works.
        self._test_window = None
        self._evo_window = None
        self._pokemon_pc = None
        self._reviewer = None
        self._shop_manager = None
        self._items_web_window = None
        self._ankidex_window = None
        self._item_window = None
        self._starter_window = None
        self._achievement_bag = None
        self._ankimon_tracker_window = None
        self._settings_window = None

        # The Anki collection (``mw.col``) when running inside Anki; None headless.
        self._col = None

    def _get_fallback(self, private_val, mw_attr):
        if private_val is not None:
            return private_val
        try:
            import sys
            # 1. Try mw first (since it is the ultimate live source of truth in Anki/tests)
            if "aqt" in sys.modules:
                from aqt import mw
                if mw is not None:
                    from unittest.mock import Mock
                    if isinstance(mw, Mock):
                        if mw_attr in mw.__dict__ or (hasattr(mw, "_mock_children") and mw_attr in mw._mock_children):
                            val = getattr(mw, mw_attr)
                            if val is not None:
                                return val
                    elif hasattr(mw, mw_attr):
                        val = getattr(mw, mw_attr)
                        if val is not None:
                            return val

            # 2. Try Ankimon.singletons second
            if "Ankimon.singletons" in sys.modules:
                sing = sys.modules["Ankimon.singletons"]
                from unittest.mock import Mock
                if isinstance(sing, Mock):
                    if mw_attr in sing.__dict__ or (hasattr(sing, "_mock_children") and mw_attr in sing._mock_children):
                        return getattr(sing, mw_attr)
                elif hasattr(sing, mw_attr):
                    val = getattr(sing, mw_attr)
                    if val is not None:
                        return val
        except Exception:
            pass
        return None

    @property
    def db(self):
        return self._get_fallback(self._db, "ankimon_db")

    @db.setter
    def db(self, value):
        self._db = value

    @property
    def logger(self):
        return self._get_fallback(self._logger, "logger")

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def settings(self):
        return self._get_fallback(self._settings, "settings_obj")

    @settings.setter
    def settings(self, value):
        self._settings = value

    @property
    def translator(self):
        return self._get_fallback(self._translator, "translator")

    @translator.setter
    def translator(self, value):
        self._translator = value

    @property
    def tracker(self):
        return self._get_fallback(self._tracker, "ankimon_tracker_obj")

    @tracker.setter
    def tracker(self, value):
        self._tracker = value

    @property
    def main_pokemon(self):
        return self._get_fallback(self._main_pokemon, "main_pokemon")

    @main_pokemon.setter
    def main_pokemon(self, value):
        self._main_pokemon = value

    @property
    def enemy_pokemon(self):
        return self._get_fallback(self._enemy_pokemon, "enemy_pokemon")

    @enemy_pokemon.setter
    def enemy_pokemon(self, value):
        self._enemy_pokemon = value

    @property
    def trainer_card(self):
        return self._get_fallback(self._trainer_card, "trainer_card")

    @trainer_card.setter
    def trainer_card(self, value):
        self._trainer_card = value

    @property
    def achievements(self):
        return self._get_fallback(self._achievements, "achievements_dict")

    @achievements.setter
    def achievements(self, value):
        self._achievements = value

    @property
    def caches(self):
        return self._caches

    @caches.setter
    def caches(self, value):
        self._caches = value

    @property
    def test_window(self):
        return self._get_fallback(self._test_window, "test_window")

    @test_window.setter
    def test_window(self, value):
        self._test_window = value

    @property
    def evo_window(self):
        return self._get_fallback(self._evo_window, "evo_window")

    @evo_window.setter
    def evo_window(self, value):
        self._evo_window = value

    @property
    def pokemon_pc(self):
        return self._get_fallback(self._pokemon_pc, "pokemon_pc")

    @pokemon_pc.setter
    def pokemon_pc(self, value):
        self._pokemon_pc = value

    @property
    def reviewer(self):
        return self._get_fallback(self._reviewer, "reviewer")

    @reviewer.setter
    def reviewer(self, value):
        self._reviewer = value

    @property
    def shop_manager(self):
        return self._get_fallback(self._shop_manager, "shop_manager")

    @shop_manager.setter
    def shop_manager(self, value):
        self._shop_manager = value

    @property
    def items_web_window(self):
        return self._get_fallback(self._items_web_window, "items_web_window")

    @items_web_window.setter
    def items_web_window(self, value):
        self._items_web_window = value

    @property
    def ankidex_window(self):
        return self._get_fallback(self._ankidex_window, "ankidex_window")

    @ankidex_window.setter
    def ankidex_window(self, value):
        self._ankidex_window = value

    @property
    def item_window(self):
        return self._get_fallback(self._item_window, "item_window")

    @item_window.setter
    def item_window(self, value):
        self._item_window = value

    @property
    def starter_window(self):
        return self._get_fallback(self._starter_window, "starter_window")

    @starter_window.setter
    def starter_window(self, value):
        self._starter_window = value

    @property
    def achievement_bag(self):
        return self._get_fallback(self._achievement_bag, "achievement_bag")

    @achievement_bag.setter
    def achievement_bag(self, value):
        self._achievement_bag = value

    @property
    def ankimon_tracker_window(self):
        return self._get_fallback(self._ankimon_tracker_window, "ankimon_tracker_window")

    @ankimon_tracker_window.setter
    def ankimon_tracker_window(self, value):
        self._ankimon_tracker_window = value

    @property
    def settings_window(self):
        return self._get_fallback(self._settings_window, "settings_window")

    @settings_window.setter
    def settings_window(self, value):
        self._settings_window = value

    @property
    def col(self):
        return self._get_fallback(self._col, "col")

    @col.setter
    def col(self, value):
        self._col = value

    def populate(
        self,
        *,
        db: Optional["AnkimonDB"] = None,
        logger: Optional["ShowInfoLogger"] = None,
        settings: Optional["Settings"] = None,
        translator: Optional["Translator"] = None,
        tracker: Optional["AnkimonTracker"] = None,
        main_pokemon: Optional["PokemonObject"] = None,
        enemy_pokemon: Optional["PokemonObject"] = None,
        trainer_card: Optional["TrainerCard"] = None,
        achievements: Optional[dict] = None,
        ui=None,
        test_window=None,
        evo_window=None,
        pokemon_pc=None,
        reviewer=None,
        col=None,
        caches=None,
        shop_manager=None,
        items_web_window=None,
        ankidex_window=None,
        item_window=None,
        starter_window=None,
        achievement_bag=None,
        ankimon_tracker_window=None,
        settings_window=None,
    ) -> None:
        """Wire up services/state at the composition root.

        Keyword-only and skip-if-None so the call site reads clearly and a
        partial re-populate never clobbers an already-set value with ``None``.
        """
        if db is not None:
            self.db = db
        if logger is not None:
            self.logger = logger
        if settings is not None:
            self.settings = settings
        if translator is not None:
            self.translator = translator
        if tracker is not None:
            self.tracker = tracker
        if main_pokemon is not None:
            self.main_pokemon = main_pokemon
        if enemy_pokemon is not None:
            self.enemy_pokemon = enemy_pokemon
        if trainer_card is not None:
            self.trainer_card = trainer_card
        if achievements is not None:
            self.achievements = achievements
        if ui is not None:
            self.ui = ui
        if test_window is not None:
            self.test_window = test_window
        if evo_window is not None:
            self.evo_window = evo_window
        if pokemon_pc is not None:
            self.pokemon_pc = pokemon_pc
        if reviewer is not None:
            self.reviewer = reviewer
        if col is not None:
            self.col = col
        if caches is not None:
            self.caches = caches
        if shop_manager is not None:
            self.shop_manager = shop_manager
        if items_web_window is not None:
            self.items_web_window = items_web_window
        if ankidex_window is not None:
            self.ankidex_window = ankidex_window
        if item_window is not None:
            self.item_window = item_window
        if starter_window is not None:
            self.starter_window = starter_window
        if achievement_bag is not None:
            self.achievement_bag = achievement_bag
        if ankimon_tracker_window is not None:
            self.ankimon_tracker_window = ankimon_tracker_window
        if settings_window is not None:
            self.settings_window = settings_window

    def reset(self) -> None:
        """Clear every service/state. Intended for test isolation."""
        self.db = None
        self.logger = None
        self.settings = None
        self.translator = None
        self.tracker = None
        self.main_pokemon = None
        self.enemy_pokemon = None
        self.trainer_card = None
        self.achievements = None
        self.caches = None
        from .ui_port import HeadlessPresenter
        self.ui = HeadlessPresenter()
        self.test_window = None
        self.evo_window = None
        self.pokemon_pc = None
        self.reviewer = None
        self.shop_manager = None
        self.items_web_window = None
        self.ankidex_window = None
        self.item_window = None
        self.starter_window = None
        self.achievement_bag = None
        self.ankimon_tracker_window = None
        self.settings_window = None
        self.col = None


# The single shared registry instance. Import this, not the class.
services = Services()

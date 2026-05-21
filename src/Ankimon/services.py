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


class Services:
    """Holds the addon's own services. Has no Anki dependency."""

    def __init__(self) -> None:
        self.db: Optional["AnkimonDB"] = None
        self.logger: Optional["ShowInfoLogger"] = None
        self.settings: Optional["Settings"] = None
        self.translator: Optional["Translator"] = None

    def populate(
        self,
        *,
        db: Optional["AnkimonDB"] = None,
        logger: Optional["ShowInfoLogger"] = None,
        settings: Optional["Settings"] = None,
        translator: Optional["Translator"] = None,
    ) -> None:
        """Wire up services at the composition root.

        Keyword-only and skip-if-None so the call site reads clearly and a
        partial re-populate never clobbers an already-set service with ``None``.
        """
        if db is not None:
            self.db = db
        if logger is not None:
            self.logger = logger
        if settings is not None:
            self.settings = settings
        if translator is not None:
            self.translator = translator

    def reset(self) -> None:
        """Clear every service. Intended for test isolation."""
        self.db = None
        self.logger = None
        self.settings = None
        self.translator = None


# The single shared registry instance. Import this, not the class.
services = Services()

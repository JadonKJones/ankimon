"""Characterization tests for ``Ankimon.pyobj.ankimon_tracker.get_total_reviews``.

Ported from BRRRR_Experimental's shipped ``tests/test_ankimon_tracker.py`` and
re-fitted onto main's service-seam architecture. The experimental feature made
the daily review count *language-agnostic* by querying Anki's ``revlog`` table
directly (``col.sched.day_cutoff`` + ``col.db.scalar``) instead of regex-scraping
the English-only ``studied_today()`` string, and corrected the ``day_cutoff``
subtraction that caused runaway cash rewards. The ``faint_processed`` guard flag
is a separate net-new bit of gameplay state also carried by this feature.

Re-fit vs. the experimental original:

* Experimental code read ``mw.col`` directly and the shipped test patched
  ``Ankimon.pyobj.ankimon_tracker.mw``. On main the collection is resolved
  through the ``services`` registry (``services.col``), with a lazy ``mw.col``
  fallback for the addon-load window. So these tests drive ``services.col``
  (the seam) rather than a module-level ``mw``.
* The module is loaded in isolation with stubbed ``aqt`` / ``PyQt6`` / ``anki``
  so the pure-logic method can be exercised Qt-free (Tier-1), matching the base
  test suite's convention.
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class DynamicMockModule(types.ModuleType):
    """A module stub that dynamically returns MagicMocks for any attribute
    requests, preventing PyQt/Anki module import and lookup errors."""

    def __getattr__(self, name):
        mock = MagicMock()
        setattr(self, name, mock)
        return mock


_SRC = Path(__file__).parent.parent / "src"


@pytest.fixture
def tracker_module():
    """Load ``AnkimonTracker`` in isolation with stubbed Anki/Qt modules and
    restore ``sys.modules`` afterwards so the rest of the suite is unaffected."""
    original_modules = dict(sys.modules)

    # Parent packages so the module's relative imports resolve against the real
    # source tree without executing ``Ankimon/__init__.py`` (mirrors conftest).
    parent_pkgs = {}
    for _pkg in ("Ankimon", "Ankimon.pyobj", "Ankimon.functions"):
        _mod = types.ModuleType(_pkg)
        _mod.__path__ = [str(_SRC / _pkg.replace(".", "/"))]
        _mod.__package__ = _pkg
        parent_pkgs[_pkg] = _mod

    mocks = {
        "aqt": DynamicMockModule("aqt"),
        "aqt.qt": DynamicMockModule("aqt.qt"),
        "aqt.utils": DynamicMockModule("aqt.utils"),
        "PyQt6": DynamicMockModule("PyQt6"),
        "PyQt6.QtWidgets": DynamicMockModule("PyQt6.QtWidgets"),
        "PyQt6.QtCore": DynamicMockModule("PyQt6.QtCore"),
        "PyQt6.QtMultimedia": DynamicMockModule("PyQt6.QtMultimedia"),
        "anki": DynamicMockModule("anki"),
        "anki.buildinfo": DynamicMockModule("anki.buildinfo"),
    }
    mocks.update(parent_pkgs)

    with patch.dict(sys.modules, mocks):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "Ankimon.pyobj.ankimon_tracker",
            _SRC / "Ankimon" / "pyobj" / "ankimon_tracker.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["Ankimon.pyobj.ankimon_tracker"] = mod
        spec.loader.exec_module(mod)

        # Start every test from a clean registry so ``services.col`` is the only
        # thing steering ``get_total_reviews``.
        mod.services.reset()
        yield mod

    # Restore sys.modules to EXACTLY its pre-test state, resolving side effects.
    for key in list(sys.modules):
        if key not in original_modules:
            del sys.modules[key]
        else:
            sys.modules[key] = original_modules[key]


def _make_tracker(mod):
    return mod.AnkimonTracker(MagicMock())


def test_faint_processed_guard_defaults_false(tracker_module):
    """The net-new duplicate-faint guard initialises to ``False``."""
    tracker = _make_tracker(tracker_module)
    assert tracker.faint_processed is False


def test_get_total_reviews_database_success(tracker_module):
    """``get_total_reviews`` queries the revlog and returns the scalar count,
    filtering from the start of today (``day_cutoff`` minus 24h, in ms)."""
    tracker = _make_tracker(tracker_module)

    mock_col = MagicMock()
    mock_col.sched.day_cutoff = 1716800000
    mock_col.db.scalar.return_value = 42
    tracker_module.services.col = mock_col

    reviews = tracker.get_total_reviews()

    assert reviews == 42
    mock_col.db.scalar.assert_called_once_with(
        "SELECT count() FROM revlog WHERE id > ?", (1716800000 - 86400) * 1000
    )


def test_get_total_reviews_database_failure_fallback_english(tracker_module):
    """When the DB query fails, fall back to parsing ``studied_today`` (EN)."""
    tracker = _make_tracker(tracker_module)

    mock_col = MagicMock()
    mock_col.sched.day_cutoff = 1716800000
    mock_col.db.scalar.side_effect = Exception("Database is locked")
    mock_col.studied_today.return_value = "Studied 15 cards in 3.2 minutes today."
    tracker_module.services.col = mock_col

    reviews = tracker.get_total_reviews()

    assert reviews == 15
    mock_col.studied_today.assert_called_once()


def test_get_total_reviews_database_failure_fallback_localized(tracker_module):
    """The fallback grabs the first integer, so it works on localized strings."""
    tracker = _make_tracker(tracker_module)

    mock_col = MagicMock()
    mock_col.sched.day_cutoff = 1716800000
    mock_col.db.scalar.side_effect = Exception("Database is locked")
    mock_col.studied_today.return_value = "Heute 27 Karten in 5.4 Minuten gelernt."
    tracker_module.services.col = mock_col

    reviews = tracker.get_total_reviews()

    assert reviews == 27


def test_get_total_reviews_no_collection(tracker_module):
    """Returns 0 when neither ``services.col`` nor the ``mw.col`` fallback has a
    live collection."""
    tracker = _make_tracker(tracker_module)

    tracker_module.services.col = None
    # Force the lazy ``from aqt import mw`` fallback to yield no collection too.
    sys.modules["aqt"].mw = MagicMock()
    sys.modules["aqt"].mw.col = None

    reviews = tracker.get_total_reviews()

    assert reviews == 0

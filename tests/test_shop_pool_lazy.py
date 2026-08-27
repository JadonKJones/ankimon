"""The daily-shop item pool must not be built while importing its module.

``utils.daily_item_list()`` scans the sprites directory and, when it is absent,
opens the sprite-download agreement dialog. ``ankimon_shop`` used to call it at
module scope (``DAILY_ITEMS_POOL = daily_item_list()``), which made two things
true that should not have been:

* ``singletons`` imports ``ankimon_shop``, and ``battle_loop.on_review_card``
  lazily imports ``singletons`` — so on a profile whose sprites had not been
  downloaded, the first card review could surface a modal download dialog from
  inside a stats notification.
* Building a ``QWidget`` before a ``QApplication`` exists makes Qt call
  ``abort()``. That is a process death, not an exception, so the ``try/except
  Exception`` around that lazy import could not contain it: the Tier-1 harness
  gate died with SIGABRT on any machine where PyQt6 was importable.

These tests pin the lazy accessor and the no-QApplication guard.
"""

import importlib
import sys
import types

import pytest


@pytest.fixture
def download_sprites():
    """Import ``download_sprites`` with a genuine PyQt6 underneath it.

    Earlier modules in the suite replace ``PyQt6`` with a ``MagicMock``, which
    turns ``from PyQt6.QtWidgets import QTextEdit`` (via ``gui_entities``) into
    an ImportError and would silently skip these tests. Drop those entries for
    the duration so the real package — a documented test dependency — loads,
    then hand them back.
    """
    saved = {
        name: mod
        for name, mod in sys.modules.items()
        if name.split(".")[0] in ("PyQt6", "aqt")
    }
    for name in saved:
        del sys.modules[name]

    # `gui_entities` (imported transitively) wants `aqt.qt.QDialog/qconnect` and
    # `aqt.utils`; Anki is absent from CI, so forward to the real PyQt6 the way
    # Anki's own `aqt.qt` does.
    import PyQt6.QtCore
    import PyQt6.QtGui
    import PyQt6.QtWidgets

    aqt = types.ModuleType("aqt")
    aqt.__path__ = []
    aqt.mw = None
    aqt_qt = types.ModuleType("aqt.qt")
    for source in (PyQt6.QtCore, PyQt6.QtGui, PyQt6.QtWidgets):
        for name in dir(source):
            if not name.startswith("_"):
                setattr(aqt_qt, name, getattr(source, name))
    aqt_qt.qconnect = lambda signal, slot: signal.connect(slot)
    aqt_utils = types.ModuleType("aqt.utils")
    aqt_utils.showWarning = lambda *a, **k: None
    aqt_utils.showInfo = lambda *a, **k: None
    aqt_utils.tooltip = lambda *a, **k: None
    sys.modules["aqt"] = aqt
    sys.modules["aqt.qt"] = aqt_qt
    sys.modules["aqt.utils"] = aqt_utils

    sys.modules.pop("Ankimon.pyobj.download_sprites", None)
    sys.modules.pop("Ankimon.gui_entities", None)
    try:
        module = importlib.import_module("Ankimon.pyobj.download_sprites")
    except Exception as e:
        sys.modules.update(saved)
        # Deliberately NOT pytest.skip. PyQt6 is a documented test dependency
        # and `aqt` is supplied by this fixture, so an import failure means the
        # stub set has drifted from what the module imports — and a skip would
        # report that as green with every test here silently disabled, which is
        # the exact failure mode this file's own subject matter is about.
        raise AssertionError(
            "download_sprites is no longer importable with this fixture's Qt "
            "stubs — extend them to cover its new imports rather than letting "
            f"these tests silently skip. Original error: {e!r}"
        ) from e
    yield module
    sys.modules.update(saved)


def _fresh_import(monkeypatch, calls):
    """Import ``ankimon_shop`` fresh with ``daily_item_list`` recording calls."""
    utils = importlib.import_module("Ankimon.utils")
    monkeypatch.setattr(
        utils,
        "daily_item_list",
        lambda: calls.append(1) or [{"name": "potion", "price": 10}],
    )
    sys.modules.pop("Ankimon.pyobj.ankimon_shop", None)
    return importlib.import_module("Ankimon.pyobj.ankimon_shop")


def test_importing_ankimon_shop_does_not_build_the_pool(monkeypatch):
    calls = []
    _fresh_import(monkeypatch, calls)
    assert calls == [], "importing ankimon_shop scanned the sprites directory"


def test_pool_is_built_on_first_use_and_memoized(monkeypatch):
    calls = []
    shop = _fresh_import(monkeypatch, calls)

    assert shop.get_daily_items_pool() == [{"name": "potion", "price": 10}]
    assert calls == [1]
    # Second call must reuse the cached pool, not re-scan.
    assert shop.get_daily_items_pool() == [{"name": "potion", "price": 10}]
    assert calls == [1]


def test_pool_degrades_to_a_list_when_the_scan_returns_nothing(monkeypatch):
    # daily_item_list() returns None on some failure paths; len()/random.sample()
    # in the callers must still get a sequence.
    utils = importlib.import_module("Ankimon.utils")
    monkeypatch.setattr(utils, "daily_item_list", lambda: None)
    sys.modules.pop("Ankimon.pyobj.ankimon_shop", None)
    shop = importlib.import_module("Ankimon.pyobj.ankimon_shop")

    assert shop.get_daily_items_pool() == []


def test_download_dialog_is_skipped_without_a_qapplication(
    monkeypatch, download_sprites
):
    """The guard has to be a check, not a try/except — Qt aborts the process."""

    def _explode(*args, **kwargs):
        raise AssertionError("built a QWidget with no QApplication")

    monkeypatch.setattr(download_sprites, "AgreementDialog", _explode)
    monkeypatch.setattr(
        download_sprites.QApplication, "instance", staticmethod(lambda: None)
    )

    assert download_sprites.show_agreement_and_download_dialog() is None


def test_download_dialog_still_runs_when_a_qapplication_exists(
    monkeypatch, download_sprites
):
    built = []

    class _Dialog:
        def exec(self):
            built.append(1)
            return object()  # never equals QDialog.DialogCode.Accepted

    class _App:
        # pytest-qt's teardown hook calls processEvents() on whatever
        # QApplication.instance() hands back, so the stand-in needs it.
        def processEvents(self, *args, **kwargs):
            pass

    fake_app = _App()
    monkeypatch.setattr(download_sprites, "AgreementDialog", _Dialog)
    monkeypatch.setattr(
        download_sprites.QApplication, "instance", staticmethod(lambda: fake_app)
    )

    download_sprites.show_agreement_and_download_dialog()
    assert built == [1], "the guard swallowed a legitimate GUI-mode call"

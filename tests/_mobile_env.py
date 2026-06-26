"""Shared headless test environment for the mobile-review engine tests.

``tests.test_database_manager.setup_mocks()`` (imported first by each mobile test
for ``MockLogger``/``temp_env``) replaces ``Ankimon`` + ``Ankimon.pyobj`` /
``singletons`` / ``utils`` in ``sys.modules`` with bare/MagicMock modules so the
database manager can be loaded in isolation. The engine tests, however, need the
*real* ``Ankimon.functions.*`` / ``Ankimon.pyobj.{pokemon_obj,trainer_card}`` /
``Ankimon.business`` modules plus a real-PyQt6 ``aqt`` shim. ``setup_engine_env``
re-establishes that.

``Ankimon.menu_buttons`` and ``Ankimon.singletons`` are left as MagicMocks: the
engine only ever reaches them through the lazy ``from ..menu_buttons import
update_mobile_badge`` / ``from ..singletons import get_evo_window`` calls, which
become harmless no-ops. The genuine ``menu_buttons`` builds Qt windows at import
(needs a live QApplication); ``load_real_menu_buttons`` force-loads only it (with
those window siblings stubbed) for the one test that exercises update_mobile_badge.
"""

import sys
import types
from unittest.mock import MagicMock

_HOST_PREFIXES = ("aqt", "anki", "Ankimon", "PyQt6")


def snapshot_host_modules():
    """Capture the current aqt/anki/Ankimon/PyQt6 entries in sys.modules."""
    return {k: v for k, v in sys.modules.items() if k.split(".")[0] in _HOST_PREFIXES}


def restore_host_modules(snap):
    """Restore sys.modules' host entries to a snapshot (drop anything added since).

    Per-call (properly nested) restoration: callers snapshot right before mutating
    the env and restore right after, so the mobile modules never leak their mocked
    aqt/Ankimon into — or clobber the setup of — any other test module.
    """
    for k in list(sys.modules):
        if k.split(".")[0] in _HOST_PREFIXES:
            sys.modules.pop(k, None)
    sys.modules.update(snap)


class _PermissiveModule(types.ModuleType):
    """A real module that yields a MagicMock for any missing attribute.

    Supports both ``from mod import *`` (real empty __all__) and
    ``from mod import some_name`` (PEP 562 __getattr__ → cached MagicMock).
    """

    def __getattr__(self, name):
        m = MagicMock()
        setattr(self, name, m)
        return m


# Heavy Qt-window siblings imported at the top of menu_buttons.py; each builds a
# QWidget (or pulls WebEngine) at import, so load_real_menu_buttons stubs them.
_MENU_SIBLINGS = (
    "Ankimon.gui_classes",
    "Ankimon.gui_classes.choose_trainer_sprite_graphical",
    "Ankimon.gui_classes.pokemon_team_window",
    "Ankimon.gui_classes.check_files",
    "Ankimon.gui_classes.backup_manager_dialog",
    "Ankimon.pokedex",
    "Ankimon.pokedex.pokedex_obj",
    "Ankimon.pyobj.trainer_card_window",
    "Ankimon.pyobj.download_sprites",
    "Ankimon.pyobj.ankimon_leaderboard",
    "Ankimon.pyobj.settings",
    "Ankimon.pyobj.translator",
    "Ankimon.pyobj.InfoLogger",
    "Ankimon.pyobj.item_window",
    "Ankimon.pyobj.pc_box",
    "Ankimon.pyobj.trainer_card",
    "Ankimon.pyobj.settings_window",
    "Ankimon.pyobj.test_window",
    "Ankimon.pyobj.ankimon_shop",
    "Ankimon.pyobj.achievement_window",
    "Ankimon.pyobj.ankimon_tracker_window",
    "Ankimon.pyobj.backup_manager",
    "Ankimon.gui_entities",
)


# Cached Ankimon modules other test files leave behind (often as MagicMocks)
# must NOT shadow the real engine modules. We purge everything under Ankimon
# except these two, which the temp_env fixture / MockResources rely on.
_KEEP_ANKIMON = {"Ankimon.pyobj.database_manager", "Ankimon.resources"}


def setup_engine_env(src):
    src = str(src)

    # 0. Purge cached Ankimon modules so the engine's (lazy) imports resolve to
    #    fresh, REAL modules rather than mocks left by earlier-collected tests.
    for k in [k for k in sys.modules if k == "Ankimon" or k.startswith("Ankimon.")]:
        if k not in _KEEP_ANKIMON:
            sys.modules.pop(k, None)

    # 1. Real-path Ankimon packages so `Ankimon.<sub>` resolves to src/Ankimon/...
    for pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj"):
        sub = pkg.replace(".", "/")
        m = types.ModuleType(pkg)
        m.__path__ = [f"{src}/{sub}"]
        m.__package__ = pkg
        sys.modules[pkg] = m

    # 2. aqt / anki host: mocked, with real PyQt6 surfaced under aqt + aqt.qt.
    aqt_mod = types.ModuleType("aqt")
    sys.modules["aqt"] = aqt_mod
    aqt_mod.mw = MagicMock()

    aqt_qt = _PermissiveModule("aqt.qt")
    aqt_qt.__all__ = []
    sys.modules["aqt.qt"] = aqt_qt
    aqt_mod.qt = aqt_qt

    aqt_utils = _PermissiveModule("aqt.utils")
    aqt_utils.__all__ = []
    sys.modules["aqt.utils"] = aqt_utils
    aqt_mod.utils = aqt_utils

    for sub in ("gui_hooks", "operations", "reviewer", "webview", "main", "theme", "sound"):
        ms = MagicMock()
        sys.modules[f"aqt.{sub}"] = ms
        setattr(aqt_mod, sub, ms)
    sys.modules["aqt.operations.QueryOp"] = MagicMock()

    anki_mod = types.ModuleType("anki")
    sys.modules["anki"] = anki_mod
    for sub in ("hooks", "collection", "models", "notes", "template", "buildinfo"):
        ms = MagicMock()
        sys.modules[f"anki.{sub}"] = ms
        setattr(anki_mod, sub, ms)

    import PyQt6.QtWidgets
    import PyQt6.QtCore
    import PyQt6.QtGui
    import PyQt6.QtWebChannel  # noqa: F401

    for module in (PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui):
        for name in dir(module):
            if name.startswith("Q") or name == "Qt":
                try:
                    setattr(aqt_qt, name, getattr(module, name))
                    setattr(aqt_mod, name, getattr(module, name))
                except Exception:
                    pass

    mock_web = MagicMock()
    aqt_mod.QWebEngineView = mock_web
    aqt_qt.QWebEngineView = mock_web
    aqt_qt.qconnect = MagicMock()
    aqt_mod.qconnect = MagicMock()
    aqt_utils.qconnect = MagicMock()
    try:
        import PyQt6.sip as sip_mod
    except ImportError:  # pragma: no cover
        import sip as sip_mod
    aqt_qt.sip = sip_mod

    # 3. The engine's only menu_buttons / singletons touchpoints are lazy and
    #    harmless; keep them mocked so we never build the real Qt menu/GUI.
    sys.modules["Ankimon.menu_buttons"] = MagicMock()
    sys.modules.setdefault("Ankimon.singletons", MagicMock())

    # 4. Ankimon.utils can't be imported here (it loads data files at module top
    #    against the MockResources paths). The engine only needs the pure
    #    limit_ev_yield() + a settable in_bulk_resolve flag, so expose a stub with
    #    the GENUINE limit_ev_yield extracted from the real source.
    utils_stub = _PermissiveModule("Ankimon.utils")
    utils_stub.in_bulk_resolve = False
    try:
        import ast
        import random as _random

        with open(f"{src}/Ankimon/utils.py", "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        ns = {"random": _random}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "limit_ev_yield":
                exec(compile(ast.Module(body=[node], type_ignores=[]), "utils.py", "exec"), ns)
                break
        utils_stub.limit_ev_yield = ns["limit_ev_yield"]
    except Exception:
        pass
    sys.modules["Ankimon.utils"] = utils_stub


# Engine symbols + the headless bridge each mobile test references at module
# level. import_engine() (re-)binds them in a test module's globals to the
# freshly-imported engine so that unittest.mock.patch("...mobile_sync.X") and the
# test's bound functions are the same module object.
_ENGINE_NAMES = (
    "record_desktop_review",
    "get_desktop_session_revlog_ids",
    "clear_desktop_session",
    "detect_mobile_reviews",
    "process_mobile_reviews_after_sync",
    "MOBILE_QUEUE_CAP",
    "simulate_pending_mobile_battles",
    "resolve_all",
    "resolve_next",
    "commit_replay_outcome",
    "select_best_companion",
)


def import_engine(g):
    """Import the engine fresh and (re)bind the names used by the tests into g."""
    import importlib

    ms = importlib.import_module("Ankimon.functions.mobile_sync")
    for name in _ENGINE_NAMES:
        if hasattr(ms, name):
            g[name] = getattr(ms, name)
    from tests.mobile_engine_helpers import MobileBridge
    g["MobileBridge"] = MobileBridge
    return ms


def load_real_menu_buttons(src):
    """Force-load the genuine ``Ankimon.menu_buttons`` for the update_mobile_badge
    test, stubbing its heavy Qt-window siblings (which build widgets at import)."""
    import importlib.util

    src = str(src)
    saved = {m: sys.modules.get(m) for m in _MENU_SIBLINGS}
    for m in _MENU_SIBLINGS:
        sys.modules[m] = MagicMock()
    saved_menu = sys.modules.get("Ankimon.menu_buttons")
    try:
        spec = importlib.util.spec_from_file_location(
            "Ankimon.menu_buttons", f"{src}/Ankimon/menu_buttons.py"
        )
        menu_mod = importlib.util.module_from_spec(spec)
        sys.modules["Ankimon.menu_buttons"] = menu_mod
        spec.loader.exec_module(menu_mod)
        return menu_mod
    finally:
        for m, v in saved.items():
            if v is None:
                sys.modules.pop(m, None)
            else:
                sys.modules[m] = v
        # Leave the real menu_buttons in place if we loaded it; otherwise restore.
        if "Ankimon.menu_buttons" not in sys.modules and saved_menu is not None:
            sys.modules["Ankimon.menu_buttons"] = saved_menu

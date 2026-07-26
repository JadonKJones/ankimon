"""Regression tests for the developer hot-reload lifecycle."""

import importlib.util
import sys
import time
import types
from pathlib import Path
from types import SimpleNamespace


_SRC = Path(__file__).parent.parent / "src"


def _module(name, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def test_restart_waits_for_startup_before_teardown(monkeypatch):
    calls = []
    services = SimpleNamespace(_startup_in_progress=True)

    class FakeApplication:
        @staticmethod
        def processEvents():
            calls.append("process_events")
            services._startup_in_progress = False

        @staticmethod
        def allWidgets():
            return []

    pyqt6 = _module("PyQt6")
    pyqt6.__path__ = []
    qtwidgets = _module(
        "PyQt6.QtWidgets",
        QApplication=FakeApplication,
        QWidget=type("QWidget", (), {}),
    )
    pyqt6.QtWidgets = qtwidgets
    monkeypatch.setitem(sys.modules, "PyQt6", pyqt6)
    monkeypatch.setitem(sys.modules, "PyQt6.QtWidgets", qtwidgets)

    aqt = _module("aqt", gui_hooks=SimpleNamespace(), mw=SimpleNamespace())
    aqt.__path__ = []
    monkeypatch.setitem(sys.modules, "aqt", aqt)
    monkeypatch.setitem(
        sys.modules,
        "aqt.utils",
        _module("aqt.utils", tooltip=lambda message: calls.append(("tooltip", message))),
    )
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.services",
        _module("Ankimon.services", services=services),
    )

    spec = importlib.util.spec_from_file_location(
        "Ankimon.reloader", _SRC / "Ankimon" / "reloader.py"
    )
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "Ankimon.reloader", mod)
    spec.loader.exec_module(mod)

    monkeypatch.setattr(
        mod,
        "teardown_ankimon",
        lambda addon_package: calls.append(("teardown", addon_package)),
    )
    monkeypatch.setattr(
        mod.importlib,
        "import_module",
        lambda addon_package: calls.append(("import", addon_package)),
    )
    monkeypatch.setattr(time, "sleep", lambda delay: calls.append(("sleep", delay)))

    mod.restart_ankimon()

    assert calls[:4] == [
        "process_events",
        ("sleep", 0.02),
        ("teardown", "Ankimon"),
        ("import", "Ankimon"),
    ]
    assert calls[-1] == ("tooltip", "Ankimon reloaded.")
    # The asynchronous startup callbacks own clearing this flag.
    assert services._is_reloading is True

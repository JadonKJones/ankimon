"""Characterization tests for the Ankidex window factory (F16).

Pins the wiring contract of ``singletons.get_ankidex_window()`` without Qt:

* First access lazily constructs the ``Ankidex`` dialog exactly once, passing
  ``addon_dir`` positionally and the services-resolved tracker as
  ``ankimon_tracker=`` — never reaching into ``mw`` for either.
* The window is cached (module-level ``_ankidex_window``): a second call returns
  the same instance, and no window is constructed at import time.
* A window whose underlying C++ object died (``is_alive`` False) is transparently
  re-created instead of handed out dead — the same reload-safe idiom the other
  ``get_*_window`` factories use.

House pattern (mirrors ``test_reload_safe_singletons``): mock aqt + the
window-class modules in ``sys.modules``, then exec the real ``singletons`` module
file under its dotted name. The real ``Ankimon.utils``/``Ankimon.resources`` come
from ``tests/conftest.py``.
"""

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

_src = Path(__file__).parent.parent / "src"


class FakeWindow:
    """Stands in for any Qt window class: records constructions, is 'alive'."""

    instances = []

    def __init__(self, *args, **kwargs):
        type(self).instances.append(self)
        self.args = args
        self.kwargs = kwargs
        self._dead = False

    def objectName(self):
        if self._dead:
            raise RuntimeError("wrapped C/C++ object has been deleted")
        return ""

    def kill(self):
        """Simulate Qt deleting the underlying C++ object."""
        self._dead = True


class FakeAnkidex(FakeWindow):
    instances = []


class FakeReviewerManager:
    instances = []

    def __init__(self, *args, **kwargs):
        type(self).instances.append(self)


class FakeShopManager:
    instances = []

    def __init__(self, *args, **kwargs):
        type(self).instances.append(self)


def _stub_module(name, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def _fresh_services(monkeypatch):
    """Exec a fresh, REAL services registry (isolated from other tests)."""
    services_spec = importlib.util.spec_from_file_location(
        "Ankimon.services", _src / "Ankimon" / "services.py"
    )
    services_mod = importlib.util.module_from_spec(services_spec)
    monkeypatch.setitem(sys.modules, "Ankimon.services", services_mod)
    services_spec.loader.exec_module(services_mod)
    return services_mod.services


@pytest.fixture
def env(monkeypatch):
    """Fresh aqt stub + fresh services registry + stubbed window modules."""
    FakeAnkidex.instances = []
    FakeReviewerManager.instances = []
    FakeShopManager.instances = []

    mw = SimpleNamespace()
    monkeypatch.setitem(sys.modules, "aqt", _stub_module("aqt", mw=mw))

    # is_alive is a verbatim copy of the real one (src/Ankimon/utils.py); we stub
    # it here because other test files can leave partial Ankimon.utils stubs.
    def is_alive(obj):
        if obj is None:
            return False
        try:
            obj.objectName()
            return True
        except (RuntimeError, AttributeError):
            return False

    monkeypatch.setitem(
        sys.modules, "Ankimon.utils", _stub_module("Ankimon.utils", is_alive=is_alive)
    )

    services = _fresh_services(monkeypatch)

    calls = []

    def build_core():
        calls.append("build_core")
        core_objs = {
            "logger": MagicMock(name="logger"),
            "db": MagicMock(name="db"),
            "settings": MagicMock(name="settings"),
            "translator": MagicMock(name="translator"),
            "tracker": MagicMock(name="tracker"),
            "main_pokemon": MagicMock(name="main_pokemon"),
            "enemy_pokemon": MagicMock(name="enemy_pokemon"),
            "trainer_card": MagicMock(name="trainer_card"),
            "achievements": {"1": False},
        }
        services.populate(**core_objs)
        return SimpleNamespace(
            logger=core_objs["logger"],
            ankimon_db=core_objs["db"],
            settings_obj=core_objs["settings"],
            translator=core_objs["translator"],
            main_pokemon=core_objs["main_pokemon"],
            mainpokemon_empty=False,
            enemy_pokemon=core_objs["enemy_pokemon"],
            trainer_card=core_objs["trainer_card"],
            ankimon_tracker_obj=core_objs["tracker"],
            achievements=core_objs["achievements"],
        )

    def bind_runtime_globals():
        calls.append("bind")

    monkeypatch.setitem(
        sys.modules,
        "Ankimon.core",
        _stub_module(
            "Ankimon.core",
            build_core=build_core,
            bind_runtime_globals=bind_runtime_globals,
        ),
    )

    class QtPresenter:
        pass

    monkeypatch.setitem(
        sys.modules,
        "Ankimon.gui_presenter",
        _stub_module("Ankimon.gui_presenter", QtPresenter=QtPresenter),
    )

    monkeypatch.setitem(
        sys.modules,
        "Ankimon.pyobj.ankimon_shop",
        _stub_module("Ankimon.pyobj.ankimon_shop", PokemonShopManager=FakeShopManager),
    )
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.pyobj.reviewer_obj",
        _stub_module(
            "Ankimon.pyobj.reviewer_obj", Reviewer_Manager=FakeReviewerManager
        ),
    )

    # Stub the ankidex package + its obj module so the factory's lazy
    # ``from .ankidex.ankidex_obj import Ankidex`` resolves to the fake.
    ankidex_pkg = _stub_module("Ankimon.ankidex")
    ankidex_pkg.__path__ = [str(_src / "Ankimon" / "ankidex")]
    ankidex_pkg.__package__ = "Ankimon.ankidex"
    monkeypatch.setitem(sys.modules, "Ankimon.ankidex", ankidex_pkg)
    ankidex_obj = _stub_module("Ankimon.ankidex.ankidex_obj", Ankidex=FakeAnkidex)
    ankidex_pkg.ankidex_obj = ankidex_obj
    monkeypatch.setitem(sys.modules, "Ankimon.ankidex.ankidex_obj", ankidex_obj)

    sys.modules.pop("Ankimon.singletons", None)

    yield SimpleNamespace(services=services, calls=calls, mw=mw)

    sys.modules.pop("Ankimon.singletons", None)


def _exec_singletons():
    spec = importlib.util.spec_from_file_location(
        "Ankimon.singletons", _src / "Ankimon" / "singletons.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["Ankimon.singletons"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_ankidex_window_is_not_built_at_import(env):
    _exec_singletons()
    assert FakeAnkidex.instances == []


def test_ankidex_window_lazy_construct_cached_and_seam_wired(env):
    mod = _exec_singletons()

    win1 = mod.get_ankidex_window()
    win2 = mod.get_ankidex_window()

    # Constructed exactly once, then cached.
    assert win1 is win2
    assert len(FakeAnkidex.instances) == 1

    # Seam-correct construction: addon_dir positional, services-resolved tracker
    # passed as ankimon_tracker= (never pulled off mw).
    assert win1.args == (mod.addon_dir,)
    assert win1.kwargs == {"ankimon_tracker": env.services.tracker}


def test_ankidex_window_recreated_when_dead(env):
    mod = _exec_singletons()

    win1 = mod.get_ankidex_window()
    win1.kill()  # simulate Qt deleting the underlying C++ object

    win2 = mod.get_ankidex_window()
    assert win2 is not win1
    assert len(FakeAnkidex.instances) == 2

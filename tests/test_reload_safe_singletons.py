"""Characterization tests for the reload-safe composition root (F31).

Pins the reload-safety contract of ``singletons.py`` + ``card_hooks.py``
without Qt:

* Importing ``singletons`` builds the core exactly once; a second exec of the
  module (an add-on reload / double boot with the services registry surviving)
  REUSES the live registry objects instead of rebuilding them — in particular
  ``Reviewer_Manager`` (whose constructor registers gui_hooks) is not
  duplicated.
* No window is constructed at import time. Window names resolve lazily through
  the module-level ``__getattr__``: first access constructs, second access
  returns the same instance, and a window whose underlying C++ object died
  (``is_alive`` False) is transparently re-created.
* Every name the base consumers import from ``singletons`` still resolves.
* ``register_card_hooks()`` is idempotent: a second call must not append the
  reviewer hooks again.

House pattern: mock aqt + the window-class modules in ``sys.modules``, then
exec the real module file under its dotted name (tests/conftest.py provides the
``Ankimon`` package stubs and the real ``Ankimon.utils``/``Ankimon.resources``).
"""

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

_src = Path(__file__).parent.parent / "src"

# Every name the base consumers import from singletons (enumerated with
# `git grep "from .singletons import\|from ..singletons import"`):
# __init__.py, card_hooks.py, discord_integration.py, hook_registry.py,
# profile_hooks.py, reviewer_ui.py, startup.py, functions/
# pokemon_showdown_functions.py, functions/rate_addon_functions.py, and the
# deferred pokemon_pc / evo_window imports in pyobj/ + gui_classes/.
CONSUMED_NAMES = {
    "settings_obj",
    "settings_window",
    "logger",
    "translator",
    "reviewer_obj",
    "ankimon_tracker_obj",
    "test_window",
    "achievement_bag",
    "shop_manager",
    "ankimon_tracker_window",
    "pokedex_window",
    "eff_chart",
    "gen_id_chart",
    "license",
    "credits",
    "evo_window",
    "starter_window",
    "item_window",
    "version_dialog",
    "pokemon_pc",
    "trainer_card",
    "main_pokemon",
    "enemy_pokemon",
    "achievements",
    "ankimon_db",
    "get_test_window",
}


class FakeWindow:
    """Stands in for any Qt window class: records constructions, is 'alive'."""

    instances = []

    def __init__(self, *args, **kwargs):
        type(self).instances.append(self)
        self._dead = False

    def objectName(self):
        if self._dead:
            raise RuntimeError("wrapped C/C++ object has been deleted")
        return ""

    def kill(self):
        """Simulate Qt deleting the underlying C++ object."""
        self._dead = True


class FakeTestWindow(FakeWindow):
    instances = []


class FakeStarterWindow(FakeWindow):
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


@pytest.fixture
def env(monkeypatch):
    """Fresh aqt stub + fresh services registry + stubbed window modules."""
    FakeWindow.instances = []
    FakeTestWindow.instances = []
    FakeStarterWindow.instances = []
    FakeReviewerManager.instances = []
    FakeShopManager.instances = []

    # aqt stub: mw is a plain attribute bag (singletons only writes shims on it).
    mw = SimpleNamespace()
    monkeypatch.setitem(sys.modules, "aqt", _stub_module("aqt", mw=mw))

    # utils stub whose is_alive is a verbatim copy of the real one
    # (src/Ankimon/utils.py:1005-1018). We stub rather than exec the real
    # utils module because other test files leave partial ModuleType stubs of
    # Ankimon.utils behind that conftest keeps, which makes importing/exec'ing
    # the real module here order-dependent.
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

    # Fresh, REAL services registry per test (isolated from other tests).
    services_spec = importlib.util.spec_from_file_location(
        "Ankimon.services", _src / "Ankimon" / "services.py"
    )
    services_mod = importlib.util.module_from_spec(services_spec)
    monkeypatch.setitem(sys.modules, "Ankimon.services", services_mod)
    services_spec.loader.exec_module(services_mod)
    services = services_mod.services

    # core stub: mimics the real build_core (populates services, returns the
    # namespace) and records every call so the tests can count boots/binds.
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

    # Window/manager classes singletons touches eagerly or in the factories
    # under test.
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
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.pyobj.test_window",
        _stub_module("Ankimon.pyobj.test_window", TestWindow=FakeTestWindow),
    )
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.pyobj.starter_window",
        _stub_module("Ankimon.pyobj.starter_window", StarterWindow=FakeStarterWindow),
    )

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


def test_first_boot_builds_core_once_and_no_windows(env):
    mod = _exec_singletons()

    assert env.calls.count("build_core") == 1
    # Exactly one bind at the bottom of the module (no factory ran yet).
    assert env.calls.count("bind") == 1
    # No window constructed at import time.
    assert FakeTestWindow.instances == []
    assert FakeStarterWindow.instances == []
    # Core names are exposed as real module globals.
    assert mod.logger is env.services.logger
    assert mod.settings_obj is env.services.settings
    assert mod.ankimon_db is env.services.db
    # mw back-compat shims mirror the registry.
    assert env.mw.ankimon_db is env.services.db
    assert env.mw.settings_obj is env.services.settings


def test_second_boot_reuses_core_and_reviewer(env):
    mod1 = _exec_singletons()
    reviewer1 = mod1.reviewer_obj
    ui1 = env.services.ui
    assert env.services.reviewer is reviewer1
    assert len(FakeReviewerManager.instances) == 1

    # Simulate an add-on reload: the module is re-executed from scratch while
    # the services registry survives.
    sys.modules.pop("Ankimon.singletons")
    mod2 = _exec_singletons()

    assert env.calls.count("build_core") == 1, "second boot must not rebuild the core"
    assert mod2.logger is mod1.logger
    assert mod2.settings_obj is mod1.settings_obj
    # Reviewer_Manager registers gui_hooks in its constructor: it must be
    # get-or-create, or the double boot double-registers those hooks.
    assert len(FakeReviewerManager.instances) == 1
    assert mod2.reviewer_obj is reviewer1
    # The Qt presenter is also reused, not re-instantiated.
    assert env.services.ui is ui1


def test_window_is_lazy_idempotent_and_registered(env):
    mod = _exec_singletons()
    binds_before = env.calls.count("bind")

    win1 = mod.test_window  # attribute access -> module __getattr__ -> factory
    win2 = mod.get_test_window()

    assert win1 is win2
    assert len(FakeTestWindow.instances) == 1
    # The seam window is registered in the services registry...
    assert env.services.test_window is win1
    # ...and the runtime globals were re-bound so battle_loop/encounter code
    # picks up the live instance.
    assert env.calls.count("bind") == binds_before + 1


def test_dead_window_is_recreated(env):
    mod = _exec_singletons()

    win1 = mod.get_test_window()
    win1.kill()  # underlying C++ object deleted -> is_alive() False

    win2 = mod.get_test_window()
    assert win2 is not win1
    assert len(FakeTestWindow.instances) == 2
    assert env.services.test_window is win2


def test_from_import_resolves_lazy_names(env):
    _exec_singletons()

    # `from .singletons import starter_window` is how startup.py consumes it.
    from Ankimon.singletons import starter_window

    assert isinstance(starter_window, FakeStarterWindow)
    assert len(FakeStarterWindow.instances) == 1

    # A second from-import returns the same live instance.
    from Ankimon.singletons import starter_window as starter_window2

    assert starter_window2 is starter_window
    assert len(FakeStarterWindow.instances) == 1


def test_every_consumer_name_still_resolves(env):
    mod = _exec_singletons()

    exposed = set(vars(mod)) | set(mod._LAZY_WINDOWS)
    missing = CONSUMED_NAMES - exposed
    assert not missing, f"singletons no longer exposes consumer names: {missing}"


def test_unknown_attribute_raises(env):
    mod = _exec_singletons()
    with pytest.raises(AttributeError):
        mod.definitely_not_a_window


def test_register_card_hooks_is_idempotent(monkeypatch):
    hooks = SimpleNamespace(
        reviewer_did_show_question=[],
        reviewer_did_show_answer=[],
        reviewer_will_answer_card=[],
        reviewer_did_answer_card=[],
    )
    aqt_stub = _stub_module(
        "aqt", gui_hooks=hooks, mw=SimpleNamespace(), utils=SimpleNamespace()
    )
    monkeypatch.setitem(sys.modules, "aqt", aqt_stub)
    monkeypatch.setitem(
        sys.modules,
        "aqt.utils",
        _stub_module("aqt.utils", tooltip=lambda *a, **k: None),
    )
    monkeypatch.setitem(sys.modules, "Ankimon.singletons", MagicMock())

    spec = importlib.util.spec_from_file_location(
        "Ankimon.card_hooks", _src / "Ankimon" / "card_hooks.py"
    )
    card_hooks = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "Ankimon.card_hooks", card_hooks)
    spec.loader.exec_module(card_hooks)

    card_hooks.register_card_hooks()
    counts_after_first = (
        len(hooks.reviewer_did_show_question),
        len(hooks.reviewer_did_show_answer),
        len(hooks.reviewer_will_answer_card),
        len(hooks.reviewer_did_answer_card),
    )
    # on_show_question + on_reviewer_did_show_question share the question hook.
    assert counts_after_first == (2, 1, 1, 1)

    card_hooks.register_card_hooks()
    assert (
        len(hooks.reviewer_did_show_question),
        len(hooks.reviewer_did_show_answer),
        len(hooks.reviewer_will_answer_card),
        len(hooks.reviewer_did_answer_card),
    ) == counts_after_first, "second registration must be a no-op"

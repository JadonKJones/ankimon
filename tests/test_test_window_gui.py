"""Qt characterization tests for ``pyobj/test_window.py`` (row F51).

Pins the OBSERVABLE contract of the ported encounter display:

* ``init_ui`` builds ONE persistent layout (a ``main_label`` plus a hidden
  death-screen ``button_widget``) and a fixed 556x300 window — no
  rebuild-per-encounter: the layout and label objects keep their identity
  across ``display_first_encounter`` / ``display_battle`` /
  ``display_pokemon_death`` calls.
* ``_get_display_name`` routes mega/gmax internal names through the base's
  ``pokedex_functions.get_pretty_name_for_name`` (expectations validated
  against the real ``data_files/pokedex.json``), and everything else through
  the localized ``get_pokemon_diff_lang_name``.
* ``pokemon_display_battle`` no longer increments
  ``tracker.pokemon_encounter`` (the battle loop owns the counter) and
  ``display_first_encounter`` resets it to 0.
* The debounce is keyed per view: an immediate SAME-view repeat is dropped
  (exp's anti-flicker), while the battle->death transition — which main's
  battle loop produces on every faint — always renders.
* The death screen's catch/defeat buttons route through the base
  ``hook_registry`` seam (not ``mw.catchpokemon``/``mw.defeatpokemon``).

These need real PyQt6 (a QApplication), so they run in the Qt / Tier-2 env;
the whole module skips cleanly where PyQt6 is absent — mirroring
``test_pokemon_details_gui.py``. Run standalone with::

    pytest tests/test_test_window_gui.py
"""

import importlib
import sys
import types
from pathlib import Path

import pytest

pytest.importorskip("PyQt6")  # Qt env only; skipped in the aqt-free Tier-1 env.

_MODULE_NAME = "Ankimon.pyobj.test_window"
_SRC = Path(__file__).parent.parent / "src"

# A real, in-repo PNG so the sprite-scaling math runs on a non-null pixmap.
_REAL_SPRITE = _SRC / "Ankimon" / "ankimon_logo.png"

_EN_LANGUAGE = 9  # Translator LANG_NUMBERS: 9 -> "en"


class _FakeSettings:
    def __init__(self, values=None):
        self.values = {
            "misc.language": _EN_LANGUAGE,
            "misc.remove_level_cap": False,
        }
        self.values.update(values or {})

    def get(self, key, default=None):
        return self.values.get(key, default)


class _FakeTracker:
    def __init__(self):
        self.attack_counter = 7
        self.caught = 1
        self.pokemon_encounter = 3
        self.cards_battle_round = 0
        self.battlescene_file = "grass_pkmnbattlescene.png"


class _FakePokemon:
    def __init__(self, name, id, **kw):
        self.name = name
        self.id = id
        self.level = kw.get("level", 5)
        self.hp = kw.get("hp", 12)
        self.max_hp = kw.get("max_hp", 20)
        self.shiny = kw.get("shiny", False)
        self.type = kw.get("type", ["fire"])
        self.gender = kw.get("gender", "M")
        self.stat_stages = kw.get("stat_stages", {})
        self.xp = kw.get("xp", 0)
        self.growth_rate = kw.get("growth_rate", "medium")
        self.cp = kw.get("cp", 345)

    def get_sprite_path(self, side, ext):
        return _REAL_SPRITE


class _FakeClock:
    """Deterministic stand-in for the module's ``time`` import."""

    def __init__(self, start=1000.0):
        self.now = start

    def time(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture(autouse=True)
def _env_guard():
    """Skip gracefully when another test file has mocked PyQt6 in this run.

    Some Tier-1 test files install partial ``PyQt6`` stubs in ``sys.modules``
    at import time (e.g. ``test_settings_init_order``), which makes the
    module-level ``importorskip`` succeed while real Qt is absent — so guard
    each test too.
    """
    try:
        from PyQt6.QtWidgets import QDialog
    except ImportError:
        pytest.skip(
            "real PyQt6 not active (stubbed by another test); "
            "run tests/test_test_window_gui.py standalone"
        )

    if not isinstance(QDialog, type):  # PyQt6 was mocked by another test
        pytest.skip(
            "real PyQt6 not active (mocked by another test); "
            "run tests/test_test_window_gui.py standalone"
        )

    if str(_SRC) not in sys.path:
        sys.path.insert(0, str(_SRC))
    yield


@pytest.fixture
def tw_module(qapp):
    """Load the real ``test_window`` module with only ``aqt`` stubbed.

    Every Ankimon dependency in its import chain is aqt-free at import time,
    so the module runs its REAL code (real pokedex data, real translator,
    real painters) against a light PyQt6-backed ``aqt`` stub.
    """
    stub_names = (
        "Ankimon",
        "Ankimon.functions",
        "Ankimon.pyobj",
        "aqt",
        "aqt.qt",
        "aqt.utils",
        _MODULE_NAME,
    )
    saved = {name: sys.modules.get(name) for name in stub_names}

    for pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj"):
        mod = types.ModuleType(pkg)
        mod.__path__ = [str(_SRC / pkg.replace(".", "/"))]
        mod.__package__ = pkg
        sys.modules[pkg] = mod

    import PyQt6.QtCore as _QtCore
    import PyQt6.QtGui as _QtGui
    import PyQt6.QtWidgets as _QtWidgets

    try:
        from PyQt6 import sip as _sip
    except ImportError:  # pragma: no cover - sip packaging differences
        _sip = None

    qt_mod = types.ModuleType("aqt.qt")
    for src in (_QtCore, _QtGui, _QtWidgets):
        for attr in dir(src):
            if not attr.startswith("_"):
                setattr(qt_mod, attr, getattr(src, attr))
    qt_mod.qconnect = lambda signal, func: signal.connect(func)
    if _sip is not None:
        qt_mod.sip = _sip

    utils_mod = types.ModuleType("aqt.utils")
    utils_mod.showWarning = lambda *a, **k: None

    aqt_mod = types.ModuleType("aqt")
    aqt_mod.mw = None
    aqt_mod.qt = qt_mod
    aqt_mod.utils = utils_mod
    aqt_mod.qconnect = qt_mod.qconnect

    sys.modules["aqt"] = aqt_mod
    sys.modules["aqt.qt"] = qt_mod
    sys.modules["aqt.utils"] = utils_mod

    sys.modules.pop(_MODULE_NAME, None)
    module = importlib.import_module(_MODULE_NAME)

    yield module

    for name, mod in saved.items():
        if mod is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = mod


@pytest.fixture
def make_window(tw_module):
    windows = []

    def _make(main=None, enemy=None, tracker=None):
        main = main or _FakePokemon("pikachu", 25, type=["electric"])
        enemy = enemy or _FakePokemon("charizard", 6, type=["fire", "flying"])
        tracker = tracker or _FakeTracker()
        win = tw_module.TestWindow(
            main_pokemon=main,
            enemy_pokemon=enemy,
            settings_obj=_FakeSettings(),
            parent=None,
            ankimon_tracker_obj=tracker,
        )
        windows.append(win)
        return win

    yield _make

    for win in windows:
        win.deleteLater()


def test_init_ui_builds_persistent_scaffolding(make_window):
    win = make_window()

    layout = win.layout()
    assert layout is not None
    assert layout.count() == 2  # main_label + button_widget, nothing else
    assert layout.itemAt(0).widget() is win.main_label
    assert layout.itemAt(1).widget() is win.button_widget
    assert win.button_widget.isHidden()

    # Fixed 556x300 window (exp's fixed size/styling)
    assert (win.minimumWidth(), win.minimumHeight()) == (556, 300)
    assert (win.maximumWidth(), win.maximumHeight()) == (556, 300)
    assert "rgb(44,44,44)" in win.styleSheet()

    # The Ankimon logo landed on the persistent label
    assert win.main_label.pixmap() is not None
    assert not win.main_label.pixmap().isNull()
    assert win.windowTitle() == "Ankimon Window"


def test_layout_identity_persists_across_display_calls(make_window):
    tracker = _FakeTracker()
    win = make_window(tracker=tracker)

    layout_before = win.layout()
    label_before = win.main_label

    win.display_first_encounter()
    win._last_display_time = 0  # step past the debounce window
    win.display_battle()

    # Same layout object, same label object, same child count — no rebuild.
    assert win.layout() is layout_before
    assert win.main_label is label_before
    assert win.layout().count() == 2
    assert win.current_view == "battle"
    assert not win.main_label.pixmap().isNull()


def test_first_encounter_resets_counter_and_battle_does_not_increment(make_window):
    tracker = _FakeTracker()
    tracker.pokemon_encounter = 3
    win = make_window(tracker=tracker)

    win.display_first_encounter()
    assert tracker.pokemon_encounter == 0  # exp: reset on first encounter

    win._last_display_time = 0
    win.display_battle()
    # exp removed the per-render increment; the battle loop owns the counter.
    assert tracker.pokemon_encounter == 0


def test_get_display_name_mega_gmax_and_localized(make_window):
    from Ankimon.functions.pokedex_functions import get_pretty_name_for_name

    win = make_window()

    cases = {
        "venusaurmega": "Mega Venusaur",
        "charizardmegax": "Mega Charizard X",
        "charizardgmax": "Gigantamax Charizard",
    }
    for internal, pretty in cases.items():
        # The oracle is the real pokedex.json via the base helper...
        assert get_pretty_name_for_name(internal) == pretty
        # ...and the window routes special forms through exactly that helper.
        assert win._get_display_name(_FakePokemon(internal, 3)) == pretty

    # Normal forms keep the localized-name path (English here).
    assert win._get_display_name(_FakePokemon("charizard", 6)) == "Charizard"


def test_battle_to_death_transition_is_never_debounced(make_window, monkeypatch):
    win = make_window()
    clock = _FakeClock()
    monkeypatch.setattr(sys.modules[_MODULE_NAME], "time", clock)

    win.display_first_encounter()
    win.display_battle()  # same instant: first battle render after encounter
    assert win.current_view == "battle"

    # Main's battle loop calls display_battle() and then the death screen in
    # the same tick on a faint — the death render must not be dropped.
    win.display_pokemon_death()
    assert win.current_view == "death"
    assert not win.button_widget.isHidden()
    assert win.kill_button.text() == win.translator.translate("defeat_button")
    assert win.catch_button.text() == win.translator.translate("catch_button")
    assert win.nickname_input.placeholderText() == win.translator.translate(
        "choose_nickname"
    )


def test_same_view_repeat_is_debounced(make_window, monkeypatch):
    win = make_window()
    clock = _FakeClock()
    monkeypatch.setattr(sys.modules[_MODULE_NAME], "time", clock)

    win.display_first_encounter()
    win.display_battle()

    renders = []
    monkeypatch.setattr(
        win, "pokemon_display_battle", lambda: renders.append(1) or win.main_label
    )

    win.display_battle()  # duplicate at the same instant -> dropped
    assert renders == []

    clock.advance(0.1)  # past the 50ms window -> renders again
    win.display_battle()
    assert renders == [1]

    # Duplicate death renders are debounced the same way.
    win.display_pokemon_death()
    assert win.current_view == "death"
    death_renders = []
    monkeypatch.setattr(
        win,
        "pokemon_display_dead_pokemon",
        lambda: (
            death_renders.append(1)
            or (win.main_label, win.kill_button, win.catch_button, win.nickname_input)
        ),
    )
    win.display_pokemon_death()
    assert death_renders == []


def test_death_buttons_route_through_hook_registry_seam(make_window, monkeypatch):
    win = make_window()

    calls = []
    hook_registry = types.ModuleType("Ankimon.hook_registry")
    hook_registry.CatchPokemonHook = lambda ids: calls.append(("catch", set(ids)))
    hook_registry.DefeatPokemonHook = lambda: calls.append(("defeat",))
    reviewer_ui = types.ModuleType("Ankimon.reviewer_ui")
    reviewer_ui._collected_pokemon_ids = {6, 25}

    monkeypatch.setitem(sys.modules, "Ankimon.hook_registry", hook_registry)
    monkeypatch.setitem(sys.modules, "Ankimon.reviewer_ui", reviewer_ui)
    monkeypatch.setattr(
        sys.modules["Ankimon"], "hook_registry", hook_registry, raising=False
    )
    monkeypatch.setattr(
        sys.modules["Ankimon"], "reviewer_ui", reviewer_ui, raising=False
    )

    win.display_pokemon_death()
    assert win.windowTitle() != "Ankimon Window"  # death title shows catch_or_free

    win.catch_button.click()
    assert calls == [("catch", {6, 25})]
    assert win.windowTitle() == "Ankimon Window"  # reset before the callback runs

    win.kill_button.click()
    assert calls == [("catch", {6, 25}), ("defeat",)]

    # A second death render re-wires cleanly (disconnect + reconnect, no stacking).
    win._last_display_time = 0
    win.display_pokemon_death()
    calls.clear()
    win.catch_button.click()
    assert calls == [("catch", {6, 25})]

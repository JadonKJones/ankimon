"""Reload-safety contract for ``gui_classes/overview_team.py`` (F19).

The team-overview grid used to register its Deck Browser / Deck Overview hooks
at **import time**, gated by ``mw.settings_obj.get("gui.team_deck_view")``. That
is an unguarded side-effect: a second execution of the module (an add-on reload
in the same Anki session) would append the handlers a *second* time, so every
Deck Browser render would inject the grid twice.

The port moves registration into :func:`register_overview_hooks`, following the
F31 registry-anchored guard idiom already used by ``card_hooks.py``: the exact
``(hook, handler)`` pairs are recorded on the ``services`` registry (which
survives a module re-exec), and each call removes the previously stored pairs
before appending. A reload therefore *swaps* the handlers instead of stacking a
duplicate set. Registration is gated on ``gui.team_deck_view`` and read through
``services.settings`` rather than ``mw``.

These tests exec the real module against a ``gui_hooks`` stub (plain lists, so
an unmatched ``remove()`` would fail loudly) and a fresh, real ``services``
registry — no Anki/Qt runtime required (Tier-1).
"""

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

_src = Path(__file__).parent.parent / "src"


def _stub_module(name, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def _fresh_hooks():
    """gui_hooks stub: plain lists, so an unmatched remove() would fail loudly."""
    return SimpleNamespace(
        deck_browser_will_render_content=[],
        overview_will_render_content=[],
    )


def _counts(hooks):
    return (
        len(hooks.deck_browser_will_render_content),
        len(hooks.overview_will_render_content),
    )


def _fresh_services(monkeypatch):
    """Exec a fresh, REAL services registry (isolated from other tests)."""
    spec = importlib.util.spec_from_file_location(
        "Ankimon.services", _src / "Ankimon" / "services.py"
    )
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "Ankimon.services", mod)
    spec.loader.exec_module(mod)
    return mod.services


def _exec_overview_team(monkeypatch, hooks):
    """Exec the real overview_team.py against a gui_hooks stub. Each call returns
    a FRESH module object (fresh handler functions) — exactly what an add-on
    reload produces — while ``Ankimon.services`` is left to the caller.

    The module's leaf dependencies are stubbed so the import stays isolated and
    Qt-free; only ``gui_hooks`` (via the aqt stub) and ``services`` are real
    to the registration path under test.
    """
    monkeypatch.setitem(sys.modules, "aqt", _stub_module("aqt", gui_hooks=hooks))
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.business",
        _stub_module("Ankimon.business", calculate_cp_from_dict=lambda p: 0),
    )
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.functions.sprite_functions",
        _stub_module(
            "Ankimon.functions.sprite_functions", get_sprite_path=lambda *a, **k: ""
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.resources",
        _stub_module(
            "Ankimon.resources",
            mypokemon_path="mypokemon.json",
            icon_path="pokeball.png",
            team_pokemon_path="team.json",
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "Ankimon.utils",
        _stub_module("Ankimon.utils", png_to_base64=lambda *a, **k: ""),
    )

    # Parent package so the dotted exec + relative imports resolve.
    gui_classes_pkg = _stub_module("Ankimon.gui_classes")
    gui_classes_pkg.__path__ = [str(_src / "Ankimon" / "gui_classes")]
    monkeypatch.setitem(sys.modules, "Ankimon.gui_classes", gui_classes_pkg)

    spec = importlib.util.spec_from_file_location(
        "Ankimon.gui_classes.overview_team",
        _src / "Ankimon" / "gui_classes" / "overview_team.py",
    )
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "Ankimon.gui_classes.overview_team", mod)
    spec.loader.exec_module(mod)
    return mod


def _settings(value):
    return SimpleNamespace(get=lambda key, default=None: value)


def test_register_overview_hooks_is_idempotent(monkeypatch):
    services = _fresh_services(monkeypatch)
    services.settings = _settings(True)
    hooks = _fresh_hooks()
    mod = _exec_overview_team(monkeypatch, hooks)

    mod.register_overview_hooks()
    assert _counts(hooks) == (1, 1)

    mod.register_overview_hooks()
    assert _counts(hooks) == (1, 1), "second registration must not stack handlers"


def test_register_overview_hooks_survives_module_reexec(monkeypatch):
    """The F31 failure this guards: re-executing overview_team (an add-on
    reload) creates NEW handler function objects, so a module-level flag would
    reset and remove()-by-identity would miss the old handlers. The
    registry-stored record must swap the handlers instead of stacking."""
    services = _fresh_services(monkeypatch)
    services.settings = _settings(True)
    hooks = _fresh_hooks()

    mod1 = _exec_overview_team(monkeypatch, hooks)
    mod1.register_overview_hooks()
    assert _counts(hooks) == (1, 1)

    # Reload: fresh module + functions, same gui_hooks, surviving registry.
    mod2 = _exec_overview_team(monkeypatch, hooks)
    assert mod2.deck_browser_will_render is not mod1.deck_browser_will_render
    mod2.register_overview_hooks()

    assert _counts(hooks) == (1, 1), "reload must not stack handlers"
    # The live handlers are the reloaded module's, not the stale first set.
    assert hooks.deck_browser_will_render_content == [mod2.deck_browser_will_render]
    assert hooks.overview_will_render_content == [mod2.on_overview_will_render_content]


def test_register_overview_hooks_gated_off_clears_prior(monkeypatch):
    """Toggling the setting off then re-registering (e.g. a reload) must remove
    the previously registered handlers and append nothing new."""
    services = _fresh_services(monkeypatch)
    services.settings = _settings(True)
    hooks = _fresh_hooks()
    mod = _exec_overview_team(monkeypatch, hooks)

    mod.register_overview_hooks()
    assert _counts(hooks) == (1, 1)

    services.settings = _settings(False)
    mod.register_overview_hooks()
    assert _counts(hooks) == (0, 0)


def test_register_overview_hooks_no_settings_is_safe(monkeypatch):
    """A missing settings service must not crash registration (defensive
    None-guard); nothing is appended."""
    services = _fresh_services(monkeypatch)
    services.settings = None
    hooks = _fresh_hooks()
    mod = _exec_overview_team(monkeypatch, hooks)

    mod.register_overview_hooks()  # must not raise
    assert _counts(hooks) == (0, 0)

"""Regression test for the Active Companion clearing bug: handle_save_team()
used to treat ANY falsy companion_id (including "team.js never touched the
companion picker this save") as an explicit "clear the main Pokémon" —
meaning every ordinary team save that didn't touch the crown (reordering the
team, swapping an unrelated slot, XP Share only) wiped whatever main Pokémon
was already set, even one assigned through an older pathway (starter
selection, PC box) team.js never knew about.

The fix: team.js now sends a distinct ``_COMPANION_UNCHANGED`` sentinel when
the companion selection was never touched this session, and handle_save_team
leaves the DB's is_main row completely alone in that case. An empty/invalid
value is still an explicit clear, but only when the frontend actually says so.

Loads profile_data.py directly with its own dependencies stubbed (it's a
plain, non-Qt data layer per its own module docstring), so this pins the
branching logic without needing a real Qt/services stack.
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

_SRC = Path(__file__).parent.parent / "src"
_MODULE_NAME = "Ankimon.ankimon_profile_web.profile_data"


class _FakeDB:
    def __init__(self):
        self.saved_team = None
        self.set_main_calls = []
        self.clear_main_calls = 0

    def save_team(self, team_data):
        self.saved_team = team_data

    def set_main_pokemon(self, individual_id):
        self.set_main_calls.append(individual_id)
        return True

    def clear_main_pokemon(self):
        self.clear_main_calls += 1


class _FakeSettings:
    def __init__(self):
        self.values = {}

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, val):
        self.values[key] = val


@pytest.fixture
def pd_module(monkeypatch):
    for name in ("Ankimon", "Ankimon.ankimon_profile_web"):
        pkg = types.ModuleType(name)
        pkg.__path__ = [str(_SRC / name.replace(".", "/"))]
        pkg.__package__ = name
        sys.modules[name] = pkg

    services_mod = types.ModuleType("Ankimon.services")
    fake_services = types.SimpleNamespace(
        db=_FakeDB(),
        main_pokemon=None,
        reviewer=None,
        test_window=None,
    )
    services_mod.services = fake_services
    sys.modules["Ankimon.services"] = services_mod

    utils_mod = types.ModuleType("Ankimon.utils")
    utils_mod.get_all_sprites = lambda *a, **k: []
    utils_mod.POKEMON_NAME_LOOKUP = {}
    sys.modules["Ankimon.utils"] = utils_mod

    resources_mod = types.ModuleType("Ankimon.resources")
    resources_mod.trainer_sprites_path = Path("/tmp")
    sys.modules["Ankimon.resources"] = resources_mod

    for name in ("Ankimon.functions",):
        pkg = types.ModuleType(name)
        pkg.__path__ = [str(_SRC / name.replace(".", "/"))]
        pkg.__package__ = name
        sys.modules[name] = pkg

    update_main_pokemon_mod = types.ModuleType("Ankimon.functions.update_main_pokemon")
    update_main_pokemon_mod.update_main_pokemon = lambda *a, **k: None
    sys.modules["Ankimon.functions.update_main_pokemon"] = update_main_pokemon_mod

    sys.modules.pop(_MODULE_NAME, None)
    spec = importlib.util.spec_from_file_location(
        _MODULE_NAME, _SRC / "Ankimon" / "ankimon_profile_web" / "profile_data.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = mod
    spec.loader.exec_module(mod)

    yield mod, fake_services


def _make_pd(pd_module):
    mod, _ = pd_module
    return mod.ProfileData(
        addon_dir=Path("/tmp"),
        trainer_card=None,
        settings_obj=_FakeSettings(),
        logger=None,
    )


def test_unchanged_sentinel_leaves_existing_main_pokemon_alone(pd_module):
    """The core regression: a normal save (companion never touched) must NOT
    clear an existing main Pokémon."""
    mod, fake_services = pd_module
    pd = _make_pd(pd_module)

    result = pd.handle_save_team(
        ["a", "b"], "", mod.ProfileData._COMPANION_UNCHANGED
    )

    assert result["ok"] is True
    assert fake_services.db.clear_main_calls == 0
    assert fake_services.db.set_main_calls == []


def test_empty_companion_when_touched_clears_main_pokemon(pd_module):
    """An explicit clear (user toggled the crown off) still works."""
    mod, fake_services = pd_module
    pd = _make_pd(pd_module)

    result = pd.handle_save_team(["a", "b"], "", "")

    assert result["ok"] is True
    assert fake_services.db.clear_main_calls == 1
    assert fake_services.db.set_main_calls == []


def test_valid_companion_sets_main_pokemon(pd_module):
    mod, fake_services = pd_module
    pd = _make_pd(pd_module)

    result = pd.handle_save_team(["a", "b"], "", "a")

    assert result["ok"] is True
    assert fake_services.db.set_main_calls == ["a"]
    assert fake_services.db.clear_main_calls == 0


def test_companion_not_in_saved_team_is_rejected_and_cleared(pd_module):
    """A companion id that isn't actually part of the team being saved is
    invalid — must fall back to a clear, not silently set it anyway."""
    mod, fake_services = pd_module
    pd = _make_pd(pd_module)

    result = pd.handle_save_team(["a", "b"], "", "not-on-team")

    assert result["ok"] is True
    assert fake_services.db.set_main_calls == []
    assert fake_services.db.clear_main_calls == 1

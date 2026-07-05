"""Region-, move- and defeat-aware evolution tests (real bundled data).

These exercise the *manual-evolution readiness* path of
``Ankimon.functions.friendship_evolution`` (this unit, F40) against the real
``pokedex.json``: regional-form preference via ``misc.active_region`` (Alolan
Marowak), move-based evolutions (Mime Jr. needs Mimic) and the Kantonian- vs
Galarian-form distinction (Mr. Mime vs Mr. Rime).

Loading strategy mirrors ``tests/test_friendship_evolution.py``: ``aqt`` and the
error handler are stubbed, a fake ``singletons`` is installed and the real
``resources`` / ``pokedex_functions`` / ``friendship_evolution`` modules are
loaded so the bundled data is exercised. Settings (day/night bounds + the active
region) are driven through the ``services`` registry seam — the module reads
``services.settings`` lazily per call.

PARTITION NOTE (F40 <-> F17): the region-aware *automatic* evolution helpers
``pokedex_functions.check_evolution_by_item`` / ``check_evolution_for_pokemon``
(Pikachu/Exeggcute stone forms, Galarian Weezing, Hisuian items, Stantler ->
Wyrdeer) belong to feature **F17** (``functions/pokedex_functions.py`` +
``pokedex.json``), which is NOT part of this unit and is not yet merged onto the
integration tip. exp shipped those assertions in this same file; they are kept
here (so F17 can simply un-skip them once its region-branching lands) but marked
skipped meanwhile — running them against the current base would fail because the
base ``check_evolution_by_item`` is not region-aware.
"""

import importlib.util
import sys
import unittest.mock as mock
from datetime import datetime
from pathlib import Path

import pytest

_SRC = Path(__file__).parent.parent / "src"

# Skip marker for assertions that depend on F17's pokedex_functions region
# branching (not owned by this unit / not yet on the integration tip).
_needs_f17 = pytest.mark.skip(
    reason="depends on F17 pokedex_functions region branching "
    "(check_evolution_by_item / check_evolution_for_pokemon), not yet merged"
)


class _FakeSettings:
    """Mutable ``settings_obj`` stand-in exercised by the module under test."""

    def __init__(self):
        self.values = {
            "evolution.day_start_hour": 6,
            "evolution.night_start_hour": 18,
            "evolution.timezone_auto": True,
            "evolution.timezone_offset": 0.0,
            "evolution.friendship_time_enabled": True,
            "misc.active_region": "No Region",
        }

    def get(self, key, default=None):
        return self.values.get(key, default)


def _load_modules():
    """Load ``friendship_evolution`` + ``pokedex_functions`` against real data."""
    sys.modules["aqt"] = mock.MagicMock()
    sys.modules["aqt.qt"] = mock.MagicMock()
    sys.modules["aqt.utils"] = mock.MagicMock()
    sys.modules["Ankimon.pyobj.error_handler"] = mock.MagicMock()

    fake_settings = _FakeSettings()
    singletons_stub = importlib.util.module_from_spec(
        importlib.util.spec_from_loader("Ankimon.singletons", loader=None)
    )
    singletons_stub.settings_obj = fake_settings
    singletons_stub.get_evo_window = mock.MagicMock
    sys.modules["Ankimon.singletons"] = singletons_stub

    res_spec = importlib.util.spec_from_file_location(
        "Ankimon.resources", _SRC / "Ankimon" / "resources.py"
    )
    resources = importlib.util.module_from_spec(res_spec)
    sys.modules["Ankimon.resources"] = resources
    res_spec.loader.exec_module(resources)

    pf_spec = importlib.util.spec_from_file_location(
        "Ankimon.functions.pokedex_functions",
        _SRC / "Ankimon" / "functions" / "pokedex_functions.py",
    )
    pokedex_functions = importlib.util.module_from_spec(pf_spec)
    sys.modules["Ankimon.functions.pokedex_functions"] = pokedex_functions
    pf_spec.loader.exec_module(pokedex_functions)

    fe_spec = importlib.util.spec_from_file_location(
        "Ankimon.functions.friendship_evolution",
        _SRC / "Ankimon" / "functions" / "friendship_evolution.py",
    )
    fe = importlib.util.module_from_spec(fe_spec)
    sys.modules["Ankimon.functions.friendship_evolution"] = fe
    fe_spec.loader.exec_module(fe)
    return fe, pokedex_functions, fake_settings


fe, pf, settings = _load_modules()

_SINGLETONS_STUB = sys.modules["Ankimon.singletons"]
_POKEDEX_FUNCTIONS_STUB = sys.modules["Ankimon.functions.pokedex_functions"]


@pytest.fixture(autouse=True)
def _reset_env():
    """Restore our stubs + settings and clear the evolution caches per test."""
    sys.modules["Ankimon.singletons"] = _SINGLETONS_STUB
    sys.modules["Ankimon.functions.pokedex_functions"] = _POKEDEX_FUNCTIONS_STUB
    from Ankimon.services import services

    services.settings = settings
    settings.values.update(
        {
            "evolution.day_start_hour": 6,
            "evolution.night_start_hour": 18,
            "evolution.timezone_auto": True,
            "evolution.friendship_time_enabled": True,
            "misc.active_region": "No Region",
        }
    )
    # Region preference is read live per call, but cached level-evo tuples are
    # region-independent; clear anyway for hygiene across parametrised regions.
    fe.get_level_evolutions_for_species.cache_clear()
    fe.get_friendship_evolutions_for_species.cache_clear()
    yield


def _set_region(region):
    settings.values["misc.active_region"] = region


# --------------------------------------------------------------------------- #
# Region-aware MANUAL readiness (F40 — friendship_evolution.evolution_readiness)
# --------------------------------------------------------------------------- #
def test_manual_readiness_filtering_cubone():
    # Cubone (104) -> Marowak (105) / Alolan Marowak (10115, night-gated).
    _set_region("No Region")
    result = fe.evolution_readiness(
        {"id": 104, "level": 28}, now=datetime(2026, 1, 1, 12, 0)
    )
    assert result["evolvable"] is True
    assert result["evo_id"] == 105
    assert "Marowak" in result["evo_name"]
    assert "Alola" not in result["evo_name"]

    # Under Alola at night, the Alolan form supersedes the Kantonian one.
    _set_region("Alola")
    result = fe.evolution_readiness(
        {"id": 104, "level": 28}, now=datetime(2026, 1, 1, 23, 0)
    )
    assert result["evolvable"] is True
    assert result["evo_id"] == 10115
    assert "Alola" in result["evo_name"]


def test_mimejr_manual_evolution_readiness():
    # Mime Jr. (439) -> Mr. Mime (122) is move-based (needs Mimic).
    _set_region("No Region")
    result = fe.evolution_readiness(
        {
            "id": 439,
            "level": 32,
            "attacks": ["Mimic", "Confusion"],
            "everstone": False,
            "evolution_rejected": False,
        },
        now=datetime(2026, 1, 1, 12, 0),
    )
    assert result["evolvable"] is True
    assert result["ready"] is True
    assert result["evo_id"] == 122
    assert "Mr. Mime" in result["evo_name"]
    assert "Galar" not in result["evo_name"]

    # Without the required move it is evolvable (shown in the list) but not ready.
    result = fe.evolution_readiness(
        {
            "id": 439,
            "level": 32,
            "attacks": ["Confusion", "Tackle"],
            "everstone": False,
            "evolution_rejected": False,
        },
        now=datetime(2026, 1, 1, 12, 0),
    )
    assert result["evolvable"] is True
    assert result["ready"] is False
    assert "Needs to learn Mimic" in result["status_text"]


def test_mrmime_evolution_distinction():
    # Kantonian Mr. Mime (122) has no further evolution in pokedex.json.
    result_normal = fe.evolution_readiness(
        {
            "id": 122,
            "level": 50,
            "attacks": ["Mimic"],
            "everstone": False,
            "evolution_rejected": False,
        },
        now=datetime(2026, 1, 1, 12, 0),
    )
    assert result_normal["evolvable"] is False
    assert result_normal["ready"] is False

    # Galarian Mr. Mime (10168) -> Mr. Rime (866) at Lv42+.
    result_galar = fe.evolution_readiness(
        {
            "id": 10168,
            "level": 42,
            "attacks": ["Mimic"],
            "everstone": False,
            "evolution_rejected": False,
        },
        now=datetime(2026, 1, 1, 12, 0),
    )
    assert result_galar["evolvable"] is True
    assert result_galar["ready"] is True
    assert result_galar["evo_id"] == 866
    assert "Mr. Rime" in result_galar["evo_name"]


# --------------------------------------------------------------------------- #
# Region-aware AUTOMATIC evolution (F17 — pokedex_functions; deferred/skipped)
# --------------------------------------------------------------------------- #
@_needs_f17
def test_pikachu_evolution_by_active_region():
    _set_region("No Region")
    assert pf.check_evolution_by_item(25, 83) == 26
    _set_region("Alola")
    assert pf.check_evolution_by_item(25, 83) == 10100
    _set_region("Galar")
    assert pf.check_evolution_by_item(25, 83) == 26


@_needs_f17
def test_exeggcute_evolution_by_active_region():
    _set_region("No Region")
    assert pf.check_evolution_by_item(102, 85) == 103
    _set_region("Alola")
    assert pf.check_evolution_by_item(102, 85) == 10114


@_needs_f17
def test_koffing_evolution_by_active_region():
    mock_evo_window = mock.MagicMock()
    _set_region("No Region")
    assert pf.check_evolution_for_pokemon("p1", 109, 35, mock_evo_window) == 110
    mock_evo_window.reset_mock()
    _set_region("Galar")
    assert pf.check_evolution_for_pokemon("p2", 109, 35, mock_evo_window) == 10167


@_needs_f17
def test_dartrix_evolution_by_active_region():
    mock_evo_window = mock.MagicMock()
    _set_region("No Region")
    assert pf.check_evolution_for_pokemon("p1", 723, 36, mock_evo_window) == 724
    _set_region("Hisui")
    assert pf.check_evolution_for_pokemon("p2", 723, 36, mock_evo_window) == 10244


@_needs_f17
def test_hisuian_item_evolutions_enriched():
    _set_region("Hisui")
    assert pf.check_evolution_by_item(123, 10001) == 900
    _set_region("No Region")
    assert pf.check_evolution_by_item(123, 10001) is None
    _set_region("Hisui")
    assert pf.check_evolution_by_item(217, 10002) == 901


@_needs_f17
def test_stantler_wyrdeer_move_based_evolution():
    mock_evo_window = mock.MagicMock()
    _set_region("Hisui")
    assert pf.check_evolution_for_pokemon("p1", 234, 30, mock_evo_window) == 899
    _set_region("No Region")
    assert pf.check_evolution_for_pokemon("p1", 234, 30, mock_evo_window) is None

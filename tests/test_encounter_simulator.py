"""Parity tests for the Encounter Rate Simulator (F23).

The simulator dialog pulls in ``encounter_functions`` (a large aqt-dependent
chain) and PyQt6. We mock those so the module imports Qt-free in the Tier-1
environment, then exercise the *rate math* head-less:

* :meth:`EncounterSimulatorDialog.calculate_rates` — the seam re-fit of exp's
  monkeypatching implementation. It must inject the simulated state (Mastery
  Index ``ep`` + ``main_level`` + a read-only ``db`` provider) into
  ``encounter_functions`` **without** mutating any global (``mw`` / ``services``
  / ``main_pokemon`` / ``business.calculate_cp_from_dict``).
* :meth:`SimulatorBridge.get_initial_state` — the JS bootstrap payload.

An offscreen construct-smoke (skipped when PyQt6/QtWebEngine is unavailable)
covers the Qt wiring itself.
"""

import sys
import json
import types
import importlib.util
import unittest.mock as mock
from pathlib import Path
from types import SimpleNamespace

import pytest

# ---------------------------------------------------------------------------
# Isolated, Qt-free import of the dialog + encounter_functions.
#
# encounter_functions pulls in a large aqt-dependent chain; mock the heavy deps
# so both modules import Qt-free in the Tier-1 environment (mirrors
# tests/test_encounter_overhaul.py). We load via spec_from_file_location and
# re-establish the ``Ankimon`` package stubs first, so collection order cannot
# break us (another test module — e.g. test_database_manager — may have
# replaced ``sys.modules["Ankimon.pyobj"]`` with a MagicMock). sys.modules is
# restored afterwards so these mocks never leak into other tests.
# ---------------------------------------------------------------------------
_SRC = Path(__file__).parent.parent / "src"
_orig_modules = dict(sys.modules)

# Re-create real namespace-package stubs (with __path__) for relative imports.
for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj"):
    _mod = types.ModuleType(_pkg)
    _mod.__path__ = [str(_SRC / _pkg.replace(".", "/"))]
    _mod.__package__ = _pkg
    sys.modules[_pkg] = _mod

sys.modules["aqt"] = mock.MagicMock()
sys.modules["aqt.qt"] = mock.MagicMock()
sys.modules["aqt.utils"] = mock.MagicMock()
# Force the dialog's guarded Qt import to fall back to head-less stubs, even in
# the Qt env. Otherwise this (Tier-1) module would hold real QObject/QWidget
# subclasses with no QApplication, which hangs/segfaults the interpreter at
# teardown. The offscreen construct-smoke uses the real widgets in a subprocess.
for _qt in (
    "PyQt6.QtWidgets",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebChannel",
):
    sys.modules[_qt] = None

for _module in [
    "Ankimon.pyobj.ankimon_tracker",
    "Ankimon.pyobj.pokemon_obj",
    "Ankimon.pyobj.reviewer_obj",
    "Ankimon.pyobj.test_window",
    "Ankimon.pyobj.trainer_card",
    "Ankimon.pyobj.InfoLogger",
    "Ankimon.pyobj.evolution_window",
    "Ankimon.pyobj.attack_dialog",
    "Ankimon.pyobj.translator",
    "Ankimon.pyobj.error_handler",
    "Ankimon.functions.pokemon_functions",
    "Ankimon.functions.pokedex_functions",
    "Ankimon.functions.friendship_evolution",
    "Ankimon.functions.trainer_functions",
    "Ankimon.functions.badges_functions",
    "Ankimon.functions.drawing_utils",
    "Ankimon.utils",
    "Ankimon.business",
    "Ankimon.const",
    "Ankimon.singletons",
    "Ankimon.resources",
]:
    sys.modules[_module] = mock.MagicMock()


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, _SRC / relpath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # register so dependents share this instance
    spec.loader.exec_module(module)
    return module


ef = _load(
    "Ankimon.functions.encounter_functions",
    "Ankimon/functions/encounter_functions.py",
)
esd = _load(
    "Ankimon.pyobj.encounter_simulator_dialog",
    "Ankimon/pyobj/encounter_simulator_dialog.py",
)
_services = esd.services  # the real registry singleton, shared with ef

# Restore: drop our heavy-dep mocks so the rest of the suite is unaffected.
sys.modules.clear()
sys.modules.update(_orig_modules)


class _FakeDB:
    """Minimal database provider — records writes so we can assert read-only."""

    def __init__(self, pity=None):
        self._pity = dict(pity or {})
        self.set_calls = []

    def get_all_pokemon_ids(self):
        return []

    def get_all_pokemon(self):
        return []

    def get_user_data(self, key):
        if key == "ankimon_pity_trackers":
            return dict(self._pity)
        return None

    def set_user_data(self, key, value):  # must never be hit by the simulator
        self.set_calls.append((key, value))


@pytest.fixture
def sim_env():
    """Populate the shared service registry + ef globals with fakes."""
    fake_db = _FakeDB()
    fake_tracker = mock.MagicMock()
    fake_tracker.get_total_reviews.return_value = 100
    fake_settings = mock.MagicMock()
    fake_settings.get.return_value = 100
    fake_trainer = SimpleNamespace(level=20)
    fake_main = SimpleNamespace(level=50)

    _services.reset()
    _services.db = fake_db
    _services.tracker = fake_tracker
    _services.settings = fake_settings
    _services.trainer_card = fake_trainer
    _services.main_pokemon = fake_main

    orig_ef_main = ef.main_pokemon
    orig_flag = ef.USE_OVERHAUL_ENCOUNTER_SYSTEM
    ef.main_pokemon = fake_main  # ef's bare global drives the live-rate path
    ef.clear_encounter_cache()
    try:
        yield SimpleNamespace(db=fake_db, tracker=fake_tracker, settings=fake_settings)
    finally:
        ef.main_pokemon = orig_ef_main
        ef.USE_OVERHAUL_ENCOUNTER_SYSTEM = orig_flag
        ef.clear_encounter_cache()
        _services.reset()


def _calc(slider_state, db):
    """Call calculate_rates unbound (it uses services, never ``self``)."""
    return esd.EncounterSimulatorDialog.calculate_rates(object(), slider_state, db=db)


def _expected_overhaul(ep, main_level, pity):
    """Re-implementation of ef._modify_percentages_overhaul's post-EP pipeline."""
    weights = {}
    for tier, (base, max_val) in ef.OVERHAUL_TIER_PARAMS.items():
        weights[tier] = base * ((max_val / base) ** (ep / 100.0))
    for tier, limit in ef.OVERHAUL_LEVEL_THRESHOLDS.items():
        if main_level < limit:
            weights[tier] = 0.0
    for tier in ef.OVERHAUL_PITY_THRESHOLDS:
        p_i = pity.get(tier, 0)
        t_i = ef.OVERHAUL_PITY_THRESHOLDS[tier]
        mult = 1.0 + (max(0, (p_i - t_i) / ef.OVERHAUL_PITY_DIVISOR)) ** 2
        weights[tier] = weights[tier] * mult
    total = sum(weights.values())
    return {t: (weights[t] / total * 100.0 if total > 0 else 0.0) for t in weights}


# --- Structure + EP formula + locks (exp's documented example) --------------


def test_calculate_rates_structure_ep_and_locks(sim_env):
    slider_state = {
        "trainer_level": 25,
        "dex_completion": 50.0,
        "reviews_done": 120,
        "daily_goal": 100,
        "avg_cp": 1500,
        "main_level": 45,
    }
    result = _calc(slider_state, sim_env.db)

    for key in ("live_overhaul", "live_legacy", "overhaul", "legacy", "ep", "locks"):
        assert key in result

    # EP = 0.25*(50 + 50 + 100 + 9.375) = 52.34375 (caps 50 / 16000, weights .25)
    assert abs(result["ep"] - 52.34375) < 0.001

    # main_level 45: Legendary gate (50) locks, Ultra gate (30) does not.
    assert result["locks"]["Legendary"] is True
    assert result["locks"]["Ultra"] is False


# --- Simulated overhaul matches the algorithm exactly (injection wiring) -----


def test_simulated_overhaul_matches_algorithm(sim_env):
    slider_state = {
        "trainer_level": 25,
        "dex_completion": 50.0,
        "reviews_done": 120,
        "daily_goal": 100,
        "avg_cp": 1500,
        "main_level": 45,
    }
    result = _calc(slider_state, sim_env.db)
    expected = _expected_overhaul(52.34375, 45, {})

    assert set(result["overhaul"]) == set(expected)
    for tier, exp_val in expected.items():
        assert abs(result["overhaul"][tier] - exp_val) < 1e-6

    # Level-gated tiers are exactly zero; the open tiers carry all the mass.
    for locked in ("Legendary", "Mega", "Gmax", "Mythical", "Starter"):
        assert result["overhaul"][locked] == 0.0
    for open_tier in ("Normal", "Baby", "Ultra"):
        assert result["overhaul"][open_tier] > 0.0
    assert abs(sum(result["overhaul"].values()) - 100.0) < 1e-6


# --- Simulation is read-only w.r.t. persisted pity / user_data --------------


def test_simulation_does_not_persist_pity(sim_env):
    slider_state = {
        "trainer_level": 40,
        "dex_completion": 80.0,
        "reviews_done": 200,
        "daily_goal": 100,
        "avg_cp": 8000,
        "main_level": 80,
    }
    _calc(slider_state, sim_env.db)
    # The simulator must never write pity trackers or any user_data.
    assert sim_env.db.set_calls == []


# --- The read-only pity provider actually influences the weights ------------


def test_injected_pity_boosts_that_tier(sim_env):
    slider_state = {
        "trainer_level": 40,
        "dex_completion": 80.0,
        "reviews_done": 200,
        "daily_goal": 100,
        "avg_cp": 8000,
        "main_level": 80,  # unlocks every tier
    }
    baseline = _calc(slider_state, _FakeDB(pity={}))
    # Ultra dry-spell well past its threshold (100) -> quadratic multiplier.
    boosted = _calc(slider_state, _FakeDB(pity={"Ultra": 300}))

    assert boosted["overhaul"]["Ultra"] > baseline["overhaul"]["Ultra"]
    assert abs(sum(boosted["overhaul"].values()) - 100.0) < 1e-6


# --- The live overhaul path reads pity from the injected db (DI, not global) -


def test_live_overhaul_uses_injected_db(sim_env):
    """The *live* overhaul rates must read pity from the injected ``db`` provider
    too — not from the global ``services.db``. Otherwise the DI provider only
    reaches the simulated path and the live path silently leaks to global state,
    which is exactly the global-state coupling the F23 DI refit exists to remove.

    ``ef.main_pokemon.level == 50`` (the fixture) drives the live path's tier
    gates, so Ultra (threshold 30) is unlocked and its pity boost is visible.
    ``services.db`` is left at the fixture's empty-pity db, so a rate change can
    only come from the ``db`` passed to ``calculate_rates``.
    """
    slider_state = {
        "trainer_level": 25,
        "dex_completion": 50.0,
        "reviews_done": 120,
        "daily_goal": 100,
        "avg_cp": 1500,
        "main_level": 45,
    }
    baseline = _calc(slider_state, _FakeDB(pity={}))
    boosted = _calc(slider_state, _FakeDB(pity={"Ultra": 300}))

    assert boosted["live_overhaul"]["Ultra"] > baseline["live_overhaul"]["Ultra"]
    assert abs(sum(boosted["live_overhaul"].values()) - 100.0) < 1e-6


# --- Simulated legacy honours level gates + Starter clamp -------------------


def test_simulated_legacy_level_gates(sim_env):
    slider_state = {
        "trainer_level": 5,
        "dex_completion": 10.0,
        "reviews_done": 90,
        "daily_goal": 100,
        "avg_cp": 500,
        "main_level": 10,  # below every rare-tier threshold
    }
    result = _calc(slider_state, sim_env.db)
    legacy = result["legacy"]
    for gated in ("Starter", "Ultra", "Legendary", "Mythical", "Mega", "Gmax"):
        assert legacy.get(gated, 0) == 0
    assert abs(sum(legacy.values()) - 100.0) < 0.001


# --- get_initial_state returns a valid JS bootstrap payload -----------------


def test_get_initial_state_payload(sim_env):
    bridge = esd.SimulatorBridge(None)
    state = json.loads(bridge.get_initial_state())

    for key in (
        "trainer_level",
        "dex_completion",
        "reviews_done",
        "daily_goal",
        "avg_cp",
        "main_level",
        "config",
        "active_system",
    ):
        assert key in state

    assert state["trainer_level"] == 20  # from services.trainer_card.level
    assert state["reviews_done"] == 100  # from services.tracker
    assert state["active_system"] in ("Overhaul", "Legacy")

    cfg = state["config"]
    assert cfg["trainer_level_cap"] == ef.TRAINER_LEVEL_CAP
    assert cfg["core_team_power_cap"] == ef.CORE_TEAM_POWER_CAP
    assert cfg["pity_divisor"] == ef.OVERHAUL_PITY_DIVISOR
    assert cfg["level_thresholds"] == ef.OVERHAUL_LEVEL_THRESHOLDS


# --- Offscreen Qt construct-smoke (skipped without QtWebEngine) -------------
#
# Constructing a real QWebEngineView spins up QtWebEngine's Chromium process,
# which does not tear down cleanly at a normal Python/pytest exit (it hangs the
# interpreter). We therefore run the construction in a throw-away subprocess
# that ``os._exit(0)``s on success, so this real Qt smoke can never hang the
# test runner. Skipped when QtWebEngine is unavailable (the Tier-1 env).

_CONSTRUCT_SCRIPT = r"""
import os, sys, types
import unittest.mock as mock
import importlib.util
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    # QtWebEngine must be imported before the QApplication is created.
    from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
    from PyQt6.QtWebChannel import QWebChannel  # noqa: F401
    from PyQt6.QtWidgets import QApplication
except Exception:
    print("NO_QTWEBENGINE", flush=True)
    os._exit(0)

SRC = Path(sys.argv[1])
for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj"):
    _m = types.ModuleType(_pkg)
    _m.__path__ = [str(SRC / _pkg.replace(".", "/"))]
    _m.__package__ = _pkg
    sys.modules[_pkg] = _m
# The dialog's __init__ touches only Qt; mock its aqt/logic deps.
for _name in (
    "aqt", "aqt.qt", "aqt.utils",
    "Ankimon.services",
    "Ankimon.functions.encounter_functions",
    "Ankimon.business",
    "Ankimon.functions.pokedex_functions",
):
    sys.modules[_name] = mock.MagicMock()

_spec = importlib.util.spec_from_file_location(
    "Ankimon.pyobj.encounter_simulator_dialog",
    SRC / "Ankimon" / "pyobj" / "encounter_simulator_dialog.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod
_spec.loader.exec_module(_mod)

# A non-empty argv is required or QtWebEngine's Chromium CommandLine init
# hangs ("the program name is not passed to QCoreApplication").
app = QApplication.instance() or QApplication(["ankimon"])
dialog = _mod.EncounterSimulatorDialog()
assert dialog.webview is not None
assert dialog.bridge is not None
assert dialog.windowTitle() == "Ankimon Encounter Rate Simulator"
print("CONSTRUCT_OK", flush=True)
os._exit(0)
"""


def test_dialog_constructs_offscreen():
    # Run entirely in a child process: importing PyQt6 in this (Tier-1) parent
    # would segfault it at teardown without a QApplication, and constructing a
    # real QWebEngineView never tears down cleanly under a normal interpreter
    # exit. The child reports availability itself so the parent never imports Qt.
    import os
    import subprocess

    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env.setdefault(
        "QTWEBENGINE_CHROMIUM_FLAGS",
        "--no-sandbox --disable-gpu --disable-software-rasterizer",
    )
    env["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

    proc = subprocess.run(
        [sys.executable, "-c", _CONSTRUCT_SCRIPT, str(_SRC)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        stdin=subprocess.DEVNULL,
        start_new_session=True,  # isolate QtWebEngine's Chromium helper processes
    )
    detail = f"rc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
    if "NO_QTWEBENGINE" in proc.stdout:
        pytest.skip("QtWebEngine unavailable (Tier-1 env)")
    assert "CONSTRUCT_OK" in proc.stdout, detail

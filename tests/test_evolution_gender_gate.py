"""Tests for gender-gated item evolutions and CSV helper hygiene.

Covers two same-class findings discovered while reviewing PRs #785/#744/#706
(evolution requirements carried by the bundled data but ignored by the code):

* ``check_evolution_by_item`` now honors the ``gender_id`` column of
  ``pokemon_evolution.csv`` when the caller supplies a gender: Gallade (475)
  requires a male Kirlia, Froslass (478) a female Snorunt/Kirlia. Without a
  gender argument the historical no-check behavior is preserved.
* ``rows_for_key_in_table`` was defined twice in pokedex_functions.py; the
  second definition shadowed the first, so only one may exist.

Loading strategy mirrors ``tests/test_move_evo_timing.py``: stub Anki/aqt,
load ``resources`` + ``pokedex_functions`` FOR REAL so the bundled data drives
every lookup.
"""

import importlib.util
import sys
import unittest.mock as mock
from pathlib import Path

import pytest

_SRC = Path(__file__).parent.parent / "src"


class _FakeSettings:
    """Minimal stand-in for ``settings_obj`` backed by a mutable dict."""

    def __init__(self):
        self.values = {"misc.active_region": None}

    def get(self, key, default=None):
        return self.values.get(key, default)


def _load_pf():
    sys.modules["aqt"] = mock.MagicMock()
    sys.modules["aqt.qt"] = mock.MagicMock()
    sys.modules["aqt.utils"] = mock.MagicMock()
    sys.modules["Ankimon.pyobj.error_handler"] = mock.MagicMock()

    fake_settings = _FakeSettings()
    singletons_stub = importlib.util.module_from_spec(
        importlib.util.spec_from_loader("Ankimon.singletons", loader=None)
    )
    singletons_stub.settings_obj = fake_settings
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
    return pokedex_functions


pf = _load_pf()

_SINGLETONS_STUB = sys.modules["Ankimon.singletons"]
_POKEDEX_FUNCTIONS_STUB = sys.modules["Ankimon.functions.pokedex_functions"]

# Dawn Stone item id from items.csv (Kirlia -> Gallade/Froslass).
_DAWN_STONE_ID = 109


@pytest.fixture(autouse=True)
def _reset_env():
    sys.modules["Ankimon.singletons"] = _SINGLETONS_STUB
    sys.modules["Ankimon.functions.pokedex_functions"] = (
        _POKEDEX_FUNCTIONS_STUB
    )
    yield


# --------------------------------------------------------------------------- #
# Gender-gated useItem evolutions (Kirlia 281 -> Gallade 475 / Froslass 478)
# --------------------------------------------------------------------------- #
def test_dawn_stone_on_male_kirlia_gives_gallade():
    assert (
        pf.check_evolution_by_item(281, _DAWN_STONE_ID, gender="Male") == 475
    )


def test_dawn_stone_on_female_snorunt_gives_froslass():
    # Froslass (478) evolves only from a FEMALE Snorunt (361) with a Dawn
    # Stone; the CSV gender gate must make this exact and not leak to males.
    assert pf.check_evolution_by_item(361, _DAWN_STONE_ID, gender="F") == 478


def test_dawn_stone_gender_mismatch_does_not_evolve_to_wrong_species():
    # The core bug: without a gender gate either sex could become Gallade.
    assert pf.check_evolution_by_item(281, _DAWN_STONE_ID, gender="F") != 475
    assert pf.check_evolution_by_item(281, _DAWN_STONE_ID, gender="M") != 478


def test_female_snorunt_with_dawn_stone_gives_froslass():
    # Snorunt (361) has both Glalie (plain level) and Froslass (female +
    # Dawn Stone); only the female form is item-reachable.
    assert pf.check_evolution_by_item(361, _DAWN_STONE_ID, gender="Female") == 478


def test_male_snorunt_with_dawn_stone_gets_no_female_locked_evo():
    assert pf.check_evolution_by_item(361, _DAWN_STONE_ID, gender="M") is None


def test_unknown_gender_preserves_historical_no_check_behavior():
    # Callers without gender data keep working exactly as before.
    result = pf.check_evolution_by_item(281, _DAWN_STONE_ID, gender=None)
    assert result in (475, 478)


def test_junk_gender_values_degrade_to_no_check():
    for junk in ("Genderless", "", "x"):
        result = pf.check_evolution_by_item(281, _DAWN_STONE_ID, gender=junk)
        assert result in (475, 478)


def test_non_gendered_items_unaffected_by_gender_argument():
    # A Thunder Stone on Pikachu must behave identically with or without gender.
    thunder_stone_id = 82
    without = pf.check_evolution_by_item(25, thunder_stone_id)
    for gender in ("M", "F", None):
        assert pf.check_evolution_by_item(25, thunder_stone_id, gender=gender) == without


def test_csv_gender_id_normalization():
    assert pf._csv_gender_id("M") == 2
    assert pf._csv_gender_id("male") == 2
    assert pf._csv_gender_id("F") == 1
    assert pf._csv_gender_id("Female") == 1
    assert pf._csv_gender_id("Genderless") is None
    assert pf._csv_gender_id(None) is None
    assert pf._csv_gender_id(7) is None


def test_rows_for_key_in_table_defined_exactly_once():
    # The helper used to be defined twice (the second shadowing the first);
    # pin the de-duplicated state.
    import inspect

    source = inspect.getsource(pf)
    count = source.count("def rows_for_key_in_table(")
    assert count == 1

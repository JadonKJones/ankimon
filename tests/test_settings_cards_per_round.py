"""Tier-1 regression guard for web-settings cards_per_round coercion.

The legacy QMainWindow settings (pyobj/settings_window.py::on_save) preserves the
PREVIOUS stored value when the user submits non-numeric, non-range garbage for
"Cards per Round". The web settings screen's ``settings_schema`` must match that:
non-dashed garbage keeps the prior value, a *malformed dashed range* still falls
back to 2 (legacy parity), and valid ints/ranges pass through.

``settings_schema`` has no third-party imports, so it loads standalone in the
Qt-free Tier-1 env without any Ankimon/aqt bootstrap.
"""

import importlib.util
from pathlib import Path

import pytest

_SCHEMA = (
    Path(__file__).resolve().parent.parent
    / "src" / "Ankimon" / "ankimon_items_web" / "settings_schema.py"
)


@pytest.fixture(scope="module")
def schema():
    spec = importlib.util.spec_from_file_location("_ankimon_settings_schema", _SCHEMA)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_coerce_preserves_prior_value_on_non_dashed_garbage(schema):
    # Regression: previously returned a hardcoded 2, silently discarding the
    # stored range. Must now preserve the prior value like the legacy window.
    assert schema._coerce_cards_per_round("abc", "1-3") == "1-3"
    assert schema._coerce_cards_per_round("", 4) == 4


def test_coerce_malformed_dashed_range_still_falls_back_to_2(schema):
    # Legacy parity: a dash present but unparseable resets to 2 (not the prior).
    assert schema._coerce_cards_per_round("x-y", "1-3") == 2


def test_coerce_valid_inputs_pass_through(schema):
    assert schema._coerce_cards_per_round("4", "1-3") == 4
    assert schema._coerce_cards_per_round("3-1", "2") == "1-3"  # normalized low-high
    assert schema._coerce_cards_per_round(0, 5) == 1            # 0 -> 1 floor
    assert schema._coerce_cards_per_round(2, 5) == 2


def test_validate_and_clamp_threads_original_snapshot(schema):
    # End-to-end through the public entry point: garbage in the edited config,
    # the pre-edit snapshot supplies the value to preserve.
    original = {"battle.cards_per_round": "1-3"}
    config = {"battle.cards_per_round": "garbage"}
    out, adjustments = schema.validate_and_clamp(config, original)
    assert out["battle.cards_per_round"] == "1-3"


def test_validate_and_clamp_without_snapshot_defaults_to_2(schema):
    # No snapshot passed (back-compat call) → falls back to 2 rather than raising.
    config = {"battle.cards_per_round": "garbage"}
    out, _ = schema.validate_and_clamp(config)
    assert out["battle.cards_per_round"] == 2

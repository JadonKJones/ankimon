"""Characterization tests for the shared MovePickerDialog (inventory row F41).

``pyobj/move_picker.py`` is an exp-only NEW module: a pure-Qt move-selection
dialog shared by three leaves (PC-box move manager, pokemon-details
remember-attack, evolution learn-move). It has no ``aqt.mw``/``services`` usage
at all -- callers pass data in -- so this pins the dialog's OBSERVABLE contract
(rows built from resolvable moves, current-move marking, learn-button state,
selection round-trip, search filtering, and the two custom sort-item ``__lt__``
semantics) against a stubbed data layer.

These need real PyQt6 (a QApplication), so they run in the Qt / Tier-2 env; the
whole module skips cleanly where PyQt6 is absent OR has been mocked in
``sys.modules`` by another (Tier-1) test file -- mirroring
``test_scaffolding_smoke.py``. Run standalone with::

    pytest tests/test_move_picker.py
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

pytest.importorskip("PyQt6")  # Qt env only; skipped in the aqt-free Tier-1 env.


_MODULE_NAME = "Ankimon.pyobj.move_picker"

# Deterministic stub move table for the stubbed ``find_details_move``.
_STUB_MOVES = {
    "tackle": {
        "type": "Normal",
        "category": "Physical",
        "basePower": 40,
        "accuracy": 100,
        "pp": 35,
        "shortDesc": "A physical attack.",
    },
    "thunderbolt": {
        "type": "Electric",
        "category": "Special",
        "basePower": 90,
        "accuracy": 100,
        "pp": 15,
        "shortDesc": "May paralyze the target.",
    },
    "growl": {
        "type": "Normal",
        "category": "Status",
        "basePower": 0,
        "accuracy": True,  # non-int accuracy -> displayed as "---"
        "pp": 40,
        "shortDesc": "Lowers the target's Attack.",
    },
    "swift": {
        "type": "Normal",
        "category": "Special",
        "basePower": 60,
        "accuracy": True,
        "pp": 20,
        "shortDesc": "Never misses.",
    },
}


class _NoIconPath:
    """Stand-in for ``type_icon_path``/``move_category_path`` results.

    The dialog only calls ``.exists()`` before loading an icon; returning False
    keeps the test independent of on-disk sprite assets.
    """

    def exists(self):
        return False


@pytest.fixture(autouse=True)
def _env_guard():
    """Skip gracefully when another test file has mocked PyQt6 in this run.

    Several base test files mock ``PyQt6``/``aqt`` in ``sys.modules``; un-mocking
    a compiled Qt extension mid-process is not reliable, so we skip rather than
    fail when real Qt is not active. Matches ``test_scaffolding_smoke.py``.
    """
    from PyQt6.QtWidgets import QDialog

    if not isinstance(QDialog, type):  # PyQt6 was mocked by another test
        pytest.skip(
            "real PyQt6 not active (mocked by another test); "
            "run tests/test_move_picker.py standalone"
        )

    src = Path(__file__).parent.parent / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    yield


@pytest.fixture
def move_picker(qapp):
    """Load ``move_picker`` in isolation with its three deps stubbed.

    Mirrors the base-suite idiom (see ``test_learnset_retrieval.py``): stub the
    modules the target imports at module level, then load the single file via
    ``spec_from_file_location`` so ``Ankimon/__init__.py`` never runs.
    """
    saved = {
        name: sys.modules.get(name)
        for name in (
            "Ankimon",
            "Ankimon.functions",
            "Ankimon.pyobj",
            "Ankimon.functions.pokedex_functions",
            "Ankimon.functions.gui_functions",
            "Ankimon.utils",
            _MODULE_NAME,
        )
    }
    src = Path(__file__).parent.parent / "src"

    for pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj"):
        mod = types.ModuleType(pkg)
        mod.__path__ = [str(src / pkg.replace(".", "/"))]
        mod.__package__ = pkg
        sys.modules[pkg] = mod

    pf = types.ModuleType("Ankimon.functions.pokedex_functions")
    pf.find_details_move = lambda name: _STUB_MOVES.get(name)
    sys.modules["Ankimon.functions.pokedex_functions"] = pf

    gf = types.ModuleType("Ankimon.functions.gui_functions")
    gf.type_icon_path = lambda t: _NoIconPath()
    gf.move_category_path = lambda c: _NoIconPath()
    sys.modules["Ankimon.functions.gui_functions"] = gf

    ut = types.ModuleType("Ankimon.utils")
    ut.format_move_name = lambda s: s.replace("-", " ").title()
    sys.modules["Ankimon.utils"] = ut

    spec = importlib.util.spec_from_file_location(
        _MODULE_NAME, src / "Ankimon" / "pyobj" / "move_picker.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module
    spec.loader.exec_module(module)

    try:
        yield module
    finally:
        for name, val in saved.items():
            if val is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = val


def _rows_by_userrole(dialog):
    """Map each visible row's stored move key (UserRole) -> row index."""
    from PyQt6.QtCore import Qt

    out = {}
    for row in range(dialog.table.rowCount()):
        item = dialog.table.item(row, 0)
        out[item.data(Qt.ItemDataRole.UserRole)] = row
    return out


def test_only_resolvable_moves_become_rows(move_picker):
    dialog = move_picker.MovePickerDialog(
        "Pikachu",
        all_moves=["tackle", "thunderbolt", "growl", "does-not-exist"],
        current_moves=["tackle"],
    )
    # "does-not-exist" has no move data -> skipped by ``if not move: continue``.
    assert set(_rows_by_userrole(dialog)) == {"tackle", "thunderbolt", "growl"}


def test_current_move_is_marked(move_picker):
    dialog = move_picker.MovePickerDialog(
        "Pikachu",
        all_moves=["tackle", "thunderbolt"],
        current_moves=["tackle"],
    )
    rows = _rows_by_userrole(dialog)
    known_text = dialog.table.item(rows["tackle"], 0).text()
    unknown_text = dialog.table.item(rows["thunderbolt"], 0).text()
    assert "●" in known_text  # known move gets the ● badge
    assert "●" not in unknown_text


def test_learn_button_starts_disabled(move_picker):
    dialog = move_picker.MovePickerDialog(
        "Pikachu", all_moves=["thunderbolt"], current_moves=[]
    )
    assert dialog.learn_btn.isEnabled() is False


def test_button_state_tracks_selection(move_picker):
    dialog = move_picker.MovePickerDialog(
        "Pikachu",
        all_moves=["tackle", "thunderbolt"],
        current_moves=["tackle"],
    )
    rows = _rows_by_userrole(dialog)

    dialog.table.selectRow(rows["tackle"])  # already known
    assert dialog.learn_btn.isEnabled() is False
    assert dialog.learn_btn.text() == "Already Known"

    dialog.table.selectRow(rows["thunderbolt"])  # learnable
    assert dialog.learn_btn.isEnabled() is True
    assert dialog.learn_btn.text() == "Learn Move"
    assert dialog.get_selected_move() == "thunderbolt"


def test_search_filter_narrows_rows(move_picker):
    dialog = move_picker.MovePickerDialog(
        "Pikachu",
        all_moves=["tackle", "thunderbolt", "growl"],
        current_moves=[],
    )
    assert dialog.table.rowCount() == 3

    dialog.filter_moves("thunder")
    assert set(_rows_by_userrole(dialog)) == {"thunderbolt"}

    dialog.filter_moves("")  # cleared -> all resolvable rows return
    assert dialog.table.rowCount() == 3


def test_force_show_current_toggles_extra_row(move_picker):
    with_current = move_picker.MovePickerDialog(
        "Eevee",
        all_moves=["tackle"],
        current_moves=["swift"],
        force_show_current=True,
    )
    assert set(_rows_by_userrole(with_current)) == {"tackle", "swift"}

    without_current = move_picker.MovePickerDialog(
        "Eevee",
        all_moves=["tackle"],
        current_moves=["swift"],
        force_show_current=False,
    )
    assert set(_rows_by_userrole(without_current)) == {"tackle"}


def test_numeric_item_sort_semantics(move_picker):
    numeric = move_picker.NumericTableWidgetItem
    # placeholder tokens collapse to 0, then numeric comparison
    assert (numeric("--") < numeric("40")) is True
    assert (numeric("90") < numeric("40")) is False
    assert (numeric("---") < numeric("5")) is True
    # non-numeric text falls back to the default (string) comparison
    assert (numeric("abc") < numeric("bcd")) == ("abc" < "bcd")


def test_icon_item_sorts_by_lowercased_tooltip(move_picker):
    icon_item = move_picker.SortableIconTableWidgetItem
    electric = icon_item("")
    electric.setToolTip("Electric")
    normal = icon_item("")
    normal.setToolTip("normal")
    # case-insensitive: "electric" < "normal"
    assert (electric < normal) is True
    assert (normal < electric) is False

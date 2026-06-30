import sys
import unittest.mock as mock
import pytest
import types
import importlib.util
from pathlib import Path

_SRC = Path(__file__).parent.parent / "src"

def setup_test_mocks():
    # Mock aqt/anki namespaces
    for name in [
        "aqt", "aqt.utils", "aqt.gui_hooks", "aqt.operations",
        "aqt.reviewer", "aqt.webview", "aqt.main", "aqt.operations.QueryOp",
        "aqt.theme", "aqt.theme.theme_manager",
        "anki", "anki.hooks", "anki.collection", "anki.models", "anki.notes", "anki.template", "anki.buildinfo"
    ]:
        if name not in sys.modules or isinstance(sys.modules[name], mock.MagicMock):
            sys.modules[name] = mock.MagicMock()

    # Stub aqt.qt with pure Python mock objects/classes so NO C++ Qt code runs and we avoid C++ segfaults
    class DummyClass(object):
        def __init__(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            return mock.MagicMock()

    class AqtQtModule(types.ModuleType):
        def __getattr__(self, name):
            if name == "Qt":
                return mock.MagicMock()
            elif name == "qconnect":
                return lambda signal, slot: signal.connect(slot)
            elif name == "sip":
                return mock.MagicMock()
            return DummyClass

    m = AqtQtModule("aqt.qt")
    sys.modules["aqt.qt"] = m

    # Stub parent packages so relative imports resolve without loading __init__.py
    for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj"):
        if _pkg not in sys.modules or isinstance(sys.modules[_pkg], mock.MagicMock):
            _mod = types.ModuleType(_pkg)
            _mod.__path__ = [str(_SRC / _pkg.replace(".", "/"))]
            _mod.__package__ = _pkg
            sys.modules[_pkg] = _mod

    sys.modules["Ankimon.singletons"] = mock.MagicMock()
    sys.modules["Ankimon.pyobj.error_handler"] = mock.MagicMock()
    sys.modules["Ankimon.gui_classes.pokemon_details"] = mock.MagicMock()

def force_load_module(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def test_integrate_move_manager_removes_evolution_button():
    setup_test_mocks()

    # Create QApplication first to allow QWidget instantiation without crashing
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # Force load pc_box to bypass mock pollution from other test runs
    pc_box_mod = force_load_module("Ankimon.pyobj.pc_box", _SRC / "Ankimon" / "pyobj" / "pc_box.py")
    PokemonPC = pc_box_mod.PokemonPC

    # Create mock PC box instance
    pc = mock.MagicMock()
    # Pass None as details_widget parent to satisfy QWidget argument type check
    pc.details_widget = None

    # Mock the layout structure
    h_widget = mock.MagicMock()
    pc.header_stack.currentWidget.return_value = h_widget

    h_layout = mock.MagicMock()
    h_widget.layout.return_value = h_layout
    h_layout.count.return_value = 2

    first_layout_item = mock.MagicMock()
    first_layout = mock.MagicMock()
    first_layout_item.layout.return_value = first_layout
    h_layout.itemAt.return_value = first_layout_item

    top_r_item = mock.MagicMock()
    top_r_widget = mock.MagicMock()
    top_r_item.widget.return_value = top_r_widget
    first_layout.itemAt.return_value = top_r_item

    top_r_layout = mock.MagicMock()
    top_r_widget.layout.return_value = top_r_layout

    # Set up items in top_r_layout
    # We want one item to be the evolveNowButton
    evo_btn_widget = mock.MagicMock()
    evo_btn_widget.objectName.return_value = "evolveNowButton"

    layout_item_evo = mock.MagicMock()
    layout_item_evo.widget.return_value = evo_btn_widget

    other_widget = mock.MagicMock()
    other_widget.objectName.return_value = "otherButton"
    layout_item_other = mock.MagicMock()
    layout_item_other.widget.return_value = other_widget

    items = [layout_item_other, layout_item_evo]
    top_r_layout.count.return_value = len(items)
    top_r_layout.itemAt.side_effect = lambda idx: items[idx]

    # Mock MoveManagerWidget
    sys.modules["Ankimon.gui_classes.pokemon_details"].MoveManagerWidget = mock.MagicMock()

    pokemon = {
        "individual_id": "test-uuid-123",
        "id": 790,
        "name": "Cosmoem",
    }

    # Call the method directly from the class
    PokemonPC._integrate_move_manager(pc, pokemon)

    # Verify that removeWidget was called with evo_btn_widget
    top_r_layout.removeWidget.assert_called_once_with(evo_btn_widget)

    # Verify addWidget order: move_manager then evo_btn
    add_calls = top_r_layout.addWidget.call_args_list
    assert len(add_calls) >= 2
    # The last call should be for the evolution button
    assert add_calls[-1][0][0] == evo_btn_widget

if __name__ == "__main__":
    test_integrate_move_manager_removes_evolution_button()
    print("Test passed successfully!")

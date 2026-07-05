"""Qt characterization tests for the F43 additions to ``gui_entities.py``.

Pins the exp-ported behaviour layered onto main's version of the module:

* ``NatureTableWidget`` — the new nature-chart window backed by the real
  ``addon_files/nature_chart.html`` asset via ``resources.nature_chart_html_path``.
* Lazy initialisation (``initialized``/``loaded`` flags, initUI-on-show) for
  ``TableWidget``/``IDTableWidget``/``License``/``Credits``/``Version_Dialog``
  so eager singleton construction at startup stays cheap.
* ``Pokedex_Widget`` stays present: exp deleted it, but main's ``singletons.py``
  still constructs it, and F43 is not authorized to remove it.

These need real PyQt6 (a QApplication), so they run in the Qt / Tier-2 env; the
whole module skips cleanly where PyQt6 is absent OR has been mocked in
``sys.modules`` by another (Tier-1) test file -- mirroring
``test_move_picker.py``. Run standalone with::

    pytest tests/test_gui_entities_nature_chart.py
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

pytest.importorskip("PyQt6")  # Qt env only; skipped in the aqt-free Tier-1 env.


_MODULE_NAME = "Ankimon.gui_entities"
_SRC = Path(__file__).parent.parent / "src"


@pytest.fixture(autouse=True)
def _env_guard():
    """Skip gracefully when another test file has mocked PyQt6 in this run."""
    from PyQt6.QtWidgets import QDialog

    if not isinstance(QDialog, type):  # PyQt6 was mocked by another test
        pytest.skip(
            "real PyQt6 not active (mocked by another test); "
            "run tests/test_gui_entities_nature_chart.py standalone"
        )

    if str(_SRC) not in sys.path:
        sys.path.insert(0, str(_SRC))
    yield


@pytest.fixture
def gui_entities(qapp):
    """Load ``gui_entities`` in isolation with aqt/utils/texts stubbed.

    ``Ankimon.resources`` is the REAL module so the widgets read the real
    shipped HTML assets (nature_chart.html, eff chart, license, credits).
    """
    saved = {
        name: sys.modules.get(name)
        for name in (
            "Ankimon",
            "Ankimon.pyobj",
            "Ankimon.pyobj.error_handler",
            "Ankimon.resources",
            "Ankimon.texts",
            "Ankimon.utils",
            "aqt",
            "aqt.qt",
            "aqt.utils",
            "markdown",
            _MODULE_NAME,
        )
    }

    from PyQt6.QtWidgets import QDialog

    for pkg in ("Ankimon", "Ankimon.pyobj"):
        mod = types.ModuleType(pkg)
        mod.__path__ = [str(_SRC / pkg.replace(".", "/"))]
        mod.__package__ = pkg
        sys.modules[pkg] = mod

    # aqt stub: gui_entities only needs mw (as an error-dialog parent),
    # QDialog/qconnect and the three notification helpers.
    aqt_mod = types.ModuleType("aqt")
    aqt_mod.mw = None
    aqt_qt = types.ModuleType("aqt.qt")
    aqt_qt.QDialog = QDialog
    aqt_qt.qconnect = lambda signal, func: signal.connect(func)
    aqt_utils = types.ModuleType("aqt.utils")
    aqt_utils.showWarning = lambda *a, **k: None
    aqt_utils.showInfo = lambda *a, **k: None
    aqt_utils.tooltip = lambda *a, **k: None
    aqt_mod.qt = aqt_qt
    aqt_mod.utils = aqt_utils
    sys.modules["aqt"] = aqt_mod
    sys.modules["aqt.qt"] = aqt_qt
    sys.modules["aqt.utils"] = aqt_utils

    md = types.ModuleType("markdown")
    md.markdown = lambda text: f"<p>{text}</p>"
    sys.modules["markdown"] = md

    # Real resources module (aqt-free) so asset paths are the shipped ones.
    spec = importlib.util.spec_from_file_location(
        "Ankimon.resources", _SRC / "Ankimon" / "resources.py"
    )
    resources = importlib.util.module_from_spec(spec)
    sys.modules["Ankimon.resources"] = resources
    spec.loader.exec_module(resources)

    texts = types.ModuleType("Ankimon.texts")
    texts.terms_text = "terms"
    texts.pokedex_html_template = "<!-- Table Rows Will Go Here -->"
    sys.modules["Ankimon.texts"] = texts

    ut = types.ModuleType("Ankimon.utils")

    def read_html_file(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def read_local_file(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    ut.read_html_file = read_html_file
    ut.read_local_file = read_local_file
    ut.read_github_file = lambda url: None
    ut.compare_files = lambda a, b: a == b
    ut.write_local_file = lambda path, content: None
    sys.modules["Ankimon.utils"] = ut

    eh = types.ModuleType("Ankimon.pyobj.error_handler")

    def _raise(parent=None, exception=None, message=""):
        raise AssertionError(f"show_warning_with_traceback called: {message}") from (
            exception
        )

    eh.show_warning_with_traceback = _raise
    sys.modules["Ankimon.pyobj.error_handler"] = eh

    spec = importlib.util.spec_from_file_location(
        _MODULE_NAME, _SRC / "Ankimon" / "gui_entities.py"
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


def _label_texts(widget):
    from PyQt6.QtWidgets import QLabel

    return [lbl.text() for lbl in widget.findChildren(QLabel)]


def test_nature_table_widget_is_lazy_and_renders_the_real_asset(gui_entities):
    w = gui_entities.NatureTableWidget()
    assert w.initialized is False
    assert w.layout() is None  # nothing built at construction time

    w.show_nature_chart()
    try:
        assert w.initialized is True
        assert w.windowTitle() == "Pokémon Nature Chart"
        texts = " ".join(_label_texts(w))
        # Real addon_files/nature_chart.html content reached the label.
        assert "Adamant" in texts
        assert "Boosted Stat (+10%)" in texts
    finally:
        w.close()

    # Second show must not rebuild the UI (single scroll area child).
    from PyQt6.QtWidgets import QScrollArea

    w.show_nature_chart()
    try:
        assert len(w.findChildren(QScrollArea)) == 1
    finally:
        w.close()


def test_eff_and_gen_chart_widgets_init_lazily(gui_entities):
    eff = gui_entities.TableWidget()
    gen = gui_entities.IDTableWidget()
    assert eff.initialized is False
    assert gen.initialized is False

    eff.show_eff_chart()
    gen.show_gen_chart()
    try:
        assert eff.initialized is True
        assert eff.windowTitle() == "Pokémon Type Effectiveness Table"
        assert gen.initialized is True
        assert gen.windowTitle() == "Pokémon - Generations and ID"
    finally:
        eff.close()
        gen.close()


def test_license_and_credits_init_lazily(gui_entities):
    lic = gui_entities.License()
    cred = gui_entities.Credits()
    assert lic.initialized is False
    assert cred.initialized is False

    lic.show_window()
    cred.show_window()
    try:
        assert lic.initialized is True
        assert cred.initialized is True
    finally:
        lic.close()
        cred.close()


def test_version_dialog_defers_reading_updateinfos(gui_entities):
    dlg = gui_entities.Version_Dialog()
    # Construction must not read/convert updateinfos.md (the file is only
    # written at runtime by changelog.py; eager markdown(None) used to crash).
    assert dlg.loaded is False
    assert dlg.text_browser.toPlainText() == ""
    assert not hasattr(dlg, "local_content")


def test_pokedex_widget_still_exists_for_singletons(gui_entities):
    # exp deleted Pokedex_Widget, but main's singletons.py still constructs it;
    # F43 keeps it (removal belongs to the Ankidex row).
    assert hasattr(gui_entities, "Pokedex_Widget")

"""Characterization test for ``Translator.change_language()`` (feature F02).

Pins the observable contract of the live-language-reload helper ported from
BRRRR_Experimental onto main's ``pyobj/translator.py``:

* ``change_language(n)`` re-points ``self.filepath`` to the ``LANG_PATHS`` entry
  for ``LANG_NUMBERS[int(n)]`` and reloads ``self.translations`` from that file.
* An unknown language id falls back to English (``lang_path_en``).
* Any error — an unparsable id (non-numeric / ``None``) or a load failure — is
  swallowed (printed, not raised) and the previous language is kept, so a bad
  language setting can never crash the caller.

``translator.py`` is aqt-free (pure file I/O + ``json.load``), so it runs in the
Qt-free Tier-1 env. It is loaded here under a *private* module namespace
(``_f02_ankimon``) rather than the shared ``Ankimon.*`` names, because sibling
test modules (``test_encounter_functions``, ``test_cp_formula``) replace
``Ankimon.pyobj.translator`` / ``Ankimon.resources`` in ``sys.modules`` with
MagicMocks. The private namespace makes this test order-independent.
"""

import importlib.util
import json
import sys
import types
from pathlib import Path

_ANK = Path(__file__).parent.parent / "src" / "Ankimon"
_PKG = "_f02_ankimon"


def _ensure_pkg(name, path):
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(path)]
        mod.__package__ = name
        sys.modules[name] = mod


def _load(modname, filepath, package):
    spec = importlib.util.spec_from_file_location(modname, filepath)
    module = importlib.util.module_from_spec(spec)
    module.__package__ = package
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module


_ensure_pkg(_PKG, _ANK)
_ensure_pkg(_PKG + ".pyobj", _ANK / "pyobj")
_resources = _load(_PKG + ".resources", _ANK / "resources.py", _PKG)
_translator = _load(
    _PKG + ".pyobj.translator", _ANK / "pyobj" / "translator.py", _PKG + ".pyobj"
)

Translator = _translator.Translator
LANG_PATHS = _translator.LANG_PATHS
lang_path_en = _resources.lang_path_en
lang_path_de = _resources.lang_path_de


def test_change_language_switches_filepath_and_reloads_translations():
    t = Translator(9)  # English
    assert t.filepath == lang_path_en

    t.change_language(6)  # German
    assert t.filepath == LANG_PATHS["de"] == lang_path_de

    with open(lang_path_de, "r", encoding="utf-8") as f:
        expected = json.load(f)
    assert t.translations == expected


def test_change_language_round_trip_restores_english():
    t = Translator(9)
    original = dict(t.translations)
    t.change_language(6)
    assert t.translations != original
    t.change_language(9)
    assert t.filepath == lang_path_en
    assert t.translations == original


def test_change_language_unknown_id_falls_back_to_english():
    t = Translator(6)  # German
    t.change_language(999)  # id not in LANG_NUMBERS -> "en"
    assert t.filepath == lang_path_en


def test_change_language_accepts_string_numeric_like_init():
    t = Translator(9)
    t.change_language("6")  # int() coercion, mirroring __init__
    assert t.filepath == LANG_PATHS["de"]


def test_change_language_swallows_load_error(monkeypatch, capsys):
    t = Translator(9)
    before_filepath = t.filepath
    before_translations = t.translations

    def _boom(*args, **kwargs):
        raise OSError("simulated read failure")

    monkeypatch.setattr("builtins.open", _boom)
    # Must not raise even though the reload open() fails, and the previous
    # language must stay fully intact (no torn filepath/translations state).
    t.change_language(6)
    assert t.filepath == before_filepath
    assert t.translations is before_translations
    out = capsys.readouterr().out
    assert "Error reloading language" in out


def test_change_language_swallows_non_numeric_input(capsys):
    t = Translator(9)
    before_filepath = t.filepath
    before_translations = t.translations

    # Must not raise; the previous language must stay intact.
    t.change_language("not-a-number")
    assert t.filepath == before_filepath
    assert t.translations is before_translations
    assert "Error reloading language" in capsys.readouterr().out


def test_change_language_swallows_none_input(capsys):
    t = Translator(9)
    before_filepath = t.filepath
    before_translations = t.translations

    # Must not raise; the previous language must stay intact.
    t.change_language(None)
    assert t.filepath == before_filepath
    assert t.translations is before_translations
    assert "Error reloading language" in capsys.readouterr().out

"""Shared test configuration.

Stub the Ankimon package in sys.modules so that individual submodules can be
imported without triggering Ankimon/__init__.py, which depends on Anki internals.
"""

import sys
import types
from pathlib import Path

_src = Path(__file__).parent.parent / "src"

import unittest.mock as mock

class ParentlessMock(mock.MagicMock):
    def _get_child_mock(self, **kw):
        child = ParentlessMock(**kw)
        child._mock_parent = None
        return child

_GLOBAL_MW = ParentlessMock()

# Setup permanent parent mock instances for aqt and anki to ensure stable import-time references
_PERMANENT_AQT = sys.modules.get("aqt")
if not isinstance(_PERMANENT_AQT, ParentlessMock):
    _PERMANENT_AQT = ParentlessMock()
    _PERMANENT_AQT.mw = _GLOBAL_MW
sys.modules["aqt"] = _PERMANENT_AQT
sys.modules["aqt.mw"] = _GLOBAL_MW

_PERMANENT_AQT_QT = sys.modules.get("aqt.qt")
if _PERMANENT_AQT_QT is None:
    _PERMANENT_AQT_QT = ParentlessMock()
    import PyQt6.QtWidgets
    import PyQt6.QtCore
    import PyQt6.QtGui
    for module in [PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui]:
        for name in dir(module):
            if name.startswith("Q") or name == "Qt":
                try:
                    setattr(_PERMANENT_AQT_QT, name, getattr(module, name))
                except Exception:
                    pass
    sys.modules["aqt.qt"] = _PERMANENT_AQT_QT
    sys.modules["aqt"].qt = _PERMANENT_AQT_QT

_PERMANENT_ANKI = sys.modules.get("anki")
if not isinstance(_PERENT_ANKI if "_PERENT_ANKI" in globals() else _PERMANENT_ANKI, ParentlessMock):
    _PERMANENT_ANKI = ParentlessMock()
sys.modules["anki"] = _PERMANENT_ANKI

# Stub parent packages so relative imports resolve without loading __init__.py
for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj", "Ankimon.ankimon_items_web"):
    if _pkg not in sys.modules:
        _mod = types.ModuleType(_pkg)
        _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
        _mod.__package__ = _pkg
        sys.modules[_pkg] = _mod

import pytest

def pytest_runtest_logreport(report):
    if report.failed:
        import sys
        import os
        print("\n=== TEST FAILED INTERCEPTED ===", file=sys.stderr)
        print(report.longrepr, file=sys.stderr)
        sys.stderr.flush()
        os._exit(1)


@pytest.fixture(autouse=True)
def restore_package_stubs():
    from unittest.mock import Mock
    
    def do_restore():
        from unittest.mock import Mock, MagicMock
        # Remove globally mocked Ankimon submodules to avoid test pollution
        for name in list(sys.modules.keys()):
            if name.startswith("Ankimon.") or name.startswith("src.Ankimon."):
                mod = sys.modules.get(name)
                if mod is None or isinstance(mod, (Mock, MagicMock)) or not isinstance(mod, types.ModuleType):
                    if name not in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj", "Ankimon.ankimon_items_web"):
                        sys.modules.pop(name, None)

        # Explicitly remove encounter_functions to reload it fresh and prevent import mock poisoning
        sys.modules.pop("Ankimon.functions.encounter_functions", None)
        sys.modules.pop("src.Ankimon.functions.encounter_functions", None)


        # Restore encounter system flag and ServiceProxy objects to avoid leakage
        for suffix in ("Ankimon.functions.encounter_functions", "src.Ankimon.functions.encounter_functions"):
            ef_mod = sys.modules.get(suffix)
            if ef_mod is not None:
                ef_mod.USE_OVERHAUL_ENCOUNTER_SYSTEM = False

                ServiceProxy = getattr(ef_mod, "ServiceProxy", None)
                if ServiceProxy is not None:
                    ef_mod.main_pokemon = ServiceProxy("main_pokemon", "main_pokemon")
                    ef_mod.ankimon_tracker_obj = ServiceProxy("tracker", "ankimon_tracker_obj")
                    ef_mod.trainer_card = ServiceProxy("trainer_card", "trainer_card")
                    ef_mod.settings_obj = ServiceProxy("settings", "settings_obj")
                    ef_mod.translator = ServiceProxy("translator", "translator")
                    ef_mod.ankimon_db = ServiceProxy("db", "ankimon_db")
                    ef_mod.pokemon_pc = ServiceProxy("pokemon_pc", "pokemon_pc")

        # Remove globally mocked aqt and anki submodules to avoid mock leakage (keeping permanent parent modules)
        for name in list(sys.modules.keys()):
            if (name.startswith("aqt.") and name not in ("aqt.mw", "aqt.qt")) or name.startswith("anki."):
                mod = sys.modules[name]
                if isinstance(mod, (Mock, MagicMock, ParentlessMock)) or type(mod).__name__ in ("AqtQtModule", "DummyClass") or getattr(mod, "__class__", None).__name__ == "DummyClass" or not isinstance(mod, types.ModuleType):
                    del sys.modules[name]

        # Re-populate clean ParentlessMocks for aqt and anki submodules
        for name in [
            "aqt.utils", "aqt.gui_hooks", "aqt.operations", 
            "aqt.reviewer", "aqt.webview", "aqt.main", "aqt.theme", "aqt.sound",
            "anki.hooks", "anki.collection", "anki.models", "anki.notes", "anki.template", "anki.buildinfo"
        ]:
            if name not in sys.modules:
                sys.modules[name] = ParentlessMock()

        # Wire permanent mock references on parent aqt module
        sys.modules["aqt.qt"] = _PERMANENT_AQT_QT
        sys.modules["aqt"] = _PERMANENT_AQT
        sys.modules["anki"] = _PERMANENT_ANKI
        sys.modules["aqt.mw"] = _GLOBAL_MW
        sys.modules["aqt"].mw = _GLOBAL_MW
        sys.modules["aqt"].qt = _PERMANENT_AQT_QT

        # Safely reset parent mocks and persistent mw to keep reference identity without corrupting children
        _GLOBAL_MW.reset_mock(return_value=True, side_effect=True)
        sys.modules["aqt"].reset_mock(return_value=True, side_effect=True)
        sys.modules["aqt.qt"].reset_mock(return_value=True, side_effect=True)
        sys.modules["anki"].reset_mock(return_value=True, side_effect=True)

        # Clear custom attributes of permanent mocks safely without touching _mock_children or standard mock attributes
        MOCK_PROTECTED = {"method_calls", "mock_calls", "called", "call_count", "call_args", "call_args_list", "return_value", "side_effect", "reset_mock", "configure_mock"}
        for attr in list(_GLOBAL_MW.__dict__.keys()):
            if not attr.startswith("_") and attr not in MOCK_PROTECTED:
                _GLOBAL_MW.__dict__.pop(attr, None)
        for attr in list(sys.modules["aqt"].__dict__.keys()):
            if not attr.startswith("_") and attr not in ("mw", "qt") and attr not in MOCK_PROTECTED:
                sys.modules["aqt"].__dict__.pop(attr, None)
        for attr in list(sys.modules["aqt.qt"].__dict__.keys()):
            if not attr.startswith("_") and not attr.startswith("Q") and attr != "Qt" and attr not in MOCK_PROTECTED:
                sys.modules["aqt.qt"].__dict__.pop(attr, None)
        for attr in list(sys.modules["anki"].__dict__.keys()):
            if not attr.startswith("_") and attr not in MOCK_PROTECTED:
                sys.modules["anki"].__dict__.pop(attr, None)

        try:
            services_mod = sys.modules.get("Ankimon.services")
            if services_mod is not None:
                services = getattr(services_mod, "services", None)
                if services is not None:
                    services.reset()
        except Exception:
            pass
        # After each test, restore the stubs if they were replaced by MagicMock/None/etc.
        for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj", "Ankimon.ankimon_items_web"):
            current = sys.modules.get(_pkg)
            if current is None or not hasattr(current, "__path__") or not isinstance(current, types.ModuleType) or isinstance(current, MagicMock):
                _mod = types.ModuleType(_pkg)
                _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
                _mod.__package__ = _pkg
                sys.modules[_pkg] = _mod

        # Link sub-packages and sub-modules to parent packages so attribute access works
        for name, mod in list(sys.modules.items()):
            if name.startswith("Ankimon.") and mod is not None:
                parts = name.split(".")
                parent_name = ".".join(parts[:-1])
                if parent_name in sys.modules and sys.modules[parent_name] is not None:
                    # Avoid setting attribute on MagicMock that might cause infinite mock recursion
                    from unittest.mock import Mock
                    if not isinstance(sys.modules[parent_name], Mock):
                        setattr(sys.modules[parent_name], parts[-1], mod)

        from unittest.mock import Mock
        # Also restore Ankimon.resources to the real resources module if it was mocked with tmp paths
        current_res = sys.modules.get("Ankimon.resources")
        if current_res is None or isinstance(current_res, (Mock, ParentlessMock)) or not isinstance(current_res, types.ModuleType):
            try:
                import importlib
                importlib.import_module("Ankimon.resources")
            except Exception:
                pass
        
        current_res = sys.modules.get("Ankimon.resources")
        if (
            current_res is None
            or not isinstance(current_res, types.ModuleType)
            or isinstance(current_res, Mock)
            or type(current_res).__name__ == "MockModule"
            or not hasattr(current_res, "pokedex_path")
            or "tmp" in str(getattr(current_res, "pokedex_path", ""))
            or getattr(current_res, "pokedex_path", "") == "dummy"
        ):
            import importlib.util
            res_spec = importlib.util.spec_from_file_location(
                "Ankimon.resources", _src / "Ankimon" / "resources.py"
            )
            resources = importlib.util.module_from_spec(res_spec)
            sys.modules["Ankimon.resources"] = resources
            try:
                res_spec.loader.exec_module(resources)
            except Exception:
                pass

        # Also restore Ankimon.utils if it is a Mock/MockModule or partially loaded
        current_utils = sys.modules.get("Ankimon.utils")
        if (
            current_utils is None
            or isinstance(current_utils, Mock)
            or type(current_utils).__name__ == "MockModule"
            or not hasattr(current_utils, "random_battle_scene")
        ):
            import importlib.util
            utils_spec = importlib.util.spec_from_file_location(
                "Ankimon.utils", _src / "Ankimon" / "utils.py"
            )
            utils_mod = importlib.util.module_from_spec(utils_spec)
            sys.modules["Ankimon.utils"] = utils_mod
            try:
                utils_spec.loader.exec_module(utils_mod)
            except Exception as e:
                print(f"CONFTEST UTILS EXCEPTION: {e}")

        # Also restore Ankimon.services if it is None or a Mock/MockModule
        current_serv = sys.modules.get("Ankimon.services")
        if (
            current_serv is None
            or isinstance(current_serv, Mock)
            or type(current_serv).__name__ == "MockModule"
            or not hasattr(current_serv, "services")
        ):
            import importlib.util
            serv_spec = importlib.util.spec_from_file_location(
                "Ankimon.services", _src / "Ankimon" / "services.py"
            )
            serv_mod = importlib.util.module_from_spec(serv_spec)
            sys.modules["Ankimon.services"] = serv_mod
            try:
                serv_spec.loader.exec_module(serv_mod)
            except Exception:
                pass

        # Delete or reset Ankimon.singletons to a clean mock instead of reloading the real module (which crashes in tests)
        current_sing = sys.modules.get("Ankimon.singletons")
        if (
            current_sing is None
            or isinstance(current_sing, Mock)
            or type(current_sing).__name__ == "MockModule"
            or not hasattr(current_sing, "settings_obj")
        ):
            from unittest.mock import MagicMock
            sys.modules["Ankimon.singletons"] = MagicMock()




        try:
            from Ankimon.functions.pokedex_functions import clear_pokedex_caches
            clear_pokedex_caches()
        except Exception:
            pass

        try:
            from Ankimon.business import _load_type_chart
            _load_type_chart.cache_clear()
        except Exception:
            pass

        try:
            from Ankimon.functions.friendship_evolution import get_friendship_evolutions_for_species, get_level_evolutions_for_species
            get_friendship_evolutions_for_species.cache_clear()
            get_level_evolutions_for_species.cache_clear()
        except Exception:
            pass

        # Ensure the real Ankimon.resources is loaded and in sys.modules if it was mocked/deleted/stubbed
        res_mod = sys.modules.get("Ankimon.resources")
        if res_mod is None or isinstance(res_mod, (Mock, ParentlessMock)) or not isinstance(res_mod, types.ModuleType):
            try:
                import importlib
                importlib.import_module("Ankimon.resources")
            except Exception:
                pass

        # Align all already-loaded Ankimon submodules to point back to the restored real resources path attributes
        current_res = sys.modules.get("Ankimon.resources")
        if current_res and not isinstance(current_res, (Mock, ParentlessMock)) and hasattr(current_res, "pokedex_path"):
            for mod_name in list(sys.modules.keys()):
                if mod_name.startswith("Ankimon.") and mod_name != "Ankimon.resources":
                    mod = sys.modules[mod_name]
                    if mod and isinstance(mod, types.ModuleType):
                        for attr in ["effectiveness_chart_file_path", "pokedex_path", "learnsets_path", "csv_file_items", "csv_file_descriptions", "poke_evo_path", "items_path", "badges_path", "mypokemon_path", "mainpokemon_path", "itembag_path", "badgebag_path"]:
                            if hasattr(mod, attr) and hasattr(current_res, attr):
                                setattr(mod, attr, getattr(current_res, attr))

        # Align all loaded Ankimon submodules to use the correct live mw reference
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("Ankimon."):
                mod = sys.modules[mod_name]
                if mod and isinstance(mod, types.ModuleType):
                    if hasattr(mod, "mw"):
                        setattr(mod, "mw", _GLOBAL_MW)

    do_restore()
    yield
    do_restore()




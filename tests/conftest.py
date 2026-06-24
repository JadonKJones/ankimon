"""Shared test configuration.

Stub the Ankimon package in sys.modules so that individual submodules can be
imported without triggering Ankimon/__init__.py, which depends on Anki internals.
"""

import sys
import types
from pathlib import Path

_src = Path(__file__).parent.parent / "src"

# Stub parent packages so relative imports resolve without loading __init__.py
for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj", "Ankimon.ankimon_items_web"):
    if _pkg not in sys.modules:
        _mod = types.ModuleType(_pkg)
        _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
        _mod.__package__ = _pkg
        sys.modules[_pkg] = _mod

import pytest

@pytest.fixture(autouse=True)
def restore_package_stubs():
    from unittest.mock import MagicMock
    
    def do_restore():
        # After each test, restore the stubs if they were replaced by MagicMock/None/etc.
        for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj", "Ankimon.ankimon_items_web"):
            current = sys.modules.get(_pkg)
            if current is None or not hasattr(current, "__path__") or not isinstance(current, types.ModuleType) or isinstance(current, MagicMock):
                _mod = types.ModuleType(_pkg)
                _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
                _mod.__package__ = _pkg
                sys.modules[_pkg] = _mod

        # Link sub-packages to parent packages so attribute access works
        if "Ankimon" in sys.modules:
            for attr in ("functions", "pyobj", "ankimon_items_web"):
                subpkg = f"Ankimon.{attr}"
                if subpkg in sys.modules:
                    setattr(sys.modules["Ankimon"], attr, sys.modules[subpkg])

        # Also restore Ankimon.resources to the real resources module if it was mocked with tmp paths
        current_res = sys.modules.get("Ankimon.resources")
        if (
            current_res is None
            or not isinstance(current_res, types.ModuleType)
            or isinstance(current_res, MagicMock)
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

        # Also restore Ankimon.utils if it is a MagicMock
        current_utils = sys.modules.get("Ankimon.utils")
        if current_utils is None or isinstance(current_utils, MagicMock):
            import importlib.util
            utils_spec = importlib.util.spec_from_file_location(
                "Ankimon.utils", _src / "Ankimon" / "utils.py"
            )
            utils_mod = importlib.util.module_from_spec(utils_spec)
            sys.modules["Ankimon.utils"] = utils_mod
            try:
                utils_spec.loader.exec_module(utils_mod)
            except Exception:
                pass

        # Also restore Ankimon.singletons if it is None or a MagicMock
        current_sing = sys.modules.get("Ankimon.singletons")
        if current_sing is None or isinstance(current_sing, MagicMock):
            import importlib.util
            sing_spec = importlib.util.spec_from_file_location(
                "Ankimon.singletons", _src / "Ankimon" / "singletons.py"
            )
            sing_mod = importlib.util.module_from_spec(sing_spec)
            sys.modules["Ankimon.singletons"] = sing_mod
            try:
                sing_spec.loader.exec_module(sing_mod)
            except Exception:
                pass

    do_restore()
    yield
    do_restore()




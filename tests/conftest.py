"""Shared test configuration.

Stub the Ankimon package in sys.modules so that individual submodules can be
imported without triggering Ankimon/__init__.py, which depends on Anki internals.
"""

import sys
import types
from pathlib import Path

_src = Path(__file__).parent.parent / "src"

# Stub parent packages so relative imports resolve without loading __init__.py
for _pkg in ("Ankimon", "Ankimon.functions"):
    if _pkg not in sys.modules:
        _mod = types.ModuleType(_pkg)
        _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
        _mod.__package__ = _pkg
        sys.modules[_pkg] = _mod

# The encounter-weighting simulations are heavyweight, *unseeded* statistical
# dev tools (one is a bare script with no test functions). They mutate sys.modules
# globally at import time, which pollutes the deterministic unit suite, and their
# random sampling is unsuited to a CI gate. Skip them by default — run manually
# with `pytest tests/encounter_weighting_simulations/`.
collect_ignore_glob = ["encounter_weighting_simulations/*"]

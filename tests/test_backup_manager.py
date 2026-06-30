import os
import sys
import json
import sqlite3
import pytest
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import types

# 1. SETUP CLEAN MOCKS BEFORE ANY IMPORTS
_src = Path(__file__).parent.parent / "src"

def setup_mocks():
    # Mock aqt/anki namespaces
    for name in [
        "aqt", "aqt.qt", "aqt.utils", "aqt.gui_hooks", "aqt.operations",
        "aqt.reviewer", "aqt.webview", "aqt.main", "aqt.operations.QueryOp",
        "anki", "anki.hooks", "anki.collection", "anki.models", "anki.notes", "anki.template", "anki.buildinfo"
    ]:
        if name not in sys.modules:
            sys.modules[name] = MagicMock()

    # Define a robust mock for resources
    class MockResources:
        user_path = Path("/tmp")
        csv_file_items_cost = Path("/tmp/items.csv")
        items_path = Path("/tmp/items.json")
        badges_path = Path("/tmp/badges.json")
        mypokemon_path = Path("/tmp/mypokemon.json")
        mainpokemon_path = Path("/tmp/mainpokemon.json")
        team_pokemon_path = Path("/tmp/team.json")
        def __getattr__(self, name): return Path("/tmp") / name

    # Stub parent packages so relative imports resolve without loading __init__.py
    if "Ankimon" not in sys.modules:
        _mod = types.ModuleType("Ankimon")
        _mod.__path__ = [str(_src / "Ankimon")]
        _mod.__package__ = "Ankimon"
        sys.modules["Ankimon"] = _mod
    else:
        _mod = sys.modules["Ankimon"]
        if not hasattr(_mod, "__path__") or not _mod.__path__:
            _mod.__path__ = [str(_src / "Ankimon")]

    sys.modules["Ankimon.resources"] = MaskedResources = MockResources()

    if "Ankimon.singletons" not in sys.modules:
        sys.modules["Ankimon.singletons"] = MagicMock()
    if "Ankimon.utils" not in sys.modules:
        sys.modules["Ankimon.utils"] = MagicMock()

    if "Ankimon.pyobj" not in sys.modules:
        _pyobj = types.ModuleType("Ankimon.pyobj")
        _pyobj.__path__ = [str(_src / "Ankimon" / "pyobj")]
        _pyobj.__package__ = "Ankimon.pyobj"
        sys.modules["Ankimon.pyobj"] = _pyobj
    else:
        _pyobj = sys.modules["Ankimon.pyobj"]
        if not hasattr(_pyobj, "__path__") or not _pyobj.__path__:
            _pyobj.__path__ = [str(_src / "Ankimon" / "pyobj")]

setup_mocks()

# Dynamically load modules to avoid importing __init__.py directly
def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, _src / relative_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_db_mod = load_module("Ankimon.pyobj.database_manager", "Ankimon/pyobj/database_manager.py")
_bm_mod = load_module("Ankimon.pyobj.backup_manager", "Ankimon/pyobj/backup_manager.py")

from Ankimon.pyobj.database_manager import AnkimonDB
from Ankimon.pyobj.backup_manager import BackupManager

class MockLogger:
    def log(self, level, msg): pass

@pytest.fixture
def mock_env(tmp_path):
    # Create temp user path and backup path structure
    user_files_dir = tmp_path / "user_files"
    user_files_dir.mkdir()
    addon_dir = tmp_path / "Ankimon"
    addon_dir.mkdir()

    # Mock resources within database_manager and backup_manager namespaces
    with patch.object(_db_mod, "user_path", user_files_dir), \
         patch.object(_bm_mod, "user_path", user_files_dir), \
         patch.object(_bm_mod, "addon_dir", addon_dir):

        # Instantiate test database manager
        db = AnkimonDB(MockLogger())

        # Set config settings in the database config table
        db.set_config_value("trainer.name", "Red")
        db.set_config_value("trainer.cash", 5000)
        db.set_config_value("trainer.level", 12)

        # Instantiate test backup manager
        settings_mock = MagicMock()
        settings_mock.get.side_effect = lambda k, default=None: {
            "misc.developer_mode": False
        }.get(k, default)

        bm = BackupManager(MockLogger(), settings_mock)

        # Mock global mw and its ankimon_db attribute
        mock_mw = MagicMock()
        mock_mw.ankimon_db = db

        with patch("Ankimon.pyobj.backup_manager.mw", mock_mw):
            yield bm, db, user_files_dir, addon_dir

def test_backup_summary_trainer_info(mock_env):
    bm, db, user_files_dir, addon_dir = mock_env

    # 1. Create a dummy backup directory
    backup_dir = bm.backups_path / "backup_2026-05-31_23-00-00"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 2. Run generate_summary
    summary = bm._generate_summary(backup_dir)

    # 3. Assertions: check that trainer fields are loaded correctly from config (not user_data)
    assert summary["trainer_name"] == "Red"
    assert summary["trainer_cash"] == 5000
    assert summary["trainer_level"] == 12

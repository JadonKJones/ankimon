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

    # Load the REAL resources module (not a /tmp mock). This module also runs at
    # collection time; leaving a /tmp-path mock in sys.modules would poison other
    # modules that bind resource paths at import (e.g. business.py caches
    # ``effectiveness_chart_file_path``), breaking unrelated tests like
    # test_cp_formula. The fixture patches ``user_path`` per test for filesystem
    # isolation, so we do not need a mock here.
    _existing_res = sys.modules.get("Ankimon.resources")
    if (
        _existing_res is None
        or isinstance(_existing_res, MagicMock)
        or not hasattr(_existing_res, "effectiveness_chart_file_path")
    ):
        _res_spec = importlib.util.spec_from_file_location(
            "Ankimon.resources", _src / "Ankimon" / "resources.py"
        )
        _resources = importlib.util.module_from_spec(_res_spec)
        sys.modules["Ankimon.resources"] = _resources
        _res_spec.loader.exec_module(_resources)

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
# The seam registry backup_manager reads its database from (replaces mw.ankimon_db).
from Ankimon.services import services

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

        # Point the service registry's db at our test database. On main the seam
        # replaces exp's direct mw.ankimon_db access, so backup_manager reads
        # services.db instead of a mocked mw.
        with patch.object(services, "db", db):
            yield bm, db, user_files_dir, addon_dir

def test_backup_summary_trainer_info(mock_env):
    bm, db, user_files_dir, addon_dir = mock_env

    # 1. Create a dummy backup directory (no DB files -> live fallback path)
    backup_dir = bm.backups_path / "backup_2026-05-31_23-00-00"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 2. Run generate_summary
    summary = bm._generate_summary(backup_dir)

    # 3. Assertions: check that trainer fields are loaded correctly from config (not user_data)
    assert summary["trainer_name"] == "Red"
    assert summary["trainer_cash"] == 5000
    assert summary["trainer_level"] == 12


def _seed_db(db_path, name, cash, level=7):
    """Create a real Ankimon SQLite file with trainer config values."""
    seeded = AnkimonDB(MockLogger(), db_path=db_path)
    seeded.set_config_value("trainer.name", name)
    seeded.set_config_value("trainer.cash", cash)
    seeded.set_config_value("trainer.level", level)
    seeded.close()


def test_dual_db_summary(mock_env):
    bm, db, user_files_dir, addon_dir = mock_env

    # A backup directory that actually contains BOTH database files.
    backup_dir = bm.backups_path / "backup_2026-06-01_10-00-00"
    backup_dir.mkdir(parents=True, exist_ok=True)
    _seed_db(backup_dir / "ankimon.db", "Blue", 999)
    _seed_db(backup_dir / "ankimonDEV.db", "DevGuy", 111)

    summary = bm._generate_summary(backup_dir)

    # Per-database sections are read from each backed-up DB file.
    assert summary["normal_stats"]["trainer_name"] == "Blue"
    assert summary["normal_stats"]["trainer_cash"] == 999
    assert summary["dev_stats"]["trainer_name"] == "DevGuy"
    assert summary["dev_stats"]["trainer_cash"] == 111

    # Active DB is ankimon.db (services.db.db_path.name) -> root mirrors normal_stats.
    assert summary["trainer_name"] == "Blue"
    assert summary["trainer_cash"] == 999


def test_get_backups_active_db_filtering(mock_env):
    bm, db, user_files_dir, addon_dir = mock_env

    # Backup A: a normal-mode backup (contains ankimon.db).
    a = bm.backups_path / "backup_2026-06-03_08-00-00"
    a.mkdir(parents=True, exist_ok=True)
    (a / "ankimon.db").write_bytes(b"x")
    with open(a / "summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "date": "2026-06-03 08-00-00",
            "normal_stats": {"trainer_name": "Norm"},
            "dev_stats": {"trainer_name": "Dev"},
        }, f)

    # Backup B: a dev-only backup (contains ankimonDEV.db, NOT ankimon.db).
    b = bm.backups_path / "backup_2026-06-03_09-00-00"
    b.mkdir(parents=True, exist_ok=True)
    (b / "ankimonDEV.db").write_bytes(b"x")
    with open(b / "summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "date": "2026-06-03 09-00-00",
            "normal_stats": {"trainer_name": "Norm2"},
            "dev_stats": {"trainer_name": "Dev2"},
        }, f)

    # Active DB is ankimon.db -> only the normal backup is listed.
    backups = bm.get_backups()
    names = {Path(bk["path"]).name for bk in backups}
    assert "backup_2026-06-03_08-00-00" in names
    assert "backup_2026-06-03_09-00-00" not in names

    a_entry = next(bk for bk in backups if Path(bk["path"]).name == "backup_2026-06-03_08-00-00")
    # The active DB's stats section is merged onto the root for the UI.
    assert a_entry["trainer_name"] == "Norm"


def test_restore_only_active_db(mock_env):
    bm, db, user_files_dir, addon_dir = mock_env

    backup_dir = bm.backups_path / "backup_2026-06-02_09-00-00"
    backup_dir.mkdir(parents=True, exist_ok=True)
    (backup_dir / "ankimon.db").write_bytes(b"NORMAL_DB_CONTENT")
    (backup_dir / "ankimonDEV.db").write_bytes(b"DEV_DB_CONTENT")

    # Active DB is ankimon.db -> only that file is restored; the dev DB is untouched.
    bm.restore_backup(str(backup_dir))

    restored = user_files_dir / "ankimon.db"
    assert restored.exists()
    assert restored.read_bytes() == b"NORMAL_DB_CONTENT"
    assert not (user_files_dir / "ankimonDEV.db").exists()

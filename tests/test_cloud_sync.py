import sys
import sqlite3
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch
import types

import pytest

_src = Path(__file__).parent.parent / "src"


def setup_mocks():
    for name in [
        "aqt", "aqt.qt", "aqt.utils", "aqt.gui_hooks", "aqt.operations",
        "aqt.reviewer", "aqt.webview", "aqt.main",
        "anki", "anki.hooks", "anki.collection", "anki.models", "anki.notes",
        "anki.template", "anki.buildinfo",
    ]:
        if name not in sys.modules:
            sys.modules[name] = MagicMock()

    if "Ankimon" not in sys.modules:
        _mod = types.ModuleType("Ankimon")
        _mod.__path__ = [str(_src / "Ankimon")]
        _mod.__package__ = "Ankimon"
        sys.modules["Ankimon"] = _mod

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


setup_mocks()


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, _src / relative_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_db_mod = load_module("Ankimon.pyobj.database_manager", "Ankimon/pyobj/database_manager.py")
_bm_mod = load_module("Ankimon.pyobj.backup_manager", "Ankimon/pyobj/backup_manager.py")
_cs_mod = load_module("Ankimon.pyobj.cloud_sync", "Ankimon/pyobj/cloud_sync.py")

from Ankimon.pyobj.database_manager import AnkimonDB
from Ankimon.pyobj.cloud_sync import CloudSync
from Ankimon.services import services


class MockLogger:
    def __init__(self):
        self.entries = []

    def log(self, level, msg):
        self.entries.append((level, msg))


@pytest.fixture
def env(tmp_path):
    user_files_dir = tmp_path / "user_files"
    user_files_dir.mkdir()
    addon_dir = tmp_path / "Ankimon"
    addon_dir.mkdir()
    media_dir = tmp_path / "profile" / "collection.media"
    media_dir.mkdir(parents=True)

    fake_mw = MagicMock()
    fake_mw.pm.profileFolder.return_value = str(tmp_path / "profile")

    with patch.object(_db_mod, "user_path", user_files_dir), \
         patch.object(_bm_mod, "user_path", user_files_dir), \
         patch.object(_bm_mod, "addon_dir", addon_dir), \
         patch.object(_bm_mod, "askUser", return_value=True), \
         patch.object(_bm_mod, "showInfo"), \
         patch.object(_bm_mod, "showWarning"), \
         patch.object(_bm_mod, "close_anki"), \
         patch.object(_cs_mod, "mw", fake_mw), \
         patch.object(_cs_mod, "askUser", return_value=True) as p_ask, \
         patch.object(_cs_mod, "showInfo") as p_info, \
         patch.object(_cs_mod, "showWarning") as p_warn, \
         patch.object(_cs_mod, "close_anki") as p_close:

        db = AnkimonDB(MockLogger())
        db.set_config_value("leaderboard.api_key", "SECRET-TOKEN-123")
        db.save_pokemon({"individual_id": "ind-1", "name": "Pikachu", "id": 25, "level": 5, "shiny": False})

        settings_mock = MagicMock()
        settings_mock.get.side_effect = lambda k, default=None: {
            "misc.developer_mode": False
        }.get(k, default)

        cs = CloudSync(MockLogger(), settings_mock)

        with patch.object(services, "db", db):
            yield types.SimpleNamespace(
                cs=cs, db=db, media_dir=media_dir,
                ask=p_ask, info=p_info, warn=p_warn, close=p_close,
            )


def _cloud_db_path(env):
    return env.media_dir / "_ankimon_cloud.db"


def test_push_creates_cloud_copy(env):
    env.cs.push()

    cloud_path = _cloud_db_path(env)
    assert cloud_path.is_file()
    env.info.assert_called_once()
    env.warn.assert_not_called()


def test_push_scrubs_leaderboard_api_key(env):
    env.cs.push()

    with sqlite3.connect(str(_cloud_db_path(env))) as conn:
        row = conn.execute(
            "SELECT value FROM config WHERE key = ?", ("leaderboard.api_key",)
        ).fetchone()
    assert row == ("",)
    # The live db must be untouched.
    assert env.db.get_config_value("leaderboard.api_key", None) == "SECRET-TOKEN-123"


def test_push_declined_confirmation_does_nothing(env):
    env.ask.return_value = False
    env.cs.push()

    assert not _cloud_db_path(env).is_file()
    env.info.assert_not_called()


def test_push_noop_when_db_not_initialized(env):
    with patch.object(services, "db", None):
        env.cs.push()
    env.warn.assert_called_once()
    assert not _cloud_db_path(env).is_file()


def test_pull_warns_when_no_cloud_copy(env):
    env.cs.pull()
    env.warn.assert_called_once()
    env.close.assert_not_called()


def test_pull_aborts_on_corrupt_cloud_copy(env):
    _cloud_db_path(env).write_bytes(b"not a real sqlite file")
    env.cs.pull()
    env.warn.assert_called_once()
    env.close.assert_not_called()


def test_pull_declined_confirmation_leaves_local_db_untouched(env):
    env.cs.push()
    env.db.set_config_value("trainer.cash", 999)
    env.ask.return_value = False

    env.cs.pull()

    assert env.db.get_config_value("trainer.cash", None) == 999
    env.close.assert_not_called()


def test_pull_replaces_local_db_and_closes_anki(env):
    env.cs.push()  # cloud copy now holds cash=default (0)
    env.db.set_config_value("trainer.cash", 4242)  # diverge local from cloud

    env.cs.pull()

    env.close.assert_called_once()
    # Re-open the file on disk (the live AnkimonDB connection was quiesced
    # and the underlying file replaced) to confirm the pulled content landed.
    with sqlite3.connect(str(env.db.db_path)) as conn:
        row = conn.execute(
            "SELECT value FROM config WHERE key = ?", ("trainer.cash",)
        ).fetchone()
    assert row is None or row[0] in ("0", "", None)

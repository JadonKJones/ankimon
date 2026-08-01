import json
import sys
import types
from unittest.mock import patch, MagicMock

# Stub aqt, aqt.operations, and aqt.qt for headless test environment
if "aqt" not in sys.modules:
    aqt = types.ModuleType("aqt")
    aqt.__path__ = []
    aqt.mw = MagicMock()
    sys.modules["aqt"] = aqt

if "aqt.operations" not in sys.modules:
    ops = types.ModuleType("aqt.operations")
    ops.QueryOp = MagicMock
    sys.modules["aqt.operations"] = ops

if "aqt.qt" not in sys.modules:
    qt = types.ModuleType("aqt.qt")
    qt.QDialog = MagicMock
    qt.QVBoxLayout = MagicMock
    qt.QLabel = MagicMock
    qt.QDialogButtonBox = MagicMock
    qt.Qt = MagicMock()
    sys.modules["aqt.qt"] = qt

from Ankimon.pyobj.update_manager import (
    read_update_state,
    save_update_state,
    get_update_channel,
    CHANNEL_MAIN,
)
from Ankimon.pyobj.brrr_deprecation_dialog import (
    check_and_show_brrr_deprecation_notice,
    BRRR_DEPRECATION_SETTING_KEY,
)
from Ankimon.ui_port import HeadlessPresenter
from Ankimon.events import events


def test_read_update_state_migrates_brrr_experimental_to_main(tmp_path, monkeypatch):
    state_file = tmp_path / "user_files" / "update_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    legacy_data = {
        "source_type": "branch",
        "source_name": "BRRRR_Experimental",
        "commit_sha": "1234567890abcdef",
    }
    state_file.write_text(json.dumps(legacy_data), encoding="utf-8")

    monkeypatch.setattr(
        "Ankimon.pyobj.update_manager.get_update_state_path",
        lambda: state_file,
    )

    state = read_update_state()
    assert state is not None
    assert state["source_name"] == CHANNEL_MAIN
    assert state["brrr_migrated_to_main"] is True

    # Confirm it was written back to disk migrated
    disk_data = json.loads(state_file.read_text(encoding="utf-8"))
    assert disk_data["source_name"] == CHANNEL_MAIN


def test_save_update_state_redirects_brrr_experimental_to_main(tmp_path, monkeypatch):
    state_file = tmp_path / "user_files" / "update_state.json"
    monkeypatch.setattr(
        "Ankimon.pyobj.update_manager.get_update_state_path",
        lambda: state_file,
    )

    save_update_state("branch", "BRRRR_Experimental", "abcdef1234567890")

    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["source_name"] == CHANNEL_MAIN


def test_get_update_channel_migrates_brrr_experimental_setting():
    mock_settings = MagicMock()
    mock_settings.get.return_value = "BRRRR_Experimental"

    with patch("Ankimon.pyobj.update_manager._get_settings", return_value=mock_settings):
        channel = get_update_channel()
        assert channel == CHANNEL_MAIN
        mock_settings.set.assert_called_with("misc.update_channel", CHANNEL_MAIN)


def test_deprecation_notice_runs_once(monkeypatch):
    stored_settings = {}

    class DummySettings:
        def get(self, key, default=None):
            return stored_settings.get(key, default)

        def set(self, key, value):
            stored_settings[key] = value

    monkeypatch.setattr("Ankimon.pyobj.brrr_deprecation_dialog.Settings", DummySettings)

    with patch("Ankimon.pyobj.brrr_deprecation_dialog.BRRRDeprecationNoticeDialog") as mock_dialog:
        # First call: should display notice and set shown flag
        shown_1 = check_and_show_brrr_deprecation_notice()
        assert shown_1 is True
        assert stored_settings.get(BRRR_DEPRECATION_SETTING_KEY) is True

        # Second call: should return False and not display dialog
        shown_2 = check_and_show_brrr_deprecation_notice()
        assert shown_2 is False


def test_headless_presenter_emits_deprecation_event():
    events.enable()
    presenter = HeadlessPresenter()
    presenter.notify_brrr_deprecation()
    drained = events.drain()

    assert any(e.get("type") == "brrr_deprecation_notice" for e in drained)

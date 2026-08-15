"""Tests for meta.json update_enabled toggle and sync_ankiweb_update_state.

Ensures that AnkiWeb auto-update checking is disabled to prevent accidental downgrades
unless a strictly newer STABLE release exists on GitHub.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

for _name in [
    "aqt",
    "aqt.qt",
    "aqt.utils",
    "aqt.gui_hooks",
    "aqt.operations",
    "aqt.reviewer",
    "aqt.webview",
    "aqt.main",
    "anki",
    "anki.hooks",
    "anki.collection",
]:
    sys.modules.setdefault(_name, MagicMock())
sys.modules["aqt.operations"].QueryOp = MagicMock()

from Ankimon.pyobj import update_manager as um
from Ankimon import changelog


def test_meta_json_toggle_preserves_existing_keys(tmp_path: Path):
    meta_path = tmp_path / "meta.json"
    initial_data = {
        "name": "Ankimon",
        "mod": 1745007743,
        "disabled": False,
        "config": {"some_key": "some_val"},
    }
    meta_path.write_text(json.dumps(initial_data), encoding="utf-8")

    with patch.object(um, "get_meta_json_path", return_value=meta_path):
        assert um.get_anki_update_enabled() is None

        # Disable update
        assert um.set_anki_update_enabled(False) is True
        assert um.get_anki_update_enabled() is False

        saved = json.loads(meta_path.read_text(encoding="utf-8"))
        assert saved["name"] == "Ankimon"
        assert saved["mod"] == 1745007743
        assert saved["disabled"] is False
        assert saved["config"] == {"some_key": "some_val"}
        assert saved["update_enabled"] is False

        # Re-enable update
        assert um.set_anki_update_enabled(True) is True
        assert um.get_anki_update_enabled() is True
        saved = json.loads(meta_path.read_text(encoding="utf-8"))
        assert saved["update_enabled"] is True
        assert saved["config"] == {"some_key": "some_val"}


def test_meta_json_toggle_creates_file_if_missing(tmp_path: Path):
    meta_path = tmp_path / "meta.json"
    assert not meta_path.exists()

    with patch.object(um, "get_meta_json_path", return_value=meta_path):
        assert um.set_anki_update_enabled(False) is True
        assert meta_path.exists()
        saved = json.loads(meta_path.read_text(encoding="utf-8"))
        assert saved["update_enabled"] is False


def test_sync_ankiweb_update_state_cases(tmp_path: Path):
    meta_path = tmp_path / "meta.json"

    with patch.object(um, "get_meta_json_path", return_value=meta_path):
        # Case 1: Local E (2.3-E), newer stable (2.4) -> enabled = True
        with patch.object(
            um,
            "latest_release_for_channel",
            return_value={"name": "2.4", "body": "", "zipball_url": ""},
        ), patch("Ankimon.changelog.addon_ver", "2.3-E"):
            res = changelog.sync_ankiweb_update_state()
            assert res is True
            assert um.get_anki_update_enabled() is True

        # Case 2: Local E (2.3-E), older stable (2.2) -> enabled = False
        with patch.object(
            um,
            "latest_release_for_channel",
            return_value={"name": "2.2", "body": "", "zipball_url": ""},
        ), patch("Ankimon.changelog.addon_ver", "2.3-E"):
            res = changelog.sync_ankiweb_update_state()
            assert res is False
            assert um.get_anki_update_enabled() is False

        # Case 3: Local stable (2.2), newer stable (2.3) -> enabled = True
        with patch.object(
            um,
            "latest_release_for_channel",
            return_value={"name": "2.3", "body": "", "zipball_url": ""},
        ), patch("Ankimon.changelog.addon_ver", "2.2"):
            res = changelog.sync_ankiweb_update_state()
            assert res is True
            assert um.get_anki_update_enabled() is True

        # Case 4: Local stable (2.3), older stable (2.2) -> enabled = False
        with patch.object(
            um,
            "latest_release_for_channel",
            return_value={"name": "2.2", "body": "", "zipball_url": ""},
        ), patch("Ankimon.changelog.addon_ver", "2.3"):
            res = changelog.sync_ankiweb_update_state()
            assert res is False
            assert um.get_anki_update_enabled() is False

        # Case 5: Local E (2.3-E), older stable (2.2), newer E (2.4-E)
        # Note: latest_release_for_channel(CHANNEL_STABLE) returns the stable release 2.2
        with patch.object(
            um,
            "latest_release_for_channel",
            return_value={"name": "2.2", "body": "", "zipball_url": ""},
        ), patch("Ankimon.changelog.addon_ver", "2.3-E"):
            res = changelog.sync_ankiweb_update_state()
            assert res is False
            assert um.get_anki_update_enabled() is False


def test_sync_ankiweb_update_state_no_releases(tmp_path: Path):
    meta_path = tmp_path / "meta.json"
    with patch.object(um, "get_meta_json_path", return_value=meta_path), patch.object(
        um, "latest_release_for_channel", return_value=None
    ), patch("Ankimon.changelog.addon_ver", "2.3-E"):
        res = changelog.sync_ankiweb_update_state()
        assert res is False
        assert um.get_anki_update_enabled() is False

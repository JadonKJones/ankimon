import sys
from unittest.mock import MagicMock
import PyQt6.QtWidgets
import PyQt6.QtCore
import PyQt6.QtGui

# 1. Mock aqt and its submodules completely
for name in [
    "aqt", "aqt.qt", "aqt.utils", "aqt.gui_hooks", "aqt.operations",
    "aqt.reviewer", "aqt.webview", "aqt.main", "aqt.theme", "aqt.sound",
    "anki", "anki.hooks", "anki.collection", "anki.models", "anki.notes", "anki.template", "anki.buildinfo"
]:
    sys.modules[name] = MagicMock()

# Setup real PyQt classes on aqt.qt so classes inheriting from it compile
aqt_qt = sys.modules["aqt.qt"]
for module in [PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui]:
    for name in dir(module):
        if name.startswith("Q") or name == "Qt":
            try:
                setattr(aqt_qt, name, getattr(module, name))
            except Exception:
                pass

import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QMainWindow
import aqt

class MockMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pm = MagicMock()
        self.pm.profileFolder = MagicMock(return_value="/tmp")
        self.taskman = MagicMock()
        self.logger = MagicMock()
        self.ankimon_db = MagicMock()
        self.settings_obj = MagicMock()
        self.translator = MagicMock()
        self.main_pokemon = MagicMock()
        self.enemy_pokemon = MagicMock()
        self.trainer_card = MagicMock()
        self.ankimon_tracker_obj = MagicMock()
        self.shop_manager = MagicMock()
        self.reviewer_obj = MagicMock()
        self.achievements_dict = MagicMock()
        self.items_web_window = MagicMock()
        self.evo_window = MagicMock()
        self.item_window = MagicMock()
        self.pokemon_pc = MagicMock()
        self.col = None

def test_register_profile_hooks_already_loaded(qapp):
    orig_mw = aqt.mw
    mock_mw = MockMainWindow()
    aqt.mw = mock_mw
    sys.modules["aqt"].mw = mock_mw
    sys.modules["aqt.mw"] = mock_mw

    # Import inside the test function so that autouse fixture has restored packages
    import Ankimon.menu_buttons
    import Ankimon.functions.mobile_sync
    import Ankimon.profile_hooks

    try:
        mock_mw.col = MagicMock()
        mock_mw.ankimon_db.get_mobile_watermark.return_value = 1000
        mock_mw.ankimon_db.get_pending_mobile_count.return_value = 5
        mock_mw.settings_obj.get.return_value = True # mobile.enabled = True

        # Mock functions that will be imported/called
        mock_process = MagicMock(return_value=3)
        mock_update_badge = MagicMock()
        mock_tip = MagicMock()

        # Patch the functions inside profile_hooks or mobile_sync and target mw/module references
        with patch("Ankimon.profile_hooks.mw", mock_mw), \
             patch("Ankimon.menu_buttons.mw", mock_mw), \
             patch("Ankimon.functions.mobile_sync.process_mobile_reviews_after_sync", mock_process), \
             patch("Ankimon.menu_buttons.update_mobile_badge", mock_update_badge), \
             patch("Ankimon.profile_hooks.show_tip_of_the_day", mock_tip), \
             patch("Ankimon.profile_hooks.logger", mock_mw.logger), \
             patch("Ankimon.profile_hooks.settings_obj", mock_mw.settings_obj):

            from Ankimon.profile_hooks import register_profile_hooks

            # Reset mocks
            mock_process.reset_mock()
            mock_update_badge.reset_mock()

            register_profile_hooks(
                online_connectivity=False,
                backup_manager=MagicMock(),
                CatchPokemonHook=MagicMock(),
                DefeatPokemonHook=MagicMock(),
                add_catch_pokemon_hook=MagicMock(),
                add_defeat_pokemon_hook=MagicMock(),
                collected_pokemon_ids=set(),
            )

            # Assert that loaded/open hooks were called immediately
            mock_process.assert_called_once()
            mock_update_badge.assert_called_with(5)

    finally:
        # Restore original mw reference and clean up Qt widget
        aqt.mw = orig_mw
        sys.modules["aqt"].mw = orig_mw
        if "aqt.mw" in sys.modules:
            sys.modules["aqt.mw"] = orig_mw
        mock_mw.deleteLater()

def test_register_profile_hooks_not_loaded_yet(qapp):
    orig_mw = aqt.mw
    mock_mw = MockMainWindow()
    aqt.mw = mock_mw
    sys.modules["aqt"].mw = mock_mw
    sys.modules["aqt.mw"] = mock_mw

    # Import inside the test function so that autouse fixture has restored packages
    import Ankimon.menu_buttons
    import Ankimon.functions.mobile_sync
    import Ankimon.profile_hooks

    mock_mw.col = None # Profile not loaded yet

    mock_process = MagicMock()
    mock_update_badge = MagicMock()

    try:
        with patch("Ankimon.profile_hooks.mw", mock_mw), \
             patch("Ankimon.menu_buttons.mw", mock_mw), \
             patch("Ankimon.functions.mobile_sync.process_mobile_reviews_after_sync", mock_process), \
             patch("Ankimon.menu_buttons.update_mobile_badge", mock_update_badge):

            from Ankimon.profile_hooks import register_profile_hooks

            mock_process.reset_mock()
            mock_update_badge.reset_mock()

            register_profile_hooks(
                online_connectivity=False,
                backup_manager=MagicMock(),
                CatchPokemonHook=MagicMock(),
                DefeatPokemonHook=MagicMock(),
                add_catch_pokemon_hook=MagicMock(),
                add_defeat_pokemon_hook=MagicMock(),
                collected_pokemon_ids=set(),
            )

            # Since mw.col is None, the hooks should NOT be called immediately
            mock_process.assert_not_called()
            mock_update_badge.assert_not_called()

    finally:
        # Restore original mw reference and clean up Qt widget
        aqt.mw = orig_mw
        sys.modules["aqt"].mw = orig_mw
        if "aqt.mw" in sys.modules:
            sys.modules["aqt.mw"] = orig_mw
        mock_mw.deleteLater()

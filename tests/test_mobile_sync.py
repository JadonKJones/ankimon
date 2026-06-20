import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import types

# Capture original aqt/anki modules before we mock them
_original_sys_modules = {k: v for k, v in sys.modules.items() if k.startswith("aqt") or k.startswith("anki")}

# Import test_database_manager first (which triggers its setup_mocks() and writes over sys.modules)
from tests.test_database_manager import MockLogger, temp_env

def setup_real_aqt_qt():
    # Re-configure real module objects for aqt and aqt.qt to override database manager's MagicMocks
    aqt_mod = types.ModuleType("aqt")
    sys.modules["aqt"] = aqt_mod
    aqt_mod.mw = MagicMock()

    aqt_qt = types.ModuleType("aqt.qt")
    sys.modules["aqt.qt"] = aqt_qt
    aqt_mod.qt = aqt_qt

    # Mock other aqt submodules
    for sub in ["utils", "gui_hooks", "operations", "reviewer", "webview", "main", "theme", "sound"]:
        mock_sub = MagicMock()
        sys.modules[f"aqt.{sub}"] = mock_sub
        setattr(aqt_mod, sub, mock_sub)

    sys.modules["aqt.operations.QueryOp"] = MagicMock()

    # Mock anki package and submodules
    anki_mod = types.ModuleType("anki")
    sys.modules["anki"] = anki_mod
    for sub in ["hooks", "collection", "models", "notes", "template", "buildinfo"]:
        mock_sub = MagicMock()
        sys.modules[f"anki.{sub}"] = mock_sub
        setattr(anki_mod, sub, mock_sub)

    import PyQt6.QtWidgets
    import PyQt6.QtCore
    import PyQt6.QtGui
    import PyQt6.QtWebChannel

    for module in [PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui]:
        for name in dir(module):
            if name.startswith("Q") or name == "Qt":
                try:
                    setattr(aqt_qt, name, getattr(module, name))
                    setattr(aqt_mod, name, getattr(module, name))
                except Exception:
                    pass

    # Explicitly mock QWebEngineView, qconnect, and sip to support Anki imports
    if not hasattr(aqt_mod, "QWebEngineView"):
        mock_web = MagicMock()
        setattr(aqt_mod, "QWebEngineView", mock_web)
        setattr(aqt_qt, "QWebEngineView", mock_web)

    aqt_qt.qconnect = MagicMock()
    aqt_mod.qconnect = MagicMock()
    aqt_mod.utils.qconnect = MagicMock()

    try:
        import PyQt6.sip as sip_mod
    except ImportError:
        try:
            import PyQt5.sip as sip_mod
        except ImportError:
            import sip as sip_mod
    aqt_qt.sip = sip_mod
    return aqt_mod, aqt_qt

aqt_mod, aqt_qt = setup_real_aqt_qt()

def force_load_module(name, rel_path):
    import sys
    import importlib.util
    from pathlib import Path
    _src = Path(__file__).parent.parent / "src"
    spec = importlib.util.spec_from_file_location(name, _src / rel_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

from Ankimon.functions.mobile_sync import (
    record_desktop_review,
    get_desktop_session_revlog_ids,
    clear_desktop_session,
    detect_mobile_reviews,
    process_mobile_reviews_after_sync,
    MOBILE_QUEUE_CAP,
    simulate_pending_mobile_battles
)

def test_mobile_sync_database_and_engine(temp_env):
    db, tmp_path = temp_env

    # 1. Test watermark methods
    assert db.get_mobile_watermark() == 0
    db.set_mobile_watermark(12345)
    assert db.get_mobile_watermark() == 12345

    # 2. Test queue insertion & duplicate checks
    reviews = [
        {"id": 101, "cid": 1001, "ease": 3, "time": 15000, "type": 1},
        {"id": 102, "cid": 1002, "ease": 2, "time": 20000, "type": 2},
    ]
    inserted = db.queue_mobile_battles(reviews)
    assert inserted == 2
    assert db.get_pending_mobile_count() == 2

    # Insert again with same revlog_id, should ignore
    inserted_dup = db.queue_mobile_battles(reviews)
    assert inserted_dup == 0
    assert db.get_pending_mobile_count() == 2

    # 3. Test retrieving batches
    batch = db.get_next_pending_mobile_batch(limit=1)
    assert len(batch) == 1
    assert batch[0]["revlog_id"] == 101
    assert batch[0]["card_id"] == 1001

    batch_all = db.get_next_pending_mobile_batch(limit=10)
    assert len(batch_all) == 2

    # 4. Test resolving a battle
    db.mark_mobile_battle_resolved(batch[0]["queue_id"])
    assert db.get_pending_mobile_count() == 1

    batch_after_resolve = db.get_next_pending_mobile_batch(limit=10)
    assert len(batch_after_resolve) == 1
    assert batch_after_resolve[0]["revlog_id"] == 102

    # 5. Test session sets
    clear_desktop_session()
    assert len(get_desktop_session_revlog_ids()) == 0
    record_desktop_review(103)
    record_desktop_review(104)
    assert get_desktop_session_revlog_ids() == frozenset({103, 104})
    clear_desktop_session()
    assert len(get_desktop_session_revlog_ids()) == 0

def test_cross_db_resolution_sync(temp_env):
    db, tmp_path = temp_env
    # Ensure current database is ankimon.db
    assert db.db_path.name == "ankimon.db"
    
    # Create the other database file: ankimonDEV.db
    other_path = tmp_path / "ankimonDEV.db"
    
    # Initialize other database schema
    import sqlite3
    conn = sqlite3.connect(str(other_path))
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pending_mobile_battles (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                revlog_id     INTEGER UNIQUE NOT NULL,
                card_id       INTEGER NOT NULL,
                ease          INTEGER NOT NULL,
                review_time   INTEGER NOT NULL,
                review_type   INTEGER NOT NULL,
                queued_at     INTEGER NOT NULL,
                resolved      INTEGER NOT NULL DEFAULT 0,
                resolved_at   INTEGER
            )
        """)
        # Insert a matching pending battle in the other database
        conn.execute(
            "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at) VALUES (?, ?, ?, ?, ?, ?)",
            (101, 1001, 3, 15000, 1, 123456)
        )
        conn.commit()
    finally:
        conn.close()
        
    # Queue the battle in the active database
    db.queue_mobile_battles([
        {"id": 101, "cid": 1001, "ease": 3, "time": 15000, "type": 1}
    ])
    
    # Get the queue_id from the active DB
    batch = db.get_next_pending_mobile_batch(limit=1)
    assert len(batch) == 1
    queue_id = batch[0]["queue_id"]
    
    # Patch user_path in database_manager to use our temp path
    with patch("Ankimon.pyobj.database_manager.user_path", tmp_path):
        # Resolve in active database
        db.mark_mobile_battle_resolved(queue_id)
        
    # Assert it was resolved in active DB
    assert db.get_pending_mobile_count() == 0
    
    # Assert it was automatically resolved in the other DB
    conn = sqlite3.connect(str(other_path))
    try:
        cursor = conn.execute("SELECT resolved, resolved_at FROM pending_mobile_battles WHERE revlog_id = 101")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 1  # resolved
        assert row[1] is not None  # resolved_at
    finally:
        conn.close()

def test_detect_mobile_reviews():
    # Mocking col.db
    col = MagicMock()
    # Mock database returning 3 reviews:
    # 201 (mature review), 202 (relearn), 203 (mature review)
    col.db.all.return_value = [
        (201, 1001, 3, 12000, 1),
        (202, 1002, 1, 15000, 2),
        (203, 1003, 4, 8000, 1),
    ]

    desktop_ids = frozenset({202}) # 202 was done on desktop
    mobile_reviews = detect_mobile_reviews(col, 200, desktop_ids)

    # 201 and 203 should be detected as mobile reviews
    assert len(mobile_reviews) == 2
    assert mobile_reviews[0]["id"] == 201
    assert mobile_reviews[1]["id"] == 203
    col.db.all.assert_called_once_with(
        """
        SELECT id, cid, ease, time, type
        FROM revlog
        WHERE id > ?
          AND type IN (0, 1, 2, 3)
        ORDER BY id ASC
        """,
        200
    )

def test_process_mobile_reviews_after_sync(temp_env):
    db, tmp_path = temp_env
    col = MagicMock()
    # Watermark initially at 300. We have reviews up to 305.
    db.set_mobile_watermark(300)
    col.db.all.return_value = [
        (301, 1001, 3, 10000, 1),
        (302, 1002, 3, 10000, 1),
        (303, 1003, 3, 10000, 1),
        (304, 1004, 3, 10000, 1),
        (305, 1005, 3, 10000, 1),
    ]
    col.db.scalar.return_value = 305

    settings_obj = MagicMock()
    settings_obj.get.return_value = True # mobile.enabled = True

    logger = MagicMock()

    clear_desktop_session()
    record_desktop_review(302)
    record_desktop_review(304)

    newly_queued = process_mobile_reviews_after_sync(col, db, settings_obj, logger)
    # Total 5 reviews, 2 done on desktop, so 3 should be queued (301, 303, 305)
    assert newly_queued == 3
    assert db.get_pending_mobile_count() == 3

    # Watermark should be advanced to 305
    assert db.get_mobile_watermark() == 305

    # Session set should be cleared
    assert len(get_desktop_session_revlog_ids()) == 0

def test_update_mobile_badge():
    from Ankimon.menu_buttons import update_mobile_badge
    import Ankimon.menu_buttons

    mock_menu = MagicMock()
    mock_game_menu = MagicMock()
    mock_action = MagicMock()

    # Mocking translator translate
    from aqt import mw
    mw.translator = MagicMock()
    mw.translator.translate.return_value = "Game"

    Ankimon.menu_buttons._ankimon_menu = mock_menu
    Ankimon.menu_buttons._ankimon_menu_base_title = "&Ankimon"
    Ankimon.menu_buttons.game_menu = mock_game_menu
    Ankimon.menu_buttons._mobile_battles_action = mock_action

    # Test count > 0 shows badge in Game and Mobile Battles menu items
    update_mobile_badge(47)
    mock_menu.setTitle.assert_called_with("&Ankimon")
    mock_game_menu.setTitle.assert_called_with("(47) Game")
    mock_action.setText.assert_called_with("(47) Mobile & Web Reviews")

    # Test count = 0 removes badge
    update_mobile_badge(0)
    mock_menu.setTitle.assert_called_with("&Ankimon")
    mock_game_menu.setTitle.assert_called_with("Game")
    mock_action.setText.assert_called_with("Mobile & Web Reviews")

def test_mobile_bridge(temp_env):
    db, tmp_path = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from Ankimon.functions.mobile_sync import clear_desktop_session
    from aqt import mw

    # Set singletons on mw mock
    mw.ankimon_db = db
    mw.main_pokemon = MagicMock(name="Charizard", level=50)
    mw.main_pokemon.name = "Charizard"
    mw.main_pokemon.level = 50

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_wishlist": [],
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.xp_multiplier": 1.5,
        "controls.allow_to_choose_moves": False,
        "misc.language": 0
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    mw.settings_obj = settings_mock

    bridge = MobileBridge(MagicMock())

    # Case A: 0 pending
    status = bridge.getMobileStatus()
    assert status["pending_count"] == 0

    # Case B: pending reviews exists
    reviews = [
        {"id": 501, "cid": 1001, "ease": 1, "time": 10000, "type": 1},
        {"id": 502, "cid": 1002, "ease": 3, "time": 10000, "type": 1},
        {"id": 503, "cid": 1003, "ease": 3, "time": 10000, "type": 1},
    ]
    db.queue_mobile_battles(reviews)

    with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")):
        status = bridge.getMobileStatus()
    assert status["pending_count"] == 3
    assert status["ease_breakdown"] == {"1": 1, "2": 0, "3": 2, "4": 0}
    assert status["estimates"]["encounters"] == 2  # 3 reviews / 2 cards_per_round = 2 encounters (second triggers on leftover last card)

    assert "xp" in status["estimates"]
    assert "catches" in status["estimates"]
    assert "caught_list" in status["estimates"]
    assert status["auto_battle_mode"] == "Catch Uncollected"
    assert status["rare_catch_active"] is True
    assert status["main_pokemon_name"] == "Charizard"
    assert status["main_pokemon_level"] == 50

    # Test dismissAll
    res = bridge.dismissAll()
    assert res.get("success") is True, f"dismissAll failed: {res.get('error')}"
    assert res.get("dismissed") == 3
    assert db.get_pending_mobile_count() == 0

    # Test triggerAnkiSync
    mw.onSync = MagicMock()
    with patch("aqt.qt.QTimer.singleShot", lambda ms, func: func()):
        sync_res = bridge.triggerAnkiSync()
        assert sync_res.get("success") is True
        assert mw.onSync.called

def test_mobile_bridge_resolve_all(temp_env):
    db, tmp_path = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw

    # Set singletons on mw mock
    mw.ankimon_db = db
    mw.main_pokemon = MagicMock(name="Charizard", level=50)
    mw.main_pokemon.name = "Charizard"
    mw.main_pokemon.level = 50

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_wishlist": [],
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.xp_multiplier": 1.5,
        "controls.allow_to_choose_moves": False,
        "trainer.xp": 100,
        "trainer.total_xp": 100,
        "trainer.cash": 200,
        "trainer.cash_reward_interval": 5,
        "trainer.cash_reward_amount": 10,
        "misc.language": 0
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    mw.settings_obj = settings_mock
    mw.logger = MagicMock()

    trainer_card_mock = MagicMock()
    trainer_card_mock.xp = 100
    trainer_card_mock.total_xp = 100
    trainer_card_mock.cash = 200
    mw.trainer_card = trainer_card_mock

    # Queue some reviews
    reviews = [
        {"id": 601, "cid": 1001, "ease": 1, "time": 10000, "type": 1},
        {"id": 602, "cid": 1002, "ease": 3, "time": 10000, "type": 1},
        {"id": 603, "cid": 1003, "ease": 3, "time": 10000, "type": 1},
    ]
    db.queue_mobile_battles(reviews)
    assert db.get_pending_mobile_count() == 3

    bridge = MobileBridge(MagicMock())

    # We patch save_main_pokemon_progress, save_caught_pokemon, generate_random_pokemon, simulate_battle_with_poke_engine
    from unittest.mock import patch
    with patch("Ankimon.functions.encounter_functions.save_main_pokemon_progress") as mock_save_progress, \
         patch("Ankimon.functions.encounter_functions.save_caught_pokemon") as mock_save_caught, \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")) as mock_simulate_battle, \
         patch("Ankimon.menu_buttons.update_mobile_badge") as mock_update_badge:

        # Let generate_random_pokemon return a mockup (pikachu id = 25, level 5)
        mock_gen_random.return_value = (
            "Pikachu", 25, 5, "Run Away", ["Electric"], 
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium", 
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        res = bridge.resolveAll()

        assert res.get("success") is True, f"resolveAll failed: {res.get('error')}"
        assert res.get("resolved") == 2
        assert len(res.get("caught_list")) == 1
        assert "cp" in res.get("caught_list")[0]
        assert isinstance(res.get("caught_list")[0]["cp"], int)
        # 3 reviews / 2 cards_per_round = 2 encounters (including the leftover review)
        assert mock_gen_random.call_count == 2
        assert mock_save_caught.call_count == 1  # 1st encounter Pikachu caught
        assert mock_save_progress.call_count == 1  # 2nd encounter Pikachu defeated
        mock_update_badge.assert_called_with(0)
        assert db.get_pending_mobile_count() == 0

def test_items_web_mobile_integration(temp_env):
    db, tmp_path = temp_env
    import importlib.util
    from unittest.mock import MagicMock, patch
    
    with patch("PyQt6.QtWidgets.QStackedWidget"), \
         patch("aqt.QWebEngineView"), \
         patch("PyQt6.QtWebChannel.QWebChannel"):
         
        class QDialogStub:
            def __init__(self, *args, **kwargs): pass
            def __getattr__(self, name):
                if name.startswith("_"):
                    raise AttributeError(name)
                def dummy(*args, **kwargs):
                    if name == "windowFlags":
                        return 0
                    return None
                return dummy
                
        import aqt
        aqt.QDialog = QDialogStub
        aqt.QVBoxLayout = MagicMock
        class MockQFrame(MagicMock):
            class Shape:
                NoFrame = 0
        aqt.qt.QFrame = MockQFrame
        aqt.qt.QVBoxLayout = MagicMock
        
        # Force reload shop_obj to pick up QDialogStub
        _src = Path(__file__).parent.parent / "src"
        spec = importlib.util.spec_from_file_location(
            "Ankimon.ankimon_items_web.shop_obj", 
            _src / "Ankimon" / "ankimon_items_web" / "shop_obj.py"
        )
        shop_obj_mod = importlib.util.module_from_spec(spec)
        sys.modules["Ankimon.ankimon_items_web.shop_obj"] = shop_obj_mod
        spec.loader.exec_module(shop_obj_mod)
        
        AnkimonItemsWeb = shop_obj_mod.AnkimonItemsWeb
        
        mock_shop_manager = MagicMock()
        mock_shop_manager.todays_daily_items = []
        mock_shop_manager.todays_daily_tms = []
        mock_shop_manager.get_callback.return_value = 0
        
        web_win = AnkimonItemsWeb(
            addon_dir=Path("/tmp"),
            shop_manager=mock_shop_manager,
            item_window=MagicMock(),
            ankimon_tracker=MagicMock(),
            trainer_card=MagicMock(),
            settings_obj=MagicMock(),
            logger=MagicMock()
        )
        
        web_win.ready_screens.add("mobile")
        web_win.current_screen = "mobile"
        
        mock_page = MagicMock()
        web_win.webview_mobile.page = MagicMock(return_value=mock_page)
        
        try:
            web_win.push_screen_data()
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e
            
        mock_page.runJavaScript.assert_called_once()
        js_call = mock_page.runJavaScript.call_args[0][0]
        assert "window.initializeMobile" in js_call
        assert '"pending_count": 0' in js_call

@pytest.fixture(scope="module", autouse=True)
def cleanup_sys_modules():
    yield
    # Restore sys.modules to original state after this module finishes
    for k in list(sys.modules):
        if k.startswith("PyQt6") or k.startswith("aqt") or k.startswith("anki"):
            if k in _original_sys_modules:
                sys.modules[k] = _original_sys_modules[k]
            else:
                del sys.modules[k]

@pytest.fixture(autouse=True)
def clean_mw():
    from aqt import mw
    attrs_to_remove = ["main_pokemon", "settings_obj", "trainer_card", "ankimon_db", "ankimon_tracker_obj", "logger", "evo_window"]
    for attr in attrs_to_remove:
        if hasattr(mw, attr):
            try:
                delattr(mw, attr)
            except AttributeError:
                pass
    yield
    for attr in attrs_to_remove:
        if hasattr(mw, attr):
            try:
                delattr(mw, attr)
            except AttributeError:
                pass

def test_sync_did_finish_routing(temp_env):
    from Ankimon.pyobj.ankimon_sync import setup_ankimon_sync_hooks
    from aqt import mw, gui_hooks
    
    db, tmp_path = temp_env
    mw.ankimon_db = db
    mw.col = MagicMock()
    
    # Setup mock reviews
    mw.col.db.all.return_value = [
        (501, 1001, 3, 10000, 1),
        (502, 1002, 3, 10000, 1),
    ]
    mw.col.db.scalar.return_value = 502
    
    settings_obj = MagicMock()
    settings_obj.get.return_value = True # mobile.enabled
    
    logger = MagicMock()
    
    # Temporarily stub gui_hooks.sync_did_finish to capture the callback
    gui_hooks.sync_did_finish = MagicMock()
    
    setup_ankimon_sync_hooks(settings_obj, logger)
    assert gui_hooks.sync_did_finish.append.called
    on_sync_did_finish = gui_hooks.sync_did_finish.append.call_args[0][0]
    
    # Create dev database file to trigger dual database queueing
    dev_db = tmp_path / "ankimonDEV.db"
    dev_db.write_text("")  # Empty file
    
    with patch("Ankimon.pyobj.ankimon_sync.user_path", tmp_path), \
         patch("Ankimon.pyobj.ankimon_sync.tooltip") as mock_tooltip:
         
        # Stub database switch to track calls
        db.switch_database = MagicMock()
        db.queue_mobile_battles = MagicMock(return_value=2)
        
        # Invoke sync finish
        on_sync_did_finish()
        
        # Verify switch_database was called to switch to dev database and back
        assert db.switch_database.called
        assert db.queue_mobile_battles.called
        # Verify watermark is set
        assert db.get_mobile_watermark() == 502


def test_simulate_extrapolation(temp_env):
    """Verify that simulate_pending_mobile_battles handles >100 reviews
    by extrapolating rather than crashing or silently dropping data."""
    db, tmp_path = temp_env
    from aqt import mw
    mw.ankimon_db = db

    # Create 150 fake reviews
    reviews = [
        {"id": i, "revlog_id": i, "card_id": i * 10, "ease": 3,
         "review_time": 10000, "review_type": 1}
        for i in range(1, 151)
    ]

    settings_obj = MagicMock()
    settings_obj.get.side_effect = lambda key, default=None: {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.auto_catch_wishlist": [],
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False,
    }.get(key, default)

    main_pokemon = MagicMock()
    main_pokemon.level = 30
    main_pokemon.held_item = None

    from unittest.mock import patch
    with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")):
        result = simulate_pending_mobile_battles(reviews, main_pokemon, settings_obj, None, None)

    # Should not crash
    assert result["xp"] > 0
    assert result["encounters"] > 0
    assert result["is_truncated"] is True
    assert result["simulated_reviews"] == 100
    assert result["total_reviews"] == 150
    # Extrapolated encounters = encounters from 100 + extra for 50 remaining
    assert result["encounters"] >= 50  # at least 50 reviews / 2 cards_per_round
    assert "catches_count" in result
    assert result["catches_count"] >= len(result["caught"])
    assert result["catches_count"] > 0


def test_companion_strength_scaling(temp_env):
    """Verify that stronger companions resolve encounters in fewer turns
    than weaker ones for the same review count."""
    db, tmp_path = temp_env
    from aqt import mw
    mw.ankimon_db = db

    # 10 fake reviews (5 rounds of 2 reviews)
    reviews = [
        {"id": i, "revlog_id": i, "card_id": i * 10, "ease": 3,
         "review_time": 10000, "review_type": 1}
        for i in range(1, 11)
    ]

    settings_obj = MagicMock()
    settings_obj.get.side_effect = lambda key, default=None: {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_legendary": False,
        "battle.auto_catch_mythical": False,
        "battle.auto_catch_ultra": False,
        "battle.auto_catch_starter": False,
        "battle.auto_catch_mega": False,
        "battle.auto_catch_gmax": False,
        "battle.auto_catch_regional": False,
        "battle.auto_catch_wishlist": [],
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False,
    }.get(key, default)

    # 1. Weak companion (level 5)
    weak_companion = MagicMock()
    weak_companion.level = 5
    weak_companion.held_item = None
    weak_companion.attacks = ["Tackle"]
    weak_companion.hp = 20
    weak_companion.max_hp = 20
    weak_companion.stat_stages = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}
    weak_companion.volatile_status = set()

    # Mock battle engine simulation so weak companion deals 5 damage per turn (takes 4 turns to defeat 20 HP enemy)
    # Mock battle engine simulation so strong companion deals 20 damage per turn (takes 1 turn to defeat 20 HP enemy)
    def mock_simulate_battle(user, enemy, user_move, enemy_move, mutator, state=None):
        damage = 20 if user.level >= 50 else 5
        enemy.hp = max(0, enemy.hp - damage)
        if hasattr(enemy, "current_hp"):
            enemy.current_hp = enemy.hp
        fake_state = MagicMock()
        fake_state.user.active.hp = user.hp
        fake_state.opponent.active.hp = enemy.hp
        return ({}, fake_state, 0, damage, mutator)

    from unittest.mock import patch
    with patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate_battle):

        # We generate random pokemon with hp base stat resulting in 20 max hp
        # At level 5, if base_stats hp is 50, iv is 15, ev is 0:
        # hp = 10 + 5 + int((100 + 15) * 5 / 100) = 15 + 5 = 20 hp
        mock_gen_random.return_value = (
            "Pikachu", 25, 5, "Run Away", ["Electric"], 
            {"hp": 50, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium", 
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        res_weak = simulate_pending_mobile_battles(reviews, weak_companion, settings_obj, None, None)

    # 2. Strong companion (level 50)
    strong_companion = MagicMock()
    strong_companion.level = 50
    strong_companion.held_item = None
    strong_companion.attacks = ["Thunderbolt"]
    strong_companion.hp = 100
    strong_companion.max_hp = 100
    strong_companion.stat_stages = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}
    strong_companion.volatile_status = set()

    with patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate_battle):

        mock_gen_random.return_value = (
            "Pikachu", 25, 5, "Run Away", ["Electric"], 
            {"hp": 50, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium", 
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        res_strong = simulate_pending_mobile_battles(reviews, strong_companion, settings_obj, None, None)

    assert res_strong["encounters"] > res_weak["weak_encounters" if "weak_encounters" in res_weak else "encounters"]


def test_diagnostic_level_100(temp_env):
    """Run a diagnostic simulation with a level 100 companion and review-based damage."""
    db, tmp_path = temp_env
    from aqt import mw
    mw.ankimon_db = db

    # 48 fake reviews with ease 3 (Good)
    reviews = [
        {"id": i, "revlog_id": i, "card_id": i * 10, "ease": 3,
         "review_time": 10000, "review_type": 1}
        for i in range(1, 49)
    ]

    settings_obj = MagicMock()
    settings_obj.get.side_effect = lambda key, default=None: {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_legendary": False,
        "battle.auto_catch_mythical": False,
        "battle.auto_catch_ultra": False,
        "battle.auto_catch_starter": False,
        "battle.auto_catch_mega": False,
        "battle.auto_catch_gmax": False,
        "battle.auto_catch_regional": False,
        "battle.auto_catch_wishlist": [],
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False,
        "battle.review_based_damage": True,
    }.get(key, default)
    mw.settings_obj = settings_obj

    # We need a real tracker so we can set/get the multiplier
    AnkimonTracker = force_load_module("Ankimon.pyobj.ankimon_tracker", "Ankimon/pyobj/ankimon_tracker.py").AnkimonTracker
    AnkimonTracker.randomize_battle_scene = lambda self: None
    tracker = AnkimonTracker(trainer_card=MagicMock())
    tracker.get_total_reviews = MagicMock(return_value=0)
    tracker.multiplier = 1.0
    mw.ankimon_tracker_obj = tracker

    PokemonObject = force_load_module("Ankimon.pyobj.pokemon_obj", "Ankimon/pyobj/pokemon_obj.py").PokemonObject
    force_load_module("Ankimon.functions.ankimon_hooks_to_poke_engine", "Ankimon/functions/ankimon_hooks_to_poke_engine.py")
    force_load_module("Ankimon.functions.encounter_functions", "Ankimon/functions/encounter_functions.py")
    companion = PokemonObject(
        type=["Fire", "Flying"],
        name="Charizard",
        id=6,
        shiny=False,
        level=100,
        ability="Blaze",
        gender="M",
        growth_rate="Medium",
        captured_date=None,
        tier="Normal",
        individual_id="charizard_100",
        base_stats={"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100},
        attacks=["Flamethrower", "Slash", "Dragon Rage", "Wing Attack"],
        base_experience=240,
        hp=297,
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        battle_status="Fighting"
    )

    print("\n--- DIAGNOSTIC 100 START ---")
    res = simulate_pending_mobile_battles(reviews, companion, settings_obj, None, tracker)
    print("SIMULATION RESULTS:")
    print("XP:", res["xp"])
    print("Encounters:", res["encounters"])
    print("Caught:", len(res["caught"]))
    print("Defeated:", len(res["defeated"]))
    print("--- DIAGNOSTIC 100 END ---")


def test_mewtwo_mega_x(temp_env):
    """Diagnostic test for level 500 Mega Mewtwo X with 12 reviews."""
    db, tmp_path = temp_env
    from aqt import mw
    mw.ankimon_db = db

    # 12 reviews with ease 3 (Good)
    reviews = [
        {"id": i, "revlog_id": i, "card_id": i * 10, "ease": 3,
         "review_time": 10000, "review_type": 1}
        for i in range(1, 13)
    ]

    settings_obj = MagicMock()
    settings_obj.get.side_effect = lambda key, default=None: {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.auto_catch_wishlist": [],
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False,
        "battle.review_based_damage": True,
    }.get(key, default)
    mw.settings_obj = settings_obj

    AnkimonTracker = force_load_module("Ankimon.pyobj.ankimon_tracker", "Ankimon/pyobj/ankimon_tracker.py").AnkimonTracker
    AnkimonTracker.randomize_battle_scene = lambda self: None
    tracker = AnkimonTracker(trainer_card=MagicMock())
    tracker.get_total_reviews = MagicMock(return_value=0)
    tracker.multiplier = 1.0
    mw.ankimon_tracker_obj = tracker

    PokemonObject = force_load_module("Ankimon.pyobj.pokemon_obj", "Ankimon/pyobj/pokemon_obj.py").PokemonObject
    force_load_module("Ankimon.functions.ankimon_hooks_to_poke_engine", "Ankimon/functions/ankimon_hooks_to_poke_engine.py")
    force_load_module("Ankimon.functions.encounter_functions", "Ankimon/functions/encounter_functions.py")
    companion = PokemonObject(
        type=["Psychic", "Fighting"],
        name="Mewtwo-Mega-X",
        id=10043,
        shiny=False,
        level=500,
        ability="Steadfast",
        gender="N",
        growth_rate="Slow",
        captured_date=None,
        tier="Illegal",
        individual_id="mewtwo_500",
        base_stats={"hp": 106, "atk": 190, "def": 100, "spa": 154, "spd": 100, "spe": 130},
        attacks=["psychocut"],
        base_experience=342,
        hp=1725,
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        battle_status="Fighting"
    )

    print("\n--- MEWTWO DIAGNOSTIC START ---")
    res = simulate_pending_mobile_battles(reviews, companion, settings_obj, None, tracker)
    print("SIMULATION RESULTS:")
    print("XP:", res["xp"])
    print("Encounters:", res["encounters"])
    print("Caught:", len(res["caught"]))
    print("Defeated:", len(res["defeated"]))
    print("--- MEWTWO DIAGNOSTIC END ---")

    # Assertions
    assert res["xp"] > 0, "XP gained should be positive"
    assert res["encounters"] > 0, "Encounters should be simulated"
    assert (len(res["caught"]) + len(res["defeated"])) > 0, "Should catch or defeat at least one opponent"


def test_reshiram_vs_wynaut_12_reviews(temp_env):
    """Test that Level 172 Reshiram successfully defeats Level 175 Wynaut within 12 reviews now that the multiplier is corrected."""
    db, tmp_path = temp_env
    from aqt import mw
    mw.ankimon_db = db

    # 12 reviews with ease 3 (Good)
    reviews = [
        {"id": i, "revlog_id": i, "card_id": i * 10, "ease": 3,
         "review_time": 10000, "review_type": 1}
        for i in range(1, 13)
    ]

    settings_obj = MagicMock()
    settings_obj.get.side_effect = lambda key, default=None: {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_legendary": False,
        "battle.auto_catch_mythical": False,
        "battle.auto_catch_ultra": False,
        "battle.auto_catch_starter": False,
        "battle.auto_catch_mega": False,
        "battle.auto_catch_gmax": False,
        "battle.auto_catch_regional": False,
        "battle.auto_catch_wishlist": [],
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False,
        "battle.review_based_damage": True,
    }.get(key, default)
    mw.settings_obj = settings_obj

    AnkimonTracker = force_load_module("Ankimon.pyobj.ankimon_tracker", "Ankimon/pyobj/ankimon_tracker.py").AnkimonTracker
    AnkimonTracker.randomize_battle_scene = lambda self: None
    tracker = AnkimonTracker(trainer_card=MagicMock())
    tracker.get_total_reviews = MagicMock(return_value=0)
    tracker.multiplier = 1.0
    mw.ankimon_tracker_obj = tracker

    PokemonObject = force_load_module("Ankimon.pyobj.pokemon_obj", "Ankimon/pyobj/pokemon_obj.py").PokemonObject
    force_load_module("Ankimon.functions.ankimon_hooks_to_poke_engine", "Ankimon/functions/ankimon_hooks_to_poke_engine.py")
    force_load_module("Ankimon.functions.encounter_functions", "Ankimon/functions/encounter_functions.py")
    
    companion = PokemonObject(
        type=["Dragon", "Fire"],
        name="Reshiram",
        id=643,
        shiny=False,
        level=172,
        ability="Turboblaze",
        gender="N",
        growth_rate="Slow",
        captured_date=None,
        tier="Legendary",
        individual_id="reshiram_172",
        base_stats={"hp": 100, "atk": 120, "def": 100, "spa": 150, "spd": 120, "spe": 90},
        attacks=["dragonbreath", "fireblast", "flamethrower", "imprison"],
        base_experience=340,
        hp=555,
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        battle_status="Fighting"
    )

    from unittest.mock import patch
    with patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random:
        mock_gen_random.return_value = (
            "Wynaut", 360, 175, "Shadow Tag", ["Psychic"],
            {"hp": 95, "atk": 23, "def": 48, "spa": 23, "spd": 48, "spe": 23},
            ["encore", "amnesia", "charm", "destinybond"], 44, "Medium",
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"hp": 1}, False, "serious"
        )

        res = simulate_pending_mobile_battles(reviews, companion, settings_obj, None, tracker)

    # Wynaut has 573 HP. With corrected multiplier, Reshiram should easily defeat it and gain XP.
    assert res["encounters"] > 0, "At least one encounter should occur"
    assert len(res["defeated"]) > 0, "Wynaut should be defeated"
    assert res["xp"] > 0, "XP gained should be positive"


def test_mobile_bridge_resolve_next(temp_env):
    db, tmp_path = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw

    mw.ankimon_db = db
    mw.main_pokemon = MagicMock()
    mw.main_pokemon.name = "Charizard"
    mw.main_pokemon.level = 50
    mw.main_pokemon.id = 6
    mw.main_pokemon.shiny = False
    mw.main_pokemon.gender = "M"
    mw.main_pokemon.attacks = ["Slash"]

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_wishlist": [],
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.xp_multiplier": 1.5,
        "controls.allow_to_choose_moves": False,
        "trainer.cash_reward_interval": 5,
        "trainer.cash_reward_amount": 10,
        "misc.language": 0
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    mw.settings_obj = settings_mock

    bridge = MobileBridge(MagicMock())

    reviews = [
        {"id": 701, "cid": 1001, "ease": 1, "time": 10000, "type": 1},
        {"id": 702, "cid": 1002, "ease": 3, "time": 10000, "type": 1},
    ]
    db.queue_mobile_battles(reviews)

    from unittest.mock import patch
    with patch("Ankimon.functions.encounter_functions.save_main_pokemon_progress") as mock_save_progress, \
         patch("Ankimon.functions.encounter_functions.save_caught_pokemon") as mock_save_caught, \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")) as mock_simulate_battle, \
         patch("Ankimon.menu_buttons.update_mobile_badge") as mock_update_badge:

        # Let generate_random_pokemon return a mockup (pikachu id = 25, level 5)
        mock_gen_random.return_value = (
            "Pikachu", 25, 5, "Run Away", ["Electric"], 
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium", 
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        res = bridge.resolveNext()
    print("RESOLVE NEXT RESULT:", res)
    assert res is not None
    assert "enemy_name" in res
    assert "companion_name" in res


def test_mobile_bridge_commit_replay_outcome(temp_env):
    db, tmp_path = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw

    mw.ankimon_db = db
    mw.main_pokemon = MagicMock()
    mw.main_pokemon.name = "Charizard"
    mw.main_pokemon.level = 50
    mw.main_pokemon.id = 6
    mw.main_pokemon.shiny = False
    mw.main_pokemon.gender = "M"
    mw.main_pokemon.attacks = ["Slash"]

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_wishlist": [],
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.xp_multiplier": 1.5,
        "controls.allow_to_choose_moves": False,
        "trainer.cash_reward_interval": 5,
        "trainer.cash_reward_amount": 10,
        "misc.language": 0
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    mw.settings_obj = settings_mock

    bridge = MobileBridge(MagicMock())

    reviews = [
        {"id": 801, "cid": 1001, "ease": 1, "time": 10000, "type": 1},
        {"id": 802, "cid": 1002, "ease": 3, "time": 10000, "type": 1},
    ]
    db.queue_mobile_battles(reviews)

    from unittest.mock import patch
    with patch("Ankimon.functions.encounter_functions.save_main_pokemon_progress") as mock_save_progress, \
         patch("Ankimon.functions.encounter_functions.save_caught_pokemon") as mock_save_caught, \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")) as mock_simulate_battle, \
         patch("Ankimon.menu_buttons.update_mobile_badge") as mock_update_badge:

        mock_gen_random.return_value = (
            "Pikachu", 25, 5, "Run Away", ["Electric"], 
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium", 
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        res = bridge.resolveNext()
        assert bridge._current_pending_outcome is not None
        
        # Test Catch choice
        commit_res = bridge.commitReplayOutcome("catch")
        assert commit_res["success"] is True
        assert commit_res["outcome"] == "caught"
        assert "cp" in commit_res
        assert isinstance(commit_res["cp"], int)
        assert mock_save_caught.call_count == 1
        assert bridge._current_pending_outcome is None

        # Verify history is correctly saved
        history = db.get_mobile_history()
        assert len(history) == 1
        assert history[0]["enemy_name"] == "Pikachu"
        assert history[0]["outcome"] == "caught"


def test_mobile_queue_cap(temp_env):
    db, tmp_path = temp_env
    col = MagicMock()
    # Watermark initially at 0.
    db.set_mobile_watermark(0)
    
    # Generate 10001 mock reviews.
    mock_reviews = [
        (i, 1000 + i, 3, 10000, 1) for i in range(1, 10002)
    ]
    col.db.all.return_value = mock_reviews
    col.db.scalar.return_value = 10001

    settings_obj = MagicMock()
    settings_obj.get.return_value = True

    logger = MagicMock()

    clear_desktop_session()

    newly_queued = process_mobile_reviews_after_sync(col, db, settings_obj, logger)

    # We expect exactly 10,000 to be queued.
    assert newly_queued == 10000
    assert db.get_pending_mobile_count() == 10000

    # Let's verify that the oldest review (ID 1) was discarded and ID 2 to 10001 are queued.
    rows = db.execute("SELECT revlog_id FROM pending_mobile_battles ORDER BY revlog_id ASC").fetchall()
    queued_ids = [r[0] for r in rows]
    assert 1 not in queued_ids
    assert queued_ids[0] == 2
    assert queued_ids[-1] == 10001


def test_load_active_team_clones_fallback():
    from Ankimon.functions.mobile_sync import load_active_team_clones
    from Ankimon.pyobj.pokemon_obj import PokemonObject

    # Given an empty team, return a clone of main_pokemon
    main_pokemon = PokemonObject(
        type=["Fire"], name="Charmander", id=4, shiny=False, level=5, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Starter", individual_id="charmander-id"
    )
    settings = MagicMock()
    settings.get.return_value = []

    db = MagicMock()
    db.get_team.return_value = []

    clones = load_active_team_clones(db, settings, main_pokemon)
    assert len(clones) == 1
    assert clones[0].name == "Charmander"
    assert clones[0].hp == clones[0].max_hp


def test_load_active_team_clones_inactive_filter():
    from Ankimon.functions.mobile_sync import load_active_team_clones
    from Ankimon.pyobj.pokemon_obj import PokemonObject

    main_pokemon = PokemonObject(
        type=["Fire"], name="Charmander", id=4, shiny=False, level=5, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Starter", individual_id="charmander-id"
    )
    settings = MagicMock()
    settings.get.return_value = ["pkmn-2"] # pkmn-2 is inactive

    db = MagicMock()
    db.get_team.return_value = [
        {"individual_id": "pkmn-1"},
        {"individual_id": "pkmn-2"},
        {"individual_id": "pkmn-3"},
    ]
    db.get_pokemon_by_individual_id.side_effect = lambda uid: {
        "type": ["Normal"], "name": uid, "id": 19, "shiny": False, "level": 10, "ability": "Run Away",
        "gender": "F", "growth_rate": "Medium", "captured_date": None, "tier": "Normal", "individual_id": uid
    }

    clones = load_active_team_clones(db, settings, main_pokemon)
    # Expected only pkmn-1 and pkmn-3
    assert len(clones) == 2
    assert clones[0].name == "pkmn-1"
    assert clones[1].name == "pkmn-3"


def test_select_best_companion_type_score():
    from Ankimon.functions.mobile_sync import select_best_companion
    from Ankimon.pyobj.pokemon_obj import PokemonObject
    from unittest.mock import patch

    # Fire companion with Fire move (Ember)
    p_fire = PokemonObject(
        type=["Fire"], name="Fire Companion", id=4, shiny=False, level=10, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="1",
        attacks=["Ember"]
    )
    # Water companion with Water move (Water Gun)
    p_water = PokemonObject(
        type=["Water"], name="Water Companion", id=7, shiny=False, level=10, ability="Torrent",
        gender="F", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="2",
        attacks=["Water Gun"]
    )
    
    # Enemy is Fire-type
    enemy = PokemonObject(
        type=["Fire"], name="Enemy Fire", id=4, shiny=False, level=10, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="enemy"
    )

    with patch("Ankimon.business.type_compatibility_multiplier") as mock_mult, \
         patch("Ankimon.business._load_type_chart", return_value={}), \
         patch("Ankimon.business.calculate_cp_from_dict", return_value=100):
        mock_mult.side_effect = lambda attacker, defender: 2.0 if "Water" in attacker else 0.5
        best = select_best_companion([p_fire, p_water], enemy)
        assert best.name == "Water Companion"


def test_select_best_companion_cp_beats_type_advantage():
    from Ankimon.functions.mobile_sync import select_best_companion
    from Ankimon.pyobj.pokemon_obj import PokemonObject
    from unittest.mock import patch

    # Companion A: Level 80 Mewtwo with Confusion, Psychic moves, and high base stats
    p_a = PokemonObject(
        type=["Psychic"], name="Psychic Companion", id=150, shiny=False, level=80, ability="Pressure",
        gender="N", growth_rate="Slow", captured_date=None, tier="Legendary", individual_id="1",
        base_stats={"hp": 106, "atk": 110, "def": 90, "spa": 154, "spd": 90, "spe": 130},
        attacks=["Confusion"]
    )
    # Companion B: Level 36 Blastoise with Water Gun, Water moves, and lower base stats
    p_b = PokemonObject(
        type=["Water"], name="Water Companion", id=9, shiny=False, level=36, ability="Torrent",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="2",
        base_stats={"hp": 79, "atk": 83, "def": 100, "spa": 85, "spd": 105, "spe": 78},
        attacks=["Water Gun"]
    )

    enemy = PokemonObject(
        type=["Fire"], name="Enemy Fire", id=4, shiny=False, level=10, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="enemy"
    )

    with patch("Ankimon.business.type_compatibility_multiplier") as mock_mult, \
         patch("Ankimon.business._load_type_chart", return_value={}), \
         patch("Ankimon.business.calculate_cp_from_dict") as mock_cp:
        
        mock_cp.side_effect = lambda d: 8000 if d.get("name") == "Psychic Companion" else 3000
        mock_mult.side_effect = lambda attacker, defender: 1.5 if "Water" in attacker else 1.0

        best = select_best_companion([p_a, p_b], enemy)
        assert best.name == "Psychic Companion"


def test_enemy_level_uses_team_max_not_main_pokemon(temp_env):
    db, tmp_path = temp_env
    from Ankimon.functions.mobile_sync import simulate_pending_mobile_battles
    from Ankimon.pyobj.pokemon_obj import PokemonObject
    from unittest.mock import patch, MagicMock
    from aqt import mw

    mw.ankimon_db = db
    p_main = PokemonObject(
        type=["Fire"], name="Main", id=4, shiny=False, level=30, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="main"
    )
    p_team1 = PokemonObject(
        type=["Fire"], name="Team1", id=4, shiny=False, level=80, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="1"
    )
    p_team2 = PokemonObject(
        type=["Water"], name="Team2", id=7, shiny=False, level=60, ability="Torrent",
        gender="F", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="2"
    )

    pending_reviews = [{"id": 1, "ease": 3, "revlog_id": 100}]

    with patch("Ankimon.functions.mobile_sync.load_active_team_clones", return_value=[p_team1, p_team2]), \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen:
        
        mock_gen.return_value = (
            "Pikachu", 25, 80, "Run Away", ["Electric"],
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium",
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        simulate_pending_mobile_battles(
            pending_reviews, p_main, settings_obj=None,
            trainer_card=None, ankimon_tracker_obj=None, ankimon_db=db
        )

        # Assert generate_random_pokemon was called with max level of team clones (80), not main pokemon (30)
        assert mock_gen.call_args[0][0] == 80


def test_select_best_companion_all_fainted_revives():
    from Ankimon.functions.mobile_sync import select_best_companion
    from Ankimon.pyobj.pokemon_obj import PokemonObject

    p1 = PokemonObject(
        type=["Fire"], name="P1", id=4, shiny=False, level=10, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="1"
    )
    p1.hp = 0
    p1.current_hp = 0

    p2 = PokemonObject(
        type=["Water"], name="P2", id=7, shiny=False, level=10, ability="Torrent",
        gender="F", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="2"
    )
    p2.hp = 0
    p2.current_hp = 0

    enemy = PokemonObject(
        type=["Grass"], name="Enemy", id=1, shiny=False, level=10, ability="Overgrow",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="enemy"
    )

    best = select_best_companion([p1, p2], enemy)
    assert best is not None
    # Verify both clones revived to full max_hp
    assert p1.hp == p1.max_hp
    assert p2.hp == p2.max_hp


def test_mobile_bridge_resolve_next_companion_override(temp_env):
    db, tmp_path = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw

    mw.ankimon_db = db
    mw.main_pokemon = MagicMock()
    mw.main_pokemon.name = "Charizard"
    mw.main_pokemon.level = 50
    mw.main_pokemon.id = 6
    mw.main_pokemon.shiny = False
    mw.main_pokemon.gender = "M"
    mw.main_pokemon.attacks = ["Slash"]

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_wishlist": [],
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.xp_multiplier": 1.5,
        "controls.allow_to_choose_moves": False,
        "trainer.cash_reward_interval": 5,
        "trainer.cash_reward_amount": 10,
        "misc.language": 0,
        "mobile.inactive_companions": []
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    mw.settings_obj = settings_mock

    # Setup a team of two in the mock DB
    db.get_team = MagicMock(return_value=[
        {"individual_id": "pkmn-1"},
        {"individual_id": "pkmn-2"}
    ])
    
    def get_pkmn_by_id_mock(uid):
        if uid == "pkmn-1":
            return {"type": ["Grass"], "name": "Bulbasaur", "id": 1, "shiny": False, "level": 10, "ability": "Overgrow",
                    "gender": "M", "growth_rate": "Medium", "captured_date": None, "tier": "Normal", "individual_id": "pkmn-1"}
        else:
            return {"type": ["Fire"], "name": "Charmander", "id": 4, "shiny": False, "level": 10, "ability": "Blaze",
                    "gender": "M", "growth_rate": "Medium", "captured_date": None, "tier": "Normal", "individual_id": "pkmn-2"}

    db.get_pokemon_by_individual_id = MagicMock(side_effect=get_pkmn_by_id_mock)

    bridge = MobileBridge(MagicMock())

    reviews = [
        {"id": 901, "cid": 1001, "ease": 1, "time": 10000, "type": 1},
        {"id": 902, "cid": 1002, "ease": 3, "time": 10000, "type": 1},
    ]
    db.queue_mobile_battles(reviews)

    from unittest.mock import patch
    with patch("Ankimon.functions.encounter_functions.save_main_pokemon_progress"), \
         patch("Ankimon.functions.encounter_functions.save_caught_pokemon"), \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")), \
         patch("Ankimon.functions.pokedex_functions.get_pokemon_diff_lang_name", side_effect=lambda pid, lang: "Charmander" if pid == 4 else "Bulbasaur"), \
         patch("Ankimon.menu_buttons.update_mobile_badge"):

        mock_gen_random.return_value = (
            "Pikachu", 25, 5, "Run Away", ["Electric"], 
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium", 
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        # Force resolveNext with "pkmn-2" (Charmander override)
        res = bridge.resolveNext("pkmn-2")
        
        assert res is not None
        assert res["companion_id"] == "pkmn-2"
        assert res["companion_name"] == "Charmander"


def test_companion_fainting_resolves_battle(temp_env):
    db, tmp_path = temp_env
    from Ankimon.functions.mobile_sync import simulate_pending_mobile_battles
    from Ankimon.pyobj.pokemon_obj import PokemonObject
    from unittest.mock import patch, MagicMock
    from aqt import mw

    mw.ankimon_db = db

    p_main = PokemonObject(
        type=["Fire"], name="Main", id=4, shiny=False, level=30, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="main"
    )
    p_main.hp = 0

    pending_reviews = [{"id": 1, "ease": 3, "revlog_id": 100}]

    with patch("Ankimon.functions.mobile_sync.load_active_team_clones", return_value=[p_main]), \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine") as mock_sim:
        
        def sim_effect(companion, enemy, *args):
            companion.hp = 0
            return (None, None, None, None, 1)
        mock_sim.side_effect = sim_effect

        mock_gen.return_value = (
            "Pikachu", 25, 30, "Run Away", ["Electric"],
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium",
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        res = simulate_pending_mobile_battles(
            pending_reviews, p_main, settings_obj=None,
            trainer_card=None, ankimon_tracker_obj=None, ankimon_db=db
        )

        assert res["encounters"] == 1
        assert len(res["caught"]) == 0


def test_resolve_chunk_limit(temp_env):
    """Verify that resolveChunk resolves battles in chunks up to a limit and returns appropriate state keys."""
    db, tmp_path = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw

    mw.ankimon_db = db
    mw.main_pokemon = MagicMock(name="Charizard", level=50)
    
    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "trainer.cash_reward_interval": 5,
        "trainer.cash_reward_amount": 10,
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(key, default)
    mw.settings_obj = settings_mock
    
    # Queue 10 reviews
    reviews = [
        {"id": i, "cid": 1000 + i, "ease": 3, "time": 10000, "type": 1}
        for i in range(1, 11)
    ]
    db.queue_mobile_battles(reviews)
    assert db.get_pending_mobile_count() == 10

    bridge = MobileBridge(MagicMock())

    from unittest.mock import patch
    with patch("Ankimon.functions.encounter_functions.save_main_pokemon_progress"), \
         patch("Ankimon.functions.encounter_functions.save_caught_pokemon"), \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine") as mock_sim:
        
        mock_gen.return_value = (
            "Pikachu", 25, 30, "Run Away", ["Electric"],
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium",
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )
        mock_sim.return_value = (None, None, None, None, 1)

        # Resolve first chunk of 4 reviews (2 encounters)
        res1 = bridge.resolveChunk(4)
        assert res1["success"] is True
        assert res1["reviews_processed"] == 4
        assert res1["done"] is False
        assert db.get_pending_mobile_count() == 6

        # Resolve second chunk of 10 reviews (more than remaining 6)
        res2 = bridge.resolveChunk(10)
        assert res2["success"] is True
        assert res2["reviews_processed"] == 6
        assert res2["done"] is True
        assert db.get_pending_mobile_count() == 0


def test_dynamic_total_reviews_calculation(temp_env):
    """Verify that temp_tracker.total_reviews correctly accounts for unresolved and resolved reviews,
    and increments card-by-card."""
    db, tmp_path = temp_env
    from Ankimon.functions.mobile_sync import simulate_pending_mobile_battles
    from aqt import mw
    from unittest.mock import MagicMock, patch

    mw.ankimon_db = db
    mw.col = MagicMock()
    mw.col.sched.day_cutoff = 1000000  # Cutoff timestamp in seconds
    cutoff_ms = (1000000 - 86400) * 1000

    # Let's insert some mock records into pending_mobile_battles.
    # 2 unresolved from today (revlog_id >= cutoff_ms)
    # 2 unresolved from yesterday (revlog_id < cutoff_ms)
    # 2 resolved today from yesterday's reviews (resolved=1, resolved_at >= cutoff_ms, revlog_id < cutoff_ms)
    db.execute("DELETE FROM pending_mobile_battles")
    db.execute(
        "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at, resolved, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cutoff_ms + 1000, 1, 3, 1000, 1, cutoff_ms + 1000, 0, None)
    )
    db.execute(
        "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at, resolved, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cutoff_ms + 2000, 2, 3, 1000, 1, cutoff_ms + 2000, 0, None)
    )
    db.execute(
        "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at, resolved, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cutoff_ms - 1000, 3, 3, 1000, 1, cutoff_ms - 1000, 0, None)
    )
    db.execute(
        "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at, resolved, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cutoff_ms - 2000, 4, 3, 1000, 1, cutoff_ms - 2000, 0, None)
    )
    db.execute(
        "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at, resolved, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cutoff_ms - 3000, 5, 3, 1000, 1, cutoff_ms - 3000, 1, cutoff_ms + 500)
    )
    db.execute(
        "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at, resolved, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cutoff_ms - 4000, 6, 3, 1000, 1, cutoff_ms - 4000, 1, cutoff_ms + 600)
    )

    tracker_mock = MagicMock()
    # Say today's get_total_reviews() from revlog is 10
    tracker_mock.get_total_reviews.return_value = 10

    main_pokemon = MagicMock()
    main_pokemon.level = 10
    
    captured_trackers = []
    def mock_gen(level, tracker):
        captured_trackers.append(tracker.get_total_reviews())
        return (
            "Pikachu", 25, level, "Run Away", ["Electric"],
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium",
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

    reviews_to_simulate = [
        {"id": 1, "revlog_id": cutoff_ms + 1000, "card_id": 1, "ease": 3},
        {"id": 2, "revlog_id": cutoff_ms + 2000, "card_id": 2, "ease": 3},
        {"id": 3, "revlog_id": cutoff_ms - 1000, "card_id": 3, "ease": 3},
        {"id": 4, "revlog_id": cutoff_ms - 2000, "card_id": 4, "ease": 3},
    ]

    def mock_sim(companion, enemy, *args, **kwargs):
        enemy.hp = 0
        return (None, None, None, None, 1)

    with patch("Ankimon.functions.encounter_functions.generate_random_pokemon", side_effect=mock_gen), \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_sim):
        simulate_pending_mobile_battles(
            reviews_to_simulate, main_pokemon, settings_obj=None,
            trainer_card=None, ankimon_tracker_obj=tracker_mock, ankimon_db=db
        )

    # Initial reviews calculation:
    # get_total_reviews() (10) - unresolved_today (2) + resolved_today_past (2) = 10.
    # First encounter is generated when loop is on review 2, so count incremented to 12.
    # Second encounter is generated on review 4, so count incremented to 14.
    assert len(captured_trackers) == 2
    assert captured_trackers[0] == 12
    assert captured_trackers[1] == 14



"""Mobile/web reviews engine tests (database + detection + simulation + bridge).

Adapted to main's seams: the engine lives in ``Ankimon.functions.mobile_sync``
and the (deferred) web-shell ``MobileBridge`` is replaced by the headless
``tests.mobile_engine_helpers.MobileBridge`` that delegates to that engine.
"""

import os
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_src = Path(__file__).parent.parent / "src"


class FakePokemon:
    def __init__(self, **kwargs):
        self.individual_id = kwargs.get("individual_id", "active-uuid")
        self.name = kwargs.get("name", "Pikachu")
        self.display_name = self.name
        self.id = kwargs.get("id", 25)
        self.level = kwargs.get("level", 30)
        self.attacks = kwargs.get("attacks", ["Thunderbolt"])
        self.hp = kwargs.get("hp", 100)
        self.max_hp = kwargs.get("max_hp", 100)
        self.type = kwargs.get("type", ["Electric"])
        self.base_stats = kwargs.get("base_stats", {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90})
        self.stats = kwargs.get("stats", {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90})
        self.ev = kwargs.get("ev", {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0})
        self.iv = kwargs.get("iv", {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15})
        self.ev_yield = kwargs.get("ev_yield", {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0})
        self.tier = kwargs.get("tier", "normal")
        self.shiny = kwargs.get("shiny", False)
        self.held_item = kwargs.get("held_item", None)
        self.gender = kwargs.get("gender", "M")
        self.ability = kwargs.get("ability", "Static")
        self.growth_rate = kwargs.get("growth_rate", "medium-fast")
        self.friendship = kwargs.get("friendship", 50)
        self.everstone = kwargs.get("everstone", False)
        self.evolution_rejected = kwargs.get("evolution_rejected", False)
        self.pokemon_defeated = kwargs.get("pokemon_defeated", 0)
        self.is_favorite = kwargs.get("is_favorite", False)
        self.xp = kwargs.get("xp", 0)

    def invalidate_cp_cache(self):
        pass

    def to_dict(self):
        return {
            "individual_id": self.individual_id,
            "name": self.name,
            "id": self.id,
            "level": self.level,
            "ability": self.ability,
            "type": self.type,
            "base_stats": self.base_stats,
            "stats": self.stats,
            "attacks": self.attacks,
            "base_experience": 112,
            "growth_rate": self.growth_rate,
            "ev": self.ev,
            "iv": self.iv,
            "gender": self.gender,
            "battle_status": "Fighting",
            "ev_yield": self.ev_yield,
            "friendship": self.friendship,
            "everstone": self.everstone,
            "evolution_rejected": self.evolution_rejected,
            "pokemon_defeated": self.pokemon_defeated,
            "is_favorite": self.is_favorite,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "shiny": self.shiny,
            "tier": self.tier,
            "held_item": self.held_item,
            "xp": self.xp,
        }


# Import test_database_manager first (its setup_mocks() writes over sys.modules);
# we re-establish real-path Ankimon packages + a real-PyQt6 aqt afterwards.
from tests.test_database_manager import MockLogger, temp_env  # noqa: E402,F401

from tests._mobile_env import (  # noqa: E402
    setup_engine_env,
    import_engine,
    snapshot_host_modules,
    restore_host_modules,
)

# Bind the names at import (so static checkers see them defined), then restore the
# host modules immediately so collection leaves no mocked aqt/Ankimon for other
# test files. The autouse fixture re-establishes the env + re-binds these to the
# freshly imported engine right before this module's tests run.
_snap = snapshot_host_modules()
setup_engine_env(_src)
from Ankimon.functions.mobile_sync import (  # noqa: E402
    record_desktop_review,
    get_desktop_session_revlog_ids,
    clear_desktop_session,
    detect_mobile_reviews,
    process_mobile_reviews_after_sync,
    MOBILE_QUEUE_CAP,  # noqa: F401
    simulate_pending_mobile_battles,  # noqa: F401
)
from tests.mobile_engine_helpers import MobileBridge  # noqa: E402
restore_host_modules(_snap)


@pytest.fixture(scope="module", autouse=True)
def _engine_env():
    snap = snapshot_host_modules()
    setup_engine_env(_src)
    import_engine(globals())
    yield
    restore_host_modules(snap)


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

    desktop_ids = frozenset({202})  # 202 was done on desktop
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
    settings_obj.get.return_value = True  # mobile.enabled = True

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
    from tests._mobile_env import load_real_menu_buttons
    menu = load_real_menu_buttons(_src)

    mock_menu = MagicMock()
    mock_game_menu = MagicMock()
    mock_action = MagicMock()

    # Mocking translator translate
    from aqt import mw
    mw.translator = MagicMock()
    mw.translator.translate.return_value = "Game"

    menu._ankimon_menu = mock_menu
    menu._ankimon_menu_base_title = "&Ankimon"
    menu.game_menu = mock_game_menu
    menu._mobile_battles_action = mock_action

    update_mobile_badge = menu.update_mobile_badge

    # Test count > 0 shows badge in Game and Mobile Battles menu items
    update_mobile_badge(47)
    mock_menu.setTitle.assert_called_with("&Ankimon")
    mock_game_menu.setTitle.assert_called_with("(47) Game")
    mock_action.setText.assert_called_with("(47) Mobile and Web Reviews")

    # Test count = 0 removes badge
    update_mobile_badge(0)
    mock_menu.setTitle.assert_called_with("&Ankimon")
    mock_game_menu.setTitle.assert_called_with("Game")
    mock_action.setText.assert_called_with("Mobile and Web Reviews")


def test_mobile_bridge(temp_env):
    db, tmp_path = temp_env
    from aqt import mw

    # Set singletons on mw mock
    mw.ankimon_db = db
    mw.main_pokemon = FakePokemon(name="Charizard", level=50, id=6, attacks=["Slash"])

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
    from aqt import mw

    # Set singletons on mw mock
    mw.ankimon_db = db
    mw.main_pokemon = FakePokemon(name="Charizard", level=50, id=6, attacks=["Slash"], individual_id=1003)

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
    with patch("Ankimon.functions.encounter_functions.save_main_pokemon_progress") as mock_save_progress, \
         patch("Ankimon.functions.encounter_functions.save_caught_pokemon") as mock_save_caught, \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")), \
         patch("Ankimon.menu_buttons.update_mobile_badge") as mock_update_badge, \
         patch("Ankimon.business.calculate_cp_from_dict", return_value=100):

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

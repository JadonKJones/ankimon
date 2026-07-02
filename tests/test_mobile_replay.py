"""
Tests for Phase 6: MobileBridge.resolveNext() single-battle resolution.
"""
import pytest
import time
import sqlite3
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

# ── bootstrap Anki module mocks ─────────────────────────────────────────────
import sys

@pytest.fixture(scope="module", autouse=True)
def cleanup_sys_modules():
    _original_sys_modules = {k: v for k, v in sys.modules.items() if k.startswith("aqt") or k.startswith("anki")}
    yield
    # Restore sys.modules to original state after this module finishes
    for k in list(sys.modules):
        if k.startswith("PyQt6") or k.startswith("aqt") or k.startswith("anki"):
            if k in _original_sys_modules:
                sys.modules[k] = _original_sys_modules[k]
            else:
                del sys.modules[k]

_src = Path(__file__).parent.parent / "src"


def setup_mocks():
    # Mock aqt/anki namespaces
    for name in [
        "aqt", "aqt.qt", "aqt.utils", "aqt.gui_hooks", "aqt.operations", 
        "aqt.reviewer", "aqt.webview", "aqt.main", "aqt.theme", "aqt.operations.QueryOp",
        "anki", "anki.hooks", "anki.collection", "anki.models", "anki.notes", "anki.template", "anki.buildinfo"
    ]:
        if name not in sys.modules or isinstance(sys.modules[name], MagicMock):
            sys.modules[name] = MagicMock()
    
    # Stub parent packages so relative imports resolve without loading __init__.py
    for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj", "Ankimon.ankimon_items_web"):
        if _pkg not in sys.modules:
            _mod = types.ModuleType(_pkg)
            _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
            _mod.__package__ = _pkg
            sys.modules[_pkg] = _mod
        elif isinstance(sys.modules[_pkg], MagicMock):
            # If it was mocked, restore it to a real module type so we can load submodules
            _mod = types.ModuleType(_pkg)
            _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
            _mod.__package__ = _pkg
            sys.modules[_pkg] = _mod

setup_mocks()

mw_mock = MagicMock()
sys.modules["aqt"].mw = mw_mock


def _make_db(path):
    """Create a minimal ankimon.db with the pending_mobile_battles table."""
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_mobile_battles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            revlog_id INTEGER UNIQUE NOT NULL,
            card_id INTEGER NOT NULL,
            ease INTEGER NOT NULL,
            review_time INTEGER NOT NULL,
            review_type INTEGER NOT NULL,
            queued_at INTEGER NOT NULL,
            resolved INTEGER NOT NULL DEFAULT 0,
            resolved_at INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


def _insert_pending(path, n=3):
    """Insert n fake pending battles."""
    now = int(time.time() * 1000)
    conn = sqlite3.connect(path)
    for i in range(n):
        conn.execute(
            "INSERT OR IGNORE INTO pending_mobile_battles "
            "(revlog_id, card_id, ease, review_time, review_type, queued_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (now + i, 1000 + i, 3, 5000, 1, now)
        )
    conn.commit()
    conn.close()


def _count_resolved(path):
    conn = sqlite3.connect(path)
    val = conn.execute("SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved=1").fetchone()[0]
    conn.close()
    return val


def _count_pending(path):
    conn = sqlite3.connect(path)
    val = conn.execute("SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved=0").fetchone()[0]
    conn.close()
    return val


class TestResolveNext:
    def test_resolve_next_marks_one_resolved(self, tmp_path):
        """resolveNext() resolves exactly one encounter's worth of reviews."""
        db_path = tmp_path / "ankimon.db"
        _make_db(db_path)
        _insert_pending(db_path, n=6)  # 6 reviews, cards_per_round=2 → 3 encounters

        # We just verify DB-level behaviour without running the full Anki battle stack.
        # Instead we test the queue dequeue logic by calling get_next_pending_batch directly.
        from src.Ankimon.pyobj.database_manager import AnkimonDB
        db = AnkimonDB(db_path=db_path)
        batch = db.get_next_pending_mobile_batch(limit=2)
        assert len(batch) == 2
        ids = [r["queue_id"] for r in batch] # keys in get_next_pending_mobile_batch are ["queue_id", ...]
        now_ms = int(time.time() * 1000)
        with db._get_connection() as conn:
            conn.execute(
                f"UPDATE pending_mobile_battles SET resolved=1, resolved_at=? WHERE id IN ({','.join('?'*len(ids))})",
                [now_ms] + ids
            )
        assert _count_resolved(db_path) == 2
        assert _count_pending(db_path) == 4

    def test_resolve_next_returns_done_when_empty(self, tmp_path):
        """If queue is empty, resolveNext must return {done: True}."""
        # This is a contract test. We test the return value contract by checking
        # that get_next_pending_batch returns [] on an empty queue.
        db_path = tmp_path / "ankimon.db"
        _make_db(db_path)
        from src.Ankimon.pyobj.database_manager import AnkimonDB
        db = AnkimonDB(db_path=db_path)
        batch = db.get_next_pending_mobile_batch(limit=2)
        assert batch == []

    def test_pending_count_decrements_after_each_resolve(self, tmp_path):
        """Each resolve call decrements the pending count by cards_per_round."""
        db_path = tmp_path / "ankimon.db"
        _make_db(db_path)
        _insert_pending(db_path, n=4)
        from src.Ankimon.pyobj.database_manager import AnkimonDB
        db = AnkimonDB(db_path=db_path)
        
        # Simulate two sequential single resolves (2 reviews each)
        for _ in range(2):
            batch = db.get_next_pending_mobile_batch(limit=2)
            if not batch:
                break
            ids = [r["queue_id"] for r in batch]
            now_ms = int(time.time() * 1000)
            with db._get_connection() as conn:
                conn.execute(
                    f"UPDATE pending_mobile_battles SET resolved=1, resolved_at=? WHERE id IN ({','.join('?'*len(ids))})",
                    [now_ms] + ids
                )
        assert _count_resolved(db_path) == 4
        assert _count_pending(db_path) == 0


@patch("src.Ankimon.ankimon_items_web.shop_obj.mw")
def test_toggle_mobile_companion(mock_mw):
    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.get.return_value = ["id-1", "id-2"]
    mock_mw.settings_obj = mock_settings

    # Import MobileBridge locally
    from src.Ankimon.ankimon_items_web.shop_obj import MobileBridge
    bridge = MobileBridge(window=MagicMock())

    # Toggle existing ID -> should remove it
    res1 = bridge.toggleMobileCompanion("id-1")
    assert res1["success"] is True
    assert "id-1" not in res1["inactive"]
    mock_settings.set.assert_called_with("mobile.inactive_companions", ["id-2"])

    # Toggle new ID -> should add it
    mock_settings.get.return_value = ["id-2"]
    res2 = bridge.toggleMobileCompanion("id-3")
    assert res2["success"] is True
    assert "id-3" in res2["inactive"]
    mock_settings.set.assert_called_with("mobile.inactive_companions", ["id-2", "id-3"])




def test_encounter_seeding_alignment_with_simulation(tmp_path, qtbot):
    """
    Verify that simulate_pending_mobile_battles and resolveNext seed the
    first encounter identically, resulting in the same Pokemon name/species.
    """
    from aqt import mw
    db_path = tmp_path / "ankimon.db"
    _make_db(db_path)
    _insert_pending(db_path, n=2)  # cards_per_round = 2, so 2 reviews

    from src.Ankimon.pyobj.database_manager import AnkimonDB
    db = AnkimonDB(db_path=db_path)

    # Save original database to restore it after the test
    orig_db = getattr(mw, "ankimon_db", None)
    mw.ankimon_db = db


    
    # Mock settings
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
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False,
        "battle.daily_average": 100,
        "misc.active_region": "Kanto"
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    orig_settings = getattr(mw, "settings_obj", None)
    mw.settings_obj = settings_mock

    # Mock main pokemon
    from src.Ankimon.pyobj.pokemon_obj import PokemonObject
    orig_main = getattr(mw, "main_pokemon", None)
    mw.main_pokemon = PokemonObject(
        type=["Fire"], name="Charizard", id=6, shiny=False, level=50, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="main"
    )
    mw.main_pokemon.attacks = ["Slash"]

    import sys
    # Explicitly import both services modules to ensure they are loaded and in sys.modules
    import Ankimon.services
    try:
        import src.Ankimon.services
    except ImportError:
        pass

    for name in ("Ankimon.services", "src.Ankimon.services"):
        mod = sys.modules.get(name)
        if mod is not None:
            services_instance = getattr(mod, "services", None)
            if services_instance is not None:
                services_instance.settings = settings_mock
                services_instance.db = db
                services_instance.main_pokemon = mw.main_pokemon

    # Monkeypatch PokemonObject.display_name on ALL loaded pokemon_obj modules in memory
    orig_displays = {}
    for module_name, module in list(sys.modules.items()):
        if module_name.endswith("pyobj.pokemon_obj") and module:
            if hasattr(module, "PokemonObject"):
                cls = getattr(module, "PokemonObject")
                if hasattr(cls, "display_name"):
                    orig_displays[cls] = cls.display_name
                    cls.display_name = property(lambda self: self.name.title())


    # Call simulation
    from Ankimon.functions.mobile_sync import simulate_pending_mobile_battles
    
    reviews_rows = db.execute(
        "SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at FROM pending_mobile_battles WHERE resolved = 0"
    ).fetchall()
    reviews_list = [
        {
            "id": r[0],
            "revlog_id": r[1],
            "card_id": r[2],
            "ease": r[3],
            "review_time": r[4],
            "review_type": r[5],
            "queued_at": r[6],
        }
        for r in reviews_rows
    ]
    
    def mock_simulate(companion, enemy, *args, **kwargs):
        enemy.hp = 0
        return ([], None, getattr(companion, "hp", 100), 0, 1)

    try:
        with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
            sim_res = simulate_pending_mobile_battles(
                reviews_list, mw.main_pokemon, settings_mock, None, None, ankimon_db=db
            )
        sim_pokemon = sim_res["caught"][0] if sim_res["caught"] else sim_res["defeated"][0]

        # Force re-import shop_obj under clean environment
        sys.modules.pop("Ankimon.ankimon_items_web.shop_obj", None)
        import PyQt6.QtWidgets
        import aqt
        aqt.QDialog = PyQt6.QtWidgets.QDialog
        
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "Ankimon.ankimon_items_web.shop_obj", 
            _src / "Ankimon" / "ankimon_items_web" / "shop_obj.py"
        )
        shop_obj_mod = importlib.util.module_from_spec(spec)
        sys.modules["Ankimon.ankimon_items_web.shop_obj"] = shop_obj_mod
        spec.loader.exec_module(shop_obj_mod)

        AnkimonItemsWeb = shop_obj_mod.AnkimonItemsWeb


        # Instantiate AnkimonItemsWeb using a stub __init__
        mock_shop_mgr = MagicMock()
        mock_shop_mgr.todays_daily_items = []
        mock_shop_mgr.todays_daily_tms = []
        
        def stub_init(self, addon_dir, shop_manager, item_window, ankimon_tracker,
                      trainer_card=None, settings_obj=None, logger=None):
            self.addon_dir = addon_dir
            self.shop_manager = shop_manager
            self._mobile_bridge = shop_obj_mod.MobileBridge(self)

        with patch.object(AnkimonItemsWeb, "__init__", stub_init):
            web_win = AnkimonItemsWeb(
                addon_dir=Path("/tmp"),
                shop_manager=mock_shop_mgr,
                item_window=MagicMock(),
                ankimon_tracker=MagicMock(),
                trainer_card=MagicMock(),
                settings_obj=settings_mock
            )
        
        with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
            replay_res = web_win._mobile_bridge.resolveNext()
        assert "enemy_name" in replay_res, f"replay_res is: {replay_res} (type: {type(replay_res)})"
        assert replay_res["enemy_name"] == sim_pokemon["name"]
        assert replay_res["enemy_id"] == sim_pokemon["id"]
        assert replay_res["enemy_level"] == sim_pokemon["level"]
        assert replay_res["enemy_shiny"] == sim_pokemon["shiny"]
    finally:
        for cls, orig in orig_displays.items():
            cls.display_name = orig
        mw.ankimon_db = orig_db
        mw.settings_obj = orig_settings
        mw.main_pokemon = orig_main
        for name in ("Ankimon.services", "src.Ankimon.services"):
            mod = sys.modules.get(name)
            if mod is not None:
                services_instance = getattr(mod, "services", None)
                if services_instance is not None:
                    services_instance.settings = None
                    services_instance.db = None
                    services_instance.main_pokemon = None
        sys.modules.pop("Ankimon.ankimon_items_web.shop_obj", None)


def test_resolve_next_companion_override_inactive(tmp_path):
    from aqt import mw
    # Setup test DB
    db_path = tmp_path / "ankimon.db"
    _make_db(db_path)
    _insert_pending(db_path, n=2)
    
    from src.Ankimon.pyobj.database_manager import AnkimonDB
    db = AnkimonDB(db_path=db_path)
    
    # We want to insert the captured pokemon into the DB so get_pokemon will find it
    import json
    pokemon_data = {
        "type": ["Grass"],
        "name": "Bulbasaur",
        "id": 1,
        "shiny": False,
        "level": 15,
        "ability": "Overgrow",
        "gender": "M",
        "growth_rate": "Medium",
        "captured_date": None,
        "tier": "Normal",
        "individual_id": "inactive-bulba",
        "base_stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "attacks": ["Tackle"],
        "base_experience": 64,
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "battle_status": "Fighting",
        "ev_yield": {"hp": 1},
        "nature": "hardy"
    }
    
    with db._get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS captured_pokemon (
                individual_id TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        conn.execute(
            "INSERT INTO captured_pokemon (individual_id, data) VALUES (?, ?)",
            ("inactive-bulba", json.dumps(pokemon_data))
        )
        conn.execute("""
            CREATE TABLE IF NOT EXISTS team (
                slot_position INTEGER PRIMARY KEY,
                individual_id TEXT NOT NULL
            )
        """)
        # bulba is in team
        conn.execute("INSERT INTO team (slot_position, individual_id) VALUES (?, ?)", (1, "inactive-bulba"))
    
    orig_db = getattr(mw, "ankimon_db", None)
    mw.ankimon_db = db
    
    # settings: battle.cards_per_round = 2, bulba is inactive
    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "mobile.inactive_companions": ["inactive-bulba"]
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(key, default)
    
    orig_settings = getattr(mw, "settings_obj", None)
    mw.settings_obj = settings_mock
    
    orig_main = getattr(mw, "main_pokemon", None)
    mw.main_pokemon = None
    
    orig_tracker = getattr(mw, "ankimon_tracker_obj", None)
    mw.ankimon_tracker_obj = None
    
    try:
        # Import / load MobileBridge
        sys.modules.pop("Ankimon.ankimon_items_web.shop_obj", None)
        import PyQt6.QtWidgets
        import aqt
        aqt.QDialog = PyQt6.QtWidgets.QDialog
        
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "Ankimon.ankimon_items_web.shop_obj", 
            _src / "Ankimon" / "ankimon_items_web" / "shop_obj.py"
        )
        shop_obj_mod = importlib.util.module_from_spec(spec)
        sys.modules["Ankimon.ankimon_items_web.shop_obj"] = shop_obj_mod
        spec.loader.exec_module(shop_obj_mod)
        
        bridge = shop_obj_mod.MobileBridge(window=MagicMock())
        
        # Mock simulate battle to check if our Bulbasaur is used
        def mock_simulate(companion, enemy, *args, **kwargs):
            enemy.hp = 0
            return ([], None, getattr(companion, "hp", 100), 0, 1)
            
        with patch("src.Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
            res = bridge.resolveNext("inactive-bulba")
            
        assert res is not None
        assert res.get("companion_id") == "inactive-bulba"
        assert res.get("companion_name") == "Bulbasaur"
    finally:
        mw.ankimon_db = orig_db
        mw.settings_obj = orig_settings
        mw.main_pokemon = orig_main
        mw.ankimon_tracker_obj = orig_tracker
        sys.modules.pop("Ankimon.ankimon_items_web.shop_obj", None)


def test_multi_turn_encounter_seeding_alignment(tmp_path):
    """
    Verify that if Encounter 0 takes multiple turns (e.g. 4 reviews),
    the next generated encounter's seed matches the second encounter in the preview list
    and is not skipped or shifted.
    """
    from aqt import mw
    db_path = tmp_path / "ankimon.db"
    _make_db(db_path)
    _insert_pending(db_path, n=6)  # cards_per_round = 2, so 6 reviews total

    from src.Ankimon.pyobj.database_manager import AnkimonDB
    db = AnkimonDB(db_path=db_path)

    orig_db = getattr(mw, "ankimon_db", None)
    mw.ankimon_db = db

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
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(key, default)
    orig_settings = getattr(mw, "settings_obj", None)
    mw.settings_obj = settings_mock

    from src.Ankimon.pyobj.pokemon_obj import PokemonObject
    orig_main = getattr(mw, "main_pokemon", None)
    mw.main_pokemon = PokemonObject(
        type=["Fire"], name="Charizard", id=6, shiny=False, level=50, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="main"
    )
    mw.main_pokemon.attacks = ["Slash"]

    # In the preview simulation, we want Encounter 0 to take 2 turns (4 reviews), and Encounter 1 to take 1 turn (2 reviews).
    turn_counts = {}

    def mock_simulate(companion, enemy, *args, **kwargs):
        eid = getattr(enemy, "individual_id", "default")
        turn_counts[eid] = turn_counts.get(eid, 0) + 1
        
        # If it's the first encounter, make it faint on its 2nd turn
        # Otherwise, make it faint on its 1st turn
        if len(turn_counts) == 1:
            if turn_counts[eid] >= 2:
                enemy.hp = 0
            else:
                enemy.hp = 50
        else:
            enemy.hp = 0
            
        return ([], None, getattr(companion, "hp", 100), 0, 1)

    try:
        from src.Ankimon.functions.mobile_sync import simulate_pending_mobile_battles, resolve_next, commit_replay_outcome
        
        reviews_rows = db.execute(
            "SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at FROM pending_mobile_battles WHERE resolved = 0"
        ).fetchall()
        reviews_list = [
            {
                "id": r[0],
                "revlog_id": r[1],
                "card_id": r[2],
                "ease": r[3],
                "review_time": r[4],
                "review_type": r[5],
                "queued_at": r[6],
            }
            for r in reviews_rows
        ]

        with patch("src.Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
            sim_res = simulate_pending_mobile_battles(
                reviews_list, mw.main_pokemon, settings_mock, None, None, ankimon_db=db
            )
        
        all_preview_pokemon = sim_res["caught"] + sim_res["defeated"]
        assert len(all_preview_pokemon) == 2, f"Should have 2 preview encounters, got {len(all_preview_pokemon)}"
        preview_enc_0 = all_preview_pokemon[0]
        preview_enc_1 = all_preview_pokemon[1]

        # Now run manual replay (resolve_next)
        turn_counts.clear()
        
        with patch("src.Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
            replay_res_0 = resolve_next("main", db, settings_mock, None, None, mw.main_pokemon)
            assert replay_res_0["result"]["enemy_name"] == preview_enc_0["name"]
            
            outcome_0 = replay_res_0["current_pending_outcome"]
            commit_replay_outcome("defeat", outcome_0, db, settings_mock, None, mw.main_pokemon)
            
            resolved_in_db = db.execute("SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved=1").fetchone()[0]
            assert resolved_in_db == 4

            replay_res_1 = resolve_next("main", db, settings_mock, None, None, mw.main_pokemon)
            assert replay_res_1["result"]["enemy_name"] == preview_enc_1["name"]

    finally:
        mw.ankimon_db = orig_db
        mw.settings_obj = orig_settings
        mw.main_pokemon = orig_main











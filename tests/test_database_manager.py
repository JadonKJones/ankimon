import os
import sys
import json
import csv
import sqlite3
import pytest
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch
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
        sys.modules[name] = MagicMock()
    
    # Define a robust mock for resources
    class MockResources:
        # These are used by database_manager
        user_path = Path("/tmp")
        csv_file_items_cost = Path("/tmp/items.csv")
        items_path = Path("/tmp/items.json")
        badges_path = Path("/tmp/badges.json")
        mypokemon_path = Path("/tmp/mypokemon.json")
        mainpokemon_path = Path("/tmp/mainpokemon.json")
        def __getattr__(self, name): return Path("/tmp") / name

    # Correct package structure for sys.modules
    sys.modules["Ankimon"] = types.ModuleType("Ankimon")
    sys.modules["Ankimon.resources"] = MaskedResources = MockResources()
    sys.modules["Ankimon.singletons"] = MagicMock()
    sys.modules["Ankimon.utils"] = MagicMock()
    sys.modules["Ankimon.pyobj"] = MagicMock()

setup_mocks()

# 2. DYNAMICALLY LOAD DATABASE_MANAGER
_spec = importlib.util.spec_from_file_location(
    "Ankimon.pyobj.database_manager",
    _src / "Ankimon" / "pyobj" / "database_manager.py",
)
_db_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _db_mod
_spec.loader.exec_module(_db_mod)

from Ankimon.pyobj.database_manager import AnkimonDB

class MockLogger:
    def log(self, level, msg): pass
    def log_and_showinfo(self, level, msg): pass
    def _log(self, level, msg): pass

@pytest.fixture
def temp_env(tmp_path):
    """Setup a temporary environment for the DB and its CSV files."""
    # Patch the resources in the database_manager namespace specifically
    with patch.object(_db_mod, "user_path", tmp_path), \
         patch.object(_db_mod, "csv_file_items_cost", str(tmp_path / "items.csv")), \
         patch.object(_db_mod, "items_path", tmp_path / "items_mig.json"), \
         patch.object(_db_mod, "badges_path", tmp_path / "badges_mig.json"):
        
        # Create mock items.csv
        csv_path = tmp_path / "items.csv"
        headers = ["id", "identifier", "category_id", "cost", "fling_power", "fling_effect_id"]
        rows = [
            ["1", "master-ball", "34", "0", "", ""],
            ["30", "fresh-water", "1", "200", "", ""],
            ["20225", "dragonbreath", "37", "0", "", ""],
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        db = AnkimonDB(MockLogger())
        yield db, tmp_path

def test_database_initialization(temp_env):
    db, _ = temp_env
    conn = db._get_connection()
    cursor = conn.cursor()
    
    # Table names updated based on database_manager.py _setup_database
    tables = ["metadata", "items", "badges", "captured_pokemon", "team", "pokemon_history"]
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        assert cursor.fetchone() is not None, f"Table {table} should exist"


def test_base_stats_normalization_marker_is_internal_metadata(temp_env):
    """The startup marker must not make a virgin user-config table look populated."""
    db, _ = temp_env
    conn = db._get_connection()

    marker = conn.execute(
        "SELECT value FROM metadata WHERE key = 'base_stats_normalized'"
    ).fetchone()

    assert marker[0] == "true"
    assert db.has_config() is False
    assert db.get_all_config() == {}

def test_item_save_and_smart_sync(temp_env):
    db, tmp_path = temp_env
    # 1. First add (uses CSV to discover metadata)
    db.add_item("fresh-water", 5)
    item = db.get_item("fresh-water")
    assert item["cost"] == 200

    # 2. Second save (should use DB cache, even if CSV is gone)
    os.remove(tmp_path / "items.csv")
    db.save_item(None, "fresh-water", 10)

    item = db.get_item("fresh-water")
    assert item["quantity"] == 10
    assert item["cost"] == 200 # Preserved from DB cache

def test_tm_auto_tagging(temp_env):
    db, _ = temp_env
    # add_item looks up CSV metadata, discovering category_id=37 (TM)
    db.add_item("dragonbreath", 1)

    item = db.get_item("dragonbreath")
    assert (item.get("extra_data") or {}).get("type") == "TM"

def test_badge_schema(temp_env):
    db, _ = temp_env
    db.save_badge("1", {"achieved": True})
    
    badge = db.get_badge("1")
    assert badge["badge_id"] == "1"
    assert badge["achieved"] in [True, 1]

def test_json_migration(temp_env):
    db, tmp_path = temp_env
    
    # Setup legacy files in the paths we'll pass to migrate_from_json
    mypokemon_json = tmp_path / "mypokemon.json"
    mypokemon_json.write_text(json.dumps([]))
    
    mainpokemon_json = tmp_path / "mainpokemon.json"
    mainpokemon_json.write_text(json.dumps({}))
    
    items_json = tmp_path / "items_mig.json"
    items_json.write_text(json.dumps([{"item": "master-ball", "quantity": 1}]))
    
    badges_json = tmp_path / "badges_mig.json"
    badges_json.write_text(json.dumps(["1", "2"]))
    
    with patch("Ankimon.pyobj.database_manager.Path.is_file", return_value=True):
        db.migrate_from_json(
            mypokemon_path=mypokemon_json,
            mainpokemon_path=mainpokemon_json,
            items_path=items_json,
            badges_path=badges_json
        )
        
    # Check items
    item = db.get_item("master-ball")
    assert item["id"] == 1
    
    # Check badges
    badges = db.get_all_badges()
    achieved_ids = [b["badge_id"] for b in badges]
    assert "1" in achieved_ids
    assert "2" in achieved_ids

def test_update_item_quantity_preserves_metadata(temp_env):
    db, _ = temp_env
    db.save_item(100, "elixir", 5, category_id=10, cost=500)
    db.update_item_quantity("elixir", -2)
    
    item = db.get_item("elixir")
    assert item["quantity"] == 3
    assert item["id"] == 100
    assert item["cost"] == 500

def test_get_item_returns_empty_dict_extras(temp_env):
    db, _ = temp_env
    # Inject a row with NULL data manually to test the default extra_data logic
    conn = db._get_connection()
    conn.execute("INSERT INTO items (id, item_name, quantity, data) VALUES (999, 'null-item', 1, NULL)")
    conn.commit()

    item = db.get_item("null-item")
    assert item["extra_data"] == {} # Should be {} not None


def test_busy_timeout_set_on_gui_connection(temp_env):
    """Concurrency guard: every connection must carry the generous busy-timeout
    so a GUI-thread write does not immediately raise 'database is locked' while
    mobile-sync's bulk 'Resolve All' holds its long background write transaction.
    Without the fix the connect() default (5000ms) would be in effect."""
    db, _ = temp_env
    conn = db._get_connection()
    got = conn.execute("PRAGMA busy_timeout;").fetchone()[0]
    assert got == AnkimonDB._BUSY_TIMEOUT_MS
    assert got >= 30000


def test_busy_timeout_set_on_background_thread_connection(temp_env):
    """The per-background-thread connection (used by the bulk mobile resolve) must
    get the same busy-timeout as the GUI connection — it is the one that races.
    Force the off-GUI-thread branch of _get_connection() so the dedicated
    per-thread connection is what gets probed."""
    db, _ = temp_env
    with patch.object(_db_mod, "_is_main_thread", return_value=False):
        conn = db._get_connection()  # dedicated per-thread connection
        got = conn.execute("PRAGMA busy_timeout;").fetchone()[0]
    assert got == AnkimonDB._BUSY_TIMEOUT_MS


def test_database_corruption_self_healing(temp_env):
    """Verify that repair_database() successfully prunes duplicates (keeping the one
    with the highest progress) and recovers the unique PRIMARY KEY index constraint."""
    db, _ = temp_env
    # Save base pokemon
    pk1 = {"individual_id": "duplicate-uuid", "name": "archen", "id": 566, "level": 5, "xp": 100}
    db.save_pokemon(pk1)
    db.set_main_pokemon("duplicate-uuid")
    
    # Close connections so we can bypass constraints with a custom raw connection
    db.close()
    
    raw_conn = sqlite3.connect(str(db.db_path))
    cursor = raw_conn.cursor()
    
    # Temporarily drop constraint by renaming and copying to a non-constrained table
    cursor.execute("ALTER TABLE captured_pokemon RENAME TO captured_pokemon_old")
    cursor.execute("""
        CREATE TABLE captured_pokemon (
            individual_id TEXT,
            is_main INTEGER DEFAULT 0,
            data TEXT NOT NULL,
            name TEXT GENERATED ALWAYS AS (json_extract(data, '$.name')) VIRTUAL,
            pokedex_id INTEGER GENERATED ALWAYS AS (json_extract(data, '$.id')) VIRTUAL,
            shiny BOOLEAN GENERATED ALWAYS AS (json_extract(data, '$.shiny')) VIRTUAL,
            level INTEGER GENERATED ALWAYS AS (json_extract(data, '$.level')) VIRTUAL
        )
    """)
    cursor.execute("INSERT INTO captured_pokemon (individual_id, is_main, data) SELECT individual_id, is_main, data FROM captured_pokemon_old")
    cursor.execute("DROP TABLE captured_pokemon_old")
    
    # Insert a duplicate with a higher level (Level 34)
    pk2 = {"individual_id": "duplicate-uuid", "name": "archen", "id": 566, "level": 34, "xp": 1000}
    cursor.execute("INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)", 
                   ("duplicate-uuid", json.dumps(pk2)))
                   
    # Insert another duplicate with intermediate level (Level 30)
    pk3 = {"individual_id": "duplicate-uuid", "name": "archen", "id": 566, "level": 30, "xp": 500}
    cursor.execute("INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)", 
                   ("duplicate-uuid", json.dumps(pk3)))
    
    raw_conn.commit()
    raw_conn.close()
    
    # Trigger repair
    db.repair_database()
    
    # Reopen and check: only the highest level (Level 34) should survive, constraint must be restored
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_main, data FROM captured_pokemon WHERE individual_id = 'duplicate-uuid'")
    rows = cursor.fetchall()
    assert len(rows) == 1
    is_main, data = rows[0]
    saved_pk = json.loads(data)
    assert saved_pk["level"] == 34
    assert is_main == 1
    
    # Confirm unique constraint is back by verifying that inserting a duplicate now raises IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES ('duplicate-uuid', 0, '{}')")

def test_thread_local_connection_closes_and_reopens(temp_env):
    import threading
    db, _ = temp_env
    
    results = {}
    event_start = threading.Event()
    event_closed = threading.Event()
    
    def thread_func():
        with patch("Ankimon.pyobj.database_manager._is_main_thread", return_value=False):
            # Get connection and verify it works
            conn = db._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                assert cursor.fetchone()[0] == 1
            
            # Notify main thread
            event_start.set()
            assert event_closed.wait(timeout=5), "database close was not signaled"
            
            # Get connection again. It should be refreshed automatically
            conn2 = db._get_connection()
            with conn2.cursor() as cursor2:
                cursor2.execute("SELECT 1")
                results["success"] = (cursor2.fetchone()[0] == 1)
            
    t = threading.Thread(target=thread_func)
    t.start()
    
    assert event_start.wait(timeout=5), "worker did not initialize"
    
    # Close database from main thread
    db.close()
    
    event_closed.set()
    t.join(timeout=5)
    assert not t.is_alive(), "worker did not finish"
    
    assert results.get("success") is True


def test_close_reports_timeout_while_cursor_lease_is_active(temp_env):
    db, _ = temp_env
    conn = db._get_connection()
    cursor = conn.cursor()

    assert db.close(0.01) is False
    cursor.execute("SELECT 1")
    assert cursor.fetchone()[0] == 1

    cursor.close()
    assert conn._closed is True


def test_connection_lease_prevents_closure_during_inflight_operation(temp_env):
    import threading
    db, _ = temp_env
    
    event_paused = threading.Event()
    event_close_done = threading.Event()
    results = {}
    
    # Dynamically resolve the correct CursorWrapper class and module from the db instance
    conn = db._get_connection()
    with conn.cursor() as cursor:
        actual_cursor_wrapper_class = cursor.__class__
    db_module = sys.modules[db.__class__.__module__]
    
    original_cursor_execute = actual_cursor_wrapper_class.execute
    original_is_main_thread = db_module._is_main_thread
    
    def patched_cursor_execute(cursor_self, sql, *args, **kwargs):
        if "SELECT 'test_inflight'" in sql:
            event_paused.set()
            assert event_close_done.wait(timeout=5), "database close did not complete"
        return original_cursor_execute(cursor_self, sql, *args, **kwargs)
        
    actual_cursor_wrapper_class.execute = patched_cursor_execute
    db_module._is_main_thread = lambda: False
    
    def thread_func():
        try:
            try:
                cursor_thread = db.execute("SELECT 'test_inflight'")
                results["value"] = cursor_thread.fetchone()[0]
            except Exception as e:
                results["error"] = e
        except Exception as e:
            results["thread_error"] = str(e)
            import traceback
            results["traceback"] = traceback.format_exc()
                
    t = threading.Thread(target=thread_func)
    t.start()
    
    try:
        if not event_paused.wait(timeout=5):
            print("Thread error:", results.get("thread_error"))
            print("Traceback:", results.get("traceback"))
            assert False, f"worker did not initialize: {results.get('thread_error')}"
        
        # Close database from main thread. Since background thread holds a lease,
        # the connection closure should be deferred and the connection should stay alive.
        db.close()
        
        event_close_done.set()
        t.join(timeout=5)
        assert not t.is_alive()
        
        assert results.get("value") == "test_inflight"
        assert "error" not in results
    finally:
        actual_cursor_wrapper_class.execute = original_cursor_execute
        db_module._is_main_thread = original_is_main_thread


def test_cursor_handoff_holds_lease_before_close(temp_env):
    """Closing during cursor wrapping must not invalidate the raw cursor."""
    import threading

    db, _ = temp_env
    cursor_created = threading.Event()
    continue_wrapping = threading.Event()
    results = {}
    original_init = _db_mod.CursorWrapper.__init__

    def paused_init(cursor_self, raw_cursor, conn_wrapper, *, lease_acquired=False):
        cursor_created.set()
        assert continue_wrapping.wait(timeout=5), "cursor handoff was not resumed"
        original_init(
            cursor_self,
            raw_cursor,
            conn_wrapper,
            lease_acquired=lease_acquired,
        )

    def worker():
        try:
            with patch.object(_db_mod, "_is_main_thread", return_value=False):
                conn = db._get_connection()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    results["value"] = cursor.fetchone()[0]
        except Exception as exc:
            results["error"] = exc

    with patch.object(_db_mod.CursorWrapper, "__init__", paused_init):
        thread = threading.Thread(target=worker)
        thread.start()
        assert cursor_created.wait(timeout=5), "worker did not create its cursor"
        db.close()
        continue_wrapping.set()
        thread.join(timeout=5)
        assert not thread.is_alive(), "worker did not finish"

    assert results.get("value") == 1
    assert "error" not in results


def test_epoch_double_read_race(temp_env):
    db, _ = temp_env
    original_prepare = db._prepare_connection
    close_called = False
    
    def patched_prepare(conn):
        nonlocal close_called
        res = original_prepare(conn)
        if not close_called:
            close_called = True
            db.close()
        return res
        
    db._prepare_connection = patched_prepare
    
    import threading
    results = {}
    
    def thread_func():
        try:
            with patch("Ankimon.pyobj.database_manager._is_main_thread", return_value=False):
                conn1 = db._get_connection()
                conn2 = db._get_connection()
                with conn2.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    results["success"] = (cursor.fetchone()[0] == 1)
        except Exception as e:
            results["error"] = str(e)
            
    t = threading.Thread(target=thread_func)
    t.start()
    t.join(timeout=5)
    assert not t.is_alive()
    assert results.get("success") is True
    assert "error" not in results


def test_retry_on_closed_database_error(temp_env):
    db, _ = temp_env
    conn = db._get_connection()
    conn._conn.close()
    db._connection_epoch += 1
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1


def test_repair_aborts_when_connections_do_not_drain(temp_env):
    db, _ = temp_env

    with patch.object(db, "close", return_value=False):
        with pytest.raises(RuntimeError, match="active operations did not finish"):
            db.repair_database()

    assert db.db_path.exists()
    assert not db.db_path.with_name(db.db_path.name + ".tmp").exists()


def test_legacy_base_stats_normalization(temp_env):
    """Verify that old database entries without 'base_stats' key are normalized on repair and startup."""
    db, _ = temp_env
    # Create a pokemon with 'stats' but no 'base_stats'
    legacy_pk = {
        "individual_id": "legacy-uuid",
        "name": "pikachu",
        "id": 25,
        "level": 5,
        "xp": 100,
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "iv": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
    }

    # Save manually to bypass the save_pokemon normalization/check
    obfuscated_data = db._obfuscate(legacy_pk)
    conn = db._get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)",
            ("legacy-uuid", obfuscated_data),
        )
    conn.commit()

    # Check that it starts without base_stats
    pk_loaded = db.get_pokemon("legacy-uuid")
    assert "base_stats" not in pk_loaded

    mock_base_stats = {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90}
    with patch("Ankimon.functions.pokedex_functions.search_pokedex", return_value=mock_base_stats) as mock_search:
        db.repair_database()
    mock_search.assert_called_once_with("pikachu", "baseStats")

    # Check that base_stats was populated from pokedex lookup
    pk_repaired = db.get_pokemon("legacy-uuid")
    assert "base_stats" in pk_repaired
    assert pk_repaired["base_stats"]["hp"] == 35
    assert pk_repaired["base_stats"]["spe"] == 90


def test_base_stats_normalization_startup_sweep(temp_env):
    """The startup sweep heals legacy records without requiring a full repair."""
    db, _ = temp_env
    legacy_pk = {
        "individual_id": "legacy-uuid-2",
        "name": "pikachu",
        "id": 25,
        "level": 5,
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
    }
    conn = db._get_connection()
    conn.cursor().execute(
        "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)",
        ("legacy-uuid-2", db._obfuscate(legacy_pk))
    )
    conn.commit()

    mock_base_stats = {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90}
    with patch("Ankimon.functions.pokedex_functions.search_pokedex", return_value=mock_base_stats):
        db._normalize_pokemon_base_stats()

    assert db.get_pokemon("legacy-uuid-2")["base_stats"] == mock_base_stats


def test_unresolvable_base_stats_record_left_untouched(temp_env):
    """A record whose species is missing from the pokedex must not be modified."""
    db, _ = temp_env
    legacy_pk = {
        "individual_id": "legacy-uuid-3",
        "name": "not-a-real-species",
        "id": 9999,
        "level": 5,
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
    }
    conn = db._get_connection()
    conn.cursor().execute(
        "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)",
        ("legacy-uuid-3", db._obfuscate(legacy_pk))
    )
    conn.commit()

    with patch("Ankimon.functions.pokedex_functions.search_pokedex", return_value=[]):
        db._normalize_pokemon_base_stats()

    assert db.get_pokemon("legacy-uuid-3") == legacy_pk


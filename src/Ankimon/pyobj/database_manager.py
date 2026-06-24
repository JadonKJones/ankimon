"""
AnkimonDB - Consolidated Database Manager for Ankimon

This module provides a SQLite-based storage solution for all Ankimon game data,
replacing multiple JSON files with a single, obfuscated database file.
"""

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import csv
from ..resources import user_path, csv_file_items_cost, mypokemon_path, mainpokemon_path, items_path, badges_path, team_pokemon_path as team_path


class ConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn
        self._disable_commit = False

    def commit(self):
        if not self._disable_commit:
            self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self._conn.executemany(*args, **kwargs)

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def __enter__(self):
        if getattr(self, "_txn_depth", 0) == 0:
            self._conn.execute("BEGIN")
        self._txn_depth = getattr(self, "_txn_depth", 0) + 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._txn_depth = getattr(self, "_txn_depth", 1) - 1
        if self._txn_depth == 0:
            if exc_type is not None:
                try:
                    self._conn.rollback()
                except Exception: pass
            else:
                try:
                    self._conn.commit()
                except Exception: pass
        return False


def _is_main_thread() -> bool:
    try:
        from PyQt6.QtCore import QThread
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return True
        return QThread.currentThread() == app.thread()
    except Exception:
        return True


class AnkimonDB:
    """Handles all database operations for Ankimon. Stores data in SQLite."""
    
    DB_FILENAME = "ankimon.db"

    def __init__(self, logger=None, db_path: Optional[Union[str, Path]] = None):
        self.logger = logger
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = user_path / self.DB_FILENAME
        self._connection: Optional[ConnectionWrapper] = None
        import threading
        self._local_conn = threading.local()
        self._all_pokemon_ids_cache = None
        self._setup_database()

    def _log(self, level: str, message: str):
        """Helper for logging."""
        if self.logger:
            self.logger.log(level, message)
        else:
            print(f"[{level}] {message}")

    # --- Connection Management ---

    def _get_connection(self) -> ConnectionWrapper:
        """Gets or creates a database connection."""
        if not _is_main_thread():
            if (not hasattr(self._local_conn, "conn") or 
                self._local_conn.conn is None or 
                getattr(self._local_conn, "db_path", None) != self.db_path):
                
                if hasattr(self._local_conn, "conn") and self._local_conn.conn is not None:
                    try:
                        self._local_conn.conn.close()
                    except Exception:
                        pass
                
                conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
                conn.row_factory = sqlite3.Row  # Access columns by name
                try:
                    conn.execute("PRAGMA journal_mode=WAL;")
                    conn.execute("PRAGMA synchronous=NORMAL;")
                    conn.execute("PRAGMA temp_store=MEMORY;")
                except Exception as e:
                    self._log("warning", f"Failed to set background database PRAGMAs: {e}")
                self._local_conn.conn = ConnectionWrapper(conn)
                self._local_conn.db_path = self.db_path
            elif not isinstance(self._local_conn.conn, ConnectionWrapper):
                self._local_conn.conn = ConnectionWrapper(self._local_conn.conn)
                self._local_conn.db_path = self.db_path
            return self._local_conn.conn

        if self._connection is None:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Access columns by name
            try:
                # Check current journal mode to avoid redundant disk writes on connection open
                cursor = conn.execute("PRAGMA journal_mode;")
                current_mode = cursor.fetchone()[0]
                if current_mode.lower() != "wal":
                    conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA temp_store=MEMORY;")
            except Exception as e:
                self._log("warning", f"Failed to set database PRAGMAs: {e}")
            self._connection = ConnectionWrapper(conn)
        elif not isinstance(self._connection, ConnectionWrapper):
            self._connection = ConnectionWrapper(self._connection)
        return self._connection

    def close(self):
        """Closes the database connection."""
        if self._connection:
            try:
                self._connection.close()
            except Exception: pass
            self._connection = None
        if hasattr(self, "_local_conn"):
            if hasattr(self._local_conn, "conn") and self._local_conn.conn:
                try:
                    self._local_conn.conn.close()
                except Exception: pass
                self._local_conn.conn = None

    # --- Obfuscation / De-obfuscation ---

    def _obfuscate(self, data: Any) -> str:
        """Serializes a Python object to a JSON string. (Formerly obfuscated)"""
        return json.dumps(data, ensure_ascii=False)

    def _deobfuscate(self, data_str: str) -> Optional[Any]:
        """Deserializes a JSON string to a Python object. (Formerly deobfuscated)"""
        if not data_str:
            return None
        try:
            return json.loads(data_str)
        except Exception as e:
            self._log("error", f"Failed to load json data: {e}")
            return None

    # --- Database Setup ---

    def _setup_database(self):
        """Creates all necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # NOTE: do NOT early-return here based on a hard-coded "fully initialized"
        # table set. Every statement below is idempotent (CREATE TABLE/INDEX IF NOT
        # EXISTS, guarded ALTER TABLE), so re-running them on each init is cheap and,
        # crucially, keeps _setup_database the single place schema migrations live.
        # A short-circuit on an allow-list of table names would silently skip any
        # future migration (new column/index/table) on already-initialized DBs.

        # Table for captured pokemon (replaces mypokemon.json AND mainpokemon.json)
        # is_main flag: 0 = not main, 1 = main pokemon
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS captured_pokemon (
                individual_id TEXT PRIMARY KEY,
                is_main INTEGER DEFAULT 0,
                data TEXT NOT NULL,
                name TEXT GENERATED ALWAYS AS (json_extract(data, '$.name')) VIRTUAL,
                pokedex_id INTEGER GENERATED ALWAYS AS (json_extract(data, '$.id')) VIRTUAL,
                shiny BOOLEAN GENERATED ALWAYS AS (json_extract(data, '$.shiny')) VIRTUAL,
                level INTEGER GENERATED ALWAYS AS (json_extract(data, '$.level')) VIRTUAL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_name ON captured_pokemon(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_pokedex_id ON captured_pokemon(pokedex_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_shiny ON captured_pokemon(shiny)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_level ON captured_pokemon(level)")

        # Check if is_main column exists (for migration from old schema)
        cursor.execute("PRAGMA table_info(captured_pokemon)")
        columns = [row[1] for row in cursor.fetchall()]
        if "is_main" not in columns:
            self._log("info", "Migrating schema: adding is_main column...")
            cursor.execute("ALTER TABLE captured_pokemon ADD COLUMN is_main INTEGER DEFAULT 0")
            # Migrate data from old main_pokemon table if it exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='main_pokemon'")
            if cursor.fetchone():
                cursor.execute("SELECT individual_id, data FROM main_pokemon WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    main_id = row[0]
                    main_data = row[1]
                    # Update the existing pokemon to be main, or insert if not exists
                    cursor.execute(
                        "INSERT OR REPLACE INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 1, ?)",
                        (main_id, main_data)
                    )
                cursor.execute("DROP TABLE main_pokemon")
                self._log("info", "Migrated main_pokemon table to is_main flag")

        # Table for items (replaces items.json) - using PokeAPI integer ID as PK
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                item_name TEXT UNIQUE,
                quantity INTEGER DEFAULT 0,
                data TEXT,
                category_id INTEGER,
                cost INTEGER,
                fling_power INTEGER,
                fling_effect_id INTEGER
            )
        """)

        # Table for badges (replaces badges.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS badges (
                badge_id TEXT PRIMARY KEY,
                achieved BOOLEAN DEFAULT 0
            )
        """)

        # Metadata table for tracking migration status, etc.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Table for team composition (replaces team.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team (
                slot_position INTEGER PRIMARY KEY,
                individual_id TEXT NOT NULL
            )
        """)

        # Table for released pokemon history (replaces pokemon_history.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                individual_id TEXT UNIQUE,
                data TEXT NOT NULL
            )
        """)

        # Table for user data/credentials (replaces data.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Table for config settings (replaces config.obf)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Table for pending mobile reviews/battles (Phase 1)
        cursor.execute("""
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

        # Table for mobile battle history (Phase 2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mobile_battle_history (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp         INTEGER NOT NULL,
                enemy_id          INTEGER NOT NULL,
                enemy_name        TEXT NOT NULL,
                enemy_level       INTEGER NOT NULL,
                enemy_shiny       INTEGER NOT NULL,
                companion_name    TEXT,
                companion_level   INTEGER,
                outcome           TEXT NOT NULL,
                xp_gained         INTEGER DEFAULT 0,
                trainer_xp_gained INTEGER DEFAULT 0,
                cash_gained       INTEGER DEFAULT 0
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON mobile_battle_history(timestamp)")

        conn.commit()
        self._log("info", "AnkimonDB: Database schema initialized.")

    # --- Captured Pokemon Operations ---

    def save_pokemon(self, pokemon_data: Dict[str, Any]):
        """Saves or updates a captured pokemon. Preserves is_main flag if pokemon already exists."""
        individual_id = pokemon_data.get("individual_id")
        if not individual_id:
            self._log("error", "Cannot save pokemon without individual_id")
            return False

        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if pokemon already exists to preserve is_main flag
        cursor.execute("SELECT is_main FROM captured_pokemon WHERE individual_id = ?", (individual_id,))
        row = cursor.fetchone()
        
        if row:
            # Update existing - preserve is_main
            cursor.execute(
                "UPDATE captured_pokemon SET data = ? WHERE individual_id = ?",
                (obfuscated_data, individual_id)
            )
        else:
            # Insert new with is_main = 0
            cursor.execute(
                "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)",
                (individual_id, obfuscated_data)
            )
        conn.commit()

        # Mark as caught in pokedex_caught
        pokedex_id = pokemon_data.get("id")
        if pokedex_id:
            try:
                self.mark_as_caught(int(pokedex_id))
            except Exception as e:
                self._log("warning", f"Failed to mark pokemon as caught: {e}")

        self._clear_reviewer_ownership_cache()
        return True

    def get_pokemon(self, individual_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific pokemon by its individual_id."""
        cursor = self.execute(
            "SELECT data FROM captured_pokemon WHERE individual_id = ?",
            (individual_id,)
        )
        row = cursor.fetchone()
        if row:
            return self._deobfuscate(row["data"])
        return None

    def get_pokemon_by_individual_id(self, individual_id: str) -> Optional[Dict[str, Any]]:
        """Query captured_pokemon by individual_id, deobfuscate, and return the data dict or None."""
        return self.get_pokemon(individual_id)

    def get_all_pokemon(self) -> List[Dict[str, Any]]:
        """Retrieves all captured pokemon."""
        cursor = self.execute("SELECT data FROM captured_pokemon")
        results = []
        for row in cursor.fetchall():
            pokemon = self._deobfuscate(row["data"])
            if pokemon:
                results.append(pokemon)

        return results

    def has_pokemon_by_name(self, name: str) -> bool:
        """
        Efficiently checks if a pokemon with the given name exists in the collection.
        Uses a direct SQL query on the virtual name index.
        """
        cursor = self.execute("SELECT 1 FROM captured_pokemon WHERE LOWER(name) = LOWER(?) LIMIT 1", (name,))
        return cursor.fetchone() is not None

    def _clear_reviewer_ownership_cache(self):
        """Clears the Reviewer_Manager's ownership cache and the internal Pokémon ID cache when database changes."""
        self._all_pokemon_ids_cache = None
        from aqt import mw
        if hasattr(mw, "reviewer_obj") and mw.reviewer_obj is not None:
            if hasattr(mw.reviewer_obj, "_ownership_cache"):
                mw.reviewer_obj._ownership_cache.clear()

    def delete_pokemon(self, individual_id: str) -> bool:
        """Deletes a pokemon from the captured collection."""
        cursor = self.execute(
            "DELETE FROM captured_pokemon WHERE individual_id = ?",
            (individual_id,)
        )
        self._get_connection().commit()
        self._clear_reviewer_ownership_cache()
        return cursor.rowcount > 0

    def replace_pokemon(self, pokemon_data: Dict[str, Any], old_individual_id: str) -> bool:
        """Replaces a pokemon with the given individual_id with the given pokemon_data."""

        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()

        new_individual_id = pokemon_data["individual_id"]

        # Are we trying to replace ourselves?
        if new_individual_id == old_individual_id:
            self._log("error", f"You already have this {pokemon_data['name']} in your collection!")
            return False


        # Does the pokemon being replaced exist?
        cursor.execute(
            "SELECT is_main FROM captured_pokemon WHERE individual_id = ?",
            (old_individual_id,)
        )
        row = cursor.fetchone()

        if row is None:
            self._log("error", f"No Pokémon found with individual_id {old_individual_id}")
            return False

        is_main = row[0]

        # Does the incoming Pokémon already exist somewhere else?
        cursor.execute(
            "SELECT 1 FROM captured_pokemon WHERE individual_id = ?",
            (new_individual_id,)
        )
        if cursor.fetchone() is not None:
            self._log("error", f"You already have this {pokemon_data['name']} in your collection!")
            return False

        # You passed all the checks. Full steam ahead!
        # Replace the row in-place
        cursor.execute(
            """
            UPDATE captured_pokemon
            SET individual_id = ?, is_main = ?, data = ?
            WHERE individual_id = ?
            """,
            (new_individual_id, is_main, obfuscated_data, old_individual_id)
        )

        conn.commit()

        self._clear_reviewer_ownership_cache()
        return cursor.rowcount > 0

    def get_pokemon_count(self) -> int:
        """Returns the count of captured pokemon."""
        cursor = self.execute("SELECT COUNT(*) FROM captured_pokemon")
        return cursor.fetchone()[0]

    def get_shiny_count(self) -> int:
        """Returns the count of shiny pokemon."""
        cursor = self.execute("SELECT COUNT(*) FROM captured_pokemon WHERE shiny = 1")
        return cursor.fetchone()[0]

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Executes a custom SQL query and returns the cursor. 
        Useful for caller-specific fast-path queries without cluttering the manager."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        return cursor

    def switch_database(self, db_filename: str):
        """Closes the current connection and opens a new database file."""
        self._all_pokemon_ids_cache = None
        self.close()
        self.db_path = user_path / db_filename
        self._connection = None
        self._setup_database()
        self._log("info", f"Switched database to {db_filename}")

    def get_pokemons_by_individual_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieves multiple pokemon by their individual_ids."""
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        cursor = self.execute(f"SELECT data FROM captured_pokemon WHERE individual_id IN ({placeholders})", ids)
        results = []
        for row in cursor.fetchall():
            pokemon = self._deobfuscate(row["data"])
            if pokemon:
                results.append(pokemon)
        return results

    def get_all_pokemon_ids(self) -> set:
        """Returns a set of all captured pokemon's pokedex IDs using the virtual index, history, and explicit caught tracking."""
        if hasattr(self, "_all_pokemon_ids_cache") and self._all_pokemon_ids_cache is not None:
            return set(self._all_pokemon_ids_cache)

        # 1. Currently owned
        cursor = self.execute("SELECT pokedex_id FROM captured_pokemon WHERE pokedex_id IS NOT NULL")
        caught_ids = {int(row[0]) for row in cursor.fetchall() if row[0] is not None}
        
        # 2. Released (history)
        try:
            cursor = self.execute("SELECT DISTINCT json_extract(data, '$.id') FROM pokemon_history")
            for row in cursor.fetchall():
                if row[0] is not None:
                    caught_ids.add(int(row[0]))
        except Exception:
            pass

        # 3. Explicitly recorded caught IDs (from evolutions, etc.)
        try:
            caught_ids.update(self.get_caught_ids())
        except Exception:
            pass

        self._all_pokemon_ids_cache = set(caught_ids)
        return caught_ids

    # --- Main Pokemon Operations ---

    def save_main_pokemon(self, pokemon_data: Dict[str, Any]):
        """Saves/updates the main pokemon. Sets is_main=1 on this pokemon, is_main=0 on all others."""
        individual_id = pokemon_data.get("individual_id")
        if not individual_id:
            self._log("error", "Cannot save main pokemon without individual_id")
            return False

        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Clear the main flag from all pokemon first
        cursor.execute("UPDATE captured_pokemon SET is_main = 0 WHERE is_main = 1")
        
        # Save/update this pokemon and set as main
        cursor.execute("SELECT 1 FROM captured_pokemon WHERE individual_id = ?", (individual_id,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE captured_pokemon SET is_main = 1, data = ? WHERE individual_id = ?",
                (obfuscated_data, individual_id)
            )
        else:
            cursor.execute(
                "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 1, ?)",
                (individual_id, obfuscated_data)
            )
        conn.commit()

        # Mark as caught in pokedex_caught
        pokedex_id = pokemon_data.get("id")
        if pokedex_id:
            try:
                self.mark_as_caught(int(pokedex_id))
            except Exception as e:
                self._log("warning", f"Failed to mark main pokemon as caught: {e}")

        self._clear_reviewer_ownership_cache()
        return True

    def get_main_pokemon(self) -> Optional[Dict[str, Any]]:
        """Retrieves the main pokemon (the one with is_main=1)."""
        cursor = self.execute("SELECT data FROM captured_pokemon WHERE is_main = 1")
        row = cursor.fetchone()
        if row:
            return self._deobfuscate(row["data"])
        return None

    def set_main_pokemon(self, individual_id: str) -> bool:
        """Sets a pokemon as the main pokemon by individual_id. Returns False if pokemon not found."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if pokemon exists
        cursor.execute("SELECT individual_id FROM captured_pokemon WHERE individual_id = ?", (individual_id,))
        if not cursor.fetchone():
            return False
        
        # Clear old main
        cursor.execute("UPDATE captured_pokemon SET is_main = 0 WHERE is_main = 1")
        # Set new main
        cursor.execute("UPDATE captured_pokemon SET is_main = 1 WHERE individual_id = ?", (individual_id,))
        conn.commit()
        return True

    # --- Item Operations ---

    def add_item(self, item_name: str, quantity: int = 1, extra_data: Optional[Dict] = None, commit: bool = True) -> bool:
        """
        Adds a new item to the database with metadata discovery from items.csv.
        Use this for the first time an item is introduced (e.g. migration, looting).
        """
        item_id = None
        category_id = None
        cost = None
        fling_power = None
        fling_effect_id = None

        # Look up metadata from items.csv
        if Path(csv_file_items_cost).is_file():
            try:
                with open(csv_file_items_cost, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if r['identifier'] == item_name:
                            item_id = int(r['id'])
                            if r.get('category_id'): category_id = int(r['category_id'])
                            if r.get('cost'): cost = int(r['cost'])
                            if r.get('fling_power'): fling_power = int(r['fling_power'])
                            if r.get('fling_effect_id'): fling_effect_id = int(r['fling_effect_id'])
                            break
            except Exception as e:
                self._log("error", f"Failed to look up item '{item_name}' in items.csv: {e}")

        return self.save_item(
            item_id, item_name, quantity, extra_data,
            category_id=category_id, cost=cost,
            fling_power=fling_power, fling_effect_id=fling_effect_id,
            commit=commit
        )

    def save_item(self, item_id: Optional[int], item_name: str, quantity: int, extra_data: Optional[Dict] = None,
                  category_id: Optional[int] = None, cost: Optional[int] = None, 
                  fling_power: Optional[int] = None, fling_effect_id: Optional[int] = None,
                  commit: bool = True) -> bool:
        """
        Low-level upsert for items. Lenient with metadata: if missing, tries to fetch from 
        existing DB records but DOES NOT perform CSV lookups.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Lenient metadata resolution: try to fetch existing metadata from DB if NOT provided
        if item_name and (item_id is None or cost is None or category_id is None):
            cursor.execute("SELECT id, category_id, cost, fling_power, fling_effect_id FROM items WHERE item_name = ?", (item_name,))
            row = cursor.fetchone()
            if row:
                if item_id is None: item_id = row["id"]
                if category_id is None: category_id = row["category_id"]
                if cost is None: cost = row["cost"]
                if fling_power is None: fling_power = row["fling_power"]
                if fling_effect_id is None: fling_effect_id = row["fling_effect_id"]

        # Ensure type: "TM" for UI filtering if applicable
        if category_id == 37:
            if extra_data is None: extra_data = {}
            if extra_data.get("type") != "TM": extra_data["type"] = "TM"

        obfuscated_data = self._obfuscate(extra_data) if extra_data else None
        cursor.execute(
            """INSERT OR REPLACE INTO items 
               (id, item_name, quantity, data, category_id, cost, fling_power, fling_effect_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_id, item_name, quantity, obfuscated_data, category_id, cost, fling_power, fling_effect_id)
        )
        if commit:
            conn.commit()
        return True

    def get_item(self, identifier: Any) -> Optional[Dict[str, Any]]:
        """Retrieves an item by name (identifier) or integer ID."""
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            field = "id"
        else:
            field = "item_name"
            
        cursor = self.execute(
            f"SELECT id, item_name, quantity, data, category_id, cost, fling_power, fling_effect_id FROM items WHERE {field} = ?",
            (identifier,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "item_name": row["item_name"],
                "quantity": row["quantity"],
                "extra_data": self._deobfuscate(row["data"]) if row["data"] else {},
                "category_id": row["category_id"],
                "cost": row["cost"],
                "fling_power": row["fling_power"],
                "fling_effect_id": row["fling_effect_id"]
            }
        return None

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Retrieves all items."""
        cursor = self.execute("SELECT id, item_name, quantity, data, category_id, cost, fling_power, fling_effect_id FROM items")
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "item_name": row["item_name"],
                "quantity": row["quantity"],
                "extra_data": self._deobfuscate(row["data"]) if row["data"] else {},
                "category_id": row["category_id"],
                "cost": row["cost"],
                "fling_power": row["fling_power"],
                "fling_effect_id": row["fling_effect_id"]
            })
        return results

    def update_item_quantity(self, item_name: str, delta: int) -> int:
        """Updates item quantity by delta. Returns new quantity."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get current quantity
        cursor.execute("SELECT quantity FROM items WHERE item_name = ?", (item_name,))
        row = cursor.fetchone()
        current_qty = row["quantity"] if row else 0
        if current_qty == 0:
            self._log("warning", f"Item '{item_name}' not found in inventory.")
            return 0
        new_qty = current_qty + delta
        if new_qty < 0:
            self._log("warning", f"Item '{item_name}' has insufficient quantity.")
            return current_qty

        if new_qty > 0:
            cursor.execute(
                "UPDATE items SET quantity = ? WHERE item_name = ?",
                (new_qty, item_name)
            )
        else:
            cursor.execute("DELETE FROM items WHERE item_name = ?", (item_name,))

        conn.commit()
        return new_qty

    # --- Badge Operations ---

    def save_badge(self, badge_id: str, badge_data: Dict[str, Any]):
        """Saves or updates a badge."""
        achieved = badge_data.get("achieved", "false")
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO badges (badge_id, achieved) VALUES (?, ?)",
            (badge_id, achieved)
        )
        conn.commit()
        return True

    def get_badge(self, badge_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a badge by ID."""
        cursor = self.execute("SELECT * FROM badges WHERE badge_id = ?", (badge_id,))
        row = cursor.fetchone()
        if row:
            return {
                "badge_id": row["badge_id"],
                "achieved": row["achieved"]
            }
        return None

    def get_all_badges(self) -> List[Dict[str, Any]]:
        """Retrieves all badges."""
        cursor = self.execute("SELECT badge_id, achieved FROM badges")
        results = []
        for row in cursor.fetchall():
            badge = {
                "badge_id": row["badge_id"],
                "achieved": row["achieved"]
            }
            results.append(badge)
        return results

    # --- Team Operations ---

    def save_team(self, team_list: List[Dict[str, Any]]):
        """Saves the team composition. Replaces existing team."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # clear existing team
        cursor.execute("DELETE FROM team")
        
        for i, member in enumerate(team_list):
            individual_id = member.get("individual_id")
            if individual_id:
                cursor.execute(
                    "INSERT INTO team (slot_position, individual_id) VALUES (?, ?)",
                    (i + 1, individual_id)
                )
        conn.commit()
        return True

    def get_team(self) -> List[Dict[str, Any]]:
        """Retrieves the current team as a list of dicts with individual_id."""
        cursor = self.execute("SELECT individual_id FROM team ORDER BY slot_position ASC")
        results = []
        for row in cursor.fetchall():
            results.append({"individual_id": row["individual_id"]})
        return results

    # --- Pokemon History Operations ---

    def add_to_history(self, pokemon_data: Dict[str, Any]):
        """Adds a released pokemon to history."""
        self._all_pokemon_ids_cache = None
        # Ensure individual_id exists to avoid duplicates if possible, or just generate one
        individual_id = pokemon_data.get("individual_id") or str(uuid.uuid4())
        
        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO pokemon_history (individual_id, data) VALUES (?, ?)",
                (individual_id, obfuscated_data)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            self._log("warning", f"Pokemon {individual_id} already in history.")
            return False

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieves all released pokemon history."""
        cursor = self.execute("SELECT data FROM pokemon_history")
        results = []
        for row in cursor.fetchall():
            data = self._deobfuscate(row["data"])
            if data:
                results.append(data)
        return results

    # --- User Data Operations ---

    def set_user_data(self, key: str, value: Any):
        """Sets a user data key-value pair."""
        # Store as simple string if possible, or JSON string for complex objects
        str_value = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_data (key, value) VALUES (?, ?)",
            (key, str_value)
        )
        conn.commit()
        return True

    def get_user_data(self, key: str, default: Any = None) -> Any:
        """Retrieves user data by key."""
        cursor = self.execute("SELECT value FROM user_data WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            val = row["value"]
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(val)
            except:
                return val
        return default

    def get_all_user_data(self) -> Dict[str, Any]:
        """Retrieves all user data as a dictionary."""
        cursor = self.execute("SELECT key, value FROM user_data")
        result = {}
        for row in cursor.fetchall():
            key = row[0]
            val = row[1]
            try:
                result[key] = json.loads(val)
            except:
                result[key] = val
        return result

    # --- Pokedex Seen Tracking ---

    def mark_as_seen(self, pokedex_id: int):
        """Marks a Pokémon ID as seen in the user_data."""
        seen_ids = self.get_seen_ids()
        if pokedex_id not in seen_ids:
            seen_ids.add(pokedex_id)
            self.set_user_data("pokedex_seen", list(seen_ids))

    def get_seen_ids(self) -> set:
        """Retrieves the set of seen Pokémon IDs."""
        data = self.get_user_data("pokedex_seen", [])
        if isinstance(data, list):
            return set(data)
        return set()

    def mark_as_caught(self, pokedex_id: int):
        """Marks a Pokémon ID as caught in the user_data."""
        self._all_pokemon_ids_cache = None
        caught_ids = self.get_caught_ids()
        if pokedex_id not in caught_ids:
            caught_ids.add(pokedex_id)
            self.set_user_data("pokedex_caught", list(caught_ids))
        self.mark_as_seen(pokedex_id)

    def get_caught_ids(self) -> set:
        """Retrieves the set of caught Pokémon IDs."""
        data = self.get_user_data("pokedex_caught", [])
        if isinstance(data, list):
            return set(data)
        return set()

    # --- Config Operations (replaces config.obf) ---

    def set_config_value(self, key: str, value: Any):
        """Sets a config key-value pair."""
        # Store as JSON string to preserve type information
        str_value = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, str_value)
        )
        conn.commit()
        return True

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Retrieves a config value by key."""
        cursor = self.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            val = row["value"]
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(val)
            except:
                return val
        return default

    def get_all_config(self) -> Dict[str, Any]:
        """Retrieves all config settings as a dictionary."""
        cursor = self.execute("SELECT key, value FROM config")
        result = {}
        for row in cursor.fetchall():
            key = row["key"]
            val = row["value"]
            try:
                result[key] = json.loads(val)
            except:
                result[key] = val
        return result

    def save_all_config(self, config_dict: Dict[str, Any]):
        """Bulk saves a config dictionary to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        for key, value in config_dict.items():
            str_value = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)
            cursor.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, str_value)
            )
        conn.commit()
        return True

    def has_config(self) -> bool:
        """Checks if config data exists in the database."""
        cursor = self.execute("SELECT COUNT(*) FROM config")
        return cursor.fetchone()[0] > 0

    def get_stats(self) -> Dict[str, int]:
        """Returns a summary of database contents for synchronization/backup comparison."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Count pokemon
        cursor.execute("SELECT COUNT(*) as count FROM captured_pokemon")
        stats["pokemon"] = cursor.fetchone()["count"]
        
        # Count items
        cursor.execute("SELECT COUNT(*) as count FROM items")
        stats["items"] = cursor.fetchone()["count"]
        
        # Count history
        cursor.execute("SELECT COUNT(*) as count FROM pokemon_history")
        stats["history"] = cursor.fetchone()["count"]
        
        # Count badges
        cursor.execute("SELECT COUNT(*) as count FROM badges")
        stats["badges"] = cursor.fetchone()["count"]
        
        return stats

    # --- Migration from JSON Files ---

    def migrate_from_json(self, mypokemon_path: Path, mainpokemon_path: Path,
                          items_path: Path, badges_path: Path,
                          team_path: Path = None, history_path: Path = None,
                          data_path: Path = None, rate_path: Path = None) -> Dict[str, int]:
        """
        Migrates data from JSON files to the database.
        Returns a dict with counts of migrated items.
        """
        stats = {"pokemon": 0, "main": 0, "items": 0, "badges": 0, 
                 "team": 0, "history": 0, "userdata": 0}

        # Check if already migrated
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated_phase2'")
        if cursor.fetchone():
            self._log("info", "Database Phase 2 (full) already migrated. Checking Phase 1...")
            # If Phase 2 is done, Phase 1 is definitely done.
            return stats
        
        # Check Phase 1 migration (captured, items, badges)
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated'")
        phase1_done = cursor.fetchone() is not None

        if not phase1_done:
            # Migrate mypokemon.json
            if mypokemon_path.is_file():
                try:
                    with open(mypokemon_path, 'r', encoding='utf-8') as f:
                        pokemon_list = json.load(f)
                    for pokemon in pokemon_list:
                        if self.save_pokemon(pokemon):
                            stats["pokemon"] += 1
                    self._log("info", f"Migrated {stats['pokemon']} pokemon from mypokemon.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate mypokemon.json: {e}")

            # Migrate mainpokemon.json
            if mainpokemon_path.is_file():
                try:
                    with open(mainpokemon_path, 'r', encoding='utf-8') as f:
                        main_data = json.load(f)
                    if main_data:
                        # mainpokemon.json is a list with one item
                        main_pokemon = main_data[0] if isinstance(main_data, list) else main_data
                        if self.save_main_pokemon(main_pokemon):
                            stats["main"] = 1
                    self._log("info", "Migrated main pokemon from mainpokemon.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate mainpokemon.json: {e}")

            # Migrate items.json
            if items_path.is_file():
                try:
                    with open(items_path, 'r', encoding='utf-8') as f:
                        items_list = json.load(f)
                    
                    for item in items_list:
                        if not item: continue
                        # Support multiple legacy keys for item name
                        item_name = item.get("item") or item.get("name") or item.get("item_name")
                        quantity = item.get("quantity", item.get("amount", 1))
                        if item_name:
                            if self.add_item(item_name, quantity, extra_data=item, commit=False):
                                stats["items"] += 1
                    
                    self._get_connection().commit()
                    self._log("info", f"Migrated {stats['items']} items from items.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate items.json: {e}")

            # Migrate badges.json - handles both [1, 2, 3] and [{"id": 1}, ...] formats
            if badges_path.is_file():
                try:
                    with open(badges_path, 'r', encoding='utf-8') as f:
                        badges_list = json.load(f)
                    for badge in badges_list:
                        # Handle both integer, string, and dict formats
                        if isinstance(badge, (int, str)):
                            badge_id = str(badge)
                            badge_data = {"achieved": True}
                        else:
                            badge_id = str(badge.get("id", badge.get("badge_id", "")))
                            # Ensure we have achieved status preserved
                            badge_data = badge
                            badge_data["achieved"] = True
                                
                        if badge_id:
                            self.save_badge(badge_id, badge_data)
                            stats["badges"] += 1
                    self._log("info", f"Migrated {stats['badges']} badges from badges.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate badges.json: {e}")
            
            # Mark Phase 1 as done
            cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('migrated', 'true')")

        # --- Phase 2 Migration (Team, History, UserData) ---
        
        # Migrate team.json
        if team_path and team_path.is_file():
            try:
                with open(team_path, 'r', encoding='utf-8') as f:
                    team_list = json.load(f)
                if self.save_team(team_list):
                    stats["team"] = len(team_list)
                self._log("info", f"Migrated {stats['team']} team members from team.json")
            except Exception as e:
                self._log("error", f"Failed to migrate team.json: {e}")

        # Migrate pokemon_history.json
        if history_path and history_path.is_file():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    history_list = json.load(f)
                for pokemon in history_list:
                    if self.add_to_history(pokemon):
                        stats["history"] += 1
                self._log("info", f"Migrated {stats['history']} history entries from pokemon_history.json")
            except Exception as e:
                self._log("error", f"Failed to migrate pokemon_history.json: {e}")

        # Migrate data.json (User Credentials)
        if data_path and data_path.is_file():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                count = 0
                for key, value in user_data.items():
                    self.set_user_data(key, value)
                    count += 1
                stats["userdata"] = count
                self._log("info", f"Migrated {stats['userdata']} keys from data.json")
            except Exception as e:
                self._log("error", f"Failed to migrate data.json: {e}")

        # Step 8: Migrate rate_this.json
        if rate_path and rate_path.is_file():
            try:
                with open(rate_path, 'r', encoding='utf-8') as f:
                    rate_data = json.load(f)
                
                if isinstance(rate_data, dict) and rate_data.get("rate_this"):
                    self.set_user_data("rate_this", "true")
                    self._log("info", "Migrated rate_this.json")
            except Exception as e:
                self._log("error", f"Failed to migrate rate_this.json: {e}")

        # Mark Phase 2 as done
        cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('migrated_phase2', 'true')")
        conn.commit()

        # --- Integrity Check ---
        # Verify that database counts match expected counts from JSON files
        integrity_issues = []
        
        # Count JSON entries
        json_counts = {"pokemon": 0, "items": 0, "badges": 0}
        try:
            if mypokemon_path.is_file():
                with open(mypokemon_path, 'r', encoding='utf-8') as f:
                    json_counts["pokemon"] = len(json.load(f))
            if items_path.is_file():
                with open(items_path, 'r', encoding='utf-8') as f:
                    json_counts["items"] = len(json.load(f))
            if badges_path.is_file():
                with open(badges_path, 'r', encoding='utf-8') as f:
                    json_counts["badges"] = len(json.load(f))
        except Exception as e:
            self._log("warning", f"Could not read JSON files for integrity check: {e}")
        
        # Count database entries
        db_counts = {"pokemon": 0, "items": 0, "badges": 0}
        cursor.execute("SELECT COUNT(*) FROM captured_pokemon")
        db_counts["pokemon"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM items")
        db_counts["items"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM badges")
        db_counts["badges"] = cursor.fetchone()[0]
        
        # Compare counts
        for key in ["pokemon", "items", "badges"]:
            if json_counts[key] > 0 and db_counts[key] < json_counts[key]:
                integrity_issues.append(
                    f"{key}: JSON has {json_counts[key]} entries but DB only has {db_counts[key]}"
                )
        
        if integrity_issues:
            self._log("warning", f"Migration integrity issues detected: {integrity_issues}")
            stats["integrity_issues"] = integrity_issues
        else:
            self._log("info", "Migration integrity check passed - all counts match.")

        self._log("info", f"Migration complete: {stats}")
        return stats

    # --- Utility ---

    def is_migrated(self) -> bool:
        """Checks if ALL JSON data (Phase 1 & 2) has been migrated to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated_phase2'")
        row = cursor.fetchone()
        return row is not None and row["value"] == "true"

    def is_migrated_phase1(self) -> bool:
        """Checks if Phase 1 data (pokemon, items, badges) has been migrated."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated'")
        row = cursor.fetchone()
        return row is not None and row["value"] == "true"

    # --- Mobile Sync Operations ---

    def get_mobile_watermark(self) -> int:
        """Return stored watermark (ms). Returns 0 if not set (first-ever run)."""
        row = self.execute(
            "SELECT value FROM metadata WHERE key = 'mobile_revlog_watermark'"
        ).fetchone()
        return int(row[0]) if row else 0

    def set_mobile_watermark(self, watermark_ms: int) -> None:
        with self._get_connection():
            self._get_connection().execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES ('mobile_revlog_watermark', ?)",
                (str(watermark_ms),)
            )

    def queue_mobile_battles(self, reviews: list[dict]) -> int:
        """Insert mobile reviews into pending queue. Returns count inserted (skips duplicates)."""
        import time
        now = int(time.time() * 1000)
        inserted = 0
        conn = self._get_connection()
        with conn:
            for r in reviews:
                cursor = conn.execute(
                    """INSERT OR IGNORE INTO pending_mobile_battles
                       (revlog_id, card_id, ease, review_time, review_type, queued_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (r["id"], r["cid"], r["ease"], r["time"], r["type"], now)
                )
                inserted += cursor.rowcount
        return inserted

    def get_pending_mobile_count(self) -> int:
        return self.execute(
            "SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved = 0"
        ).fetchone()[0]

    def get_next_pending_mobile_batch(self, limit: int = 1) -> list[dict]:
        """Return next N unresolved battles, oldest-first (lowest revlog_id first)."""
        rows = self.execute(
            """SELECT id, revlog_id, card_id, ease, review_time, review_type
               FROM pending_mobile_battles
               WHERE resolved = 0
               ORDER BY revlog_id ASC
               LIMIT ?""",
            (limit,)
        ).fetchall()
        keys = ["queue_id", "revlog_id", "card_id", "ease", "review_time", "review_type"]
        return [dict(zip(keys, r)) for r in rows]

    def mark_mobile_battle_resolved(self, queue_id: int) -> None:
        import time
        now = int(time.time() * 1000)
        cursor = self.execute("SELECT revlog_id FROM pending_mobile_battles WHERE id = ?", (queue_id,))
        row = cursor.fetchone()
        revlog_id = row[0] if row else None
        
        with self._get_connection():
            self._get_connection().execute(
                "UPDATE pending_mobile_battles SET resolved=1, resolved_at=? WHERE id=?",
                (now, queue_id)
            )
        
        if revlog_id:
            self.sync_resolutions_to_other_db([revlog_id], now)

    def add_mobile_history_entry(self, entry: Dict[str, Any]) -> bool:
        """Saves a single mobile battle outcome to history."""
        return self.add_mobile_history_entries_batch([entry])

    def add_mobile_history_entries_batch(self, entries: List[Dict[str, Any]]) -> bool:
        """Saves a batch of mobile battle outcomes to history in a single transaction."""
        if not entries:
            return True

        def _clean_val(v, default):
            if v is None:
                return default
            return v

        try:
            conn = self._get_connection()
            with conn:
                conn.executemany(
                    """INSERT INTO mobile_battle_history (
                        timestamp, enemy_id, enemy_name, enemy_level, enemy_shiny,
                        companion_name, companion_level, outcome, xp_gained,
                        trainer_xp_gained, cash_gained
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    [
                        (
                            _clean_val(entry.get("timestamp"), 0),
                            _clean_val(entry.get("enemy_id"), 0),
                            str(_clean_val(entry.get("enemy_name"), "")),
                            _clean_val(entry.get("enemy_level"), 0),
                            1 if entry.get("enemy_shiny") else 0,
                            str(_clean_val(entry.get("companion_name"), "")),
                            _clean_val(entry.get("companion_level"), 0),
                            str(_clean_val(entry.get("outcome"), "")),
                            _clean_val(entry.get("xp_gained"), 0),
                            _clean_val(entry.get("trainer_xp_gained"), 0),
                            _clean_val(entry.get("cash_gained"), 0),
                        )
                        for entry in entries
                    ]
                )
                conn.execute(
                    """DELETE FROM mobile_battle_history
                       WHERE id NOT IN (
                           SELECT id FROM mobile_battle_history
                           ORDER BY timestamp DESC, id DESC
                           LIMIT 500
                       )"""
                )
            return True
        except Exception as e:
            self._log("error", f"Failed to batch add mobile history entries: {e}")
            return False

    def get_mobile_history(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Retrieves recent mobile battle history entries, newest first."""
        try:
            rows = self.execute(
                """SELECT id, timestamp, enemy_id, enemy_name, enemy_level, enemy_shiny,
                          companion_name, companion_level, outcome, xp_gained,
                          trainer_xp_gained, cash_gained
                   FROM mobile_battle_history
                   ORDER BY timestamp DESC, id DESC
                   LIMIT ?""",
                (limit,)
            ).fetchall()
            keys = [
                "id", "timestamp", "enemy_id", "enemy_name", "enemy_level", "enemy_shiny",
                "companion_name", "companion_level", "outcome", "xp_gained",
                "trainer_xp_gained", "cash_gained"
            ]
            result = []
            for r in rows:
                item = dict(zip(keys, r))
                item["enemy_shiny"] = bool(item["enemy_shiny"])
                result.append(item)
            return result
        except Exception as e:
            self._log("error", f"Failed to get mobile history: {e}")
            return []

    def clear_mobile_history(self) -> bool:
        """Clears all entries from the mobile battle history."""
        try:
            conn = self._get_connection()
            with conn:
                conn.execute("DELETE FROM mobile_battle_history")
            return True
        except Exception as e:
            self._log("error", f"Failed to clear mobile history: {e}")
            return False

    def sync_resolutions_to_other_db(self, revlog_ids: list[int], resolved_at: int) -> None:
        """
        If the other database exists (normal vs dev), sync the resolved status of the given
        revlog_ids to it directly.
        """
        if not revlog_ids:
            return
        
        current_name = self.db_path.name
        if current_name == "ankimon.db":
            other_name = "ankimonDEV.db"
        elif current_name == "ankimonDEV.db":
            other_name = "ankimon.db"
        else:
            return
            
        other_path = user_path / other_name
        if not other_path.is_file():
            return
            
        try:
            import sqlite3
            conn = sqlite3.connect(str(other_path), timeout=5.0)
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
                placeholders = ",".join("?" for _ in revlog_ids)
                conn.execute(
                    f"UPDATE pending_mobile_battles SET resolved=1, resolved_at=? WHERE revlog_id IN ({placeholders})",
                    [resolved_at] + list(revlog_ids)
                )
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            self._log("error", f"Failed to sync resolutions to {other_name}: {e}")



# Singleton instance for use throughout the addon
_db_instance: Optional[AnkimonDB] = None


def get_db(logger=None) -> AnkimonDB:
    """Gets the singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = AnkimonDB(logger)
    return _db_instance

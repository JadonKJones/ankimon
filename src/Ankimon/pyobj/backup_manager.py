
import base64
import json
import os
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from aqt import mw
from aqt.utils import showInfo, showWarning, askUser

from ..utils import close_anki
from ..resources import user_path, addon_dir

class BackupManager:
    """Handles creating, managing, and restoring Ankimon backups."""

    _OBFUSCATION_KEY = "H0tP-!s-N0t-4-C@tG!rL_v2"
    FILES_TO_BACKUP = [
        "ankimon.db",
        "ankimonDEV.db",
    ]
    MAX_BACKUPS = 5
    MAX_BACKUP_AGE_DAYS = 14

    def __init__(self, logger, settings_obj):
        self.logger = logger
        self.settings_obj = settings_obj
        self.user_files_path = user_path
        self.addon_path = addon_dir
        self.backups_path = self.addon_path.parent / "ankimon_backups"
        self.backups_path.mkdir(exist_ok=True)

    def _deobfuscate_data(self, obfuscated_str: str) -> Optional[Dict[str, Any]]:
        """De-obfuscates string back into a dictionary."""
        try:
            new_separator = "---DATA_START---"
            old_separator = "\n---"
            
            if new_separator in obfuscated_str:
                parts = obfuscated_str.split(new_separator)
                obfuscated_data = parts[1]
            elif old_separator in obfuscated_str:
                parts = obfuscated_str.split(old_separator)
                obfuscated_data = parts[1]
            else:
                obfuscated_data = obfuscated_str

            obfuscated_bytes = base64.b64decode(obfuscated_data)
            deobfuscated_bytes = bytearray()
            key_bytes = self._OBFUSCATION_KEY.encode('utf-8')
            for i, byte in enumerate(obfuscated_bytes):
                deobfuscated_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
            return json.loads(deobfuscated_bytes.decode('utf-8'))
        except Exception as e:
            self.logger.log("error", f"Failed to deobfuscate data: {e}")
            return None

    def get_backups(self) -> List[Dict[str, Any]]:
        """Returns a list of available backups with their summary stats."""
        backups = []
        active_db = mw.ankimon_db.db_path.name
        for backup_dir in sorted(self.backups_path.iterdir(), reverse=True):
            if backup_dir.is_dir():
                # Only show backup if it contains the database for the active mode
                if not (backup_dir / active_db).exists():
                    continue
                summary_path = backup_dir / "summary.json"
                if summary_path.exists():
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        try:
                            summary = json.load(f)
                            # Shape the summary to match what the UI expects for the active DB
                            stats_key = "dev_stats" if active_db == "ankimonDEV.db" else "normal_stats"
                            db_stats = summary.get(stats_key, {})
                            
                            # Merge DB-specific stats into the root summary object for the UI
                            summary.update(db_stats)
                            summary['path'] = str(backup_dir)
                            backups.append(summary)
                        except json.JSONDecodeError:
                            self.logger.log("error", f"Could not read summary for backup: {backup_dir.name}")
                elif active_db == "ankimon.db":
                    # Fallback for older backups without summary.json
                    summary = {
                        "date": backup_dir.name.replace("backup_", "").replace("_", " "),
                        "path": str(backup_dir)
                    }
                    backups.append(summary)
        return backups

    def create_backup(self, manual=False):
        """Creates a new backup."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir = self.backups_path / f"backup_{timestamp}"
        
        try:
            # Checkpoint the active database first to flush all WAL changes to disk!
            if hasattr(mw, "ankimon_db") and mw.ankimon_db:
                try:
                    mw.ankimon_db.execute("PRAGMA wal_checkpoint(PASSIVE);")
                    self.logger.log("info", "Checkpoint database before backup.")
                except Exception as e:
                    self.logger.log("error", f"Failed to checkpoint database before backup: {e}")

            backup_dir.mkdir()
            
            # For manual backups, only back up the currently active database
            files_to_copy = self.FILES_TO_BACKUP
            if manual and hasattr(mw, "ankimon_db") and mw.ankimon_db:
                files_to_copy = [mw.ankimon_db.db_path.name]
                
            for filename in files_to_copy:
                source_path = self.user_files_path / filename
                if source_path.exists():
                    dest_path = backup_dir / filename
                    if source_path.suffix == '.db':
                        import sqlite3
                        try:
                            src_conn = sqlite3.connect(source_path)
                            dest_conn = sqlite3.connect(dest_path)
                            with dest_conn:
                                src_conn.backup(dest_conn)
                            dest_conn.close()
                            src_conn.close()
                            continue
                        except Exception:
                            pass
                    shutil.copy2(source_path, dest_path)

            summary = self._generate_summary(backup_dir)
            summary['manual'] = manual
            with open(backup_dir / "summary.json", 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=4)
            
            if manual:
                showInfo("Manual backup created successfully.")
            self.logger.log("info", f"Created backup: {backup_dir.name}")

        except Exception as e:
            self.logger.log("error", f"Failed to create backup: {e}")
            if manual:
                showWarning(f"Failed to create backup: {e}")
        
        self.cleanup_backups()

    def _get_db_file_stats(self, db_file_path: Path) -> Dict[str, Any]:
        stats = {
            "main_pokemon_name": "N/A",
            "main_pokemon_level": "N/A",
            "pokemon_count": 0,
            "trainer_name": "N/A",
            "trainer_cash": 0,
            "trainer_level": 1,
            "item_count": 0,
        }
        if not db_file_path.exists():
            return stats
        import sqlite3
        import json
        try:
            conn = sqlite3.connect(str(db_file_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Count pokemon
            try:
                cursor.execute("SELECT COUNT(*) as count FROM captured_pokemon")
                stats["pokemon_count"] = cursor.fetchone()["count"]
            except Exception:
                pass
            
            # Count items
            try:
                cursor.execute("SELECT SUM(quantity) as count FROM items")
                row = cursor.fetchone()
                stats["item_count"] = row["count"] if row and row["count"] is not None else 0
            except Exception:
                pass
            
            # Get main pokemon
            try:
                cursor.execute("SELECT data FROM captured_pokemon WHERE is_main = 1 LIMIT 1")
                row = cursor.fetchone()
                if row:
                    main_data = json.loads(row["data"])
                    stats["main_pokemon_name"] = main_data.get("name", "N/A")
                    stats["main_pokemon_level"] = main_data.get("level", "N/A")
            except Exception:
                pass
            
            # Trainer info from config table (stored as JSON serialized strings)
            try:
                cursor.execute("SELECT value FROM config WHERE key = 'trainer.name'")
                row = cursor.fetchone()
                if row:
                    val = row["value"]
                    try:
                        stats["trainer_name"] = json.loads(val)
                    except Exception:
                        stats["trainer_name"] = val
            except Exception:
                pass
            
            try:
                cursor.execute("SELECT value FROM config WHERE key = 'trainer.cash'")
                row = cursor.fetchone()
                if row:
                    val = row["value"]
                    try:
                        stats["trainer_cash"] = int(json.loads(val))
                    except Exception:
                        stats["trainer_cash"] = int(val)
            except Exception:
                pass
                
            try:
                cursor.execute("SELECT value FROM config WHERE key = 'trainer.level'")
                row = cursor.fetchone()
                if row:
                    val = row["value"]
                    try:
                        stats["trainer_level"] = int(json.loads(val))
                    except Exception:
                        stats["trainer_level"] = int(val)
            except Exception:
                pass
                
            conn.close()
        except Exception as e:
            print(f"Ankimon BackupManager: Failed to read stats from {db_file_path.name}: {e}")
        return stats

    def _generate_summary(self, backup_dir: Path) -> Dict[str, Any]:
        """Generates a summary for a backup."""
        active_db_name = mw.ankimon_db.db_path.name if (hasattr(mw, "ankimon_db") and mw.ankimon_db) else "ankimon.db"
        
        # Read stats from files inside the backup directory
        normal_stats = self._get_db_file_stats(backup_dir / "ankimon.db")
        dev_stats = self._get_db_file_stats(backup_dir / "ankimonDEV.db")
        
        # For backward compatibility / tests (if the backup folder is dummy and doesn't have the db files yet,
        # fallback to the active database connection's current live state)
        db = mw.ankimon_db if (hasattr(mw, "ankimon_db") and mw.ankimon_db) else None
        if not (backup_dir / "ankimon.db").exists() and not (backup_dir / "ankimonDEV.db").exists():
            if db:
                try:
                    stats = db.get_stats()
                    live_stats = {
                        "pokemon_count": stats.get("pokemon", 0),
                        "item_count": stats.get("items", 0),
                        "main_pokemon_name": "N/A",
                        "main_pokemon_level": "N/A",
                        "trainer_name": db.get_config_value("trainer.name", "N/A"),
                        "trainer_cash": db.get_config_value("trainer.cash", 0),
                        "trainer_level": db.get_config_value("trainer.level", 1),
                    }
                    main_pokemon = db.get_main_pokemon()
                    if main_pokemon:
                        live_stats["main_pokemon_name"] = main_pokemon.get("name", "N/A")
                        live_stats["main_pokemon_level"] = main_pokemon.get("level", "N/A")
                        
                    if active_db_name == "ankimonDEV.db":
                        dev_stats = live_stats
                    else:
                        normal_stats = live_stats
                except Exception:
                    pass

        summary = {
            "date": backup_dir.name.replace("backup_", "").replace("_", " "),
            "normal_stats": normal_stats,
            "dev_stats": dev_stats,
        }

        # Merge active DB's stats to the root of summary for backwards compatibility/tests
        stats_key = "dev_stats" if active_db_name == "ankimonDEV.db" else "normal_stats"
        summary.update(summary.get(stats_key, {}))
        
        # Fallback to legacy JSON for older backups or migration period
        if not (backup_dir / "ankimon.db").exists() and not (backup_dir / "ankimonDEV.db").exists() and not db:
            legacy_stats = {
                "main_pokemon_name": "N/A",
                "main_pokemon_level": "N/A",
                "pokemon_count": 0,
                "trainer_name": "N/A",
                "trainer_cash": 0,
                "trainer_level": 1,
                "item_count": 0,
            }
            # Read mainpokemon.json for main Pokémon info
            mainpokemon_path = backup_dir / "mainpokemon.json"
            if mainpokemon_path.exists():
                with open(mainpokemon_path, 'r', encoding='utf-8') as f:
                    try:
                        mainpokemon_data = json.load(f)
                        if mainpokemon_data:
                            legacy_stats["main_pokemon_name"] = mainpokemon_data[0].get("name", "N/A")
                            legacy_stats["main_pokemon_level"] = mainpokemon_data[0].get("level", "N/A")
                    except (json.JSONDecodeError, IndexError):
                        pass

            # Read mypokemon.json for total Pokémon count
            mypokemon_path = backup_dir / "mypokemon.json"
            if mypokemon_path.exists():
                with open(mypokemon_path, 'r', encoding='utf-8') as f:
                    try:
                        mypokemon_data = json.load(f)
                        legacy_stats["pokemon_count"] = len(mypokemon_data)
                    except json.JSONDecodeError:
                        pass

            # Read items.json for total item count
            items_path = backup_dir / "items.json"
            if items_path.exists():
                with open(items_path, 'r', encoding='utf-8') as f:
                    try:
                        items_data = json.load(f)
                        legacy_stats["item_count"] = sum(item.get('quantity', 0) for item in items_data)
                    except json.JSONDecodeError:
                        pass

            # Read config.obf for trainer info
            config_path = backup_dir / "config.obf"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    obfuscated_data = f.read()
                config_data = self._deobfuscate_data(obfuscated_data)
                if config_data:
                    legacy_stats["trainer_name"] = config_data.get("trainer.name", "N/A")
                    legacy_stats["trainer_cash"] = config_data.get("trainer.cash", 0)
                    legacy_stats["trainer_level"] = config_data.get("trainer.level", 1)
            summary["normal_stats"] = legacy_stats
            summary.update(legacy_stats)

        return summary

    def restore_backup(self, backup_path_str: str):
        """Restores a selected backup."""
        backup_path = Path(backup_path_str)
        if not backup_path.is_dir():
            showWarning("Selected backup path does not exist.")
            return

        if not askUser(
            "Are you sure you want to restore this backup? This will overwrite your current Ankimon data. Anki will be closed to apply the changes."
        ):
            return

        try:
            active_db = mw.ankimon_db.db_path.name
            backup_file = backup_path / active_db
            if backup_file.exists():
                shutil.copy2(backup_file, self.user_files_path / active_db)
            else:
                showWarning(f"The selected backup does not contain a backup for the active database ({active_db}).")
                return

            showInfo("Backup restored successfully. Anki will now close. Please restart Anki to see the changes.")
            close_anki()

        except Exception as e:
            self.logger.log("error", f"Failed to restore backup: {e}")
            showWarning(f"Failed to restore backup: {e}")

    def delete_backup(self, backup_path_str: str):
        """Deletes a selected backup."""
        backup_path = Path(backup_path_str)
        if not backup_path.is_dir():
            showWarning("Selected backup path does not exist.")
            return
        try:
            shutil.rmtree(backup_path)
            self.logger.log("info", f"Deleted backup: {backup_path.name}")
            showInfo("Backup deleted successfully.")
        except Exception as e:
            self.logger.log("error", f"Failed to delete backup: {e}")
            showWarning(f"Failed to delete backup: {e}")

    def cleanup_backups(self):
        """Deletes old backups based on retention policy."""
        # Get only directories and sort them by modification time
        backups = sorted([p for p in self.backups_path.iterdir() if p.is_dir()], key=os.path.getmtime)
        
        backups_to_keep = []
        for backup_dir in backups:
            backup_time = datetime.datetime.fromtimestamp(os.path.getmtime(backup_dir))
            if (datetime.datetime.now() - backup_time).days > self.MAX_BACKUP_AGE_DAYS:
                shutil.rmtree(backup_dir)
                self.logger.log("info", f"Deleted old backup: {backup_dir.name}")
            else:
                backups_to_keep.append(backup_dir)

        # Keep only the latest MAX_BACKUPS, unless in developer mode
        if not self.settings_obj.get("misc.developer_mode"):
            while len(backups_to_keep) > self.MAX_BACKUPS:
                oldest_backup = backups_to_keep.pop(0)
                shutil.rmtree(oldest_backup)
                self.logger.log("info", f"Deleted oldest backup to maintain max count: {oldest_backup.name}")

    def on_anki_close(self):
        """Creates a backup when Anki is about to close."""
        # This logic can be expanded with the developer mode setting
        self.create_backup(manual=False)

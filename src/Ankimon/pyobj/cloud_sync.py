"""Manual push/pull of the Ankimon database to a user-chosen cloud folder
(e.g. one watched by Syncthing).

Deliberately has no "which side is newer" logic — that mtime-comparison
approach is what made the old automatic AnkiWeb-riding sync unreliable and
led to it being disabled (see ``ankimon_sync.py``'s dormant
``_automatic_sync_enabled`` subsystem). Here the user always decides the
direction explicitly.
"""

import shutil
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional

from aqt.utils import askUser, showInfo, showWarning

from ..services import services
from ..utils import close_anki

DEFAULT_CLOUD_FOLDER_NAME = "AnkimonCloudSync"


class CloudSync:
    """Handles pushing/pulling the active Ankimon database to a cloud folder."""

    def __init__(self, logger, settings_obj):
        self.logger = logger
        self.settings_obj = settings_obj

    def get_cloud_folder(self) -> Path:
        """Returns the fixed cloud folder, creating it if needed.

        Not user-configurable, and deliberately NOT inside Anki's addon data
        (that path looks different on every machine/install, e.g. a versioned
        addon folder vs. a dev symlink). Home directory is the one location
        that's the same shape everywhere, so pairing it in Syncthing is just
        "point both machines at ~/AnkimonCloudSync" with nothing to hunt for.
        """
        folder = Path.home() / DEFAULT_CLOUD_FOLDER_NAME
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def _cloud_db_path(self) -> Optional[Path]:
        if services.db is None:
            return None
        return self.get_cloud_folder() / services.db.db_path.name

    def _verify_sqlite_integrity(self, path: Path) -> bool:
        try:
            with closing(sqlite3.connect(str(path))) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA quick_check")
                result = cursor.fetchone()
                if not result or result[0] != "ok":
                    return False
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='captured_pokemon'"
                )
                return cursor.fetchone() is not None
        except Exception as e:
            self.logger.log("error", f"Cloud sync: integrity check failed for {path}: {e}")
            return False

    def push(self):
        """Copy the active local database into the cloud folder, overwriting it."""
        if services.db is None:
            showWarning("The Ankimon database is not initialized yet; cannot push.")
            return
        cloud_folder = self.get_cloud_folder()
        if not askUser(
            "Push your local Ankimon data to the cloud folder? This will "
            "overwrite whatever is currently saved there."
        ):
            return

        local_path = services.db.db_path
        dest_path = cloud_folder / local_path.name
        tmp_path = dest_path.with_name(dest_path.name + ".tmp")
        try:
            # Flush WAL and block new connections so the copy reads one
            # consistent snapshot of the file.
            with services.db.quiesce(2.0) as drained:
                if not drained:
                    showWarning(
                        "Push failed: could not safely pause the database "
                        "(an operation is still in progress). Try again shortly."
                    )
                    return
                shutil.copy2(local_path, tmp_path)

            if not self._verify_sqlite_integrity(tmp_path):
                tmp_path.unlink(missing_ok=True)
                showWarning("Push failed: the copied database did not pass an integrity check.")
                return

            tmp_path.replace(dest_path)
            self.logger.log("info", f"Cloud sync: pushed {local_path.name} to {dest_path}")
            showInfo("Pushed your Ankimon data to the cloud folder.")
        except Exception as e:
            tmp_path.unlink(missing_ok=True)
            self.logger.log("error", f"Cloud sync push failed: {e}")
            showWarning(f"Push failed: {e}")

    def pull(self):
        """Overwrite the active local database with the cloud folder's copy."""
        if services.db is None:
            showWarning("The Ankimon database is not initialized yet; cannot pull.")
            return
        cloud_path = self._cloud_db_path()
        if cloud_path is None or not cloud_path.is_file():
            showWarning("No matching database was found in the Cloud Sync Folder.")
            return

        if not self._verify_sqlite_integrity(cloud_path):
            showWarning(
                "Pull aborted: the database in the Cloud Sync Folder failed an "
                "integrity check. Nothing was changed locally."
            )
            return

        if not askUser(
            "Pull data from the cloud folder? This will overwrite your local "
            "Ankimon data with what's saved there. A backup of your current "
            "data will be made first, then Anki will close so you can restart "
            "and see the pulled data."
        ):
            return

        local_path = services.db.db_path
        try:
            from .backup_manager import BackupManager

            backup_ok = BackupManager(self.logger, self.settings_obj).create_backup(
                manual=True, required_file=local_path.name
            )
            if not backup_ok:
                showWarning(
                    "Pull aborted: could not create a safety backup of your "
                    "current data, so nothing was changed."
                )
                return

            with services.db.quiesce(2.0) as drained:
                if not drained:
                    showWarning(
                        "Pull failed: could not safely pause the database "
                        "(an operation is still in progress). Try again shortly."
                    )
                    return
                tmp_local = local_path.with_name(local_path.name + ".pulling")
                shutil.copy2(cloud_path, tmp_local)
                tmp_local.replace(local_path)
                for sidecar in ("-wal", "-shm"):
                    sidecar_file = local_path.with_name(local_path.name + sidecar)
                    if sidecar_file.exists():
                        sidecar_file.unlink()

            self.logger.log("info", f"Cloud sync: pulled {cloud_path} into {local_path.name}")
            showInfo(
                "Pulled cloud data successfully. Anki will now close. "
                "Please restart Anki to see the changes."
            )
            close_anki()
        except Exception as e:
            self.logger.log("error", f"Cloud sync pull failed: {e}")
            showWarning(f"Pull failed: {e}")

"""Manual push/pull of the Ankimon database to a cloud copy that rides along
on Anki's own AnkiWeb sync — no separate sync tool (Syncthing etc.) needed.

Deliberately has no "which side is newer" logic — that mtime-comparison
approach is what made the old automatic AnkiWeb-riding sync unreliable and
led to it being disabled (see ``ankimon_sync.py``'s dormant
``_automatic_sync_enabled`` subsystem). Here the user always decides the
direction explicitly: Push writes the cloud copy, then the user runs Anki's
normal sync (the button they already use for their cards) to move it to the
other device, then Pull reads it there.

The cloud copy lives in ``collection.media`` — the one folder AnkiWeb already
syncs — with a leading underscore (``_ankimon_cloud.db``), the standard Anki
add-on convention for a file that should ride sync but be exempt from Anki's
"check media" unused-file cleanup (it isn't referenced by any note).
"""

import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from aqt import mw
from aqt.utils import askUser, showInfo, showWarning

from ..services import services
from ..utils import close_anki

CLOUD_DB_NAME = "_ankimon_cloud.db"

# Config keys never written to the cloud copy. collection.media is uploaded to
# AnkiWeb's servers on the next sync, so a credential stored in ankimon.db's
# config table (unlike ankimon.db itself, which never leaves the local
# machine) would otherwise be handed to a third party.
_SECRET_CONFIG_KEYS = ("leaderboard.api_key",)


class CloudSync:
    """Handles pushing/pulling the active Ankimon database to its cloud copy."""

    def __init__(self, logger, settings_obj):
        """Store the shared logger/settings used for backups and diagnostics."""
        self.logger = logger
        self.settings_obj = settings_obj

    def _cloud_db_path(self) -> Path:
        """Path of the cloud copy inside the current profile's collection.media."""
        return Path(mw.pm.profileFolder()) / "collection.media" / CLOUD_DB_NAME

    def _scrub_secrets(self, path: Path) -> None:
        """Blank credential-bearing config rows in a standalone db copy.

        Called only on the copy about to be uploaded to AnkiWeb — never on the
        live ``ankimon.db``, which stays local.
        """
        try:
            with closing(sqlite3.connect(str(path))) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='config'"
                )
                if cursor.fetchone() is None:
                    return
                cursor.executemany(
                    "UPDATE config SET value = '' WHERE key = ?",
                    [(key,) for key in _SECRET_CONFIG_KEYS],
                )
                conn.commit()
        except Exception as e:
            self.logger.log("error", f"Cloud sync: failed to scrub secrets from {path}: {e}")
            raise

    def _verify_sqlite_integrity(self, path: Path) -> bool:
        """Run a quick_check and confirm the core game table is present."""
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
        """Copy the active local database into ankimon_cloud.db, overwriting it."""
        if services.db is None:
            showWarning("The Ankimon database is not initialized yet; cannot push.")
            return
        if not askUser("Push your data to the cloud copy? This overwrites it."):
            return

        local_path = services.db.db_path
        dest_path = self._cloud_db_path()
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

            # Scrub credentials from the STANDALONE copy (never the live db)
            # before it can be finalized into collection.media / uploaded.
            self._scrub_secrets(tmp_path)

            if not self._verify_sqlite_integrity(tmp_path):
                tmp_path.unlink(missing_ok=True)
                showWarning("Push failed: the copied database did not pass an integrity check.")
                return

            tmp_path.replace(dest_path)
            self.logger.log("info", f"Cloud sync: pushed {local_path.name} to {dest_path}")
            showInfo("Pushed. Sync Anki now to send it to your other device.")
        except Exception as e:
            tmp_path.unlink(missing_ok=True)
            self.logger.log("error", f"Cloud sync push failed: {e}")
            showWarning(f"Push failed: {e}")

    def pull(self):
        """Overwrite the active local database with the ankimon_cloud.db copy."""
        if services.db is None:
            showWarning("The Ankimon database is not initialized yet; cannot pull.")
            return
        cloud_path = self._cloud_db_path()
        if not cloud_path.is_file():
            showWarning("No cloud copy found. Push from your other device, sync, then try again.")
            return

        if not self._verify_sqlite_integrity(cloud_path):
            showWarning("Pull aborted: the cloud copy looks incomplete. Try syncing again first.")
            return

        if not askUser("Pull from the cloud copy? This overwrites your local data and restarts Anki."):
            return

        local_path = services.db.db_path
        try:
            from .backup_manager import BackupManager

            # Backup and replace share ONE quiesce: a backup taken before
            # (or after releasing) the lock could still race a write landing
            # between the checkpoint and the file copy, making it an
            # inconsistent recovery point. Holding the lock across both means
            # nothing can write to the live db from backup through replace.
            with services.db.quiesce(2.0) as drained:
                if not drained:
                    showWarning(
                        "Pull failed: could not safely pause the database "
                        "(an operation is still in progress). Try again shortly."
                    )
                    return

                backup_ok = BackupManager(self.logger, self.settings_obj).create_backup(
                    manual=True, required_file=local_path.name
                )
                if not backup_ok:
                    showWarning(
                        "Pull aborted: could not create a safety backup of your "
                        "current data, so nothing was changed."
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
            showInfo("Pulled. Anki will close — restart it to see the changes.")
            close_anki()
        except Exception as e:
            self.logger.log("error", f"Cloud sync pull failed: {e}")
            showWarning(f"Pull failed: {e}")

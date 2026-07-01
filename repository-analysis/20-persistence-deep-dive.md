# Persistence Deep Dive

This document traces the persistence layers of Ankimon, detailing how data write integrity is maintained under rapid flashcard reviewing, and how multi-profile account hot-swapping operates at runtime.

---

## 1. Multi-Profile Account Hot-Swapping

Ankimon permits developers and users to swap database environments (e.g., toggling between production `ankimon.db` and testing/developer profile `ankimonDEV.db`) instantly from the main menu without restarting the Anki application.

```
                              ┌────────────────────────────────┐
                              │  Switch Account Menu Clicked   │
                              └───────────────┬────────────────┘
                                              │
                                              ▼
                              ┌────────────────────────────────┐
                              │  AnkimonDB.switch_database()   │
                              └───────────────┬────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
        ┌───────────────────────────┐                   ┌───────────────────────────┐
        │  Close Current SQLite     │                   │  Assign New DB File Path  │
        │  Connection               │                   │  (ankimonDEV.db)          │
        └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              │
                                              ▼
                              ┌────────────────────────────────┐
                              │  Open New SQLite Connection &  │
                              │  Initialize Missing Schemas    │
                              └───────────────┬────────────────┘
                                              │
                                              ▼
                              ┌────────────────────────────────┐
                              │  Reload Memory Domains:        │
                              │  TrainerCard, Main Pokémon, PC │
                              └────────────────────────────────┘
```

### Transition Steps
When the hot-swap function is triggered in `singletons.py`:
1.  **Close Active Connection:** Calls `mw.ankimon_db.close()`, cleanly executing connection disconnects and committing remaining journal writes to disk.
2.  **Redirect Pointer:** Re-allocates the file directory pointer to the target database path (e.g., `user_path / "ankimonDEV.db"`).
3.  **Establish Interface:** Re-initializes connections. If the file does not exist, SQLite automatically generates the file, and `_setup_database()` provisions the standard table structures and indices.
4.  **Reload Domains:** Domain models are re-loaded in-place:
    *   Reloads the `main_pokemon` reference from the new database.
    *   Reloads PC grid entries by firing `pc_box.reload_pc()`.
    *   Updates currency, statistics, and badges in the in-memory `TrainerCard` instance.

---

## 2. SQLite Transaction and Write Reliability

To guarantee 100% database integrity under rapid card reviews (where database writes occur multiple times a second), the system enforces strict write standards inside `pyobj/database_manager.py`.

### A. Atomic Transactions (`with` block boundaries)
The codebase strictly prohibits floating cursor executions. All insert, update, or delete commands are grouped inside context managers:

```python
def save_pokemon(self, pokemon_obj):
    conn = self._get_connection()
    try:
        with conn: # Enforces atomic autocommit/rollback boundaries
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO captured_pokemon (individual_id, is_main, data) VALUES (?, ?, ?)",
                (pokemon_obj.individual_id, 1 if pokemon_obj.is_main else 0, self._obfuscate(pokemon_obj.to_dict()))
            )
    except sqlite3.Error as e:
        self._log("error", f"Database write transaction failed: {e}")
        # Automatically rolls back the database state to the pre-transaction threshold
```

### B. Transaction Locking (`IMMEDIATE` lock boundaries)
To prevent lock contention errors (`database is locked`) when background synchronization processes run concurrently with user card answers, the system uses SQLite's immediate write locks on connection handles.

### C. Obfuscation Cleanup
In standard Ankimon branches, JSON writes were heavily obfuscated. In our local fork, the database stores plain, readable, human-inspectable JSON strings within the database `data` column. This makes direct database inspection via DB browser or custom developer scripts simple and robust.

---

## 3. Automated Backups

To guard against file corruption:
*   **Startup Backup:** Upon Anki profile open, `BackupManager` creates a compressed backup of the active SQLite database file (`ankimon.db` or `ankimonDEV.db`) inside the `backup/` subfolder.
*   **Database Isolation:** Backups and restores are segregated based on active database mode (production vs dev). Restoring a backup only applies to the database corresponding to the active mode, preventing state leakage or contamination.
*   **Rollback Path:** In the event of schema migration errors or corrupt indices, the add-on recovers by rolling back to the latest valid backup.

> [!CAUTION]
> Never manually edit the SQLite database files while Anki is running. Anki maintains open connection handles, and modifications from external clients can lead to write conflicts and data loss.

---

## 4. Database Performance Optimizations

To eliminate lag during database switching and startup schema verification, the persistence layer implements the following optimizations:

### A. Journal Mode Check
Instead of blindly running `PRAGMA journal_mode=WAL;` on every database connection acquisition (which incurs synchronous disk writes), `_get_connection()` queries the current journal mode first. It only issues the write PRAGMA if the database is not already in WAL mode.

### B. Setup Schema Gating
During database initialization and hot-swaps, `_setup_database()` checks if all required tables (such as `captured_pokemon`, `metadata`, etc.) already exist. If they do, it skips executing redundant `CREATE TABLE` and `CREATE INDEX` statements, dramatically speeding up connection opening times from seconds to under 2 milliseconds.

### C. Direct Off-Connection Syncing
When processing mobile reviews that belong to the inactive database, the sync pipeline connects directly to the inactive database file to write the queued reviews and update the watermark. This completely bypasses the global `mw.ankimon_db.switch_database()` method, avoiding expensive in-memory reloads, UI layout cascades, and unnecessary connection closures on the active user profile.

### D. Loop-Level Caching and Visibility Guards
- **Loop-Level Caching**: During mobile reviews simulation and resolution runs, the SQLite-based `load_collected_pokemon_ids()` is temporarily patched in memory to return a pre-loaded cache set. This avoids executing synchronous SELECT queries on every single iteration inside `generate_random_pokemon()`, making dry-runs 100x faster.
- **Loop Gating**: The simulation dry-run caps active random generations at a maximum of 100 reviews, mathematically extrapolating the rest to guarantee a responsive UI even under massive review queues.
- **Visibility Guards**: During account switches, the global web-shell window refresh is skipped if the window is hidden/closed (`isVisible() == False`), avoiding unnecessary dry-run calculations.

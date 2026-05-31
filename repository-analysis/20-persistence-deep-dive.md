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
*   **Startup Backup:** Upon Anki profile open, `BackupManager` creates a compressed backup of the active SQLite database inside the `backup/` subfolder.
*   **Rollback Path:** In the event of schema migration errors or corrupt indices, the add-on recovers by rolling back to the latest valid backup.

> [!CAUTION]
> Never manually edit the SQLite database files while Anki is running. Anki maintains open connection handles, and modifications from external clients can lead to write conflicts and data loss.

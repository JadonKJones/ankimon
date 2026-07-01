"""
Scaffolding smoke tests (Stage A, section 16).

Stub-driven proofs that the reconciled substrate carries behaviour rather than
just compiling as dead code — while porting ZERO leaf features:

  (a) construct the web-shell HOST and mount a trivial STUB screen;
  (b) open a thread-safe DB connection under WAL from two threads;
  (c) fire one live-update push (notify_stats_changed) and observe it arrive;
  (d) run one QueryOp-style async boot to completion.

These need real PyQt6 (a QApplication), so they run in the Qt / Tier-2 environment;
the whole module skips cleanly where PyQt6 is absent (the aqt-free Tier-1 env).
"""

import json
import threading

import pytest

pytest.importorskip("PyQt6")  # Qt env only; skipped in the aqt-free Tier-1 env.


# --- (a) web-shell host mounts a stub screen -------------------------------


def test_webshell_host_mounts_stub_screen(qapp):
    from PyQt6.QtWidgets import QLabel

    from Ankimon.webshell import WebShellHost

    host = WebShellHost(title="Ankimon (smoke)")
    stub = QLabel("stub screen")
    index = host.mount("stub", stub, label="Stub")

    assert index == 0
    assert host.screen_ids() == ["stub"]

    host.show_screen("stub")  # must not raise; stub becomes current

    # A second screen mounts alongside the first (host is genuinely multi-screen).
    host.mount("stub2", QLabel("second"), label="Stub 2")
    assert host.screen_ids() == ["stub", "stub2"]

    # Duplicate screen ids are rejected.
    with pytest.raises(ValueError):
        host.mount("stub", QLabel("dupe"))


# --- (b) thread-safe DB connection under WAL, from two threads -------------


def test_threadsafe_db_under_wal_two_threads(qapp, tmp_path):
    from Ankimon.pyobj.database_manager import AnkimonDB

    db = AnkimonDB(db_path=str(tmp_path / "smoke.db"), wal=True)

    gui_conn = db._get_connection()  # GUI thread connection
    assert str(gui_conn.execute("PRAGMA journal_mode;").fetchone()[0]).lower() == "wal"
    gui_conn.execute("CREATE TABLE IF NOT EXISTS t (x INTEGER)")
    gui_conn.execute("INSERT INTO t VALUES (1)")
    gui_conn.commit()

    out = {}

    def worker():
        # A real QApplication exists (qapp), and this is not its thread, so the DB
        # layer hands out a DEDICATED per-thread connection (check_same_thread=False).
        conn = db._get_connection()
        out["distinct_conn"] = conn is not gui_conn
        out["mode"] = str(conn.execute("PRAGMA journal_mode;").fetchone()[0]).lower()
        out["seen_before"] = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        conn.execute("INSERT INTO t VALUES (2)")
        conn.commit()
        conn.close()

    th = threading.Thread(target=worker)
    th.start()
    th.join()

    assert out["distinct_conn"] is True  # separate connection per thread
    assert out["mode"] == "wal"  # background connection is WAL too
    assert out["seen_before"] == 1  # WAL reader saw the GUI thread's commit
    assert (
        gui_conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 2
    )  # sees worker's commit

    db.close()


# --- (c) live-update push arrives ------------------------------------------


def test_live_update_push_arrives(qapp):
    from Ankimon.webshell import LiveUpdateBridge

    bridge = LiveUpdateBridge()
    received = []
    bridge.stats_changed.connect(received.append)

    bridge.notify_stats_changed({"cash": 500, "level": 3, "caught": 7})

    assert len(received) == 1, "the push did not arrive"
    payload = json.loads(received[0])
    assert payload == {"cash": 500, "level": 3, "caught": 7}

    # The JS-invokable refresh slot also emits (empty nudge).
    bridge.request_refresh()
    assert json.loads(received[-1]) == {}


# --- (d) async QueryOp boot runs to completion -----------------------------


def test_async_boot_runs_to_completion():
    from Ankimon.boot_async import run_startup_boot

    class SyncQueryOp:
        """Mirrors aqt.operations.QueryOp's synchronous contract for testing."""

        def __init__(self, *, parent, op, success):
            self._op = op
            self._success = success

        def with_progress(self, *a, **k):
            return self

        def run_in_background(self):
            result = self._op(None)  # op receives the collection; None here
            self._success(result)
            return result

    calls = {}

    def background():
        calls["ran_op"] = True
        return {"booted": True, "value": 42}

    def on_complete(result):
        calls["result"] = result

    run_startup_boot(background, on_complete, parent=object(), query_op_cls=SyncQueryOp)

    assert calls.get("ran_op") is True
    assert calls["result"] == {"booted": True, "value": 42}

"""Tier-1 seam tests for the Mobile & Web Reviews sync engine (F14/F25/F29).

These exercise the mobile-review backend through the service seam (``services``
+ ``events``) rather than exp's direct ``aqt.mw.*`` access:

* the deferred ``AnkimonDB`` mobile accessors (watermark / queue / history /
  cross-DB resolution sync);
* the desktop-session bookkeeping + revlog detection + post-sync queueing
  pipeline;
* the pure helpers (``_parse_cards_per_round`` / ``_normalize_ev_yield``);
* ``menu_buttons.update_mobile_badge`` as a guarded no-op before F36 builds the
  menu action.

The engine imports are stdlib-only at module load, so this runs Qt-free in the
Tier-1 venv; ``aqt`` / ``anki`` / ``PyQt6`` are stubbed so any lazy import of a
sibling module resolves without a real Anki/Qt runtime.
"""

import os
import sys
import types
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# --- Tier-1 bootstrap: real addon modules, faked Anki/Qt runtime ------------
_SRC = Path(__file__).resolve().parent.parent / "src"

for _name in (
    "aqt", "aqt.qt", "aqt.utils", "aqt.gui_hooks", "aqt.operations",
    "aqt.theme", "aqt.sound", "aqt.webview", "aqt.main",
    "anki", "anki.hooks", "anki.collection", "anki.utils",
    "PyQt6", "PyQt6.QtGui", "PyQt6.QtWidgets", "PyQt6.QtCore",
    "PyQt6.QtWebChannel", "PyQt6.QtWebEngineWidgets",
):
    sys.modules.setdefault(_name, MagicMock())

for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj", "Ankimon.ankimon_items_web"):
    _existing = sys.modules.get(_pkg)
    if _existing is None or not hasattr(_existing, "__path__"):
        _mod = types.ModuleType(_pkg)
        _mod.__path__ = [str(_SRC / _pkg.replace(".", "/"))]
        _mod.__package__ = _pkg
        sys.modules[_pkg] = _mod

if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Point the DB layer's user_path at a scratch dir before it is imported.
_USER_DIR = Path(tempfile.mkdtemp(prefix="ankimon_mobile_ut_"))
os.environ.setdefault("ANKIMON_USER_PATH", str(_USER_DIR))

from Ankimon.services import services  # noqa: E402
from Ankimon.functions import mobile_sync as ms  # noqa: E402
from Ankimon.pyobj.database_manager import AnkimonDB  # noqa: E402


class _Logger:
    def log(self, *a, **k): pass
    def game_log(self, *a, **k): pass
    def log_and_showinfo(self, *a, **k): pass


class _Settings:
    def __init__(self, d=None):
        self.d = dict(d or {})

    def get(self, key, default=None):
        return self.d.get(key, default)

    def set(self, key, value):
        self.d[key] = value


@pytest.fixture
def mobile_db(tmp_path):
    """Fresh AnkimonDB wired into the service seam; state reset afterwards."""
    db = AnkimonDB(_Logger(), db_path=str(tmp_path / "ankimon.db"))
    prev_db, prev_col = services.db, services.col
    services.db = db
    services.col = None
    ms.clear_desktop_session()
    try:
        yield db, tmp_path
    finally:
        ms.clear_desktop_session()
        services.db, services.col = prev_db, prev_col
        try:
            db.close()
        except Exception:
            pass


# --- DB mobile accessors ----------------------------------------------------

def test_watermark_get_set_defaults_to_zero(mobile_db):
    db, _ = mobile_db
    assert db.get_mobile_watermark() == 0
    db.set_mobile_watermark(123456)
    assert db.get_mobile_watermark() == 123456


def test_queue_dedup_and_pending_count(mobile_db):
    db, _ = mobile_db
    reviews = [
        {"id": 101, "cid": 1001, "ease": 3, "time": 15000, "type": 1},
        {"id": 102, "cid": 1002, "ease": 2, "time": 20000, "type": 2},
    ]
    assert db.queue_mobile_battles(reviews) == 2
    assert db.get_pending_mobile_count() == 2
    # revlog_id is UNIQUE -> a re-queue of the same ids inserts nothing.
    assert db.queue_mobile_battles(reviews) == 0
    assert db.get_pending_mobile_count() == 2


def test_next_batch_ordering_and_mark_resolved(mobile_db):
    db, _ = mobile_db
    db.queue_mobile_battles([
        {"id": 205, "cid": 1, "ease": 3, "time": 1, "type": 1},
        {"id": 101, "cid": 2, "ease": 3, "time": 1, "type": 1},
    ])
    # oldest-first == lowest revlog_id first
    batch = db.get_next_pending_mobile_batch(limit=1)
    assert len(batch) == 1
    assert batch[0]["revlog_id"] == 101

    db.mark_mobile_battle_resolved(batch[0]["queue_id"])
    assert db.get_pending_mobile_count() == 1
    remaining = db.get_next_pending_mobile_batch(limit=10)
    assert [r["revlog_id"] for r in remaining] == [205]


def test_get_next_batch_empty(mobile_db):
    db, _ = mobile_db
    assert db.get_next_pending_mobile_batch(limit=5) == []


# --- Cross-DB resolution sync ----------------------------------------------

def test_cross_db_resolution_sync(mobile_db, monkeypatch):
    db, tmp_path = mobile_db
    # Route the "other DB" lookup at this test's scratch dir. Patch the module
    # globals the method actually reads (another test may have loaded a second
    # copy of database_manager into sys.modules, so patch via the class method).
    monkeypatch.setitem(
        AnkimonDB.sync_resolutions_to_other_db.__globals__, "user_path", tmp_path
    )

    other = tmp_path / "ankimonDEV.db"
    import sqlite3
    conn = sqlite3.connect(str(other))
    conn.execute(
        """CREATE TABLE pending_mobile_battles (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               revlog_id INTEGER UNIQUE NOT NULL, card_id INTEGER NOT NULL,
               ease INTEGER NOT NULL, review_time INTEGER NOT NULL,
               review_type INTEGER NOT NULL, queued_at INTEGER NOT NULL,
               resolved INTEGER NOT NULL DEFAULT 0, resolved_at INTEGER)"""
    )
    conn.execute(
        "INSERT INTO pending_mobile_battles (revlog_id, card_id, ease, review_time, review_type, queued_at) "
        "VALUES (777, 1, 3, 1, 1, 1)"
    )
    conn.commit()
    conn.close()

    db.sync_resolutions_to_other_db([777], resolved_at=999)

    conn = sqlite3.connect(str(other))
    row = conn.execute("SELECT resolved, resolved_at FROM pending_mobile_battles WHERE revlog_id=777").fetchone()
    conn.close()
    assert row == (1, 999)


# --- History table ----------------------------------------------------------

def test_history_add_get_clear_and_none_safety(mobile_db):
    db, _ = mobile_db
    assert db.get_mobile_history() == []
    # companion_* None and a missing xp_gained must not crash the insert.
    ok = db.add_mobile_history_entry({
        "timestamp": 10, "enemy_id": 25, "enemy_name": "Pikachu",
        "enemy_level": 5, "enemy_shiny": True, "companion_name": None,
        "companion_level": None, "outcome": "caught",
    })
    assert ok is True
    hist = db.get_mobile_history()
    assert len(hist) == 1
    assert hist[0]["enemy_name"] == "Pikachu"
    assert hist[0]["enemy_shiny"] is True
    assert hist[0]["xp_gained"] == 0
    assert db.clear_mobile_history() is True
    assert db.get_mobile_history() == []


def test_history_trims_to_500(mobile_db):
    db, _ = mobile_db
    entries = [
        {"timestamp": i, "enemy_id": i, "enemy_name": f"e{i}", "enemy_level": 1,
         "enemy_shiny": False, "outcome": "defeated", "xp_gained": 1}
        for i in range(520)
    ]
    assert db.add_mobile_history_entries_batch(entries) is True
    hist = db.get_mobile_history(limit=1000)
    assert len(hist) == 500
    # Newest kept, oldest trimmed.
    assert hist[0]["timestamp"] == 519
    assert min(h["timestamp"] for h in hist) == 20


# --- Desktop-session bookkeeping + watermark ------------------------------

def test_record_desktop_review_durably_records_without_advancing_watermark(mobile_db):
    db, _ = mobile_db
    prev_settings = services.settings
    services.settings = _Settings({"mobile.enabled": True, "misc.ankiweb_sync": True})
    try:
        db.set_mobile_watermark(1000)
        ms.record_desktop_review(1200)
        ms.record_desktop_review(1500)
        # The watermark is NOT advanced: advancing it would permanently skip an
        # older, not-yet-synced mobile review whose revlog id is below a desktop
        # review's timestamp.
        assert db.get_mobile_watermark() == 1000
        # Ids are tracked via the in-memory session set + the durable store.
        assert ms.get_desktop_session_revlog_ids() == frozenset({1200, 1500})
        # Durable: they survive an in-memory session clear (a mid-session restart).
        ms.clear_desktop_session()
        assert ms.get_desktop_session_revlog_ids() == frozenset({1200, 1500})
        # Advancing the watermark past an id prunes it from the durable store (it
        # is already excluded by the `id > watermark` detection filter).
        db.set_mobile_watermark(1300)
        assert ms.get_desktop_session_revlog_ids() == frozenset({1500})
    finally:
        services.settings = prev_settings
        db.clear_desktop_processed_reviews()
        ms.clear_desktop_session()


def test_record_desktop_review_skips_durable_write_when_sync_off(mobile_db):
    db, _ = mobile_db
    prev_settings = services.settings
    # Mobile reviews only arrive via AnkiWeb sync; with it off the durable
    # per-review write (an fsync) is skipped, but session de-dupe still works.
    services.settings = _Settings({"mobile.enabled": True, "misc.ankiweb_sync": False})
    try:
        ms.record_desktop_review(2000)
        assert 2000 in ms.get_desktop_session_revlog_ids()
        assert db.get_desktop_processed_revlog_ids() == set()
    finally:
        services.settings = prev_settings
        ms.clear_desktop_session()


def test_get_desktop_session_resolves_card_ids_via_col(mobile_db):
    db, _ = mobile_db
    ms.record_desktop_review(0, card_id=42)   # revlog_id falsy -> only card recorded

    class _Col:
        class db:
            @staticmethod
            def list(q, *cids):
                return [9001] if 42 in cids else []

    ids = ms.get_desktop_session_revlog_ids(_Col())
    assert 9001 in ids


# --- detect / process pipeline ---------------------------------------------

class _FakeCol:
    """Minimal stand-in for mw.col with just the revlog queries the engine uses."""

    def __init__(self, rows):
        self._rows = rows  # list of (id, cid, ease, time, type)
        outer = self

        class _DB:
            def all(self, _q, watermark):
                return [r for r in outer._rows if r[0] > watermark]

            def scalar(self, _q):
                return max((r[0] for r in outer._rows), default=0)

        self.db = _DB()


def test_detect_mobile_reviews_filters_watermark_and_session():
    col = _FakeCol([(10, 1, 3, 100, 1), (20, 2, 2, 200, 1), (30, 3, 4, 300, 0)])
    result = ms.detect_mobile_reviews(col, watermark_ms=5, desktop_revlog_ids=frozenset({20}))
    # > watermark AND not in the desktop session set.
    assert [r["id"] for r in result] == [10, 30]


def test_process_mobile_reviews_queues_and_advances_watermark(mobile_db):
    db, _ = mobile_db
    col = _FakeCol([(11, 1, 3, 100, 1), (22, 2, 2, 200, 1), (33, 3, 4, 300, 0)])
    queued = ms.process_mobile_reviews_after_sync(col, db, _Settings({"mobile.enabled": True}), _Logger())
    assert queued == 3
    assert db.get_pending_mobile_count() == 3
    assert db.get_mobile_watermark() == 33


def test_process_respects_mobile_disabled(mobile_db):
    db, _ = mobile_db
    col = _FakeCol([(11, 1, 3, 100, 1)])
    assert ms.process_mobile_reviews_after_sync(col, db, _Settings({"mobile.enabled": False}), _Logger()) == 0
    assert db.get_pending_mobile_count() == 0


def test_process_applies_queue_cap(mobile_db, monkeypatch):
    db, _ = mobile_db
    monkeypatch.setattr(ms, "MOBILE_QUEUE_CAP", 2)
    col = _FakeCol([(1, 1, 3, 1, 1), (2, 2, 3, 1, 1), (3, 3, 3, 1, 1)])
    queued = ms.process_mobile_reviews_after_sync(col, db, _Settings({"mobile.enabled": True}), _Logger())
    # cap keeps the most recent 2 (highest ids).
    assert queued == 2
    batch = db.get_next_pending_mobile_batch(limit=10)
    assert sorted(r["revlog_id"] for r in batch) == [2, 3]


# --- Pure helpers -----------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (4, 4),
    ("3", 3),
    ("1-3", 2),
    # cards_per_round must never be 0 — a range whose average truncates to 0
    # (e.g. "0-0" / "0-1") or a plain 0/negative would ZeroDivide at the
    # mobile-sync entry point; every branch clamps to >= 1.
    ("0-0", 1),
    ("0-1", 1),
    (0, 1),
    (-5, 1),
    (None, 2),
])
def test_parse_cards_per_round(value, expected):
    settings = _Settings({"battle.cards_per_round": value}) if value is not None else None
    assert ms._parse_cards_per_round(settings)[0] == expected


@pytest.mark.parametrize("earned,earner,share_id,expected", [
    (100, "A", "B", (50, 50)),      # even split
    (101, "A", "B", (51, 50)),      # earner keeps the odd remainder, no XP lost
    (100, "A", "A", (100, 0)),      # can't share with yourself
    (100, "A", None, (100, 0)),     # XP-Share not configured
    (0, "A", "B", (0, 0)),          # nothing to split
    (100, "A", "b", (50, 50)),      # distinct ids -> split applies
])
def test_xp_share_split(earned, earner, share_id, expected):
    assert ms._xp_share_split(earned, earner, share_id) == expected


def test_commit_replay_defeat_applies_xp_share(monkeypatch):
    """XP-Share parity on the MANUAL replay-resolve path: commit_replay_outcome
    ('defeat', ...) must split the battling companion's XP 50/50 with the
    configured trainer.xp_share target, exactly like the bulk-resolve commit
    block. Without the split this path grants the companion 100% and the
    XP-Share target nothing (finding: mobile_sync commit_replay_outcome)."""
    class _S:
        def __init__(self, d): self._d = dict(d)
        def get(self, k, default=None): return self._d.get(k, default)
        def set(self, k, v): self._d[k] = v

    # Spy on the attribution seam so we can see who got how much XP.
    calls = []
    monkeypatch.setattr(
        ms, "_attribute_xp_and_evs_to_companion",
        lambda cid, xp, evs, settings_obj, battles_fought=1, db=None, logger=None: calls.append((str(cid), xp)),
    )
    # Patch on the imported module object (not a dotted string path, which is
    # import-order fragile across the full suite).
    import Ankimon.business as _biz
    monkeypatch.setattr(_biz, "calculate_cp_from_dict", lambda d: 10)

    settings = _S({"trainer.xp_share": "TARGET"})
    db = MagicMock()
    db.get_pending_mobile_count.return_value = 0
    enemy = MagicMock()
    outcome_data = {
        "enemy_pokemon": enemy,
        "battle_xp": 100,
        "total_xp": 100,
        "accumulated_evs": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "total_trainer_xp": 0,
        "gained_cash": 0,
        "companion_id": "COMP",
        "companion_name": "Comp",
        "companion_level": 5,
        "review_ids": [],
        "companion_fainted": False,
    }

    res = ms.commit_replay_outcome("defeat", outcome_data, db, settings, None, None)
    assert res.get("success") is True
    # Companion keeps half; the XP-Share target receives the other half.
    assert ("COMP", 50) in calls
    assert ("TARGET", 50) in calls


def test_commit_replay_defeat_no_share_when_unset(monkeypatch):
    """With XP-Share unset the manual replay-defeat path grants the companion the
    full battle XP and makes no second attribution call."""
    class _S:
        def __init__(self, d): self._d = dict(d)
        def get(self, k, default=None): return self._d.get(k, default)
        def set(self, k, v): self._d[k] = v

    calls = []
    monkeypatch.setattr(
        ms, "_attribute_xp_and_evs_to_companion",
        lambda cid, xp, evs, settings_obj, battles_fought=1, db=None, logger=None: calls.append((str(cid), xp)),
    )
    import Ankimon.business as _biz
    monkeypatch.setattr(_biz, "calculate_cp_from_dict", lambda d: 10)

    settings = _S({})  # no trainer.xp_share
    db = MagicMock()
    db.get_pending_mobile_count.return_value = 0
    outcome_data = {
        "enemy_pokemon": MagicMock(),
        "battle_xp": 100, "total_xp": 100,
        "accumulated_evs": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "total_trainer_xp": 0, "gained_cash": 0,
        "companion_id": "COMP", "companion_name": "Comp", "companion_level": 5,
        "review_ids": [], "companion_fainted": False,
    }
    res = ms.commit_replay_outcome("defeat", outcome_data, db, settings, None, None)
    assert res.get("success") is True
    assert calls == [("COMP", 100)]


def test_normalize_ev_yield_renames_keys():
    assert ms._normalize_ev_yield({"attack": 4, "speed": 2, "hp": 1}) == {"atk": 4, "spe": 2, "hp": 1}
    assert ms._normalize_ev_yield({}) == {}


def test_answercard_after_records_desktop_review(monkeypatch):
    """F29 de-dupe: answerCard_after must record the just-resolved review's
    revlog id + card id into the mobile-sync exclusion set, so the next
    detect pass does not re-queue it as a mobile battle (double XP/catches)."""
    # card_hooks pulls the heavy singletons module (markdown/Qt) transitively;
    # stub it with just the two names the module binds at import.
    stub = types.ModuleType("Ankimon.singletons")
    stub.ankimon_tracker_obj = MagicMock()
    stub.reviewer_obj = MagicMock()
    monkeypatch.setitem(sys.modules, "Ankimon.singletons", stub)
    monkeypatch.delitem(sys.modules, "Ankimon.card_hooks", raising=False)

    import Ankimon.card_hooks as ch

    ms.clear_desktop_session()

    class _Card:
        id = 42

    class _DB:
        def scalar(self, _sql, cid):
            return 9999 if cid == 42 else 0

    class _Sched:
        def answerButtons(self, _card):
            return 4

    rev = types.SimpleNamespace(
        mw=types.SimpleNamespace(col=types.SimpleNamespace(db=_DB(), sched=_Sched()))
    )

    try:
        ch.answerCard_after(rev, _Card(), ease=4)
        ids = ms.get_desktop_session_revlog_ids()
        assert 9999 in ids
    finally:
        ms.clear_desktop_session()

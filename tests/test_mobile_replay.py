"""Tier-1 seam tests for single-battle mobile resolution (F14 replay path).

Covers the DB-backed dequeue semantics behind ``MobileBridge.resolveNext`` and
the engine's ``resolve_next`` empty-queue contract, all through the service seam
and without a real Anki/Qt runtime.
"""

import os
import sys
import time
import types
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

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

_USER_DIR = Path(tempfile.mkdtemp(prefix="ankimon_replay_ut_"))
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
    db = AnkimonDB(_Logger(), db_path=str(tmp_path / "ankimon.db"))
    prev_db, prev_col = services.db, services.col
    services.db = db
    services.col = None
    ms.clear_desktop_session()
    try:
        yield db
    finally:
        ms.clear_desktop_session()
        services.db, services.col = prev_db, prev_col
        try:
            db.close()
        except Exception:
            pass


def _seed(db, n):
    now = int(time.time() * 1000)
    db.queue_mobile_battles([
        {"id": now + i, "cid": 1000 + i, "ease": 3, "time": 5000, "type": 1}
        for i in range(n)
    ])


def test_resolve_next_marks_one_batch_resolved(mobile_db):
    """A single dequeue-of-two resolves exactly two reviews, leaving the rest."""
    db = mobile_db
    _seed(db, 6)  # cards_per_round default 2 -> 3 encounters
    batch = db.get_next_pending_mobile_batch(limit=2)
    assert len(batch) == 2
    for row in batch:
        db.mark_mobile_battle_resolved(row["queue_id"])
    assert db.get_pending_mobile_count() == 4


def test_pending_count_decrements_each_resolve(mobile_db):
    db = mobile_db
    _seed(db, 4)
    for _ in range(2):
        batch = db.get_next_pending_mobile_batch(limit=2)
        if not batch:
            break
        for row in batch:
            db.mark_mobile_battle_resolved(row["queue_id"])
    assert db.get_pending_mobile_count() == 0


def test_resolved_flag_persists_and_batch_skips_resolved(mobile_db):
    db = mobile_db
    _seed(db, 3)
    first = db.get_next_pending_mobile_batch(limit=1)[0]
    db.mark_mobile_battle_resolved(first["queue_id"])
    # a resolved row is never handed out again
    remaining = db.get_next_pending_mobile_batch(limit=10)
    assert first["revlog_id"] not in [r["revlog_id"] for r in remaining]
    assert len(remaining) == 2


def test_resolve_next_returns_done_when_empty(mobile_db):
    """The engine's public resolve_next contract: empty queue -> {'done': True}."""
    db = mobile_db
    result = ms.resolve_next(
        companion_id="",
        db=db,
        settings_obj=_Settings({"battle.cards_per_round": 2}),
        tracker=None,
        trainer_card=None,
        main_pokemon=None,
        logger=_Logger(),
        day_cutoff=1,  # non-zero so the mw.col scheduler lookup is skipped
    )
    assert result == {"done": True}

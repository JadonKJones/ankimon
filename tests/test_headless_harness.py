"""
Regression test: the headless agent harness can boot and play Ankimon.

This is the high-value end-to-end test the whole refactor exists to enable — it
runs the *real* battle loop / encounter logic against a throwaway profile with no
Anki and no Qt, and asserts the core loop produces the right observable events
with zero errors.

Runs under pytest (CI) or as a plain script:  python3 tests/test_headless_harness.py
"""

import sys
import pathlib

_repo = pathlib.Path(__file__).resolve().parents[1]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))


def test_play_session_runs_without_errors():
    from harness.scenarios import smoke_play

    summary = smoke_play.run(verbose=False)
    assert summary["caught"] >= 1
    assert summary["defeated"] >= 1
    assert summary["event_counts"].get("battle", 0) > 0
    assert summary["event_counts"].get("encounter", 0) > 0
    assert summary["event_counts"].get("faint", 0) > 0
    assert "error" not in summary["event_counts"], "play produced error events"
    assert summary["collection"] >= 1


def test_state_snapshot_and_single_answer():
    from harness.driver import Driver

    d = Driver(settings_overrides={"battle.cards_per_round": 1})
    st = d.get_state()
    for key in ("main", "enemy", "tracker", "collection", "trainer"):
        assert key in st, f"missing state key: {key}"
    assert st["main"]["max_hp"] >= 1
    assert isinstance(st["enemy"]["attacks"], list)

    events = d.answer("good")
    assert any(e["type"] == "battle" for e in events), "answering produced no battle"
    assert not any(e["type"] == "error" for e in events), "answering produced an error"


def test_auto_battle_mode_cycles():
    from harness.scenarios import auto_battle

    result = auto_battle.run(mode=2, answers=30, verbose=False)
    assert result["event_counts"].get("encounter", 0) >= 1
    assert "error" not in result["event_counts"]


if __name__ == "__main__":
    test_play_session_runs_without_errors()
    test_state_snapshot_and_single_answer()
    test_auto_battle_mode_cycles()
    print("headless harness tests: OK")

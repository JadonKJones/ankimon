"""
Regression test: the headless agent harness can boot and play Ankimon.

This is the high-value end-to-end test the whole refactor exists to enable — it
runs the *real* battle loop / encounter logic against a throwaway profile with no
Anki and no Qt, and asserts the core loop produces the right observable events
with zero errors.

Isolation: these tests need the GENUINE ``Ankimon`` package booted fresh. The rest
of the unit suite (and this repo's conftest.py) stub ``aqt`` / ``Ankimon.*`` in
sys.modules at import time, which makes an in-process real boot unreliable when
this file runs after them. So — exactly like ``harness/check.py`` — each test runs
its scenario in a CLEAN child interpreter and asserts on a JSON result. That makes
the suite robust (no in-process pollution) without any mocking.

Runs under pytest (CI) or as a plain script:  python3 tests/test_headless_harness.py
"""

import json
import pathlib
import subprocess
import sys

_repo = pathlib.Path(__file__).resolve().parents[1]
_MARKER = "HARNESS_RESULT:"


# Force the Tier-1 contract in the child: NO Qt. This unit suite (integrity_tests)
# installs aqt+PyQt6 (requirements.txt) and runs under xvfb, so an Ankimon leaf
# module's "Qt present" path would construct a QWidget at import with no
# QApplication and SIGABRT the child. The dedicated harness CI (harness.yml) runs
# Tier-1 with no Qt deps at all; we reproduce that by making aqt/PyQt6 unimportable
# in the child, so the guarded modules take their headless no-Qt path.
_BLOCK_QT = (
    "import sys\n"
    "class _NoQt:\n"
    "    _b = ('aqt', 'PyQt6', 'PyQt5')\n"
    "    def find_spec(self, name, path=None, target=None):\n"
    "        if name.split('.')[0] in self._b:\n"
    "            raise ModuleNotFoundError(name + ' blocked: harness Tier-1 is Qt-free')\n"
    "        return None\n"
    "sys.meta_path.insert(0, _NoQt())\n"
)


def _subrun(snippet):
    """Run a harness snippet in a fresh, Qt-free interpreter; return its JSON result.

    The snippet must print ``HARNESS_RESULT:<json>`` once. We isolate in a child
    process so the in-process sys.modules stubs other test files install can't
    break the real Ankimon boot (the same reason check.py shells out per probe),
    and we block Qt so the child runs the genuine Tier-1 (no-Anki/no-Qt) path."""
    code = _BLOCK_QT + "import json\nsys.path.insert(0, %r)\n%s" % (str(_repo), snippet)
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=300
    )
    assert proc.returncode == 0, (
        "harness subprocess failed (rc=%d):\n--- stdout ---\n%s\n--- stderr ---\n%s"
        % (proc.returncode, proc.stdout, proc.stderr)
    )
    for line in reversed(proc.stdout.splitlines()):
        if line.startswith(_MARKER):
            return json.loads(line[len(_MARKER) :])
    raise AssertionError(
        "no %s in harness output:\n%s\n%s" % (_MARKER, proc.stdout, proc.stderr)
    )


def test_play_session_runs_without_errors():
    summary = _subrun(
        "from harness.scenarios import smoke_play\n"
        "print(%r + json.dumps(smoke_play.run(verbose=False)))" % _MARKER
    )
    assert summary["caught"] >= 1
    assert summary["defeated"] >= 1
    assert summary["event_counts"].get("battle", 0) > 0
    assert summary["event_counts"].get("encounter", 0) > 0
    assert summary["event_counts"].get("faint", 0) > 0
    assert "error" not in summary["event_counts"], "play produced error events"
    assert summary["collection"] >= 1


def test_state_snapshot_and_single_answer():
    result = _subrun(
        "from harness.driver import Driver\n"
        "d = Driver(settings_overrides={'battle.cards_per_round': 1})\n"
        "st = d.get_state()\n"
        "events = d.answer('good')\n"
        "print(%r + json.dumps({\n"
        "    'state_keys': list(st.keys()),\n"
        "    'max_hp': st['main']['max_hp'],\n"
        "    'enemy_attacks_is_list': isinstance(st['enemy']['attacks'], list),\n"
        "    'has_battle': any(e['type'] == 'battle' for e in events),\n"
        "    'has_error': any(e['type'] == 'error' for e in events),\n"
        "}))" % _MARKER
    )
    for key in ("main", "enemy", "tracker", "collection", "trainer"):
        assert key in result["state_keys"], f"missing state key: {key}"
    assert result["max_hp"] >= 1
    assert result["enemy_attacks_is_list"]
    assert result["has_battle"], "answering produced no battle"
    assert not result["has_error"], "answering produced an error"


def test_auto_battle_mode_cycles():
    result = _subrun(
        "from harness.scenarios import auto_battle\n"
        "r = auto_battle.run(mode=2, answers=30, verbose=False)\n"
        "print(%r + json.dumps(r['event_counts']))" % _MARKER
    )
    assert result.get("encounter", 0) >= 1
    assert "error" not in result


def test_battle_loop_survives_dead_windows():
    """F24: on_review_card's is_alive guards must skip a deleted (dead) window
    instead of raising 'wrapped C/C++ object of type X has been deleted'.

    We swap the live test_window/evo_window for a stand-in whose every attribute
    access (including the ``objectName`` liveness probe) raises RuntimeError —
    exactly what a Qt widget does once its C++ half is destroyed. The battle loop
    must keep running: real battle/faint/encounter events, zero error events.
    Auto-catch mode (1) is used so the faint path never routes through the
    evo_window level-up branch, isolating this to the battle_loop guards."""
    result = _subrun(
        "from collections import Counter\n"
        "from harness.driver import Driver\n"
        # Deterministic RNG in the child: enemy faints are stochastic
        # (~1-2 per 60 'good' answers), so an unseeded run can produce zero
        # faints and flake the gate. seed(0) is verified to exercise the
        # faint-guard path with zero error events.
        "import random\n"
        "random.seed(0)\n"
        "class _DeadWindow:\n"
        "    # Simulates a Qt window whose underlying C++ object was deleted.\n"
        "    def objectName(self):\n"
        "        raise RuntimeError('wrapped C/C++ object of type TestWindow has been deleted')\n"
        "    def __getattr__(self, name):\n"
        "        raise RuntimeError('wrapped C/C++ object of type TestWindow has been deleted')\n"
        "d = Driver(settings_overrides={'battle.cards_per_round': 1, 'battle.automatic_battle': 1})\n"
        "d.services.test_window = _DeadWindow()\n"
        "d.services.evo_window = _DeadWindow()\n"
        "events = []\n"
        "for _ in range(60):\n"
        "    events += d.answer('good')\n"
        "kinds = Counter(e['type'] for e in events)\n"
        "errs = [e for e in events if e['type'] == 'error']\n"
        "print(%r + json.dumps({\n"
        "    'has_battle': kinds.get('battle', 0) > 0,\n"
        "    'has_faint': kinds.get('faint', 0) > 0,\n"
        "    'has_encounter': kinds.get('encounter', 0) > 0,\n"
        "    'errors': kinds.get('error', 0),\n"
        "    'first_error': (errs[0].get('exception') if errs else None),\n"
        "}))" % _MARKER
    )
    assert result["has_battle"], "no battle turns with dead windows"
    assert result["has_faint"], "enemy never fainted (faint guard path not exercised)"
    assert result["has_encounter"], "auto-catch never spawned a new encounter"
    assert result["errors"] == 0, (
        "dead-window touch raised instead of being guarded: %s" % result["first_error"]
    )


def test_victory_path_move_gate_sees_moves_learned_at_level_up():
    """The victory-time move-type gate must evaluate the CURRENT moveset.

    Regression for a tempting but wrong optimization. The friendship checker
    falls back to a services.db.get_pokemon() read for whichever of `attacks` /
    `pokemon_defeated` the caller leaves as None, and most defeats grant no
    level-up, so `attacks` is None on the common path. Replacing that read with
    the in-memory `main_pokemon.attacks` looks free but is not: the level-up
    merge writes the learned move to the DB dict only, so the PokemonObject's
    moveset goes stale on the first level-up and never re-syncs (verified: still
    ['tackle','growl'] 1200 answers after the DB reached
    ['tackle','growl','babydolleyes','swift']).

    Concretely: an Eevee that learns Baby-Doll Eyes at Lv15 must be offered
    Sylveon (700) on a later defeat, not Espeon/Umbreon. Reading the stale
    in-memory list breaks exactly that, and flip-flops, because the rarer
    level-up defeats still pass a fresh list.
    """
    result = _subrun(
        "from harness.driver import Driver\n"
        "import random\n"
        "random.seed(0)\n"
        # Starts below Lv15 knowing no Fairy move, with room in the moveset for
        # Baby-Doll Eyes, and enough friendship that Sylveon is offerable as
        # soon as the gate is met.
        "d = Driver(seed={'main': {'species': 'Eevee', 'level': 14, 'gender': 'M',\n"
        "                          'friendship': 300,\n"
        "                          'attacks': ['Tackle', 'Growl']}},\n"
        "           settings_overrides={'battle.cards_per_round': 1},\n"
        "           evolution_policy='ignore')\n"
        "import Ankimon.functions.encounter_functions as ef\n"
        "import Ankimon.functions.friendship_evolution as fe\n"
        "s = d.services\n"
        "offers = []\n"
        "_real = fe.check_friendship_evolution_for_pokemon\n"
        # The moveset the gate actually evaluates: what the caller passed, or —
        # when it passes None — the stored one the checker falls back to.
        "def spy(*a, **kw):\n"
        "    stored = (s.db.get_main_pokemon() or {}).get('attacks') or []\n"
        "    passed = kw.get('attacks')\n"
        "    effective = stored if passed is None else passed\n"
        "    norm = lambda ms: [str(m).lower().replace(' ', '').replace('-', '')\n"
        "                       for m in (ms or [])]\n"
        "    r = _real(*a, **kw)\n"
        "    offers.append({'evo': r,\n"
        "                   'learned': 'babydolleyes' in norm(stored),\n"
        "                   'gate_saw_it': 'babydolleyes' in norm(effective)})\n"
        "    return r\n"
        "ef.check_friendship_evolution_for_pokemon = spy\n"
        "for _ in range(700):\n"
        "    d.answer('good')\n"
        "    if s.enemy_pokemon.hp <= 0:\n"
        "        d.defeat()\n"
        "after = [o for o in offers if o['learned']]\n"
        "print(%r + json.dumps({\n"
        "    'checks': len(offers),\n"
        "    'after_learning': len(after),\n"
        "    'gate_blind_to_learned_move': sum(1 for o in after if not o['gate_saw_it']),\n"
        "    'sylveon': sum(1 for o in after if o['evo'] == 700),\n"
        "    'wrong_eeveelution': sorted({o['evo'] for o in after\n"
        "                                 if o['evo'] not in (None, 700)}),\n"
        "    'db_attacks': (d.services.db.get_main_pokemon() or {}).get('attacks'),\n"
        "    'obj_attacks': list(s.main_pokemon.attacks),\n"
        "}))" % _MARKER
    )
    assert result["checks"] > 0, "no defeats occurred; the check never ran"
    assert "babydolleyes" in (result["db_attacks"] or []), (
        "Eevee never learned Baby-Doll Eyes; the scenario did not exercise the gate"
    )
    assert result["after_learning"] > 0, (
        "no victory check ran after the move was learned"
    )
    # The invariant: once the move is in the save, every victory-time check must
    # evaluate a moveset that contains it.
    assert result["gate_blind_to_learned_move"] == 0, (
        "%d/%d victory checks evaluated a moveset missing the learned Fairy move "
        "(db=%s, in-memory=%s)"
        % (
            result["gate_blind_to_learned_move"],
            result["after_learning"],
            result["db_attacks"],
            result["obj_attacks"],
        )
    )
    assert not result["wrong_eeveelution"], (
        "move gate evaluated a stale moveset: offered %s instead of Sylveon after "
        "the Fairy move was learned (db=%s, in-memory=%s)"
        % (result["wrong_eeveelution"], result["db_attacks"], result["obj_attacks"])
    )
    assert result["sylveon"] > 0, (
        "Sylveon was never offered after the Fairy move was learned (db=%s)"
        % (result["db_attacks"],)
    )


if __name__ == "__main__":
    test_play_session_runs_without_errors()
    test_state_snapshot_and_single_answer()
    test_auto_battle_mode_cycles()
    test_battle_loop_survives_dead_windows()
    test_victory_path_move_gate_sees_moves_learned_at_level_up()
    print("headless harness tests: OK")

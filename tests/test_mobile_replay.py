"""Mobile/web reviews: per-encounter resolveNext + encounter-seeding alignment.

Adapted to main's seams: the (deferred) web-shell ``MobileBridge`` is replaced by
``tests.mobile_engine_helpers.MobileBridge`` (delegates to the engine), the queue
dequeue tests use the real ``AnkimonDB`` mobile methods via the ``temp_env``
fixture (main's ctor takes no ``db_path=``), and imports use ``Ankimon.*`` rather
than BRRRR's ``src.Ankimon.*``.
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_src = Path(__file__).parent.parent / "src"

# Import test_database_manager first (which triggers its setup_mocks()).
from tests.test_database_manager import MockLogger, temp_env  # noqa: E402,F401

from tests._mobile_env import (  # noqa: E402
    setup_engine_env,
    import_engine,
    snapshot_host_modules,
    restore_host_modules,
)

# Bind names at import for static checkers, then restore host modules so
# collection leaves no mocked aqt/Ankimon behind. The autouse fixture
# re-establishes the env + re-binds MobileBridge before this module's tests.
_snap = snapshot_host_modules()
setup_engine_env(_src)
from tests.mobile_engine_helpers import MobileBridge  # noqa: E402
restore_host_modules(_snap)


@pytest.fixture(scope="module", autouse=True)
def _engine_env():
    snap = snapshot_host_modules()
    setup_engine_env(_src)
    import_engine(globals())
    yield
    restore_host_modules(snap)


def _insert_pending(db, n=3):
    db.queue_mobile_battles(
        [{"id": 1000 + i, "cid": 1000 + i, "ease": 3, "time": 5000, "type": 1} for i in range(n)]
    )


class TestResolveNext:
    def test_resolve_next_marks_one_resolved(self, temp_env):
        """One encounter's worth of reviews (cards_per_round=2) resolves exactly two."""
        db, _ = temp_env
        _insert_pending(db, n=6)  # 6 reviews, cards_per_round=2 → 3 encounters

        batch = db.get_next_pending_mobile_batch(limit=2)
        assert len(batch) == 2
        for r in batch:
            db.mark_mobile_battle_resolved(r["queue_id"])
        assert db.get_pending_mobile_count() == 4

    def test_resolve_next_returns_done_when_empty(self, temp_env):
        """An empty queue yields an empty batch (the done contract)."""
        db, _ = temp_env
        assert db.get_next_pending_mobile_batch(limit=2) == []

    def test_pending_count_decrements_after_each_resolve(self, temp_env):
        """Each resolve call decrements the pending count by cards_per_round."""
        db, _ = temp_env
        _insert_pending(db, n=4)

        for _ in range(2):
            batch = db.get_next_pending_mobile_batch(limit=2)
            if not batch:
                break
            for r in batch:
                db.mark_mobile_battle_resolved(r["queue_id"])
        assert db.get_pending_mobile_count() == 0


def test_toggle_mobile_companion():
    from aqt import mw
    mock_settings = MagicMock()
    mock_settings.get.return_value = ["id-1", "id-2"]
    mw.settings_obj = mock_settings

    bridge = MobileBridge(window=MagicMock())

    # Toggle existing ID -> should remove it
    res1 = bridge.toggleMobileCompanion("id-1")
    assert res1["success"] is True
    assert "id-1" not in res1["inactive"]
    mock_settings.set.assert_called_with("mobile.inactive_companions", ["id-2"])

    # Toggle new ID -> should add it
    mock_settings.get.return_value = ["id-2"]
    res2 = bridge.toggleMobileCompanion("id-3")
    assert res2["success"] is True
    assert "id-3" in res2["inactive"]
    mock_settings.set.assert_called_with("mobile.inactive_companions", ["id-2", "id-3"])


def test_encounter_seeding_alignment_with_simulation(temp_env):
    """
    simulate_pending_mobile_battles and resolveNext must seed the first encounter
    identically, yielding the same Pokemon name/species/level/shiny.
    """
    from aqt import mw
    db, _ = temp_env
    _insert_pending(db, n=2)  # cards_per_round = 2, so 2 reviews

    mw.ankimon_db = db

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_wishlist": [],
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    mw.settings_obj = settings_mock

    from Ankimon.pyobj.pokemon_obj import PokemonObject
    mw.main_pokemon = PokemonObject(
        type=["Fire"], name="Charizard", id=6, shiny=False, level=50, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="main"
    )
    mw.main_pokemon.attacks = ["Slash"]

    def mock_simulate(companion, enemy, *args, **kwargs):
        enemy.hp = 0
        return ([], None, getattr(companion, "hp", 100), 0, 1)

    from Ankimon.functions.mobile_sync import simulate_pending_mobile_battles, resolve_next

    reviews_rows = db.execute(
        "SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at FROM pending_mobile_battles WHERE resolved = 0"
    ).fetchall()
    reviews_list = [
        {
            "id": r[0], "revlog_id": r[1], "card_id": r[2], "ease": r[3],
            "review_time": r[4], "review_type": r[5], "queued_at": r[6],
        }
        for r in reviews_rows
    ]

    with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
        sim_res = simulate_pending_mobile_battles(
            reviews_list, mw.main_pokemon, settings_mock, None, None, ankimon_db=db
        )
    sim_pokemon = sim_res["caught"][0] if sim_res["caught"] else sim_res["defeated"][0]

    # resolveNext (the web-shell wrapper is deferred; call the engine directly).
    with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
        replay = resolve_next("main", db, settings_mock, None, None, mw.main_pokemon)
    replay_res = replay["result"]

    assert replay_res["enemy_name"] == sim_pokemon["name"]
    assert replay_res["enemy_id"] == sim_pokemon["id"]
    assert replay_res["enemy_level"] == sim_pokemon["level"]
    assert replay_res["enemy_shiny"] == sim_pokemon["shiny"]


def test_resolve_next_companion_override_inactive(temp_env):
    from aqt import mw
    db, _ = temp_env
    _insert_pending(db, n=2)

    pokemon_data = {
        "type": ["Grass"],
        "name": "Bulbasaur",
        "id": 1,
        "shiny": False,
        "level": 15,
        "ability": "Overgrow",
        "gender": "M",
        "growth_rate": "Medium",
        "captured_date": None,
        "tier": "Normal",
        "individual_id": "inactive-bulba",
        "base_stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "attacks": ["Tackle"],
        "base_experience": 64,
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "battle_status": "Fighting",
        "ev_yield": {"hp": 1},
        "nature": "hardy"
    }
    db.save_pokemon(pokemon_data)
    db.save_team([{"individual_id": "inactive-bulba"}])

    mw.ankimon_db = db

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "mobile.inactive_companions": ["inactive-bulba"]
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(key, default)
    mw.settings_obj = settings_mock
    mw.main_pokemon = None
    mw.ankimon_tracker_obj = None

    bridge = MobileBridge(window=MagicMock())

    def mock_simulate(companion, enemy, *args, **kwargs):
        enemy.hp = 0
        return ([], None, getattr(companion, "hp", 100), 0, 1)

    with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
        res = bridge.resolveNext("inactive-bulba")

    assert res is not None
    assert res.get("companion_id") == "inactive-bulba"
    assert res.get("companion_name") == "Bulbasaur"


def test_multi_turn_encounter_seeding_alignment(temp_env):
    """
    If Encounter 0 takes multiple turns (4 reviews), the next generated encounter's
    seed must match the second encounter in the preview list (not skipped/shifted).
    """
    from aqt import mw
    db, _ = temp_env
    _insert_pending(db, n=6)  # cards_per_round = 2, so 6 reviews total

    mw.ankimon_db = db

    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "battle.automatic_battle": 3,
        "battle.auto_catch_wishlist": [],
        "battle.auto_catch_legendary": True,
        "battle.auto_catch_mythical": True,
        "battle.auto_catch_ultra": True,
        "battle.auto_catch_starter": True,
        "battle.auto_catch_mega": True,
        "battle.auto_catch_gmax": True,
        "battle.auto_catch_regional": True,
        "battle.xp_multiplier": 1.0,
        "controls.allow_to_choose_moves": False
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(key, default)
    mw.settings_obj = settings_mock

    from Ankimon.pyobj.pokemon_obj import PokemonObject
    mw.main_pokemon = PokemonObject(
        type=["Fire"], name="Charizard", id=6, shiny=False, level=50, ability="Blaze",
        gender="M", growth_rate="Medium", captured_date=None, tier="Normal", individual_id="main"
    )
    mw.main_pokemon.attacks = ["Slash"]

    # Encounter 0 takes 2 turns (4 reviews), Encounter 1 takes 1 turn (2 reviews).
    turn_counts = {}

    def mock_simulate(companion, enemy, *args, **kwargs):
        eid = getattr(enemy, "individual_id", "default")
        turn_counts[eid] = turn_counts.get(eid, 0) + 1
        if len(turn_counts) == 1:
            if turn_counts[eid] >= 2:
                enemy.hp = 0
            else:
                enemy.hp = 50
        else:
            enemy.hp = 0
        return ([], None, getattr(companion, "hp", 100), 0, 1)

    from Ankimon.functions.mobile_sync import simulate_pending_mobile_battles, resolve_next, commit_replay_outcome

    reviews_rows = db.execute(
        "SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at FROM pending_mobile_battles WHERE resolved = 0"
    ).fetchall()
    reviews_list = [
        {
            "id": r[0], "revlog_id": r[1], "card_id": r[2], "ease": r[3],
            "review_time": r[4], "review_type": r[5], "queued_at": r[6],
        }
        for r in reviews_rows
    ]

    with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
        sim_res = simulate_pending_mobile_battles(
            reviews_list, mw.main_pokemon, settings_mock, None, None, ankimon_db=db
        )

    all_preview_pokemon = sim_res["caught"] + sim_res["defeated"]
    assert len(all_preview_pokemon) == 2, f"Should have 2 preview encounters, got {len(all_preview_pokemon)}"
    preview_enc_0 = all_preview_pokemon[0]
    preview_enc_1 = all_preview_pokemon[1]

    # Now run manual replay (resolve_next)
    turn_counts.clear()

    with patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=mock_simulate):
        replay_res_0 = resolve_next("main", db, settings_mock, None, None, mw.main_pokemon)
        assert replay_res_0["result"]["enemy_name"] == preview_enc_0["name"]

        outcome_0 = replay_res_0["current_pending_outcome"]
        commit_replay_outcome("defeat", outcome_0, db, settings_mock, None, mw.main_pokemon)

        resolved_in_db = db.execute("SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved=1").fetchone()[0]
        assert resolved_in_db == 4

        replay_res_1 = resolve_next("main", db, settings_mock, None, None, mw.main_pokemon)
        assert replay_res_1["result"]["enemy_name"] == preview_enc_1["name"]

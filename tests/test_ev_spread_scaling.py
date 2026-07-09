"""Tier-1 contract for utils.scale_ev_spread_to_level (wild-Pokemon EV fairness).

get_ev_spread hands out full competitive budgets (up to 510 EVs). Unscaled,
every wild Pokemon spawned stat-inflated relative to the player's Pokemon,
which earns EVs a few points per defeat — the root cause of enemy CP/BP
readouts dwarfing the player's in the early game. The scaler caps a wild
Pokemon's total EVs at min(510, level × 5.1) while preserving the spread's
shape and the per-stat 252 cap.
"""

import pytest


@pytest.fixture
def ev_funcs():
    # Imported lazily (repo convention): module-level Ankimon imports at
    # collection time race with other test modules' resources stubs; the
    # autouse conftest fixture restores the real modules around each test.
    from Ankimon.utils import get_ev_spread, scale_ev_spread_to_level

    return get_ev_spread, scale_ev_spread_to_level


STATS = ["hp", "atk", "def", "spa", "spd", "spe"]


def _total(ev):
    return sum(ev.values())


class TestScaleEvSpreadToLevel:
    def test_low_level_shrinks_full_spread(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        ev = {"hp": 0, "atk": 252, "def": 0, "spa": 252, "spd": 4, "spe": 0}
        scaled = scale_ev_spread_to_level(ev, 10)
        assert _total(scaled) <= 51  # 10 × 5.1

    def test_level_100_keeps_full_budget(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        ev = {"hp": 0, "atk": 252, "def": 0, "spa": 252, "spd": 4, "spe": 0}
        scaled = scale_ev_spread_to_level(ev, 100)
        assert scaled == ev  # 508 <= 510 budget → untouched

    def test_shape_preserved(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        # A stat with 0 EVs stays 0; the favoured stats stay favoured.
        ev = {"hp": 0, "atk": 252, "def": 0, "spa": 252, "spd": 4, "spe": 0}
        scaled = scale_ev_spread_to_level(ev, 40)
        assert scaled["hp"] == scaled["def"] == scaled["spe"] == 0
        assert scaled["atk"] == scaled["spa"] > scaled["spd"]

    def test_budget_grows_linearly_with_level(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        ev = {s: 85 for s in STATS}  # 510 total
        totals = [_total(scale_ev_spread_to_level(ev, lvl)) for lvl in (10, 30, 60, 100)]
        assert totals == sorted(totals)
        assert totals[0] < totals[-1]

    def test_per_stat_cap_respected(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        ev = {"hp": 252, "atk": 252, "def": 4, "spa": 0, "spd": 0, "spe": 0}
        for lvl in (1, 25, 50, 75, 100):
            scaled = scale_ev_spread_to_level(ev, lvl)
            assert all(0 <= v <= 252 for v in scaled.values())

    def test_small_spread_untouched(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        # A spread already under budget passes through unchanged.
        ev = {"hp": 10, "atk": 20, "def": 0, "spa": 5, "spd": 0, "spe": 0}
        assert scale_ev_spread_to_level(ev, 20) == ev

    def test_garbage_level_falls_back_to_1(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        ev = {s: 85 for s in STATS}
        scaled = scale_ev_spread_to_level(ev, "not-a-level")
        assert _total(scaled) <= 5  # level 1 budget

    def test_negative_values_clamped(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        ev = {"hp": -10, "atk": 600, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        scaled = scale_ev_spread_to_level(ev, 50)
        assert scaled["hp"] == 0
        assert 0 <= scaled["atk"] <= 252

    def test_per_stat_cap_applies_under_budget_too(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        # One stat over 252 but total within budget must still be capped —
        # the pass-through branch enforces the same invariant as scaling.
        ev = {"hp": 0, "atk": 400, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        assert scale_ev_spread_to_level(ev, 100)["atk"] == 252

    def test_empty_dict_no_division_error(self, ev_funcs):
        _, scale_ev_spread_to_level = ev_funcs
        # total=0 must short-circuit before budget/total division
        assert scale_ev_spread_to_level({}, 10) == {}
        assert scale_ev_spread_to_level({s: 0 for s in STATS}, 0) == {
            s: 0 for s in STATS
        }

    @pytest.mark.parametrize("mode", ["random", "pair", "defense", "uniform"])
    def test_every_generator_mode_lands_within_budget(self, ev_funcs, mode):
        get_ev_spread, scale_ev_spread_to_level = ev_funcs
        for lvl in (1, 12, 47, 100):
            scaled = scale_ev_spread_to_level(get_ev_spread(mode), lvl)
            assert _total(scaled) <= min(510, round(lvl * 5.1))
            assert all(0 <= v <= 252 for v in scaled.values())
            assert set(scaled) == set(STATS)

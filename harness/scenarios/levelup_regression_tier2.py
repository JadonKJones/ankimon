"""Tier-2 regression for PR #630's multi-level-up safeguards.

Boots the genuine Ankimon add-on with real offscreen Qt windows, then exercises
all three production XP attribution paths that previously could freeze or run
away:

* main Pokemon defeat progression
* XP Share progression
* mobile-sync companion progression

Run with a Python environment containing PyQt6, requests, and markdown:

    QT_QPA_PLATFORM=offscreen python -m harness.scenarios.levelup_regression_tier2
"""

from __future__ import annotations

import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from harness.fixtures import build_pokemon
from harness.real_driver import RealDriver

ZERO_EVS = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
MAX_RUNTIME_SECONDS = 5.0


def _feebas(level: int):
    pokemon = build_pokemon(
        {
            "species": "Feebas",
            "level": level,
            "xp": 0,
            "moves": ["Splash", "Tackle"],
            "friendship": 0,
        }
    )
    pokemon.everstone = True
    pokemon.evolution_rejected = True
    pokemon.pokemon_defeated = 0
    pokemon.is_favorite = False
    return pokemon


def _expected_capped_xp(find_experience_for_level, pokemon) -> int:
    return (
        int(
            find_experience_for_level(
                pokemon.growth_rate,
                pokemon.level,
                True,
            )
        )
        - 1
    )


def _assert_fast(label: str, started: float) -> float:
    elapsed = time.perf_counter() - started
    assert elapsed < MAX_RUNTIME_SECONDS, (
        f"{label} took {elapsed:.3f}s; possible level-up loop regression"
    )
    return elapsed


def _install_main(driver: RealDriver, pokemon) -> None:
    driver.services.db.save_main_pokemon(pokemon.to_dict())
    driver.services.main_pokemon = pokemon

    # Keep the production back-compat singleton aligned with the service registry.
    import Ankimon.singletons as singletons

    singletons.main_pokemon = pokemon


def _test_main_progression(driver: RealDriver, start_level: int, xp_award: int) -> None:
    from Ankimon.functions.encounter_functions import save_main_pokemon_progress
    from Ankimon.functions.pokemon_functions import find_experience_for_level

    main = _feebas(start_level)
    enemy = build_pokemon({"species": "Magikarp", "level": 5, "moves": ["Splash"]})
    _install_main(driver, main)
    driver.events.reset()

    started = time.perf_counter()
    result_level = save_main_pokemon_progress(
        main,
        enemy,
        xp_award,
        driver.services.achievements,
        driver.services.logger,
        driver.services.evo_window,
    )
    elapsed = _assert_fast(f"main progression from level {start_level}", started)

    events = driver.drain_events()
    level_events = [event for event in events if event["type"] == "levelup"]
    xp_tooltips = [
        event
        for event in events
        if event["type"] == "tooltip" and "has gained" in event.get("message", "")
    ]
    persisted = driver.services.db.get_main_pokemon()

    assert result_level == start_level + 10
    assert main.level == start_level + 10
    assert len(level_events) == 10
    expected_xp = _expected_capped_xp(find_experience_for_level, main)
    assert main.xp == expected_xp
    assert persisted["level"] == main.level
    assert persisted["xp"] == main.xp

    spent_xp = sum(
        int(find_experience_for_level(main.growth_rate, level, True))
        for level in range(start_level, start_level + 10)
    )
    discarded_xp = xp_award - spent_xp - main.xp
    final_threshold = expected_xp + 1

    print(
        f"main Lv{start_level}: OK -> Lv{main.level}, xp={main.xp}, "
        f"discarded={discarded_xp}, events={len(level_events)}, {elapsed:.3f}s"
    )

    assert xp_tooltips, "main progression emitted no XP summary tooltip"
    assert str(final_threshold) in xp_tooltips[-1]["message"], (
        "XP tooltip uses a stale threshold; "
        f"expected {final_threshold}, got {xp_tooltips[-1]['message']!r}"
    )


def _test_xp_share(driver: RealDriver) -> None:
    from Ankimon.functions.pokemon_functions import find_experience_for_level
    from Ankimon.functions.trainer_functions import xp_share_gain_exp

    target = _feebas(52)
    driver.services.db.save_pokemon(target.to_dict())
    driver.services.settings.set("trainer.xp_share", target.individual_id)

    started = time.perf_counter()
    xp_share_gain_exp(
        driver.services.logger,
        driver.services.settings,
        driver.services.evo_window,
        driver.services.main_pokemon.individual_id,
        2_000_000,  # XP Share halves this to the one-million-XP regression case.
        target.individual_id,
    )
    elapsed = _assert_fast("XP Share progression", started)

    persisted = driver.services.db.get_pokemon(target.individual_id)
    assert persisted["level"] == 62
    expected_xp = int(find_experience_for_level(target.growth_rate, 62, True)) - 1
    assert persisted["xp"] == expected_xp

    print(
        f"XP Share: OK -> Lv{persisted['level']}, xp={persisted['xp']}, "
        f"{elapsed:.3f}s"
    )


def _test_mobile_sync(driver: RealDriver) -> None:
    from Ankimon.functions.mobile_sync import _attribute_xp_and_evs_to_companion
    from Ankimon.functions.pokemon_functions import find_experience_for_level

    target = _feebas(52)
    driver.services.db.save_pokemon(target.to_dict())

    started = time.perf_counter()
    _attribute_xp_and_evs_to_companion(
        target.individual_id,
        1_000_000,
        ZERO_EVS,
        driver.services.settings,
        battles_fought=0,
        db=driver.services.db,
        logger=driver.services.logger,
    )
    elapsed = _assert_fast("mobile-sync progression", started)

    persisted = driver.services.db.get_pokemon(target.individual_id)
    assert persisted["level"] == 62
    expected_xp = int(find_experience_for_level(target.growth_rate, 62, True)) - 1
    assert persisted["xp"] == expected_xp

    print(
        f"mobile sync: OK -> Lv{persisted['level']}, xp={persisted['xp']}, "
        f"{elapsed:.3f}s"
    )


def main() -> int:
    driver = RealDriver(
        first_encounter=False,
        settings_overrides={
            "misc.remove_level_cap": True,
            "controls.allow_to_choose_moves": False,
            "gui.pop_up_dialog_message_on_defeat": False,
            "audio.sounds": False,
            "audio.sound_effects": False,
            "trainer.xp_share": None,
        },
    )

    from Ankimon.functions.pokemon_functions import find_experience_for_level

    high_level_costs = [
        int(find_experience_for_level("erratic", level, True))
        for level in range(140, 251)
    ]
    assert min(high_level_costs) > 0
    print(
        "erratic curve Lv140-250: OK "
        f"(min={min(high_level_costs)}, max={max(high_level_costs)})"
    )

    # Original runaway report: level-52 Feebas receiving one million XP.
    _test_main_progression(driver, start_level=52, xp_award=1_000_000)

    # Original freeze region: erratic growth above level 142.
    _test_main_progression(driver, start_level=143, xp_award=10_000_000)

    _test_xp_share(driver)
    _test_mobile_sync(driver)

    print("levelup_regression_tier2: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

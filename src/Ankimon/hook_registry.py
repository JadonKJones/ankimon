from .singletons import (
    enemy_pokemon,
    main_pokemon,
    ankimon_tracker_obj,
    get_test_window,
    get_evo_window,
    logger,
    achievements,
    trainer_card,
    reviewer_obj,
)
from .functions.encounter_functions import (
    catch_pokemon,
    kill_pokemon,
    new_pokemon,
)

catch_pokemon_hooks = []
defeat_pokemon_hooks = []


def add_catch_pokemon_hook(func):
    catch_pokemon_hooks.append(func)


def add_defeat_pokemon_hook(func):
    defeat_pokemon_hooks.append(func)


def CatchPokemonHook(collected_pokemon_ids):
    if enemy_pokemon.hp < 1:
        catch_pokemon(
            enemy_pokemon,
            ankimon_tracker_obj,
            logger,
            "",
            collected_pokemon_ids,
            achievements,
        )
        # Resolve while this is still the defeated encounter. new_pokemon()
        # mutates the enemy singleton, so its identity cannot be checked later.
        from .battle_loop import _resolve_main_faint_for_enemy

        _resolve_main_faint_for_enemy(main_pokemon, enemy_pokemon)
        new_pokemon(
            enemy_pokemon,
            get_test_window(),
            ankimon_tracker_obj,
            reviewer_obj,
            update_hud=True,
        )
    # list(): a hook may unregister itself from this very bucket while it
    # runs (the double-faint resolver does), and removing the element at the
    # current index makes the iterator skip the NEXT hook. These buckets are
    # public to other add-ons via mw.add_catch_pokemon_hook, so that
    # skipped hook could belong to anyone.
    for hook in list(catch_pokemon_hooks):
        hook()


def DefeatPokemonHook():
    if enemy_pokemon.hp < 1:
        kill_pokemon(
            main_pokemon,
            enemy_pokemon,
            get_evo_window(),
            logger,
            achievements,
            trainer_card,
        )
        from .battle_loop import _resolve_main_faint_for_enemy

        _resolve_main_faint_for_enemy(main_pokemon, enemy_pokemon)
        new_pokemon(
            enemy_pokemon,
            get_test_window(),
            ankimon_tracker_obj,
            reviewer_obj,
            update_hud=True,
        )
    # list(): a hook may unregister itself from this very bucket while it
    # runs (the double-faint resolver does), and removing the element at the
    # current index makes the iterator skip the NEXT hook. These buckets are
    # public to other add-ons via mw.add_defeat_pokemon_hook, so that
    # skipped hook could belong to anyone.
    for hook in list(defeat_pokemon_hooks):
        hook()

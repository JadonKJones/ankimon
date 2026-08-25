"""A Pokémon's ``battle_status`` transitioning to "fainted" used to fall
through the generic status-effect message path (no ``status_fainted_apply``
translation key exists), landing on the ``status_unknown_apply`` template —
"{pokemon_name} is affected by {status_name}!" — producing the nonsensical
"X is affected by Fainted!" battle-log line. Fainting already has its own
dedicated message elsewhere (enemy_pokemon_fainted / player_pokemon_fainted),
so the fix skips the generic status-apply/-remove branches entirely for
"fainted".
"""

from unittest.mock import MagicMock

from Ankimon.functions.battle_functions import _process_battle_effects


class _FakePokemon:
    def __init__(self, name):
        self.display_name = name
        self.battle_status = "fighting"
        self.volatile_status = set()


def _translator_spy():
    translator = MagicMock()
    translator.translate.side_effect = lambda key, **kwargs: f"[{key}]"
    return translator


def test_status_transition_to_fainted_emits_no_generic_status_message():
    main_pokemon = _FakePokemon("Pikachu")
    enemy_pokemon = _FakePokemon("Rattata")
    translator = _translator_spy()

    changes = [
        {"key": "opponent.status", "before": "fighting", "after": "fainted"},
    ]

    messages = _process_battle_effects(
        instructions=[],
        translator=translator,
        main_pokemon=main_pokemon,
        enemy_pokemon=enemy_pokemon,
        current_state=None,
        changes=changes,
    )

    # No message should have been generated at all for this transition —
    # not "affected by Fainted", not any other status_*_apply template.
    assert messages == []
    requested_keys = [call.args[0] for call in translator.translate.call_args_list]
    assert not any("fainted" in key.lower() for key in requested_keys)
    assert not any("unknown_apply" in key for key in requested_keys)


def test_status_transition_from_fainted_to_fighting_emits_no_recover_message():
    """A fresh encounter resetting fainted -> fighting shouldn't print
    'X recovers from Fainted!' either."""
    main_pokemon = _FakePokemon("Pikachu")
    main_pokemon.battle_status = "fainted"
    enemy_pokemon = _FakePokemon("Rattata")
    translator = _translator_spy()

    changes = [
        {"key": "user.status", "before": "fainted", "after": "fighting"},
    ]

    messages = _process_battle_effects(
        instructions=[],
        translator=translator,
        main_pokemon=main_pokemon,
        enemy_pokemon=enemy_pokemon,
        current_state=None,
        changes=changes,
    )

    assert messages == []
    requested_keys = [call.args[0] for call in translator.translate.call_args_list]
    assert not any("fainted" in key.lower() for key in requested_keys)


def test_status_transition_to_a_real_status_still_emits_a_message():
    """Sanity check the fix didn't just silence ALL status messages —
    a normal status like poison should still produce one."""
    main_pokemon = _FakePokemon("Pikachu")
    enemy_pokemon = _FakePokemon("Rattata")
    translator = _translator_spy()

    changes = [
        {"key": "opponent.status", "before": "fighting", "after": "psn"},
    ]

    messages = _process_battle_effects(
        instructions=[],
        translator=translator,
        main_pokemon=main_pokemon,
        enemy_pokemon=enemy_pokemon,
        current_state=None,
        changes=changes,
    )

    assert len(messages) == 1

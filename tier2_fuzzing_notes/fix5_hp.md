# Issue 5: HP values going out of bounds or resolving to strings

## Description
The fuzzer caused `AssertionError: enemy HP out of range: 318/23` or similar crashes where HP would end up negative or higher than the maximum HP.

## Root Cause
In `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`, the changes from the poke-engine state back to Ankimon's `PokemonObject` were done with simple assignments:
```python
main_pokemon.hp = state.user.active.hp
enemy_pokemon.hp = state.opponent.active.hp
```
There were no clamps to ensure HP stayed within `0` and `max_hp`. Additionally, there were cases where HP could become a `NoneType` or a string during fuzzing due to bad setups, causing issues.

## Proposed Fix
Clamp the HP using `max(0, min(current_hp, max_hp))` and ensure the values are integers.

```python
        user_hp = state.user.active.hp if state.user.active.hp is not None else 0
        opponent_hp = state.opponent.active.hp if state.opponent.active.hp is not None else 0

        main_pokemon_max_hp = main_pokemon.max_hp if main_pokemon.max_hp is not None else 0
        main_pokemon.hp = max(0, min(int(user_hp), int(main_pokemon_max_hp)))
        main_pokemon.current_hp = main_pokemon.hp

        enemy_max_hp = enemy_pokemon.max_hp if enemy_pokemon.max_hp is not None else 0
        if int(enemy_max_hp) == 0:
            enemy_pokemon.hp = max(0, int(opponent_hp))
        else:
            enemy_pokemon.hp = max(0, min(int(opponent_hp), int(enemy_max_hp)))
        enemy_pokemon.current_hp = enemy_pokemon.hp
```

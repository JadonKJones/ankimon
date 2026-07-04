# Issue 2: Invalid affected_side 'adjacentAlly' in instruction generator

## Description
When running the battle engine simulation with random moves and setups, `AssertionError: error event during answer: ... 'Invalid affected_side: adjacentAlly'` or similar crashes occurred. The engine logs showed it couldn't resolve the string 'adjacentAlly'.

## Root Cause
In `src/Ankimon/poke_engine/instruction_generator.py`, the constant list `same_side_strings` didn't include `'adjacentAlly'` and `opposing_side_strings` didn't include `'adjacentFoe'`, which are standard move targets used by the underlying showdown move JSONs. When an instruction resolved to this affected side, it hit the `logger.critical("Invalid affected_side: {}".format(affected_side))` path, returning empty or failing.

## Proposed Fix
Update `same_side_strings` in `instruction_generator.py` to include `'adjacentAlly'` and update `opposing_side_strings` to include `'adjacentFoe'`.

```python
same_side_strings = [
    constants.SELF,
    constants.ALLY_SIDE,
    'adjacentAlly'
]

opposing_side_strings = [
    constants.NORMAL,
    constants.OPPONENT,
    constants.FOESIDE,
    constants.ALL_ADJACENT_FOES,
    constants.ALL_ADJACENT,
    constants.ALL,
    'adjacentFoe',
]
```

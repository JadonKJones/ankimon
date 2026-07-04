# Issue 3: KeyError crashes for random invalid move strings in poke_engine

## Description
The fuzzer naturally generates bogus move strings like `'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'` and `'hyperbeam!!!'` or even `''`. When the Ankimon hooks passed these bogus strings into the `poke_engine` (such as in `objects.py` or `find_state_instructions.py`), it resulted in `KeyError` crashes because the code blindly accessed the `all_move_json` dictionary.

## Root Cause
In `src/Ankimon/poke_engine/objects.py` inside `calculate_burn_multiplier`, it iterates through a pokemon's moves and checks:
`all_move_json[m[constants.ID]][constants.CATEGORY] == constants.PHYSICAL`
If the move is invalid or empty, this throws a `KeyError`.

Similarly, in `src/Ankimon/poke_engine/find_state_instructions.py` inside `lookup_move`:
`return all_move_json[move_name.lower()]`
This throws a `KeyError` if the move isn't found.

## Proposed Fix
Use `.get()` checks and `.get(constants.CATEGORY)` checks instead of direct indexing.
For `objects.py`:
```python
burn_multiplier = len([m for m in self.moves if m.get(constants.ID) in all_move_json and all_move_json[m[constants.ID]].get(constants.CATEGORY) == constants.PHYSICAL])
```

For `find_state_instructions.py`:
```python
return all_move_json.get(move_name.lower(), all_move_json.get("splash"))
```

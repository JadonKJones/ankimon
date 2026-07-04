# Issue 4: Type coercion crashes for trainer.cash string values

## Description
The fuzzer occasionally injects invalid types like a string `"x"` or a negative integer `-5` into `trainer.cash`. When this happens, a `TypeError` occurs later in the invariants check or battle math: `'>=' not supported between instances of 'str' and 'int'`. Additionally, there was a failure where `negative cash: -5` failed an assertion.

## Root Cause
In `src/Ankimon/pyobj/settings.py`, the `_apply_type_coercion` function was coercing specific values to `int`, but it was skipping `trainer.cash`. Also, the coercion logic was throwing a warning on `ValueError` but leaving the invalid string value intact in the `config` dictionary, breaking assumptions downstream. Finally, `trainer.cash` was not bounds-checked to prevent negative values.

## Proposed Fix
Add `trainer.cash` to `keys_to_coerce_to_int` in `_apply_type_coercion` and strengthen the coercion loop to actively default to `0` if an invalid string or type is provided, and clamp negative cash to `0`.

```python
                try:
                    config[key] = int(config[key])
                    if config[key] < 0 and key == "trainer.cash":
                        config[key] = 0
                except (ValueError, TypeError):
                    print(
                        f"Ankimon: Warning: Could not convert '{config[key]}' for key '{key}' to int."
                    )
                    # If it's a completely invalid type like string 'x', coerce to a sensible default
                    if key == "trainer.cash":
                        config[key] = 0
                    elif isinstance(config[key], str):
                        # Ensure we don't leave invalid strings in keys that expect integers
                        config[key] = 0
```

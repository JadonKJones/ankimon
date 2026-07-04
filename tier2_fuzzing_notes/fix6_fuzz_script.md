# Issue 6: Fuzz script environment issues

## Description
The fuzz script (`harness/scenarios/fuzz.py`) occasionally threw warnings or hit bugs itself rather than Ankimon's code, or was relying on implicit assumptions about `PYTHONPATH`.

## Root Cause
Fuzzing script did not inject `requests` properly, or have an automatic `PYTHONPATH` resolution for external testing if run in isolation outside of `pytest` or Anki.

## Proposed Fix
Provide a robust runner shell script or document that `PYTHONPATH=src` and `pip install requests` must be used to run the fuzz tests successfully.

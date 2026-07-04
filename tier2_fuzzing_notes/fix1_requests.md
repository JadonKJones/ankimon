# Issue 1: Missing requests module during fuzzing

## Description
During headless fuzzing, the `requests` module was throwing a `ModuleNotFoundError` in several test suites, primarily crashing test collections and stopping tests from running properly. The headless fuzz script `harness/scenarios/fuzz.py` and the main `conftest.py` use it directly or via some imports inside Ankimon.

## Root Cause
`requests` is imported in `utils.py` and `error_handler.py`, and when running fuzzing tests under a sterile environment or via pytest, the library was not available because it wasn't strictly enforced or installed in the CI container environment or test runner context.

## Proposed Fix
Make sure that `requests` is properly listed as a test or runtime dependency and ensure `pip install requests` is executed before running fuzzing/tests in CI/CD or the testing documentation. (In this session, `requests` was simply installed via pip).
